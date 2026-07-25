"""arc_selection_learned_relevance_glassbox_v1 -- LEARNED (glass-box) vs FIXED selection scoring.

The selection wall (VET 29544): retrieval REACHES the facts (wide RR pool recall@100=0.69), the
combiner USES them (oracle gold->combiner Challenge ~0.71), but SELECTION cannot ISOLATE the gold
from the contains-gold pool -- and NO fixed brain-faithful signal beats the gate (sel_gold_precision
~0.12 vs oracle ~0.97; coherence WORSE than random). MEASURED@disk:
  wide pool recall@100 (SC)             = 0.6911
  E_wide_gate Challenge (current gate)  = 0.3306
  E_oracle  Challenge (gold->combiner)  = 0.7125
    @data/exp_arc_retrieval_max_recall_ksweep_reretrieval_v1/metrics.json
  A_gate Challenge sel_gold_precision   ~= 0.12 (fixed-signal wall)
    @data/exp_arc_selection_precision_coherence_subset_v1/metrics.json

The VET flagged TWO levers beyond a surface gate: (a) LEARNED relevance (CHEAPER -- THIS cell),
(b) grounded/richer meaning (DEEPER -- next if this plateaus). This cell tests (a): can a LEARNED
(not fixed) glass-box relevance scorer isolate the gold facts from the pool better than the fixed
thin-meaning signals?

ONE variable = LEARNED-vs-FIXED selection scoring. The UNCHANGED WIDE RR pool (mr.reformulate_seeds/
_rownorm_scores, IMPORTED) and the UNCHANGED bind+bundle combiner (agg.aggregate 'bundle', IMPORTED)
are held FIXED. The ONLY new piece is a GLASS-BOX learned scorer that weights INTERPRETABLE relevance
FEATURES and picks K_SEL facts from the pool.

BRAIN-FAITHFUL: the brain LEARNS relevance from experience/reward (dopamine-tuned associative
strengths), not fixed similarity. The learner here is a linear readout trained by the DELTA-RULE /
reward-prediction-error (predicted-relevance minus is-gold reward) over interpretable features --
the same RPE-gated associative-weighting primitive as the PFC-gate CFRPE cells + the LEARNER MODULE
(29487). GLASS-BOX INVARIANT (HARD): the runtime scorer is learned WEIGHTS over interpretable
FEATURES (cos-to-stem, cos-to-each-choice, discriminative margin, coherence, lexical overlap,
retrieval score, RIF-suppression, degree, negation), NOT an opaque neural blob. The decision stays
legible: the per-feature weight vector + per-fact feature contributions are logged.

NO LEAK: questions split TRAIN/TEST (stratified by source). The learned scorer trains on TRAIN
(label = is-this-pool-fact a gold central fact) and is EVALUATED on TEST. The scorer NEVER sees the
TEST correct_index or TEST gold at inference; gold is used for the TRAIN LABEL, the ORACLE arm, and
EVALUATION only. ALL fixed arms are also evaluated on the SAME TEST split (fair comparison).

Arms (selection scoring is the ONLY variable; pool + combiner UNCHANGED):
  A_gate  -- fixed incumbent gate gate.gate_scores          [BASELINE, on TEST]
  LEARNED -- glass-box learned relevance weighting          [MECHANISM, trained on TRAIN, eval TEST]
  REL     -- fixed goal-biased relevance (reference)        [on TEST]
  COH     -- fixed coherence-subset settle (reference)      [on TEST]
  DISC    -- fixed discriminative margin (reference)        [on TEST]
  RND     -- K_SEL random pool facts                        [MUST-FAIL control, on TEST]
  ORACLE  -- gold central facts -> combiner                 [CEILING ~0.71, on TEST]

PRIMARY = end-to-end ARC Challenge (+Easy) accuracy on the TEST split, judged on the ANSWER; McNemar
LEARNED vs A_gate. SECONDARY = sel_gold_precision (does LEARNED pick more gold -- toward oracle 0.97?).
HARD_PASS = LEARNED beats A_gate on the answer by the pre-reg significant margin AND raises
sel_gold_precision materially above the gate's ~0.12; random does NOT. MIDDLE = LEARNED lifts
precision/answer modestly but plateaus below oracle. HARD_FAIL = LEARNED ~= the fixed gate -> learning
cannot squeeze relevance from the THIN features -> the ceiling is the MEANING itself -> the deep lever
is grounded/richer meaning (report STRAIGHT -- the honest ceiling test that decides learned-vs-grounding).
HONEST CEILING CAVEAT: LEARNED trains on the SAME thin GloVe/WordNet features as the fixed signals; if
the features fundamentally lack the gold-vs-lure signal, learning is CEILING-LIMITED and a plateau
redirects to grounded meaning. Overfit check: train-vs-test gap reported.

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT
remote-portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng,
sorted iteration, zero-init full-batch GD, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL RR wide pool + REAL feature matrix +
#   REAL glass-box logreg train at tiny scale + UNCHANGED combiner; a PLANTED learnable-separation case
#   asserts the LEARNED scorer FIRES (recovers gold that NO single fixed feature isolates => learned
#   weighting load-bearing); arms-differ; no-leak (train/test disjoint)
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration + zero-init GD; no hash()
# - baseline_in_band + AG-guard on A_gate TEST challenge (headroom to the 0.71 ceiling)
# - storage = SHARDED (each fact = own vector + own graph node; no superposition)
# - GLASS-BOX INVARIANT: linear weights over named features; weights + per-fact contributions logged
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

# reuse (UNCHANGED): WIDE RR pool builder, current gate, bind+settle combiner, PPR graph, arc helpers,
# the fixed selection signals. The ONLY new code is the GLASS-BOX LEARNED relevance scorer.
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr
from experiments import exp_arc_retrieval_max_recall_ksweep_reretrieval_v1 as mr
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as gate
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_selection_precision_coherence_subset_v1 as fixedsel
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_selection_learned_relevance_glassbox_v1"
SEED = 20260728

# ---- selection hyperparams (UNCHANGED pool + combiner) ----
K_WIDE = mr.K_WIDE          # UNCHANGED wide re-retrieval pool the scorer selects FROM (=100)
RR_TOP_T = mr.RR_TOP_T      # UNCHANGED re-retrieval reformulation depth
K_SEL = gate.K_SEL          # UNCHANGED clean-fact selection width (Cowan-4; =4)
MU_SUPP = gate.MU_SUPP      # UNCHANGED suppression weight (used by A_gate baseline + as a feature)
SETTLE_T = agg.SETTLE_T
SETTLE_EPS = agg.SETTLE_EPS
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# ---- glass-box learner hyperparams (author-designed a priori; delta-rule / RPE linear readout) ----
L2_REG = 1.0                # L2 penalty (fixed a priori; NOT tuned; overfit checked via train/test gap)
GD_ITERS = 400              # full-batch gradient-descent iterations (zero-init => deterministic)
GD_LR = 0.5                 # learning rate (fixed a priori)
SPLIT_FRAC_TRAIN = 0.5      # stratified-by-source train fraction
FEATURE_NAMES = (
    "g_stem",        # relu cos(fact, stem)                      [gate ingredient]
    "mean_choice",   # mean_c relu cos(fact, choice_c)           [relevance ingredient]
    "max_choice",    # max_c cos(fact, choice_c)
    "g_disc",        # choice-separating margin max_c-2nd_max_c  [gate/DISC ingredient]
    "coh",           # Kintsch/ECHO settled coherence activation [COH ingredient]
    "surf_pull",     # jaccard lexical overlap fact-words vs stem[gate ingredient]
    "rr_score",      # wide-RR retrieval pool score (row-normed) [retrieval strength]
    "lure_penalty",  # RIF suppression signal (surf * lure_align)[gate ingredient; learn its sign]
    "degree",        # #content-words in fact (specificity)
    "neg_cue",       # #negation tokens in fact sentence
)
NEG_TOKENS = frozenset({"no", "not", "never", "cannot", "cant", "without",
                        "none", "neither", "nor", "nothing", "n't", "dont", "doesnt"})

# ---- bands (author-designed a priori; PRIMARY = TEST-split Challenge accuracy, judged on ANSWER) ----
# gap to close = oracle-gold Challenge (~0.71) - current gate Challenge (~0.33) ~= 0.38.
HP_CHAL_LIFT = 0.05    # LEARNED - A_gate on TEST Challenge answer accuracy (>= ~13% of the 0.38 gap)
HP_SELPREC_MIN = 0.20  # LEARNED TEST-Challenge sel_gold_precision (materially above gate ~0.12; ~1.7x)
MB_CHAL_LIFT = 0.02    # positive-but-sub-HP band floor
RANDOM_MAX = 0.02      # RND - A_gate on Challenge must be <= this (fewer-facts is not the driver)
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95 # A_gate challenge >= this -> vacuous (no headroom)
OVERFIT_GAP_WARN = 0.15  # |train - test| LEARNED Challenge acc above this -> overfit WARN (diagnostic)

_T0 = [0.0]


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
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
# glass-box learned relevance scorer (delta-rule / RPE linear readout; CFRPE-family)
# ---------------------------------------------------------------------------
def _minmax_cols(X):
    """Per-column min-max normalize a [P,F] feature matrix to [0,1] (flat col -> zeros).
    Within-question relative encoding (matches the fixed COMB arm convention; scale-free ranking)."""
    X = np.asarray(X, dtype=np.float64)
    if X.size == 0:
        return X
    lo = X.min(axis=0, keepdims=True)
    hi = X.max(axis=0, keepdims=True)
    rng = hi - lo
    out = np.where(rng > 1e-12, (X - lo) / np.where(rng > 1e-12, rng, 1.0), 0.0)
    return out.astype(np.float64)


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))


def train_glassbox_relevance(X, y, l2=L2_REG, iters=GD_ITERS, lr=GD_LR):
    """Glass-box learned relevance = linear readout trained by the DELTA-RULE / reward-prediction-error.
      X : [n, F] interpretable features (per-question min-max normalized rows)
      y : [n] in {0,1}, reward = is-this-pool-fact a gold central fact
    Update g = (p - y) is the RPE (predicted relevance minus reward); X.T @ g is the associative
    weight update (CFRPE-family / LEARNER MODULE). Zero-init full-batch GD => fully deterministic.
    Class-balanced (rare gold up-weighted) so the boundary sharpens on the minority gold rows.
    Returns (w [F], b) -- the INSPECTABLE weight vector + intercept."""
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n, F = X.shape
    w = np.zeros(F, dtype=np.float64)   # zero init (deterministic, glass-box)
    b = 0.0
    npos = float(max(1.0, y.sum()))
    nneg = float(max(1.0, n - y.sum()))
    sw = np.where(y > 0.5, nneg / npos, 1.0)     # up-weight rare gold (class balance)
    sw = sw / sw.mean()
    for _ in range(iters):
        p = _sigmoid(X @ w + b)
        g = (p - y) * sw                          # reward-prediction-error, class-weighted
        gw = X.T @ g / n + l2 * w / n             # + L2 shrinkage
        gb = float(g.mean())
        w -= lr * gw
        b -= lr * gb
    return w, b


def learned_score(X, w, b):
    """Inference relevance score for a question's pool: linear readout X@w (+b). Higher = more relevant.
    Intercept b does not change WITHIN-question top-K ranking but is kept for completeness."""
    if X.size == 0:
        return np.zeros(0, dtype=np.float64)
    return (np.asarray(X, dtype=np.float64) @ np.asarray(w, dtype=np.float64) + b).astype(np.float64)


def _topk_idx(scores, k):
    return gate._topk_idx(np.asarray(scores, dtype=np.float64), k)


# ---------------------------------------------------------------------------
# feature assembly (interpretable; drawn from the SAME thin signals as the fixed arms)
# ---------------------------------------------------------------------------
def _neg_count(sentence):
    toks = sentence.lower().replace("'", "").split()
    return float(sum(1 for t in toks if t in NEG_TOKENS))


def question_features(fh_pool, stem_vec, choice_hd, gs, coh, rr_scores, degrees, neg_counts):
    """Assemble the [P, F] RAW feature matrix for one question's pool.
    All features are interpretable and reuse the fixed-signal primitives (gate ingredients + coherence
    + retrieval score + degree + negation). Column order = FEATURE_NAMES. Answer-agnostic."""
    P = fh_pool.shape[0]
    if P == 0:
        return np.zeros((0, len(FEATURE_NAMES)), dtype=np.float64)
    cc = (fh_pool @ choice_hd.T).astype(np.float64)                # [P,C]
    mean_choice = np.maximum(cc, 0.0).mean(axis=1) if cc.shape[1] else np.zeros(P)
    max_choice = cc.max(axis=1) if cc.shape[1] else np.zeros(P)
    X = np.stack([
        gs["g_stem"],          # 1
        mean_choice,           # 2
        max_choice,            # 3
        gs["g_disc"],          # 4
        np.asarray(coh, dtype=np.float64),      # 5
        gs["surf_pull"],       # 6
        np.asarray(rr_scores, dtype=np.float64),# 7
        gs["lure_penalty"],    # 8
        np.asarray(degrees, dtype=np.float64),  # 9
        np.asarray(neg_counts, dtype=np.float64),# 10
    ], axis=1).astype(np.float64)
    assert X.shape == (P, len(FEATURE_NAMES)), "feature matrix shape mismatch"
    return X


# ---------------------------------------------------------------------------
# self-test: planted learnable-separation discriminator + real code path + no-leak + arms-differ
# ---------------------------------------------------------------------------
def _planted_learned_separation_discriminator():
    """Synthetic feature case proving the LEARNED weighting is load-bearing + reachable.
    Setup: GOLD facts are MODERATE on BOTH feature A and feature B (co-activated); LURE facts each
    SPIKE exactly ONE feature (half spike A, half spike B) and are near-zero on the other. So:
      - ANY single fixed feature (rank by A alone, or B alone) surfaces the spiking LURES, drowning gold.
      - A LEARNED scorer with POSITIVE weight on BOTH A and B ranks the co-activated GOLD on top.
    The learner is TRAINED on a TRAIN block (gold labelled) and must recover gold on a DISJOINT TEST
    block (no leak). => learned weighting flips what every single fixed feature drowns; reachable."""
    rng = np.random.default_rng(31)
    F = len(FEATURE_NAMES)
    ia, ib = 0, 3   # use two real feature slots (g_stem, g_disc) as A and B

    def make_pool():
        # 2 gold (mod A AND mod B), 4 lures (2 spike A only, 2 spike B only); other features carry
        # NO signal (zero) so ONLY the A/B co-activation pattern separates gold -> a single feature
        # cannot isolate gold, a LEARNED positive-weight-on-both can.
        X = np.zeros((6, F), dtype=np.float64)
        # gold rows 0,1: moderate on BOTH A and B
        X[0, ia] = 0.60; X[0, ib] = 0.60
        X[1, ia] = 0.55; X[1, ib] = 0.55
        # lure rows 2,3: spike A only (B=0)
        X[2, ia] = 0.95; X[2, ib] = 0.0
        X[3, ia] = 0.90; X[3, ib] = 0.0
        # lure rows 4,5: spike B only (A=0)
        X[4, ia] = 0.0; X[4, ib] = 0.95
        X[5, ia] = 0.0; X[5, ib] = 0.90
        y = np.array([1, 1, 0, 0, 0, 0], dtype=np.float64)
        return _minmax_cols(X), y

    # single fixed feature drowns gold (top-2 by A alone or B alone are lures, not gold)
    Xtr, ytr = make_pool()
    top_A = set(int(i) for i in _topk_idx(Xtr[:, ia], 2))
    top_B = set(int(i) for i in _topk_idx(Xtr[:, ib], 2))
    assert not (top_A <= {0, 1}) and not (top_B <= {0, 1}), \
        f"planted: a single feature already isolates gold (setup weak) A={top_A} B={top_B}"

    # train on several TRAIN pools, test on a DISJOINT pool (no leak)
    Xrows, yrows = [], []
    for _ in range(20):
        Xp, yp = make_pool()
        Xrows.append(Xp); yrows.append(yp)
    Xtrain = np.concatenate(Xrows, axis=0)
    ytrain = np.concatenate(yrows, axis=0)
    w, b = train_glassbox_relevance(Xtrain, ytrain)
    assert w[ia] > 0 and w[ib] > 0, f"planted: learned weights on A,B not both positive w={w}"

    Xtest, ytest = make_pool()   # fresh draw, never in train
    s = learned_score(Xtest, w, b)
    top_learned = set(int(i) for i in _topk_idx(s, 2))
    assert top_learned == {0, 1}, f"planted: learned scorer did not recover gold; top={top_learned}"
    # arms differ: learned selection != single-feature selection
    assert top_learned != top_A and top_learned != top_B, "planted: learned == a single-feature arm"
    # determinism
    w2, b2 = train_glassbox_relevance(Xtrain, ytrain)
    assert np.allclose(w, w2) and abs(b - b2) < 1e-12, "planted: training non-deterministic"
    return True


def self_test():
    print("[self-test] planted learnable-separation discriminator "
          "(LEARNED recovers gold that NO single fixed feature isolates; no-leak train/test) ...",
          flush=True)
    _planted_learned_separation_discriminator()

    print("[self-test] REAL encoder + REAL RR wide pool + REAL feature matrix + glass-box logreg + "
          "UNCHANGED combiner ...", flush=True)
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
    degrees_all = [float(len(t)) for t in fact_terms]
    neg_all = [_neg_count(s) for s in store_sents]
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

    # REAL fixed signals + gate (UNCHANGED) --------------------------------------------------------
    lure_set, _ = gate.standout_lure_choices(stem_words, q["choices"])
    fw = [fact_word_sets[i] for i in pool_idx.tolist()]
    gs = gate.gate_scores(fh_pool, fw, stem_words, STEM, choice_hd, lure_set)
    coh = fixedsel.coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ, 0.0))
    rr_scores = F_RR[0][pool_idx]
    degs = [degrees_all[i] for i in pool_idx.tolist()]
    negs = [neg_all[i] for i in pool_idx.tolist()]

    # REAL feature matrix + glass-box train + inference --------------------------------------------
    Xraw = question_features(fh_pool, STEM, choice_hd, gs, coh, rr_scores, degs, negs)
    assert Xraw.shape == (pool_idx.size, len(FEATURE_NAMES)), "real: feature matrix shape mismatch"
    Xn = _minmax_cols(Xraw)
    # tiny synthetic label (facts 0,1 as "gold") just to exercise the REAL train path end to end
    ylab = np.zeros(pool_idx.size, dtype=np.float64)
    ylab[:min(2, pool_idx.size)] = 1.0
    w, b = train_glassbox_relevance(Xn, ylab)
    assert w.shape[0] == len(FEATURE_NAMES), "real: learned weight vector wrong length"
    s = learned_score(Xn, w, b)
    assert s.shape[0] == pool_idx.size, "real: learned score shape mismatch"

    # UNCHANGED combiner over a learned selection
    sel = pool_idx[_topk_idx(s, K_SEL)]
    fh = SV_store[sel]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
    sc_scores, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc_scores.shape[0] == len(q["choices"]), "real: combiner reuse shape mismatch"

    # determinism
    w_b, b_b = train_glassbox_relevance(Xn, ylab)
    assert np.allclose(w, w_b) and abs(b - b_b) < 1e-12, "real: training non-deterministic"

    # WorldTree parse touch
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    qs = agg.load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    print("[self-test] PASS (planted learnable-separation flips single-feature-drowned gold; real "
          "encoder+RR pool+feature matrix+glass-box logreg+UNCHANGED combiner; determinism; WT parse)",
          flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        # FULL graph (real pool at scale), question subset (pipeline + discriminator-fires gate)
        return {"n_dim": 2048, "limit_easy": 120, "limit_chal": 120}
    # FULL: bounded eval slice to fit one INLINE-LOCAL foreground call (mirrors max-recall/fixed-sel
    # slices that ran ~108s). Train/test split is stratified within this slice.
    return {"n_dim": 2048, "limit_easy": 500, "limit_chal": 600}


ARMS = ("A_gate", "LEARNED", "REL", "COH", "DISC", "RND", "ORACLE")
FIXED_REF_ARMS = ("REL", "COH", "DISC")   # fixed reference signals (context for "beats fixed?")


def _split_train_test(questions):
    """Stratified-by-source deterministic train/test split. Returns boolean masks (train, test)."""
    nQ = len(questions)
    train = np.zeros(nQ, dtype=bool)
    # group question indices by source, sort by qid for determinism, deterministic shuffle, take frac
    by_src = {}
    for qi, q in enumerate(questions):
        by_src.setdefault(q["source"], []).append(qi)
    rng = np.random.default_rng(SEED + 4242)
    for src in sorted(by_src.keys()):
        idxs = sorted(by_src[src], key=lambda i: str(questions[i].get("qid", i)))
        idxs = np.array(idxs, dtype=np.int64)
        perm = rng.permutation(idxs.size)
        n_tr = int(round(idxs.size * SPLIT_FRAC_TRAIN))
        train[idxs[perm[:n_tr]]] = True
    test = ~train
    return train, test


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
    train_mask, test_mask = _split_train_test(questions)
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f} "
          f"train={int(train_mask.sum())} test={int(test_mask.sum())}", flush=True)

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
    degrees_all = np.array([float(len(t)) for t in fact_terms], dtype=np.float64)
    neg_all = np.array([_neg_count(s) for s in sents], dtype=np.float64)
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

    # ---- WIDE RR pool (max-recall cell path, UNCHANGED) ----
    _heartbeat(output_dir, "ppr_wide_pool")
    seeds_sc = ppr.link_seeds(sc_words_per_q, vocab, t2i, term_vecs, [wvecs(ws) for ws in sc_words_per_q], SEED_COS)
    sm_sc = ppr.seeds_to_matrix(seeds_sc, nTerms)
    F_SC = ppr.fact_activation(ppr.ppr_batch(sm_sc, M, HOPS, DAMP), Sft)
    seeds2 = mr.reformulate_seeds(F_SC, seeds_sc, fact_terms, t2i, RR_TOP_T)
    F_P2 = ppr.fact_activation(ppr.ppr_batch(ppr.seeds_to_matrix(seeds2, nTerms), M, HOPS, DAMP), Sft)
    F_RR = mr._rownorm_scores(F_SC) + mr._rownorm_scores(F_P2)

    # ---- PASS A: per-question pool + features + fixed signals + gold ----
    _heartbeat(output_dir, "features")
    poolidx_list = [None] * nQ
    Xn_list = [None] * nQ           # per-question min-max normed feature matrix
    fixed_sel_local = [None] * nQ   # dict arm -> local top-K indices (A_gate/REL/COH/DISC)
    gold_rows_list = [None] * nQ
    lure_flags = np.zeros(nQ, dtype=bool)

    for qi, q in enumerate(questions):
        ci = q["correct_index"]
        stem_words = stem_words_per_q[qi]
        lure_flags[qi] = gate.is_lure_question(stem_words, q["choices"], ci)
        lure_set, _ = gate.standout_lure_choices(stem_words, q["choices"])

        pool_idx = ppr.topk_from_scores(F_RR[qi], K_WIDE)
        poolidx_list[qi] = pool_idx
        fh_pool = SV_store[pool_idx]
        chd = choice_hd_map[qi]
        fw = [fact_word_sets[i] for i in pool_idx.tolist()]

        gs = gate.gate_scores(fh_pool, fw, stem_words, STEM[qi], chd, lure_set)
        rel = fixedsel.relevance_score(fh_pool, STEM[qi], chd)
        disc = fixedsel.discriminative_score(fh_pool, chd)
        coh = fixedsel.coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ[qi], 0.0))
        rr_scores = F_RR[qi][pool_idx]
        degs = degrees_all[pool_idx]
        negs = neg_all[pool_idx]

        Xn_list[qi] = _minmax_cols(question_features(fh_pool, STEM[qi], chd, gs, coh, rr_scores, degs, negs))
        fixed_sel_local[qi] = {
            "A_gate": _topk_idx(gs["gate"], K_SEL),
            "REL": _topk_idx(rel, K_SEL),
            "COH": _topk_idx(coh, K_SEL),
            "DISC": _topk_idx(disc, K_SEL),
        }
        gold_rows_list[qi] = np.array([uid2fi[u] for u in q["gold_central"] if u in uid2fi], dtype=np.int64)

    # ---- TRAIN the glass-box learned relevance scorer on TRAIN questions ONLY (label = is-gold) ----
    _heartbeat(output_dir, "train_learned")
    Xrows, yrows = [], []
    for qi in range(nQ):
        if not train_mask[qi]:
            continue
        pool_idx = poolidx_list[qi]
        gold_set = set(int(g) for g in gold_rows_list[qi].tolist())
        y = np.array([1.0 if int(gi) in gold_set else 0.0 for gi in pool_idx.tolist()], dtype=np.float64)
        Xrows.append(Xn_list[qi])
        yrows.append(y)
    Xtrain = np.concatenate(Xrows, axis=0) if Xrows else np.zeros((0, len(FEATURE_NAMES)))
    ytrain = np.concatenate(yrows, axis=0) if yrows else np.zeros(0)
    n_train_rows = int(Xtrain.shape[0])
    n_train_pos = int(ytrain.sum())
    w, b = train_glassbox_relevance(Xtrain, ytrain)
    learned_weights = {FEATURE_NAMES[j]: round(float(w[j]), 5) for j in range(len(FEATURE_NAMES))}
    print(f"[learned] trained on {n_train_rows} rows ({n_train_pos} gold-pos); weights={learned_weights} "
          f"intercept={b:.4f}", flush=True)

    # ---- PASS B: pick answers per arm (learned scored on w; fixed arms; random; oracle) ----
    _heartbeat(output_dir, "select_and_answer")
    picks = {name: np.full(nQ, -1, dtype=np.int64) for name in ARMS}
    sel_gold_hit = {name: [None] * nQ for name in ARMS}
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
        pool_idx = poolidx_list[qi]
        gold_rows = gold_rows_list[qi]
        gold_set = set(int(g) for g in gold_rows.tolist())

        sel_local = dict(fixed_sel_local[qi])
        sel_local["LEARNED"] = _topk_idx(learned_score(Xn_list[qi], w, b), K_SEL)
        rng_r = np.random.default_rng(SEED + 7000 + qi)
        sel_local["RND"] = rng_r.permutation(pool_idx.size)[:min(K_SEL, pool_idx.size)]

        for name in ("A_gate", "LEARNED") + FIXED_REF_ARMS + ("RND",):
            sel_glob = pool_idx[sel_local[name]]
            picks[name][qi] = combiner_pick(qi, sel_glob)
            denom = min(K_SEL, sel_glob.size) if sel_glob.size else 1
            sel_gold_hit[name][qi] = sum(1 for g in sel_glob.tolist() if g in gold_set) / denom
        picks["ORACLE"][qi] = combiner_pick(qi, gold_rows)
        sel_gold_hit["ORACLE"][qi] = 1.0 if gold_rows.size else 0.0

        if len(glass) < 12 and lure_flags[qi] and test_mask[qi]:
            Xn = Xn_list[qi]
            learned_local = sel_local["LEARNED"]
            contrib = {}
            for li in learned_local.tolist():
                contrib[str(int(li))] = {FEATURE_NAMES[j]: round(float(Xn[li, j] * w[j]), 4)
                                         for j in range(len(FEATURE_NAMES))}
            glass.append({
                "qid": q["qid"], "stem": q["stem"][:120], "choices": q["choices"],
                "correct_index": q["correct_index"], "split": "test",
                "n_gold_in_store": len(gold_set),
                "gold_in_wide_pool": sum(1 for i in pool_idx.tolist() if i in gold_set),
                "picks": {name: int(picks[name][qi]) for name in ARMS},
                "LEARNED_selected": [uid2sent.get(uids[i], "")[:70] for i in pool_idx[learned_local].tolist()],
                "A_gate_selected": [uid2sent.get(uids[i], "")[:70]
                                    for i in pool_idx[sel_local["A_gate"]].tolist()],
                "LEARNED_selected_gold": [int(i in gold_set) for i in pool_idx[learned_local].tolist()],
                "A_gate_selected_gold": [int(i in gold_set)
                                         for i in pool_idx[sel_local["A_gate"]].tolist()],
                "LEARNED_feature_contributions": contrib,
            })

    # ---- accuracies (PRIMARY = TEST split; overfit check = TRAIN split for LEARNED) ----
    correct = {name: np.array([int(picks[name][qi] == questions[qi]["correct_index"])
                               for qi in range(nQ)], dtype=np.int64) for name in ARMS}
    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    is_chal = ~is_easy
    chal_lure = is_chal & lure_flags
    test_chal = test_mask & is_chal
    test_easy = test_mask & is_easy
    train_chal = train_mask & is_chal

    def acc(mask, name):
        m = correct[name][mask]
        return round(float(np.mean(m)), 4) if m.size else None

    def selprec(mask, name):
        vals = [sel_gold_hit[name][qi] for qi in range(nQ) if mask[qi] and sel_gold_hit[name][qi] is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    accs = {}
    for name in ARMS:
        accs[name] = {
            "test_easy": acc(test_easy, name), "test_challenge": acc(test_chal, name),
            "test_chal_lure": acc(test_mask & chal_lure, name),
            "test_chal_correct": int(np.sum(correct[name][test_chal])),
            "test_chal_n": int(np.sum(test_chal)),
            "sel_gold_precision": selprec(test_chal, name),
        }
        print(f"[acc] {name}: test_easy={accs[name]['test_easy']} "
              f"test_chal={accs[name]['test_challenge']} lure={accs[name]['test_chal_lure']} "
              f"sel_gold_prec={accs[name]['sel_gold_precision']}", flush=True)

    # overfit check for LEARNED (train vs test Challenge)
    learned_train_chal = acc(train_chal, "LEARNED")
    learned_test_chal = accs["LEARNED"]["test_challenge"] or 0.0
    overfit_gap = round((learned_train_chal or 0.0) - learned_test_chal, 4)
    overfit_warn = abs(overfit_gap) > OVERFIT_GAP_WARN
    learned_train_selprec = selprec(train_chal, "LEARNED")

    # ---- PRIMARY discriminator: LEARNED vs A_gate on TEST Challenge (judged on the ANSWER) ----
    A_chal = accs["A_gate"]["test_challenge"] or 0.0
    learned_chal = accs["LEARNED"]["test_challenge"] or 0.0
    oracle_chal = accs["ORACLE"]["test_challenge"] or 0.0
    gap = round(oracle_chal - A_chal, 4)
    learned_lift = round(learned_chal - A_chal, 4)
    gap_frac_closed = round(learned_lift / gap, 4) if gap > 1e-9 else None
    rand_lift = round((accs["RND"]["test_challenge"] or 0.0) - A_chal, 4)
    best_fixed = max(FIXED_REF_ARMS, key=lambda n: (accs[n]["test_challenge"] or 0.0))
    learned_vs_best_fixed = round(learned_chal - (accs[best_fixed]["test_challenge"] or 0.0), 4)

    learned_selprec = accs["LEARNED"]["sel_gold_precision"] or 0.0
    gate_selprec = accs["A_gate"]["sel_gold_precision"] or 0.0

    mc_b, mc_c, mc_stat, mc_p = gate.mcnemar(correct["A_gate"][test_chal], correct["LEARNED"][test_chal])
    sig = (mc_p is not None) and (mc_p < MCNEMAR_ALPHA)
    random_ok = rand_lift <= RANDOM_MAX
    selprec_material = learned_selprec >= HP_SELPREC_MIN

    # ---- integrity gates ----
    ag_saturated = A_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_chal < 0.95
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest() for name in ARMS}
    n_distinct = len(set(digests[n] for n in ("A_gate", "LEARNED", "REL", "COH", "DISC", "RND")))
    arms_differ = n_distinct >= 4
    learned_nontrivial = bool(np.any(np.abs(w) > 1e-6))   # scorer actually learned non-zero weights

    # ---- verdict (PRIMARY = TEST Challenge accuracy on the ANSWER + sel_gold_precision) ----
    if ag_saturated:
        verdict = "LEARNED_SELECTION_SATURATED"
        vmsg = (f"baseline A_gate TEST Challenge {A_chal} >= {AG_BASELINE_SAT}: no headroom for learned "
                f"selection (report, not a mechanism failure).")
    elif not arms_differ:
        verdict = "LEARNED_SELECTION_ARMS_IDENTICAL_META_RULE_AF"
        vmsg = (f"selection arms produced < 4 distinct pick-vectors (n_distinct={n_distinct}); arm "
                f"implementation bug -- do NOT trust the accuracy comparison.")
    elif not learned_nontrivial:
        verdict = "LEARNED_SELECTION_DEGENERATE"
        vmsg = (f"learned weight vector ~= 0 (no feature separates gold on TRAIN); training degenerate "
                f"-- inspect features/labels before interpreting.")
    elif learned_lift >= HP_CHAL_LIFT and sig and selprec_material and random_ok:
        verdict = "LEARNED_SELECTION_HARD_PASS"
        vmsg = (f"LEARNED glass-box relevance BEATS the fixed gate ON THE ANSWER and lifts precision: "
                f"LEARNED TEST Challenge {learned_chal} vs A_gate {A_chal} (lift {learned_lift:+.4f} "
                f">= {HP_CHAL_LIFT}; {gap_frac_closed} of the {gap} gap to oracle {oracle_chal}); "
                f"McNemar b={mc_b} c={mc_c} stat={mc_stat:.2f} p={mc_p:.4f} (<{MCNEMAR_ALPHA}); "
                f"sel_gold_precision LEARNED={learned_selprec} vs gate {gate_selprec} "
                f"(>= {HP_SELPREC_MIN}); RANDOM lift={rand_lift:+.4f} (<={RANDOM_MAX}); "
                f"vs best fixed ({best_fixed}) {learned_vs_best_fixed:+.4f}. "
                f"overfit train-test gap={overfit_gap} (warn={overfit_warn}). "
                f"The cheaper lever WORKS: learning squeezes relevance from the thin features.")
    elif learned_lift >= MB_CHAL_LIFT or (selprec_material and learned_lift > 0):
        verdict = "LEARNED_SELECTION_MIDDLE_BAND"
        vmsg = (f"MIDDLE: LEARNED lifts modestly but plateaus below oracle. LEARNED TEST Challenge "
                f"{learned_chal} vs A_gate {A_chal} (lift {learned_lift:+.4f} in [{MB_CHAL_LIFT},"
                f"{HP_CHAL_LIFT}) or a gate unmet -- McNemar p={mc_p} (sig={sig}), sel_gold_precision "
                f"LEARNED={learned_selprec} vs gate {gate_selprec} (material={selprec_material}), random "
                f"lift={rand_lift} (ok={random_ok}). {gap_frac_closed} of the {gap} gap; vs best fixed "
                f"({best_fixed}) {learned_vs_best_fixed:+.4f}. overfit gap={overfit_gap} (warn={overfit_warn}). "
                f"Learned helps but does not decisively close selection -> partial credit, grounding still open.")
    else:
        verdict = "LEARNED_SELECTION_HARD_FAIL"
        vmsg = (f"HONEST CEILING: LEARNED ~= the fixed gate (LEARNED TEST Challenge {learned_chal} vs "
                f"A_gate {A_chal}, lift {learned_lift:+.4f} < {MB_CHAL_LIFT}; sel_gold_precision "
                f"LEARNED={learned_selprec} vs gate {gate_selprec}, oracle {accs['ORACLE']['sel_gold_precision']}). "
                f"Learning CANNOT squeeze the gold-vs-lure signal from the THIN GloVe/WordNet features -> "
                f"the ceiling is the MEANING representation itself, NOT the scoring rule. The deep lever is "
                f"GROUNDED/richer meaning, not a learned re-weighting of the same thin features. vs best "
                f"fixed ({best_fixed}) {learned_vs_best_fixed:+.4f}; random lift={rand_lift}; overfit "
                f"gap={overfit_gap} (warn={overfit_warn}). Learned weights: {learned_weights}.")

    grade = arc._grade_proxy(accs["LEARNED"]["test_easy"], accs["LEARNED"]["test_challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [TEST Chal] A_gate={A_chal} LEARNED={learned_chal} "
                    f"REL={accs['REL']['test_challenge']} COH={accs['COH']['test_challenge']} "
                    f"DISC={accs['DISC']['test_challenge']} RND={accs['RND']['test_challenge']} "
                    f"ORACLE={oracle_chal} | learned_lift={learned_lift:+.4f} gap_frac={gap_frac_closed} "
                    f"McNemar_p={mc_p} sel_gold_prec L={learned_selprec}/gate={gate_selprec}/"
                    f"oracle={accs['ORACLE']['sel_gold_precision']} rand_lift={rand_lift} "
                    f"overfit_gap={overfit_gap} | chance={round(chance,4)}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_train": int(train_mask.sum()), "n_test": int(test_mask.sum()),
        "n_test_challenge": int(np.sum(test_chal)), "n_train_challenge": int(np.sum(train_chal)),
        "n_train_rows": n_train_rows, "n_train_gold_pos": n_train_pos,
        "chance_theoretical": round(chance, 4),
        "store_facts": nFacts, "graph_terms": nTerms,
        # selection + learner config
        "k_wide": K_WIDE, "k_sel": K_SEL, "rr_top_t": RR_TOP_T, "mu_supp": MU_SUPP,
        "settle_t": SETTLE_T, "settle_eps": SETTLE_EPS, "hops": HOPS, "damp": DAMP, "seed_cos": SEED_COS,
        "l2_reg": L2_REG, "gd_iters": GD_ITERS, "gd_lr": GD_LR, "split_frac_train": SPLIT_FRAC_TRAIN,
        # GLASS-BOX: the inspectable learned scorer
        "feature_names": list(FEATURE_NAMES),
        "learned_weights": learned_weights,
        "learned_intercept": round(float(b), 5),
        "learned_nontrivial": learned_nontrivial,
        # PRIMARY: end-to-end accuracy by arm on the TEST split (judged on the ANSWER)
        "acc_by_arm": accs,
        "A_gate_test_challenge": A_chal,
        "learned_test_challenge": learned_chal,
        "oracle_gold_test_challenge": oracle_chal,
        "selection_gap": gap,
        "learned_lift_challenge": learned_lift,
        "gap_fraction_closed": gap_frac_closed,
        "learned_vs_best_fixed_challenge": learned_vs_best_fixed, "best_fixed_arm": best_fixed,
        "random_lift_challenge": rand_lift, "random_control_ok": bool(random_ok),
        "mcnemar_challenge": {"arm": "LEARNED", "b_A_right_arm_wrong": mc_b,
                              "c_A_wrong_arm_right": mc_c,
                              "stat": None if mc_stat is None else round(mc_stat, 4),
                              "p_value": None if mc_p is None else round(mc_p, 5),
                              "significant": bool(sig)},
        # SECONDARY diagnostic: selection precision vs gold (gold for EVAL only)
        "sel_gold_precision_by_arm": {name: accs[name]["sel_gold_precision"] for name in ARMS},
        "sel_gold_precision_material": bool(selprec_material), "hp_selprec_min": HP_SELPREC_MIN,
        # overfit check
        "learned_train_challenge": learned_train_chal, "learned_test_challenge_dup": learned_test_chal,
        "overfit_gap_challenge": overfit_gap, "overfit_warn": bool(overfit_warn),
        "learned_train_sel_gold_precision": learned_train_selprec,
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band), "ag_saturated": bool(ag_saturated),
        "arms_differ_verified": bool(arms_differ), "n_distinct_pick_vectors": int(n_distinct),
        "arm_pick_digests": digests,
        "bands": {"HP_chal_lift": HP_CHAL_LIFT, "HP_selprec_min": HP_SELPREC_MIN,
                  "MB_chal_lift": MB_CHAL_LIFT, "random_max": RANDOM_MAX,
                  "mcnemar_alpha": MCNEMAR_ALPHA, "ag_baseline_sat": AG_BASELINE_SAT,
                  "overfit_gap_warn": OVERFIT_GAP_WARN},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: LEARNED-vs-FIXED selection scoring is the ONLY variable. The WIDE re-retrieval pool "
            "(RR top-100, mr.reformulate_seeds/_rownorm_scores IMPORTED UNCHANGED) and the bind+bundle "
            "combiner (agg.aggregate 'bundle' IMPORTED UNCHANGED) are held fixed. The ONE new piece is a "
            "GLASS-BOX learned relevance scorer: a linear readout over 10 interpretable features "
            "(cos-to-stem, mean/max cos-to-choice, discriminative margin, coherence, lexical overlap, "
            "retrieval score, RIF-suppression, degree, negation) trained by the delta-rule / "
            "reward-prediction-error (predicted-relevance minus is-gold reward; CFRPE-family / LEARNER "
            "MODULE 29487) on the TRAIN split, evaluated on the TEST split. GLASS-BOX INVARIANT: the "
            "runtime scorer is learned WEIGHTS over named features (logged) + per-fact feature "
            "contributions (glassbox_sample.json), NOT an opaque blob. NO LEAK: TRAIN/TEST disjoint "
            "(stratified by source); scorer never sees TEST correct_index or TEST gold; gold used for "
            "TRAIN label + ORACLE arm + eval only. Arms: A_gate (fixed incumbent baseline), LEARNED "
            "(mechanism), REL/COH/DISC (fixed reference signals), RND (must-fail), ORACLE (gold ceiling). "
            "PRIMARY = TEST-split Challenge accuracy judged on the ANSWER; McNemar LEARNED vs A_gate. "
            "SECONDARY = sel_gold_precision. "
            "STUBBED/NOTED-NOT-BUILT: grounded/richer MEANING features (the DEEPER lever) -- if this "
            "HARD_FAILs, the redirect is grounded meaning, since learning on the SAME thin features is "
            "then ceiling-limited (the honest ceiling test)."),
        "contract": ("INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree "
                     "git-ignored/large); VET-PENDING; FULL eval slice bounded (limit_easy=500 "
                     "limit_chal=600, stratified train/test split) to fit one foreground call"),
        "compute_architecture": ("mixed CPU: batched GloVe encode + scipy.sparse batched PPR (2 passes, "
                                 "UNCHANGED) + per-question feature assembly (cheap) + one glass-box "
                                 "full-batch logreg train (~50k rows x 10 feats, deterministic zero-init "
                                 "GD) + UNCHANGED combiner; wall target < 10min"),
        "storage_strategy": "sharded (each fact = own embedding + own graph node; no superposition)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": ("default_ok_for_this_regime (learner hyperparams L2=1.0/iters=400/lr=0.5 "
                              "author-set a priori; wide pool + combiner UNCHANGED; NOT tuned to force a "
                              "win; random-select must-fail present; overfit checked via train/test gap; "
                              "HONEST CEILING CAVEAT: learned trains on the SAME thin features)"),
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
