"""arc_retrieval_selection_gate_learned_credit_v1 -- the brain's STAGE-8 CREDIT-ASSIGNMENT
retrieval-SELECTION gate, wired to REAL ARC correctness for the first time.

THE #1 LEVER (VET'd): retrieval PRECISION is the ARC wall. Given GOLD central facts the
UNCHANGED bind+settle combiner reasons at Challenge 0.6899 (oracle ceiling); over the noisy
PPR spreading pool it drowns to Challenge 0.2936. ~40 pts of headroom is locked behind SELECTING
the right facts out of the pool.
  MEASURED@data/exp_arc_retrieval_selection_gate_suppression_v1/metrics.json:acc_by_arm
    A_noisy  (whole pool)            challenge = 0.2936   [sim-pool baseline]
    B_gate   (goal-bias+RIF suppr.)  challenge = 0.3409   [hand-set SIMILARITY gate]
    O_oracle (gold central facts)    challenge = 0.6899   [ceiling]
    chance                                     = 0.2502

THE ANTI-SHORTCUT CONSTRAINT (load-bearing): there is a 7x HARD_FAIL lineage of SIMILARITY/MARGIN
selection, root-caused as "the operation was STILL similarity/margin, NOT entailment" = the thin-
encoder fine-discrimination wall. A new COSINE-scoring gate will very likely fail the same way. So
the selection signal here is genuinely NON-similarity: a LEARNED VALUE gate whose weights are
trained on REAL ARC CORRECTNESS (reward) by a dopamine-RPE credit-assignment rule -- NOT cosine
margins. The value function also consumes NON-similarity STRUCTURAL features (PPR spreading-
activation strength, pool-rank, IDF overlap, degree) so learning-from-reward can up-weight real
retrieval structure the cosine gate cannot express.

BRAIN-FAITHFUL FRAME: VLPFC controlled retrieval (Badre & Wagner 2007) + basal-ganglia Go/NoGo
gating (O'Reilly & Frank 2006 PBWM) + dopamine reward-prediction-error credit-assignment
(Schultz 1997). Select task-relevant facts by LEARNED value; resist surface-lures.

HONEST TENSION (prereg): the repo's master reasoning-map RETIRED similarity-scoring-selection and
pivoted to derivation-SEARCH (coverage-blocked). This LEARNED gate is the complementary, untested
PRECISION lever (credit-assignment), cheaper than un-blocking search. Its features still partly
derive from the thin encoder (g_stem, g_disc are cosines over thin GloVe reps); credit-assignment
can only RE-WEIGHT the available features -- if none separate correct-from-lure at the needed fine
grain, learning cannot manufacture signal (the pre-registered honest-negative mechanism).

REUSE (do NOT rebuild): the UNCHANGED PPR spreading pool (arm B, imported), the UNCHANGED bind+
settle combiner (agg.aggregate 'bundle', imported), the hand-set SIMILARITY gate (gate_scores,
imported from the insertion cell), and hdlab.action_selection's Go/NoGo actor PRINCIPLE + the
cfrpe adaptive-LR / dopamine-RPE credit-assignment update. NOTE the honest adaptation: the module's
GoNoGoActionGate is a MULTI-HOP nav actor (state@W_ops + SR-transport reach); ARC fact-selection is
a ONE-SHOT contextual bandit, so we reuse the Go/NoGo WTA + RPE credit-assignment PRINCIPLE with an
ARC-native LINEAR value function over per-fact features. We do NOT force-fit the nav SR-M (that would
be a misuse). The ONE new piece = the learned value gate trained on ARC correctness at the proven
insertion point (pool -> gate -> UNCHANGED combiner).

FAIRNESS / NO-LEAK: the value gate is trained on a TRAIN split's correctness ONLY; ALL arms are
evaluated on a disjoint HELD-OUT split; feature standardization stats come from TRAIN only. Report
train vs held-out (overfit gap). Controls: L_shuffreward (train on PERMUTED reward -> must collapse
to baseline) and Sh_graph (train+eval on a SHUFFLED incidence graph -> structure destroyed -> must
collapse) prove the win needs REAL reward + REAL structure, not memorization.

ARMS (all eval on HELD-OUT; identical pool + UNCHANGED combiner; ONLY selection differs):
  A_baseline    whole K_POOL pool -> combiner                 [sim-pool baseline; reproduce insertion A]
  G_simgate     hand-set similarity gate top-K_SEL -> combiner[SIMILARITY gate; reproduce insertion B]
  L_learned     LEARNED credit-assignment value gate top-K_SEL[THE TEST]
  L_cosonly     learned gate, COSINE features only            [anti-tautology: does structure add?]
  L_shuffreward learned gate trained on PERMUTED reward       [MUST-FAIL leak control ~ baseline]
  Sh_graph      learned gate on a SHUFFLED incidence graph    [MUST-FAIL structure control ~ baseline]
  O_oracle      gold central facts -> combiner                [ceiling ~0.69]

PRIMARY discriminator = HELD-OUT Challenge accuracy: L_learned vs G_simgate (paired McNemar) and
L_learned vs A_baseline. WIN => credit-assignment is the lever. HONEST-NEG => the encoder/meaning
wall is foundational even for selection (consistent with the 7x similarity-lineage root cause).

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT remote-
portable; FULL ~100s per the insertion cell); NO push/remote-persist; ASCII-only; deterministic
(fixed int seeds, numpy default_rng, sorted iteration, no hash()); repo .venv; agent-reported
VET-PENDING (skunkworks owns landed-VET + atom banking).

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL PPR pool + REAL features + REAL
#   learned gate + UNCHANGED combiner; a PLANTED case proves the credit-assignment gate learns a
#   NON-similarity feature that a cosine-only gate cannot (train reward rises; arms differ)
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-guard on A_baseline challenge (headroom vs the 0.69 ceiling)
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

# reuse: PPR spreading pool (UNCHANGED), bind+settle combiner (UNCHANGED), arc helpers, hand-set gate
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as simgate
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)
# reuse: basal-ganglia Go/NoGo actor PRINCIPLE + dopamine-RPE adaptive-LR credit-assignment
from hdlab import action_selection as acts

ANCHOR_NAME = "arc_retrieval_selection_gate_learned_credit_v1"
SEED = 20260725

# ---- pool / selection (match the insertion cell so the comparison is one-variable) ----
K_POOL = simgate.K_POOL          # 20 -- the noisy spreading pool
K_SEL = simgate.K_SEL            # 4  -- clean facts after selection (Cowan-4 / WorldTree ~2.5 central)
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# ---- learned-gate training (dopamine-RPE REINFORCE Go/NoGo; author-set a priori) ----
N_EPOCHS = 60
LR = 0.05
BASELINE_BETA = 0.05             # EMA rate of the reward-prediction baseline (the RPE reference)
L2 = 1e-4                        # weight decay (stability)
ADAPT_LR_FLOOR = acts.ADAPT_LR_FLOOR   # reuse cfrpe adaptive per-sample LR clamp
ADAPT_LR_CEIL = acts.ADAPT_LR_CEIL
LR_DECAY_END = acts.LR_DECAY_END       # reuse linear LR-decay-to-0.2 schedule

# feature layout (index -> name). STRUCTURAL (non-similarity) first, then SIMILARITY, then bias.
FEATURES = [
    "ppr_act",        # 0 spreading-activation strength (structural, from the graph)
    "ppr_rank",       # 1 pool rank, top=1.0 (structural)
    "surf_pull",      # 2 Jaccard(fact_words, stem_words) (lexical LURE cue; gate learns its sign)
    "lure_align",     # 3 fact's best-choice == standout surface-lure (0/1) (RIF cue)
    "idf_overlap",    # 4 IDF-weighted stem overlap (structural lexical)
    "n_terms",        # 5 fact content-word count (degree proxy)
    "g_stem",         # 6 relu cos(fact, STEM) (SIMILARITY; encoder-bound)
    "g_disc",         # 7 choice-separating margin (SIMILARITY; encoder-bound)
    "best_cos",       # 8 max_c cos(fact, choice) (SIMILARITY; encoder-bound)
]
N_FEAT = len(FEATURES)
STRUCT_IDX = [0, 1, 2, 3, 4, 5]   # non-similarity features
COS_IDX = [6, 7, 8]               # cosine features (L_cosonly restricts to these)

# ---- bands (author-set a priori; PRIMARY = HELD-OUT Challenge accuracy) ----
HP_LG = 0.03        # L_learned - G_simgate on held-out Challenge (strict floor; > MB by design)
MB_LG = 0.01        # positive-but-sub-HP band floor for L vs G
HP_LA = 0.05        # L_learned - A_baseline on held-out Challenge (must clear the sim-pool baseline)
SHUFFREWARD_MAX = 0.015   # L_shuffreward - A_baseline <= this (permuted reward gives no real lift)
SHUFFGRAPH_MAX = 0.03     # Sh_graph - A_baseline <= this (shuffled structure collapses)
GEN_FRAC = 0.5      # held-out (L-A) must be >= GEN_FRAC * train (L-A) (generalizes, not pure overfit)
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95    # A_baseline challenge >= this -> vacuous (no headroom)


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat  (reused pattern from insertion cell)
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
# per-fact FEATURE extraction (structural + similarity) -- answer-agnostic
# ---------------------------------------------------------------------------
def _topk_idx(scores, k):
    """Indices of the top-k scores (descending, stable ties by index)."""
    n = scores.shape[0]
    kk = min(k, n)
    if kk <= 0:
        return np.zeros(0, dtype=np.int64)
    idx = np.argpartition(-scores, kk - 1)[:kk]
    return idx[np.argsort(-scores[idx], kind="stable")]


def build_features(pool_fh, pool_act, fact_word_sets_pool, fact_nterms_pool,
                   stem_word_set, stem_vec, choice_hd, lure_set, idf_of_term, t2i):
    """Per-candidate feature matrix Phi [P, N_FEAT] for one question. ANSWER-AGNOSTIC.
      pool_fh          : [P, N] L2 fact embeddings for the pooled facts
      pool_act         : [P] PPR spreading-activation score of each pooled fact
      fact_word_sets_pool : list length P of content-word sets per pooled fact
      fact_nterms_pool : [P] content-word count per pooled fact
      stem_word_set    : content-word set of the stem
      stem_vec         : [N] L2 stem embedding
      choice_hd        : [C, N] L2 (stem+choice) embeddings
      lure_set         : set of choice indices flagged as standout surface-lures (answer-agnostic)
      idf_of_term      : dict term->idf (aligned to vocab)
    Returns Phi [P, N_FEAT] (raw, un-standardized)."""
    P = pool_fh.shape[0]
    Phi = np.zeros((P, N_FEAT), dtype=np.float64)
    if P == 0:
        return Phi
    # cosine block
    cc = pool_fh @ choice_hd.T                      # [P, C]
    g_stem = np.maximum(pool_fh @ stem_vec, 0.0)    # [P]
    if cc.shape[1] >= 2:
        part = np.sort(cc, axis=1)
        g_disc = part[:, -1] - part[:, -2]
    else:
        g_disc = cc.max(axis=1)
    best_cos = cc.max(axis=1)
    best_choice = cc.argmax(axis=1)
    # structural block
    act = pool_act.astype(np.float64)
    amax = float(act.max()) if act.size and act.max() > 0 else 1.0
    ppr_act = act / amax
    # rank: pooled facts are typically supplied in descending-activation order; derive rank robustly
    order = np.argsort(-act, kind="stable")
    rank_pos = np.empty(P, dtype=np.float64)
    rank_pos[order] = np.arange(P, dtype=np.float64)
    ppr_rank = 1.0 - rank_pos / max(1.0, float(P - 1))     # top=1.0
    surf_pull = np.array([simgate._jaccard(fact_word_sets_pool[i], stem_word_set)
                          for i in range(P)], dtype=np.float64)
    lure_align = np.array([1.0 if int(best_choice[i]) in lure_set else 0.0
                           for i in range(P)], dtype=np.float64)
    idf_overlap = np.zeros(P, dtype=np.float64)
    for i in range(P):
        shared = fact_word_sets_pool[i] & stem_word_set
        idf_overlap[i] = float(sum(idf_of_term.get(w, 0.0) for w in shared))
    n_terms = fact_nterms_pool.astype(np.float64)

    Phi[:, 0] = ppr_act
    Phi[:, 1] = ppr_rank
    Phi[:, 2] = surf_pull
    Phi[:, 3] = lure_align
    Phi[:, 4] = idf_overlap
    Phi[:, 5] = n_terms
    Phi[:, 6] = g_stem
    Phi[:, 7] = g_disc
    Phi[:, 8] = best_cos
    return Phi


def standardize_fit(phi_list):
    """Fit per-feature mean/std over a list of [P,F] matrices (TRAIN only). Returns (mu, sd)."""
    if not phi_list:
        return np.zeros(N_FEAT), np.ones(N_FEAT)
    stacked = np.concatenate([p for p in phi_list if p.shape[0] > 0], axis=0)
    mu = stacked.mean(axis=0)
    sd = stacked.std(axis=0)
    sd[sd < 1e-6] = 1.0
    return mu, sd


def standardize_apply(Phi, mu, sd, feat_mask=None):
    """Standardize Phi with train (mu,sd). feat_mask (list of indices) zeros out masked-off features
    (used by L_cosonly to restrict to cosine features). Bias column appended (constant 1.0)."""
    if Phi.shape[0] == 0:
        return np.zeros((0, N_FEAT + 1), dtype=np.float64)
    Z = (Phi - mu) / sd
    if feat_mask is not None:
        keep = np.zeros(N_FEAT, dtype=bool)
        keep[feat_mask] = True
        Z[:, ~keep] = 0.0
    bias = np.ones((Z.shape[0], 1), dtype=np.float64)
    return np.concatenate([Z, bias], axis=1)   # [P, N_FEAT+1]


# ---------------------------------------------------------------------------
# the LEARNED CREDIT-ASSIGNMENT gate (the ONE new piece)
#   Go/NoGo linear value:  g_i = w . z_i ;  p_i = sigmoid(g_i)  (basal-ganglia disinhibition)
#   dopamine-RPE REINFORCE:  rpe = r - b ;  w += lr * rpe * sum_i (a_i - p_i) z_i  (credit assignment)
#   b = EMA reward-prediction baseline (the RPE reference).
#   Reuses acts.ADAPT_LR clamp + LR_DECAY_END schedule from the certified cfrpe value-gate.
# ---------------------------------------------------------------------------
def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))


class CreditAssignmentGate:
    """ARC-native one-shot Go/NoGo value selector, trained by dopamine-RPE on ARC correctness.

    This is the honest adaptation of hdlab.action_selection.GoNoGoActionGate (a MULTI-HOP nav actor)
    to a ONE-SHOT contextual-bandit fact-selection: same Go/NoGo WTA + RPE credit-assignment
    PRINCIPLE, ARC-native LINEAR value over per-fact features. w LEARNED from reward (not grid-tuned,
    not cosine margins)."""

    def __init__(self, n_feat_plus_bias):
        self.w = np.zeros(n_feat_plus_bias, dtype=np.float64)

    def values(self, Z):
        """Go-values g_i = w . z_i for a [P, F+1] standardized feature matrix."""
        if Z.shape[0] == 0:
            return np.zeros(0, dtype=np.float64)
        return Z @ self.w

    def select_topk(self, Z, k):
        """Deterministic greedy selection: local indices of the top-k Go-values."""
        return _topk_idx(self.values(Z), k)

    def train(self, Z_list, reward_fn, rng, n_epochs=N_EPOCHS, lr=LR):
        """REINFORCE Go/NoGo training on ARC correctness.
          Z_list    : list of [P_q, F+1] standardized feature matrices (TRAIN questions)
          reward_fn : (qi, sel_local_idx) -> reward in {0,1} (UNCHANGED combiner answer correctness)
          rng       : numpy Generator (deterministic Bernoulli sampling)
        Per (epoch, question): sample Go/NoGo a_i ~ Bernoulli(sigmoid(g_i)); selected = Go set (at
        least top-1; capped at K_SEL by value so the trained policy matches the greedy top-K eval);
        r = reward; rpe = r - baseline; w += adaptive_lr * rpe * sum_i (a_i - p_i) z_i - L2*w.
        Returns diag dict (train reward curve, |w| trace)."""
        nq = len(Z_list)
        order = np.arange(nq)
        baseline = 0.0
        reward_curve = []
        w_norm_curve = []
        for ep in range(n_epochs):
            decay = 1.0 - (1.0 - LR_DECAY_END) * (ep / max(1, n_epochs - 1))
            rng.shuffle(order)
            ep_reward = 0.0
            ep_n = 0
            for qi in order:
                Z = Z_list[qi]
                P = Z.shape[0]
                if P == 0:
                    continue
                g = Z @ self.w
                p = _sigmoid(g)
                a = (rng.random(P) < p).astype(np.float64)
                go_idx = np.where(a > 0.5)[0]
                if go_idx.size == 0:
                    go_idx = _topk_idx(g, 1)                     # NoGo-all -> force top-1 (must act)
                elif go_idx.size > K_SEL:
                    # keep the K_SEL highest-value Go facts (matches greedy top-K eval)
                    keep = go_idx[_topk_idx(g[go_idx], K_SEL)]
                    go_idx = keep
                r = float(reward_fn(qi, go_idx))
                rpe = r - baseline
                # adaptive per-sample LR: scale by |rpe| clamped to the cfrpe band (reused)
                ratio = min(max(abs(rpe) / 0.5 + ADAPT_LR_FLOOR, ADAPT_LR_FLOOR), ADAPT_LR_CEIL)
                elig = ((a - p)[:, None] * Z).sum(axis=0)         # grad log policy (credit vector)
                self.w += lr * decay * ratio * rpe * elig - L2 * self.w
                baseline += BASELINE_BETA * (r - baseline)
                ep_reward += r
                ep_n += 1
            reward_curve.append(round(ep_reward / max(1, ep_n), 4))
            w_norm_curve.append(round(float(np.linalg.norm(self.w)), 4))
        return {"train_reward_curve": reward_curve, "w_norm_curve": w_norm_curve,
                "final_baseline": round(baseline, 4)}


# ---------------------------------------------------------------------------
# McNemar (reuse insertion cell)
# ---------------------------------------------------------------------------
mcnemar = simgate.mcnemar


# ---------------------------------------------------------------------------
# deterministic stratified TRAIN / HELD-OUT split (no hash(); numpy default_rng)
# ---------------------------------------------------------------------------
def split_questions(questions, frac_train=0.5, seed=SEED):
    """Stratified-by-source 50/50 split. Deterministic (default_rng permutation over sorted qids)."""
    by_src = {}
    for i, q in enumerate(questions):
        by_src.setdefault(q["source"], []).append(i)
    rng = np.random.default_rng(seed)
    train_idx, test_idx = [], []
    for src in sorted(by_src.keys()):
        idx = np.array(sorted(by_src[src]), dtype=np.int64)   # sorted -> deterministic base order
        perm = rng.permutation(idx.size)
        idx = idx[perm]
        cut = int(round(frac_train * idx.size))
        train_idx.extend(idx[:cut].tolist())
        test_idx.extend(idx[cut:].tolist())
    return sorted(train_idx), sorted(test_idx)


# ---------------------------------------------------------------------------
# self-test: real code path + planted credit-assignment discriminator + arms-differ + determinism
# ---------------------------------------------------------------------------
def _planted_credit_assignment_discriminator():
    """PLANTED case proving the credit-assignment gate learns a NON-SIMILARITY feature that a
    cosine-only gate cannot use. Construct synthetic 'questions' where feature 0 (ppr_act analog)
    PERFECTLY predicts the correct fact, while the cosine features are UNINFORMATIVE (random). A
    learned gate over ALL features must reach ~1.0 train reward; a cosine-only learned gate stays
    near chance. Proves: (a) REINFORCE learns from reward, (b) structure carries the win where
    cosine cannot -> the anti-shortcut lever is real and reachable."""
    rng = np.random.default_rng(7)
    P = 6
    F = N_FEAT + 1
    n_q = 40
    # each question: one 'good' fact (index 0) whose structural feature 0 is high; cosine random
    Z_all, gold_local = [], []
    for _ in range(n_q):
        Z = rng.standard_normal((P, F)) * 0.3
        Z[:, N_FEAT] = 1.0                       # bias column
        good = int(rng.integers(0, P))
        Z[:, 0] = -0.5                           # structural feature 0 low for all...
        Z[good, 0] = 3.0                         # ...high ONLY for the good fact (perfectly predictive)
        Z[:, COS_IDX] = rng.standard_normal((P, len(COS_IDX))) * 0.3   # cosine = pure noise
        Z_all.append(Z)
        gold_local.append(good)

    def reward_fn(qi, sel_local_idx):
        return 1.0 if gold_local[qi] in set(sel_local_idx.tolist()) else 0.0

    # full-feature learned gate
    gate = CreditAssignmentGate(F)
    diag = gate.train(Z_all, reward_fn, np.random.default_rng(1), n_epochs=80, lr=0.1)
    full_reward = float(np.mean([reward_fn(qi, gate.select_topk(Z_all[qi], 1))
                                 for qi in range(n_q)]))
    # cosine-only learned gate (structural features zeroed): cannot see feature 0
    Z_cos = []
    for Z in Z_all:
        Zc = Z.copy()
        Zc[:, STRUCT_IDX] = 0.0
        Z_cos.append(Zc)
    gate_c = CreditAssignmentGate(F)
    gate_c.train(Z_cos, reward_fn, np.random.default_rng(1), n_epochs=80, lr=0.1)
    cos_reward = float(np.mean([reward_fn(qi, gate_c.select_topk(Z_cos[qi], 1))
                                for qi in range(n_q)]))

    assert diag["train_reward_curve"][-1] > diag["train_reward_curve"][0], (
        "planted: REINFORCE did not increase train reward %s" % diag["train_reward_curve"])
    assert full_reward > 0.85, "planted: full-feature gate failed to learn structure: %.3f" % full_reward
    assert full_reward > cos_reward + 0.30, (
        "planted: structure did not beat cosine-only (full=%.3f cos=%.3f) -- lever not isolated"
        % (full_reward, cos_reward))
    # arms differ: full-gate ranking != cos-gate ranking on q0
    r_full = gate.select_topk(Z_all[0], P)
    r_cos = gate_c.select_topk(Z_cos[0], P)
    assert not np.array_equal(r_full, r_cos), "planted: full and cos-only selections identical"
    return {"full_reward": round(full_reward, 3), "cos_reward": round(cos_reward, 3)}


def self_test():
    print("[self-test] planted credit-assignment discriminator "
          "(learned gate finds a NON-similarity feature a cosine-only gate cannot) ...", flush=True)
    planted = _planted_credit_assignment_discriminator()
    print(f"[self-test]   planted full_reward={planted['full_reward']} "
          f"cos_reward={planted['cos_reward']} (structure beats cosine)", flush=True)

    print("[self-test] REAL SemanticHDEncoder + REAL PPR pool + REAL features + REAL gate + "
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
    fact_nterms = np.array([len(t) for t in fact_terms], dtype=np.float64)
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = ppr.build_incidence(fact_terms, vocab)
    M, Sft, idf = ppr.build_transition(A, df, use_idf=True)
    idf_of_term = {vocab[i]: float(idf[i]) for i in range(len(vocab))}

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

    seeds = ppr.link_seeds([q_words], vocab, t2i, term_vecs, [q_word_vecs], SEED_COS)
    seed_mat = ppr.seeds_to_matrix(seeds, len(vocab))
    a = ppr.ppr_batch(seed_mat, M, HOPS, DAMP)
    fscore = ppr.fact_activation(a, Sft)[0]
    pool_idx = ppr.topk_from_scores(fscore, min(K_POOL, len(store_sents)))
    assert pool_idx.size > 0, "real: empty spreading pool"

    lure_set, _ = simgate.standout_lure_choices(stem_words, q["choices"])
    fw = [fact_word_sets[i] for i in pool_idx]
    Phi = build_features(SV_store[pool_idx], fscore[pool_idx], fw, fact_nterms[pool_idx],
                         stem_words, STEM, choice_hd, lure_set, idf_of_term, t2i)
    assert Phi.shape == (pool_idx.size, N_FEAT), "real: feature matrix shape mismatch"
    mu, sd = standardize_fit([Phi])
    Z = standardize_apply(Phi, mu, sd)
    assert Z.shape == (pool_idx.size, N_FEAT + 1), "real: standardized shape mismatch"

    gate = CreditAssignmentGate(N_FEAT + 1)

    def real_reward(qi, sel_local):
        sel = pool_idx[sel_local]
        fh = SV_store[sel]
        q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
        sc, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
        return 1.0 if agg._pick(sc, np.random.default_rng(0)) == q["correct_index"] else 0.0

    diag = gate.train([Z], real_reward, np.random.default_rng(3), n_epochs=10, lr=0.05)
    sel = gate.select_topk(Z, K_SEL)
    assert sel.size == min(K_SEL, pool_idx.size), "real: selection size wrong"
    # UNCHANGED combiner reuse on the learned selection
    fh = SV_store[pool_idx[sel]]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
    sc, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc.shape[0] == len(q["choices"]), "real: combiner reuse shape mismatch"

    # determinism of features
    Phi2 = build_features(SV_store[pool_idx], fscore[pool_idx], fw, fact_nterms[pool_idx],
                          stem_words, STEM, choice_hd, lure_set, idf_of_term, t2i)
    assert np.allclose(Phi, Phi2), "real: features non-deterministic"

    # split determinism
    qs = agg.load_wt_questions(limit_easy=20, limit_chal=20)
    tr1, te1 = split_questions(qs)
    tr2, te2 = split_questions(qs)
    assert tr1 == tr2 and te1 == te2, "split non-deterministic"
    assert set(tr1).isdisjoint(set(te1)), "split leak: train/test overlap"

    # McNemar sanity
    b, c, stat, p = mcnemar([1, 1, 0, 0, 1], [1, 0, 1, 1, 0])
    assert 0.0 <= p <= 1.0, "mcnemar p out of range"

    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    print("[self-test] PASS (planted credit-assignment lever isolated from cosine; real encoder+PPR-"
          "pool+features+learned-gate+UNCHANGED combiner; deterministic features + split; McNemar)",
          flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        # FULL graph (real pool at scale), question SUBSET (split into train/held-out)
        return {"n_dim": 2048, "limit_easy": 300, "limit_chal": 250, "n_epochs": 40}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None, "n_epochs": N_EPOCHS}


def _encode_all(enc, questions, sents, vocab):
    """Encode store + terms + question fields ONCE. Returns dict of encoded matrices."""
    SV_store = arc._encode_store(enc, sents)
    term_vecs = arc._encode_store(enc, vocab)
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"]) for q in questions])
    STEM = arc._encode_store(enc, [q["stem"] for q in questions])
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
                     for q in questions]
    return {"SV_store": SV_store, "term_vecs": term_vecs, "QQ": QQ, "STEM": STEM,
            "choice_hd_map": choice_hd_map}


def run(mode, output_dir):
    cfg = _config(mode)
    nd = cfg["n_dim"]
    n_epochs = cfg["n_epochs"]

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "load_questions")
    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    nQ = len(questions)
    chance = arc._chance_theoretical(questions)
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = nQ - n_easy
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f}", flush=True)

    # ---- store = FULL tablestore (gold facts are curriculum sentences, NOT answer labels) ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = agg.parse_tablestore()
    uids = sorted(uid2sent.keys())
    sents = [uid2sent[u] for u in uids]
    uid2fi = {u: i for i, u in enumerate(uids)}
    nFacts = len(uids)
    print(f"[store] full tablestore = {nFacts} facts", flush=True)

    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in sents]
    fact_word_sets = [set(t) for t in fact_terms]
    fact_nterms = np.array([len(t) for t in fact_terms], dtype=np.float64)
    vocab = sorted({t for terms in fact_terms for t in terms})

    _heartbeat(output_dir, "encode_store", {"n": nFacts})
    t_enc = time.perf_counter()
    E = _encode_all(enc, questions, sents, vocab)
    print(f"[encode] store+questions in {time.perf_counter()-t_enc:.1f}s", flush=True)
    SV_store = E["SV_store"]; term_vecs = E["term_vecs"]
    QQ = E["QQ"]; STEM = E["STEM"]; choice_hd_map = E["choice_hd_map"]

    # question words + vectors (for PPR seed-linking)
    q_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]),
                                                    MIN_TERM_LEN))) for q in questions]
    uniq_words = sorted({w for ws in q_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}
    q_word_vecs_per_q = [uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)
                         for ws in q_words_per_q]
    stem_words_per_q = [set(arc._content_words(q["stem"], MIN_TERM_LEN)) for q in questions]

    def build_pool_and_features(incidence_perm=None):
        """Build the PPR pool + per-question standardized-feature inputs.
        incidence_perm: if not None, a permutation of fact rows applied to the incidence (SHUFFLED
        graph control -> destroys real term<->fact structure). Returns (FB, idf_of_term, pool_idx_per_q,
        Phi_raw_per_q)."""
        ft = fact_terms
        if incidence_perm is not None:
            ft = [fact_terms[incidence_perm[i]] for i in range(nFacts)]   # scramble which facts hold which terms
        A, df, t2i = ppr.build_incidence(ft, vocab)
        Mtr, Sft, idf = ppr.build_transition(A, df, use_idf=True)
        idf_of_term = {vocab[i]: float(idf[i]) for i in range(len(vocab))}
        seeds = ppr.link_seeds(q_words_per_q, vocab, t2i, term_vecs, q_word_vecs_per_q, SEED_COS)
        seed_mat = ppr.seeds_to_matrix(seeds, len(vocab))
        a_real = ppr.ppr_batch(seed_mat, Mtr, HOPS, DAMP)
        FB = ppr.fact_activation(a_real, Sft)
        pool_idx_per_q = [ppr.topk_from_scores(FB[qi], K_POOL) for qi in range(nQ)]
        Phi_raw_per_q = []
        for qi in range(nQ):
            pidx = pool_idx_per_q[qi]
            lure_set, _ = simgate.standout_lure_choices(stem_words_per_q[qi], questions[qi]["choices"])
            fw = [fact_word_sets[i] for i in pidx]
            Phi = build_features(SV_store[pidx], FB[qi][pidx], fw, fact_nterms[pidx],
                                 stem_words_per_q[qi], STEM[qi], choice_hd_map[qi], lure_set,
                                 idf_of_term, t2i)
            Phi_raw_per_q.append(Phi)
        return FB, pool_idx_per_q, Phi_raw_per_q

    _heartbeat(output_dir, "ppr_pool_real")
    FB, pool_idx_per_q, Phi_raw_per_q = build_pool_and_features(incidence_perm=None)

    # ---- deterministic stratified train / held-out split ----
    train_idx, test_idx = split_questions(questions, frac_train=0.5, seed=SEED)
    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    print(f"[split] train={len(train_idx)} held-out={len(test_idx)} "
          f"(held-out challenge={sum(1 for i in test_idx if not is_easy[i])})", flush=True)

    # ---- reward via UNCHANGED combiner ----
    def combiner_pick(qi, sel_global_idx):
        if sel_global_idx.size == 0:
            sc, _ = agg.aggregate(np.zeros((0, nd), np.float32), np.zeros(0, np.float32),
                                  choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
            return agg._pick(sc, np.random.default_rng(SEED + qi))
        fh = SV_store[sel_global_idx]
        q_rel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        sc, _ = agg.aggregate(fh, q_rel, choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
        return agg._pick(sc, np.random.default_rng(SEED + qi))

    def make_reward_fn(pool_per_q, correct_of):
        def reward_fn(qi, sel_local):
            sel = pool_per_q[qi][sel_local]
            return 1.0 if combiner_pick(qi, sel) == correct_of[qi] else 0.0
        return reward_fn

    correct_true = {qi: questions[qi]["correct_index"] for qi in range(nQ)}
    # shuffled reward: permute the correct-answer used for reward on TRAIN (a wrong 'gold')
    rng_sr = np.random.default_rng(SEED + 777)
    correct_shuf = dict(correct_true)
    for qi in train_idx:
        nc = len(questions[qi]["choices"])
        correct_shuf[qi] = int(rng_sr.integers(0, nc))

    # ---- standardize on TRAIN pools only ----
    mu, sd = standardize_fit([Phi_raw_per_q[qi] for qi in train_idx])
    Z_full = [standardize_apply(Phi_raw_per_q[qi], mu, sd) for qi in range(nQ)]
    Z_cos = [standardize_apply(Phi_raw_per_q[qi], mu, sd, feat_mask=COS_IDX) for qi in range(nQ)]

    # ---- TRAIN the learned gates on TRAIN correctness ----
    _heartbeat(output_dir, "train_learned_gate")
    reward_true = make_reward_fn(pool_idx_per_q, correct_true)
    reward_shuf = make_reward_fn(pool_idx_per_q, correct_shuf)

    gate_L = CreditAssignmentGate(N_FEAT + 1)
    diag_L = gate_L.train([Z_full[qi] for qi in train_idx], _reindex(reward_true, train_idx),
                          np.random.default_rng(SEED + 1), n_epochs=n_epochs, lr=LR)
    gate_cos = CreditAssignmentGate(N_FEAT + 1)
    diag_cos = gate_cos.train([Z_cos[qi] for qi in train_idx], _reindex(reward_true, train_idx),
                              np.random.default_rng(SEED + 2), n_epochs=n_epochs, lr=LR)
    gate_sr = CreditAssignmentGate(N_FEAT + 1)
    diag_sr = gate_sr.train([Z_full[qi] for qi in train_idx], _reindex(reward_shuf, train_idx),
                            np.random.default_rng(SEED + 3), n_epochs=n_epochs, lr=LR)
    print(f"[train] L reward {diag_L['train_reward_curve'][0]}->{diag_L['train_reward_curve'][-1]} | "
          f"cos {diag_cos['train_reward_curve'][-1]} | shuffreward "
          f"{diag_sr['train_reward_curve'][0]}->{diag_sr['train_reward_curve'][-1]}", flush=True)

    # ---- SHUFFLED GRAPH control: rebuild pool+features on a scrambled incidence, retrain ----
    _heartbeat(output_dir, "shuffled_graph_control")
    perm = np.random.default_rng(SEED + 999).permutation(nFacts)
    FB_sh, pool_sh, Phi_sh = build_pool_and_features(incidence_perm=perm)
    mu_sh, sd_sh = standardize_fit([Phi_sh[qi] for qi in train_idx])
    Z_sh = [standardize_apply(Phi_sh[qi], mu_sh, sd_sh) for qi in range(nQ)]
    reward_true_sh = make_reward_fn(pool_sh, correct_true)
    gate_sh = CreditAssignmentGate(N_FEAT + 1)
    diag_shg = gate_sh.train([Z_sh[qi] for qi in train_idx], _reindex(reward_true_sh, train_idx),
                             np.random.default_rng(SEED + 4), n_epochs=n_epochs, lr=LR)

    # ---- EVAL all arms (greedy top-K_SEL) on BOTH splits ----
    _heartbeat(output_dir, "evaluate_arms")
    picks = {name: np.full(nQ, -1, dtype=np.int64)
             for name in ("A", "G", "L", "Lc", "Lsr", "Shg", "O")}
    for qi in range(nQ):
        pidx = pool_idx_per_q[qi]
        # A_baseline: whole pool
        picks["A"][qi] = combiner_pick(qi, pidx)
        # G_simgate: reuse the hand-set similarity gate (goal-bias + RIF suppression)
        lure_set, _ = simgate.standout_lure_choices(stem_words_per_q[qi], questions[qi]["choices"])
        fw = [fact_word_sets[i] for i in pidx]
        gs = simgate.gate_scores(SV_store[pidx], fw, stem_words_per_q[qi], STEM[qi],
                                 choice_hd_map[qi], lure_set)
        picks["G"][qi] = combiner_pick(qi, pidx[simgate._topk_idx(gs["gate"], K_SEL)])
        # L_learned / L_cosonly / L_shuffreward: learned gates over the real pool
        picks["L"][qi] = combiner_pick(qi, pidx[gate_L.select_topk(Z_full[qi], K_SEL)])
        picks["Lc"][qi] = combiner_pick(qi, pidx[gate_cos.select_topk(Z_cos[qi], K_SEL)])
        picks["Lsr"][qi] = combiner_pick(qi, pidx[gate_sr.select_topk(Z_full[qi], K_SEL)])
        # Sh_graph: learned gate over the SHUFFLED-graph pool
        picks["Shg"][qi] = combiner_pick(qi, pool_sh[qi][gate_sh.select_topk(Z_sh[qi], K_SEL)])
        # O_oracle: gold central facts
        grows = np.array([uid2fi[u] for u in questions[qi]["gold_central"] if u in uid2fi],
                         dtype=np.int64)
        picks["O"][qi] = combiner_pick(qi, grows)

    correct = {name: np.array([int(picks[name][qi] == questions[qi]["correct_index"])
                               for qi in range(nQ)], dtype=np.int64)
               for name in picks}

    tr_mask = np.zeros(nQ, dtype=bool); tr_mask[train_idx] = True
    te_mask = np.zeros(nQ, dtype=bool); te_mask[test_idx] = True
    chal = ~is_easy

    def acc(mask, name):
        m = correct[name][mask]
        return round(float(np.mean(m)), 4) if m.size else None

    def block(split_mask, label):
        return {name: {"all": acc(split_mask, name),
                       "easy": acc(split_mask & is_easy, name),
                       "challenge": acc(split_mask & chal, name)} for name in picks}

    heldout = block(te_mask, "heldout")
    train = block(tr_mask, "train")
    for name in ("A", "G", "L", "Lc", "Lsr", "Shg", "O"):
        print(f"[held-out] {name}: all={heldout[name]['all']} easy={heldout[name]['easy']} "
              f"chal={heldout[name]['challenge']}", flush=True)

    # ---- PRIMARY discriminator: HELD-OUT Challenge ----
    te_chal = te_mask & chal
    Lc_acc = heldout["L"]["challenge"]
    Gc_acc = heldout["G"]["challenge"]
    Ac_acc = heldout["A"]["challenge"]
    Oc_acc = heldout["O"]["challenge"]
    d_LG = round((Lc_acc or 0.0) - (Gc_acc or 0.0), 4)      # learned vs similarity gate
    d_LA = round((Lc_acc or 0.0) - (Ac_acc or 0.0), 4)      # learned vs sim-pool baseline
    d_SRA = round((heldout["Lsr"]["challenge"] or 0.0) - (Ac_acc or 0.0), 4)   # shuffled-reward - baseline
    d_SHA = round((heldout["Shg"]["challenge"] or 0.0) - (Ac_acc or 0.0), 4)   # shuffled-graph - baseline
    d_LcosA = round((heldout["Lc"]["challenge"] or 0.0) - (Ac_acc or 0.0), 4)  # cos-only learned - baseline
    # generalization: held-out (L-A) vs train (L-A)
    tr_d_LA = round((train["L"]["challenge"] or 0.0) - (train["A"]["challenge"] or 0.0), 4)
    generalizes = (tr_d_LA <= 0.0) or (d_LA >= GEN_FRAC * tr_d_LA)

    # paired McNemar on held-out Challenge (L vs G) and (L vs A)
    mcLG = mcnemar(correct["G"][te_chal], correct["L"][te_chal])
    mcLA = mcnemar(correct["A"][te_chal], correct["L"][te_chal])
    n_te_chal = int(np.sum(te_chal))

    # ---- gates ----
    ag_saturated = (Ac_acc or 0.0) >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < (Ac_acc or 0.0) < 0.95
    learn_fired = diag_L["train_reward_curve"][-1] > diag_L["train_reward_curve"][0]

    import hashlib
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest()
               for name in ("A", "G", "L", "Lc", "Lsr", "Shg")}
    arms_differ = len(set(digests.values())) == len(digests)

    sig_LG = (mcLG[3] is not None) and (mcLG[3] < MCNEMAR_ALPHA)
    shuffreward_collapses = d_SRA <= SHUFFREWARD_MAX
    shuffgraph_collapses = d_SHA <= SHUFFGRAPH_MAX

    # ---- verdict (PRIMARY = held-out Challenge; L vs G is the credit-assignment lever test) ----
    if n_te_chal < 30:
        verdict = "LEARNED_GATE_INCONCLUSIVE_SMALL_HELDOUT"
        vmsg = (f"held-out Challenge n={n_te_chal} < 30 -- too small for a decisive paired test "
                f"(run FULL). L={Lc_acc} G={Gc_acc} A={Ac_acc}.")
    elif ag_saturated:
        verdict = "LEARNED_GATE_DISCRIMINATOR_SATURATED"
        vmsg = (f"baseline A Challenge {Ac_acc} >= {AG_BASELINE_SAT}: pool already saturates; no "
                f"headroom for selection (report, not a mechanism failure).")
    elif not learn_fired:
        verdict = "LEARNED_GATE_TRAINING_DID_NOT_FIRE"
        vmsg = (f"REINFORCE did not increase TRAIN reward "
                f"({diag_L['train_reward_curve'][0]}->{diag_L['train_reward_curve'][-1]}); the "
                f"credit-assignment loop is inert -- investigate lr/features before trusting eval.")
    elif (d_LG >= HP_LG and sig_LG and d_LA >= HP_LA and shuffreward_collapses
          and shuffgraph_collapses and generalizes and arms_differ):
        verdict = "CREDIT_ASSIGNMENT_LEVER_WORKS"
        vmsg = (f"LEARNED credit-assignment gate BEATS the similarity gate on HELD-OUT Challenge: "
                f"L={Lc_acc} vs G_simgate={Gc_acc} (d={d_LG:+.4f} >= {HP_LG}); McNemar b={mcLG[0]} "
                f"c={mcLG[1]} p={mcLG[3]:.4f} (<{MCNEMAR_ALPHA}); vs A_baseline={Ac_acc} "
                f"(d={d_LA:+.4f} >= {HP_LA}); shuffled-reward R-A={d_SRA:+.4f} (<={SHUFFREWARD_MAX}, "
                f"collapses); shuffled-graph Sh-A={d_SHA:+.4f} (<={SHUFFGRAPH_MAX}, collapses); "
                f"cos-only learned-A={d_LcosA:+.4f} (structure adds {round(d_LA-d_LcosA,4):+.4f}); "
                f"generalizes (train L-A={tr_d_LA:+.4f}, held-out {d_LA:+.4f}). Ceiling O={Oc_acc}. "
                f"Credit-assignment (not similarity) is the precision lever.")
    elif d_LG <= MB_LG:
        verdict = "HONEST_NEG_encoder_wall_foundational"
        vmsg = (f"HONEST NEGATIVE: the learned credit-assignment gate does NOT beat the hand-set "
                f"similarity gate on held-out Challenge (L={Lc_acc} vs G={Gc_acc}, d={d_LG:+.4f} "
                f"<= {MB_LG}). Learning-from-correctness cannot overcome the thin encoder's fact "
                f"reps -> the encoder/meaning wall is FOUNDATIONAL even for selection (consistent "
                f"with the 7x similarity-lineage root cause). vs A_baseline d_LA={d_LA:+.4f}; "
                f"shuffled-reward R-A={d_SRA:+.4f}; ceiling O={Oc_acc}. The fix is grounded/learned "
                f"MEANING, not a better selector over thin reps.")
    else:
        verdict = "LEARNED_GATE_MIDDLE_BAND"
        vmsg = (f"MIDDLE: held-out L vs G d={d_LG:+.4f} (HARD_PASS needs d>={HP_LG} AND McNemar "
                f"p<{MCNEMAR_ALPHA} AND all controls; HONEST_NEG needs d<={MB_LG}) -- "
                f"McNemar p={mcLG[3]} (sig={sig_LG}), d_LA={d_LA:+.4f} (>= {HP_LA}? "
                f"{d_LA >= HP_LA}), shuffreward R-A={d_SRA:+.4f} (collapses={shuffreward_collapses}), "
                f"shuffgraph Sh-A={d_SHA:+.4f} (collapses={shuffgraph_collapses}), "
                f"generalizes={generalizes}. Learned selection helps but not decisively; if a control "
                f"failed to collapse, suspect leak/memorization not a real lever.")

    grade = arc._grade_proxy(heldout["L"]["easy"], heldout["L"]["challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [held-out Chal n={n_te_chal}] L={Lc_acc} G_simgate={Gc_acc} "
                    f"A_baseline={Ac_acc} O_oracle={Oc_acc} | d(L-G)={d_LG} McNemar_p={mcLG[3]} | "
                    f"d(L-A)={d_LA} | shuffreward(R-A)={d_SRA} shuffgraph(Sh-A)={d_SHA} "
                    f"cos-only(Lc-A)={d_LcosA} | train_reward "
                    f"{diag_L['train_reward_curve'][0]}->{diag_L['train_reward_curve'][-1]} | "
                    f"chance={round(chance,4)}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED, "n_epochs": n_epochs,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_train": len(train_idx), "n_heldout": len(test_idx),
        "n_heldout_challenge": n_te_chal,
        "chance_theoretical": round(chance, 4),
        "k_pool": K_POOL, "k_sel": K_SEL, "lr": LR, "l2": L2, "baseline_beta": BASELINE_BETA,
        "features": FEATURES,
        # PRIMARY: held-out + train accuracy by arm/split
        "acc_heldout": heldout, "acc_train": train,
        "d_L_minus_G_challenge": d_LG,
        "d_L_minus_A_challenge": d_LA,
        "d_shuffreward_minus_A": d_SRA,
        "d_shuffgraph_minus_A": d_SHA,
        "d_cosonly_minus_A": d_LcosA,
        "train_d_L_minus_A_challenge": tr_d_LA,
        "generalizes": bool(generalizes),
        "mcnemar_L_vs_G_heldout_chal": {"b_G_right_L_wrong": mcLG[0], "c_G_wrong_L_right": mcLG[1],
                                        "stat": None if mcLG[2] is None else round(mcLG[2], 4),
                                        "p_value": None if mcLG[3] is None else round(mcLG[3], 5),
                                        "significant": bool(sig_LG)},
        "mcnemar_L_vs_A_heldout_chal": {"b_A_right_L_wrong": mcLA[0], "c_A_wrong_L_right": mcLA[1],
                                        "p_value": None if mcLA[3] is None else round(mcLA[3], 5)},
        "shuffreward_collapses": bool(shuffreward_collapses),
        "shuffgraph_collapses": bool(shuffgraph_collapses),
        "learned_weights": {FEATURES[i]: round(float(gate_L.w[i]), 4) for i in range(N_FEAT)},
        "learned_bias": round(float(gate_L.w[N_FEAT]), 4),
        "train_diag_L": diag_L, "train_diag_cos": diag_cos, "train_diag_shuffreward": diag_sr,
        "train_diag_shuffgraph": diag_shg,
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band),
        "ag_saturated": bool(ag_saturated),
        "learn_fired": bool(learn_fired),
        "arms_differ_verified": bool(arms_differ),
        "arm_pick_digests": digests,
        "bands": {"HP_LG": HP_LG, "MB_LG": MB_LG, "HP_LA": HP_LA,
                  "shuffreward_max": SHUFFREWARD_MAX, "shuffgraph_max": SHUFFGRAPH_MAX,
                  "gen_frac": GEN_FRAC, "mcnemar_alpha": MCNEMAR_ALPHA,
                  "ag_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: the STAGE-8 CREDIT-ASSIGNMENT retrieval-selection gate. A LEARNED linear Go/NoGo "
            "value g_i = w.phi_i over per-fact features (STRUCTURAL: PPR spreading-activation, pool-"
            "rank, IDF overlap, degree; + SIMILARITY: g_stem, g_disc, best_cos) selects top-K_SEL "
            "facts, fed to the UNCHANGED bind+settle combiner (agg.aggregate 'bundle', imported) over "
            "the UNCHANGED PPR spreading pool (arm B, imported). w is trained by a dopamine-RPE "
            "REINFORCE rule on REAL ARC correctness (reward = did the selected facts yield the correct "
            "answer via the unchanged combiner), reusing hdlab.action_selection's Go/NoGo WTA + cfrpe "
            "adaptive-LR credit-assignment PRINCIPLE. Trained on a TRAIN split; ALL arms eval on a "
            "disjoint HELD-OUT split; standardization stats from TRAIN only. Controls: L_shuffreward "
            "(permuted reward), Sh_graph (scrambled incidence), L_cosonly (cosine features only). "
            "PRIMARY = held-out Challenge accuracy, L_learned vs G_simgate (paired McNemar) + vs "
            "A_baseline. ANSWER-AGNOSTIC selection; gold used only for the reward signal on TRAIN and "
            "for held-out EVALUATION. "
            "HONEST ADAPTATION (not force-fit): action_selection.GoNoGoActionGate is a MULTI-HOP nav "
            "actor (state@W_ops + SR-transport reach); ARC selection is a ONE-SHOT contextual bandit, "
            "so the SR-M reach is NOT applicable and we use an ARC-native linear value. "
            "STUBBED/NOTED-NOT-BUILT: controlled RE-RETRIEVAL (query reformulation + second PPR pass); "
            "grounded/learned meaning to replace thin GloVe fact reps (the honest-negative fix)."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING",
        "compute_architecture": "mixed CPU: batched GloVe encode + scipy.sparse batched PPR (imported) + cheap per-fact features + REINFORCE over train questions + UNCHANGED combiner; wall target < 5min",
        "storage_strategy": "sharded (each fact = own embedding + own graph node; no superposition)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": "default_ok_for_this_regime (lr/epochs/L2 author-set a priori; NOT tuned to force a win; controls collapse toward baseline by construction if there is no real signal)",
    }
    _write_metrics_atomic(output_dir, metrics)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)
    return metrics


def _reindex(reward_fn, subset_idx):
    """Wrap a global-qi reward_fn so training (which passes LOCAL 0..len(subset)-1 indices) maps
    back to the true global question index."""
    def inner(local_qi, sel_local):
        return reward_fn(subset_idx[local_qi], sel_local)
    return inner


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
