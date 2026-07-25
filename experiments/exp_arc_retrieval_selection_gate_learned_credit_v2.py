"""arc_retrieval_selection_gate_learned_credit_v2 -- POWER the credit-assignment test + add the
missing FIXED-STRUCTURAL / best-non-learned control arm (VET contract on v1's MIDDLE_BAND).

WHY v2 (the two things v1's VET said were missing, both required here):
  1. MULTI-SPLIT POOLED SIGNIFICANCE. v1 tested L_learned vs G_simgate on a SINGLE 50/50 split:
     d=+0.0411 but McNemar p=0.194 (b=19,c=29) -- UNDERPOWERED, could not establish or kill the
     credit-assignment-specific increment. v2 runs N_SPLITS independent stratified splits and POOLS
     the paired discordant pairs -> a powered pooled McNemar + a per-split sign-test.
       v1 numbers MEASURED@data/exp_arc_retrieval_selection_gate_learned_credit_v1/metrics.json:
       A_chal=0.3333 G_chal=0.3704 L_chal=0.4115 O_chal=0.7284 d(L-G)=0.0411 mcnemar_p=0.19393
  2. FIXED / BEST-NON-LEARNED SELECTOR CONTROL (F_fixed). v1 only had G_simgate (a SIMILARITY gate)
     and A_baseline. The open question the VET raised: does the LEARNED credit-assignment VALUE beat
     a TUNED-but-NOT-LEARNED selector -- i.e. is only the GENERIC gate real (what any sensible top-K
     achieves), or does learned VALUE add a credit-assignment-SPECIFIC increment? F_fixed selects
     top-K_SEL by the SINGLE best fixed rule (each per-fact feature as a sole ranker, both signs, +
     the hand-set G_simgate), CHOSEN on the TRAIN split's Challenge accuracy, applied on held-out.
     No learned weights, no RPE credit-assignment. This is the "any sensible top-K / fixed-structural"
     null. PRIMARY TEST = L_learned vs F_fixed (pooled McNemar). Reported alongside: F_struct (best
     STRUCTURAL-only feature, the literal fixed-structural arm), F_ppr (raw top-K by PPR activation),
     G_simgate, A_baseline, O_oracle.

PRE-REG (author-set a priori; PRIMARY = pooled HELD-OUT Challenge, L_learned vs F_fixed):
  HARD-PASS  (credit-assignment-SPECIFIC benefit ESTABLISHED): pooled d(L - F_fixed) >= HP_LF AND
             pooled McNemar p < ALPHA AND >= SIGN_FRAC of splits have d(L-F_fixed)>0 AND L beats
             A_baseline pooled (>= HP_LA) AND must-fail controls collapse (shuffreward + shuffgraph)
             AND arms differ.
  HONEST-NEG (credit-assignment-SPECIFIC benefit NOT established -- only the generic gate is real,
             which is already known): pooled McNemar p(L vs F_fixed) >= ALPHA. Learned VALUE does not
             beat the best fixed non-learned selector once powered -> the +pp over baseline is the
             GENERIC top-K, not credit-assignment. Fix = grounded/learned MEANING, not a learned
             re-weighting over thin reps (consistent with the 7x similarity-lineage root cause).
  MIDDLE     : pooled p<ALPHA but point-estimate/sign/sanity gate fails, OR a must-fail control did
             NOT collapse (leak/memorization suspect -> test compromised, not a clean lever).

MUST-FAIL CONTROLS (kept from v1; must collapse toward baseline on split 0): L_shuffreward (train on
PERMUTED reward) and Sh_graph (train+eval on a SHUFFLED incidence graph). No-leak: gate + F_fixed
selection use TRAIN correctness only; ALL arms eval on a DISJOINT held-out split; standardization +
feature-selection stats from TRAIN only; features answer-agnostic; gold used only for the reward
signal on TRAIN and for held-out EVALUATION.

REUSE (do NOT rebuild): everything load-bearing is imported from v1 (CreditAssignmentGate, build_
features, standardize_*, split_questions, mcnemar, the reused PPR pool / bind+settle combiner / arc
helpers / hand-set simgate). v2 adds ONLY: the multi-split loop, the F_fixed/F_struct/F_ppr fixed
selectors, and the pooled-significance aggregation.

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT remote-
portable; sized to finish < 9 min foreground); NO push/remote-persist; ASCII-only; deterministic
(fixed int seeds, numpy default_rng, sorted iteration, no hash()); repo .venv; agent-reported
VET-PENDING (skunkworks owns landed-VET + atom banking).

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test runs v1's real encoder+PPR-pool+features+gate+combiner path AND a v2
#   PLANTED case proving the learned gate exploits a COMBINATORIAL reward-predictive signal that NO
#   single fixed (structural) feature selector can capture (primary test CAN fire) + arms differ
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - cardinality_ok: EXPECTED_N_UNITS = n_splits ; verdict guards len(per_split) == n_splits
# - baseline_in_band + AG-guard on A_baseline pooled challenge (headroom vs the 0.73 ceiling)
# - storage = SHARDED (each fact = own vector + own graph node; no superposition)
# - all reported numbers MEASURED@ this cell's metrics.json (v1 numbers cited MEASURED@ v1 metrics)
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
import hashlib
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# reuse EVERYTHING load-bearing from v1 (single source of truth for the gate + features + combiner)
from experiments import exp_arc_retrieval_selection_gate_learned_credit_v1 as v1

ppr = v1.ppr
agg = v1.agg
arc = v1.arc
simgate = v1.simgate
SemanticHDEncoder = v1.SemanticHDEncoder
_load_glove = v1._load_glove
_load_wordnet = v1._load_wordnet

CreditAssignmentGate = v1.CreditAssignmentGate
build_features = v1.build_features
standardize_fit = v1.standardize_fit
standardize_apply = v1.standardize_apply
split_questions = v1.split_questions
_topk_idx = v1._topk_idx
mcnemar = v1.mcnemar

FEATURES = v1.FEATURES
N_FEAT = v1.N_FEAT
STRUCT_IDX = v1.STRUCT_IDX
COS_IDX = v1.COS_IDX
K_POOL = v1.K_POOL
K_SEL = v1.K_SEL
HOPS = v1.HOPS
DAMP = v1.DAMP
SEED_COS = v1.SEED_COS
MIN_TERM_LEN = v1.MIN_TERM_LEN
SEED = v1.SEED
LR = v1.LR
L2 = v1.L2
BASELINE_BETA = v1.BASELINE_BETA
N_EPOCHS = v1.N_EPOCHS

ANCHOR_NAME = "arc_retrieval_selection_gate_learned_credit_v2"

# ---- multi-split (author-set a priori; verified to fit the foreground budget by smoke) ----
N_SPLITS_FULL = 9        # each = an independent stratified 50/50 split (distinct seed)
N_SPLITS_SMOKE = 2       # smoke runs at FULL-N scale, 2 splits, to fire the discriminator + time it


def split_seed(s):
    """Deterministic, well-separated per-split seed (no hash(); fixed int arithmetic)."""
    return SEED + 1009 * (s + 1)


# ---- F_fixed menu: fixed NON-LEARNED selectors (feature as sole ranker, a-priori sign) + G ----
# (f_index, sign, name). sign = +1 -> higher is better; -1 -> lower is better (mechanism a priori).
STRUCT_MENU = [
    (0, +1.0, "ppr_act"),        # spreading activation -- higher = more central
    (1, +1.0, "ppr_rank"),       # top of pool
    (4, +1.0, "idf_overlap"),    # IDF-weighted stem overlap
    (5, +1.0, "n_terms"),        # degree proxy
    (2, -1.0, "surf_pull_lo"),   # avoid surface-lure pull (RIF)
    (3, -1.0, "lure_align_lo"),  # avoid the standout-lure aligned facts (RIF)
]
COS_MENU = [
    (6, +1.0, "g_stem"),
    (7, +1.0, "g_disc"),
    (8, +1.0, "best_cos"),
]
PPR_MENU_NAME = "ppr_act"        # F_ppr = raw top-K by PPR activation (feature 0, +sign)

# ---- bands (author-set a priori; PRIMARY = pooled HELD-OUT Challenge, L vs F_fixed) ----
HP_LF = 0.02        # pooled d(L - F_fixed) held-out Challenge floor (strict > 0; META_RULE_L)
HP_LA = 0.03        # pooled d(L - A_baseline) held-out Challenge (gate must do SOMETHING)
ALPHA = 0.05        # pooled McNemar significance
SIGN_FRAC = 0.6     # >= 60% of splits must show d(L - F_fixed) > 0 (robustness vs one lucky split)
SHUFFREWARD_MAX = 0.02   # split-0 held-out chal: L_shuffreward - A <= this (permuted reward collapses)
SHUFFGRAPH_MAX = 0.03    # split-0 held-out chal: Sh_graph - A <= this (shuffled structure collapses)
AG_BASELINE_SAT = 0.95   # pooled A_baseline chal >= this -> vacuous (no headroom)


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
# self-test: v1 real path + v2 PLANTED combinatorial discriminator (learned beats best FIXED single
# feature) + split determinism + arms-differ
# ---------------------------------------------------------------------------
def _planted_combinatorial_discriminator():
    """PLANTED case proving the LEARNED credit-assignment gate exploits a reward-predictive signal
    that NO fixed single-feature selector can capture. Correct fact = argmax(s1 + s2) where s1,s2 are
    two structural features; DECOYS maximize s1-alone and s2-alone. A linear Go/NoGo value learns
    w1,w2 > 0 -> ranks the (s1+s2)-max fact first (~1.0). Every FIXED single-feature ranker (either
    sign) picks a decoy (train acc ~ chance). Proves the PRIMARY test (L vs F_fixed) CAN fire when a
    credit-assignment-specific (combinatorial) signal exists -- and that F_fixed is a real competitor
    (not a straw-man) because it wins whenever a single feature suffices."""
    rng = np.random.default_rng(11)
    P = 6
    F = N_FEAT + 1
    n_q = 60
    i1, i2 = STRUCT_IDX[0], STRUCT_IDX[1]
    Z_all, gold = [], []
    for _ in range(n_q):
        Z = rng.standard_normal((P, F)) * 0.2
        Z[:, N_FEAT] = 1.0
        s1 = rng.uniform(0.0, 0.5, P)
        s2 = rng.uniform(0.0, 0.5, P)
        good = int(rng.integers(0, P))
        s1[good] = 0.70
        s2[good] = 0.70                       # sum 1.40 = unique max sum
        d1 = int((good + 1) % P)
        s1[d1] = 0.95
        s2[d1] = 0.05                         # decoy: max s1 alone (sum 1.0)
        d2 = int((good + 2) % P)
        s1[d2] = 0.05
        s2[d2] = 0.95                         # decoy: max s2 alone (sum 1.0)
        Z[:, i1] = s1
        Z[:, i2] = s2
        Z[:, COS_IDX] = rng.standard_normal((P, len(COS_IDX))) * 0.2   # cosine = noise
        Z_all.append(Z)
        gold.append(good)

    def reward(qi, sel):
        return 1.0 if gold[qi] in set(sel.tolist()) else 0.0

    gate = CreditAssignmentGate(F)
    diag = gate.train(Z_all, reward, np.random.default_rng(1), n_epochs=140, lr=0.1)
    learned_acc = float(np.mean([reward(qi, gate.select_topk(Z_all[qi], 1)) for qi in range(n_q)]))

    best_fixed = 0.0
    best_desc = None
    for f in range(N_FEAT):
        for sgn in (1.0, -1.0):
            acc = float(np.mean([reward(qi, _topk_idx(sgn * Z_all[qi][:, f], 1))
                                 for qi in range(n_q)]))
            if acc > best_fixed:
                best_fixed = acc
                best_desc = (f, sgn)

    assert diag["train_reward_curve"][-1] > diag["train_reward_curve"][0], (
        "planted: REINFORCE did not increase train reward %s" % diag["train_reward_curve"])
    assert learned_acc > 0.75, (
        "planted: learned gate failed the combinatorial signal: %.3f" % learned_acc)
    assert learned_acc > best_fixed + 0.20, (
        "planted: learned did NOT beat the best FIXED single-feature selector "
        "(learned=%.3f best_fixed=%.3f feat=%s) -- primary test cannot fire"
        % (learned_acc, best_fixed, best_desc))
    return {"learned_acc": round(learned_acc, 3), "best_fixed_single": round(best_fixed, 3),
            "best_feat_idx": None if best_desc is None else int(best_desc[0])}


def self_test():
    print("[self-test] (1) v2 PLANTED combinatorial discriminator "
          "(learned gate beats the best FIXED single-feature selector) ...", flush=True)
    planted = _planted_combinatorial_discriminator()
    print(f"[self-test]   planted learned_acc={planted['learned_acc']} "
          f"best_fixed_single={planted['best_fixed_single']} (learned beats fixed by margin)",
          flush=True)

    print("[self-test] (2) split-seed determinism + distinct partitions across splits ...", flush=True)
    qs = agg.load_wt_questions(limit_easy=40, limit_chal=40)
    parts = []
    for s in range(3):
        tr1, te1 = split_questions(qs, frac_train=0.5, seed=split_seed(s))
        tr2, te2 = split_questions(qs, frac_train=0.5, seed=split_seed(s))
        assert tr1 == tr2 and te1 == te2, "split non-deterministic at s=%d" % s
        assert set(tr1).isdisjoint(set(te1)), "split leak at s=%d" % s
        parts.append(tuple(tr1))
    assert len(set(parts)) == 3, "splits are NOT distinct across seeds (multi-split is vacuous)"
    assert split_seed(0) != split_seed(1) != split_seed(2), "split seeds not distinct"

    print("[self-test] (3) v1 REAL code path (encoder + PPR pool + features + learned gate + "
          "UNCHANGED combiner) ...", flush=True)
    ok = v1.self_test()
    assert ok is True, "v1 real-code-path self-test did not return True"

    print("[self-test] PASS (planted combinatorial lever isolates learned-value from fixed single-"
          "feature selection; distinct deterministic splits; v1 real path green)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    # smoke = FULL-N scale (all questions, full graph) but few splits -> fires discriminator at scale
    # AND measures the shared-vs-per-split cost so N_SPLITS_FULL is verified to fit the budget.
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": None, "limit_chal": None,
                "n_epochs": 40, "n_splits": N_SPLITS_SMOKE}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None,
            "n_epochs": N_EPOCHS, "n_splits": N_SPLITS_FULL}


def run(mode, output_dir):
    cfg = _config(mode)
    nd = cfg["n_dim"]
    n_epochs = cfg["n_epochs"]
    n_splits = cfg["n_splits"]

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "load_questions")
    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    nQ = len(questions)
    chance = arc._chance_theoretical(questions)
    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    chal = ~is_easy
    n_easy = int(np.sum(is_easy))
    n_chal = int(np.sum(chal))
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f} "
          f"n_splits={n_splits}", flush=True)

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
    SV_store = arc._encode_store(enc, sents)
    term_vecs = arc._encode_store(enc, vocab)
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"]) for q in questions])
    STEM = arc._encode_store(enc, [q["stem"] for q in questions])
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
                     for q in questions]
    print(f"[encode] store+questions in {time.perf_counter()-t_enc:.1f}s", flush=True)

    q_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]),
                                                   MIN_TERM_LEN))) for q in questions]
    uniq_words = sorted({w for ws in q_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}
    q_word_vecs_per_q = [uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)
                         for ws in q_words_per_q]
    stem_words_per_q = [set(arc._content_words(q["stem"], MIN_TERM_LEN)) for q in questions]

    def build_pool_and_features(incidence_perm=None):
        ft = fact_terms
        if incidence_perm is not None:
            ft = [fact_terms[incidence_perm[i]] for i in range(nFacts)]
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

    # ---- UNCHANGED bind+settle combiner + cached picks (pick is deterministic given qi + selection) ----
    _pick_cache = {}

    def combiner_pick(qi, sel_global_idx):
        if sel_global_idx.size == 0:
            sc, _ = agg.aggregate(np.zeros((0, nd), np.float32), np.zeros(0, np.float32),
                                  choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
            return agg._pick(sc, np.random.default_rng(SEED + qi))
        fh = SV_store[sel_global_idx]
        q_rel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        sc, _ = agg.aggregate(fh, q_rel, choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
        return agg._pick(sc, np.random.default_rng(SEED + qi))

    def cached_pick(qi, sel_global_idx):
        key = (qi, tuple(sorted(int(x) for x in sel_global_idx.tolist())))
        v = _pick_cache.get(key)
        if v is None:
            v = combiner_pick(qi, sel_global_idx)
            _pick_cache[key] = v
        return v

    def correct_of(qi, pick):
        return int(pick == questions[qi]["correct_index"])

    # ---- SPLIT-INDEPENDENT arm correctness (computed ONCE over all nQ) ----
    # A_baseline (whole pool), G_simgate, O_oracle, and every FIXED single-feature selector's picks
    # do NOT depend on the train/held-out split. Only WHICH fixed selector F_fixed uses is split-
    # dependent (chosen by train Challenge accuracy) -> so we precompute every candidate's correctness
    # and just index by split.
    _heartbeat(output_dir, "precompute_split_independent_arms")
    corr_A = np.zeros(nQ, dtype=np.int64)
    corr_G = np.zeros(nQ, dtype=np.int64)
    corr_O = np.zeros(nQ, dtype=np.int64)
    menu = STRUCT_MENU + COS_MENU
    struct_only_names = {name for (_, _, name) in STRUCT_MENU}
    corr_menu = {name: np.zeros(nQ, dtype=np.int64) for (_, _, name) in menu}
    corr_menu["G_simgate"] = corr_G  # G is a menu candidate too (alias to corr_G)
    for qi in range(nQ):
        pidx = pool_idx_per_q[qi]
        Phi = Phi_raw_per_q[qi]
        # A_baseline
        corr_A[qi] = correct_of(qi, cached_pick(qi, pidx))
        # G_simgate (hand-set similarity gate)
        lure_set, _ = simgate.standout_lure_choices(stem_words_per_q[qi], questions[qi]["choices"])
        fw = [fact_word_sets[i] for i in pidx]
        gs = simgate.gate_scores(SV_store[pidx], fw, stem_words_per_q[qi], STEM[qi],
                                 choice_hd_map[qi], lure_set)
        corr_G[qi] = correct_of(qi, cached_pick(qi, pidx[simgate._topk_idx(gs["gate"], K_SEL)]))
        # O_oracle
        grows = np.array([uid2fi[u] for u in questions[qi]["gold_central"] if u in uid2fi],
                         dtype=np.int64)
        corr_O[qi] = correct_of(qi, cached_pick(qi, grows))
        # fixed single-feature selectors
        if pidx.size:
            for (f, sgn, name) in menu:
                sel_local = _topk_idx(sgn * Phi[:, f], K_SEL)
                corr_menu[name][qi] = correct_of(qi, cached_pick(qi, pidx[sel_local]))

    # ---- SHUFFLED reward permutation (per v1; permute the reward gold on TRAIN only) ----
    correct_true = {qi: questions[qi]["correct_index"] for qi in range(nQ)}

    def make_reward_fn(pool_per_q, correct_map):
        def reward_fn(qi, sel_local):
            sel = pool_per_q[qi][sel_local]
            return 1.0 if cached_pick(qi, sel) == correct_map[qi] else 0.0
        return reward_fn

    # ---- SHUFFLED-GRAPH pool (built once; used for the split-0 must-fail structure control) ----
    _heartbeat(output_dir, "shuffled_graph_pool")
    perm = np.random.default_rng(SEED + 999).permutation(nFacts)
    FB_sh, pool_sh, Phi_sh = build_pool_and_features(incidence_perm=perm)

    def sh_combiner_pick(qi, sel_global_idx):
        # shuffled-graph pool indexes into the SAME SV_store facts but via a scrambled incidence;
        # selection indices are global fact rows, combiner unchanged.
        return combiner_pick(qi, sel_global_idx)

    # =========================================================================
    # MULTI-SPLIT LOOP: train the learned gate per split; accumulate pooled discordant pairs
    # =========================================================================
    per_split = []
    # pooled per-question held-out-Challenge correctness (accumulated across splits) for L and the
    # split-chosen F_fixed / F_struct; plus paired arrays for the pooled McNemar.
    pooled = {"L": [], "F_fixed": [], "F_struct": [], "F_ppr": [], "G": [], "A": []}
    learn_fired_any = False
    split0 = {}

    for s in range(n_splits):
        _heartbeat(output_dir, "split", {"s": s})
        train_idx, test_idx = split_questions(questions, frac_train=0.5, seed=split_seed(s))
        tr_mask = np.zeros(nQ, dtype=bool); tr_mask[train_idx] = True
        te_mask = np.zeros(nQ, dtype=bool); te_mask[test_idx] = True
        tr_chal = tr_mask & chal
        te_chal = te_mask & chal

        # ---- learned gate: standardize on TRAIN pools, train on TRAIN correctness ----
        mu, sd = standardize_fit([Phi_raw_per_q[qi] for qi in train_idx])
        Z_full = [standardize_apply(Phi_raw_per_q[qi], mu, sd) for qi in range(nQ)]
        reward_true = make_reward_fn(pool_idx_per_q, correct_true)
        gate_L = CreditAssignmentGate(N_FEAT + 1)
        diag_L = gate_L.train([Z_full[qi] for qi in train_idx], v1._reindex(reward_true, train_idx),
                              np.random.default_rng(split_seed(s) + 1), n_epochs=n_epochs, lr=LR)
        learn_fired = diag_L["train_reward_curve"][-1] > diag_L["train_reward_curve"][0]
        learn_fired_any = learn_fired_any or learn_fired

        # eval L on ALL questions (cached combiner picks)
        corr_L = np.zeros(nQ, dtype=np.int64)
        for qi in range(nQ):
            pidx = pool_idx_per_q[qi]
            corr_L[qi] = correct_of(qi, cached_pick(qi, pidx[gate_L.select_topk(Z_full[qi], K_SEL)]))

        # ---- F_fixed: choose the best NON-LEARNED selector by TRAIN CHALLENGE accuracy ----
        # (conservative: F_fixed is TUNED toward the eval stratum on TRAIN -> strongest fixed control)
        def train_chal_acc(corr):
            m = corr[tr_chal]
            return float(np.mean(m)) if m.size else 0.0
        cand_scores = {name: train_chal_acc(corr_menu[name]) for name in corr_menu}
        # F_fixed over the FULL non-learned menu (structural + similarity + G)
        f_fixed_name = max(sorted(cand_scores.keys()), key=lambda n: cand_scores[n])
        corr_Ffixed = corr_menu[f_fixed_name]
        # F_struct over STRUCTURAL-only candidates (the literal fixed-structural arm)
        struct_scores = {n: cand_scores[n] for n in cand_scores if n in struct_only_names}
        f_struct_name = max(sorted(struct_scores.keys()), key=lambda n: struct_scores[n])
        corr_Fstruct = corr_menu[f_struct_name]
        corr_Fppr = corr_menu[PPR_MENU_NAME]

        # ---- accumulate pooled held-out-Challenge per-question correctness ----
        idx_te_chal = np.where(te_chal)[0]
        pooled["L"].append(corr_L[idx_te_chal])
        pooled["F_fixed"].append(corr_Ffixed[idx_te_chal])
        pooled["F_struct"].append(corr_Fstruct[idx_te_chal])
        pooled["F_ppr"].append(corr_Fppr[idx_te_chal])
        pooled["G"].append(corr_G[idx_te_chal])
        pooled["A"].append(corr_A[idx_te_chal])

        def hchal(corr):
            m = corr[te_chal]
            return round(float(np.mean(m)), 4) if m.size else None

        rec = {
            "s": s, "split_seed": split_seed(s),
            "n_heldout_chal": int(np.sum(te_chal)),
            "L_chal": hchal(corr_L), "F_fixed_chal": hchal(corr_Ffixed),
            "F_struct_chal": hchal(corr_Fstruct), "F_ppr_chal": hchal(corr_Fppr),
            "G_chal": hchal(corr_G), "A_chal": hchal(corr_A), "O_chal": hchal(corr_O),
            "f_fixed_name": f_fixed_name, "f_fixed_train_chal_acc": round(cand_scores[f_fixed_name], 4),
            "f_struct_name": f_struct_name,
            "d_L_minus_Ffixed": round((hchal(corr_L) or 0) - (hchal(corr_Ffixed) or 0), 4),
            "d_L_minus_Fppr": round((hchal(corr_L) or 0) - (hchal(corr_Fppr) or 0), 4),
            "d_L_minus_G": round((hchal(corr_L) or 0) - (hchal(corr_G) or 0), 4),
            "d_L_minus_A": round((hchal(corr_L) or 0) - (hchal(corr_A) or 0), 4),
            "train_reward_curve_ends": [diag_L["train_reward_curve"][0],
                                        diag_L["train_reward_curve"][-1]],
            "learn_fired": bool(learn_fired),
        }
        per_split.append(rec)
        print(f"[split {s}] L={rec['L_chal']} F_fixed={rec['F_fixed_chal']}({f_fixed_name}) "
              f"F_struct={rec['F_struct_chal']}({f_struct_name}) F_ppr={rec['F_ppr_chal']} "
              f"G={rec['G_chal']} A={rec['A_chal']} O={rec['O_chal']} | "
              f"d(L-Ffixed)={rec['d_L_minus_Ffixed']:+.4f}", flush=True)

        # ---- split 0 ONLY: must-fail controls (shuffreward + shuffgraph) ----
        if s == 0:
            _heartbeat(output_dir, "split0_mustfail_controls")
            # shuffled reward (permute train gold; retrain; eval held-out chal)
            rng_sr = np.random.default_rng(SEED + 777)
            correct_shuf = dict(correct_true)
            for qi in train_idx:
                correct_shuf[qi] = int(rng_sr.integers(0, len(questions[qi]["choices"])))
            reward_shuf = make_reward_fn(pool_idx_per_q, correct_shuf)
            gate_sr = CreditAssignmentGate(N_FEAT + 1)
            gate_sr.train([Z_full[qi] for qi in train_idx], v1._reindex(reward_shuf, train_idx),
                          np.random.default_rng(split_seed(s) + 3), n_epochs=n_epochs, lr=LR)
            corr_SR = np.zeros(nQ, dtype=np.int64)
            for qi in test_idx:
                if not chal[qi]:
                    continue
                pidx = pool_idx_per_q[qi]
                corr_SR[qi] = correct_of(qi, cached_pick(qi, pidx[gate_sr.select_topk(Z_full[qi], K_SEL)]))
            sr_chal = round(float(np.mean(corr_SR[te_chal])), 4) if np.sum(te_chal) else None

            # shuffled graph (scrambled incidence pool; retrain; eval held-out chal)
            mu_sh, sd_sh = standardize_fit([Phi_sh[qi] for qi in train_idx])
            Z_sh = [standardize_apply(Phi_sh[qi], mu_sh, sd_sh) for qi in range(nQ)]
            reward_true_sh = make_reward_fn(pool_sh, correct_true)
            gate_sh = CreditAssignmentGate(N_FEAT + 1)
            gate_sh.train([Z_sh[qi] for qi in train_idx], v1._reindex(reward_true_sh, train_idx),
                          np.random.default_rng(split_seed(s) + 4), n_epochs=n_epochs, lr=LR)
            corr_SHG = np.zeros(nQ, dtype=np.int64)
            for qi in test_idx:
                if not chal[qi]:
                    continue
                corr_SHG[qi] = correct_of(qi, sh_combiner_pick(qi, pool_sh[qi][gate_sh.select_topk(Z_sh[qi], K_SEL)]))
            shg_chal = round(float(np.mean(corr_SHG[te_chal])), 4) if np.sum(te_chal) else None

            a_chal_0 = rec["A_chal"] or 0.0
            split0 = {
                "shuffreward_chal": sr_chal, "shuffgraph_chal": shg_chal, "A_chal": rec["A_chal"],
                "d_shuffreward_minus_A": round((sr_chal or 0) - a_chal_0, 4),
                "d_shuffgraph_minus_A": round((shg_chal or 0) - a_chal_0, 4),
                "learned_weights": {FEATURES[i]: round(float(gate_L.w[i]), 4) for i in range(N_FEAT)},
                "learned_bias": round(float(gate_L.w[N_FEAT]), 4),
            }
            print(f"[split0 controls] shuffreward={sr_chal} (d_vs_A={split0['d_shuffreward_minus_A']:+.4f}) "
                  f"shuffgraph={shg_chal} (d_vs_A={split0['d_shuffgraph_minus_A']:+.4f})", flush=True)

    # =========================================================================
    # POOLED significance
    # =========================================================================
    _heartbeat(output_dir, "pool_significance")
    L_all = np.concatenate(pooled["L"]) if pooled["L"] else np.zeros(0, dtype=np.int64)
    Ffix_all = np.concatenate(pooled["F_fixed"]) if pooled["F_fixed"] else np.zeros(0, dtype=np.int64)
    Fstr_all = np.concatenate(pooled["F_struct"]) if pooled["F_struct"] else np.zeros(0, dtype=np.int64)
    Fppr_all = np.concatenate(pooled["F_ppr"]) if pooled["F_ppr"] else np.zeros(0, dtype=np.int64)
    G_all = np.concatenate(pooled["G"]) if pooled["G"] else np.zeros(0, dtype=np.int64)
    A_all = np.concatenate(pooled["A"]) if pooled["A"] else np.zeros(0, dtype=np.int64)
    n_pooled = int(L_all.size)

    def pooled_acc(x):
        return round(float(np.mean(x)), 4) if x.size else None

    def pooled_delta_and_mcnemar(base_all):
        # pooled McNemar over accumulated discordant pairs (base right/L wrong vs base wrong/L right)
        b, c, stat, p = mcnemar(base_all, L_all)
        d = round((pooled_acc(L_all) or 0) - (pooled_acc(base_all) or 0), 4)
        return {"d": d, "b_base_right_L_wrong": b, "c_base_wrong_L_right": c,
                "stat": None if stat is None else round(stat, 4),
                "p_value": None if p is None else round(p, 6)}

    mc_LF = pooled_delta_and_mcnemar(Ffix_all)     # PRIMARY: L vs F_fixed
    mc_LFstr = pooled_delta_and_mcnemar(Fstr_all)  # L vs fixed-STRUCTURAL only
    mc_LFppr = pooled_delta_and_mcnemar(Fppr_all)  # L vs raw top-K by PPR activation
    mc_LG = pooled_delta_and_mcnemar(G_all)        # L vs G_simgate (v1's contrast, now pooled)
    mc_LA = pooled_delta_and_mcnemar(A_all)        # L vs A_baseline

    # per-split sign consistency for the PRIMARY contrast
    d_LF_per_split = [r["d_L_minus_Ffixed"] for r in per_split]
    n_splits_LF_pos = int(sum(1 for d in d_LF_per_split if d > 0))
    sign_ok = n_splits_LF_pos >= int(np.ceil(SIGN_FRAC * n_splits))

    # ---- gates ----
    A_chal_pooled = pooled_acc(A_all) or 0.0
    ag_saturated = A_chal_pooled >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_chal_pooled < 0.95
    cardinality_ok = (len(per_split) == n_splits)
    shuffreward_collapses = (split0.get("d_shuffreward_minus_A", 1.0) <= SHUFFREWARD_MAX)
    shuffgraph_collapses = (split0.get("d_shuffgraph_minus_A", 1.0) <= SHUFFGRAPH_MAX)

    # arms differ: pooled correctness vectors must not be bit-identical across the key arms
    digests = {name: hashlib.sha256(arr.tobytes()).hexdigest()
               for name, arr in [("L", L_all), ("F_fixed", Ffix_all), ("F_ppr", Fppr_all),
                                  ("G", G_all), ("A", A_all)]}
    arms_differ = len(set(digests.values())) == len(digests)

    d_LF = mc_LF["d"]
    p_LF = mc_LF["p_value"]
    d_LA = mc_LA["d"]
    sig_LF = (p_LF is not None) and (p_LF < ALPHA)

    # =========================================================================
    # VERDICT (PRIMARY = pooled held-out Challenge, L_learned vs F_fixed)
    # =========================================================================
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = f"expected {n_splits} split-units, got {len(per_split)}; run incomplete."
    elif not learn_fired_any:
        verdict = "LEARNED_GATE_TRAINING_DID_NOT_FIRE"
        vmsg = ("REINFORCE did not increase TRAIN reward on ANY split; the credit-assignment loop is "
                "inert -- investigate lr/features before trusting eval.")
    elif ag_saturated:
        verdict = "LEARNED_GATE_DISCRIMINATOR_SATURATED"
        vmsg = (f"pooled A_baseline Challenge {A_chal_pooled:.4f} >= {AG_BASELINE_SAT}: pool already "
                f"saturates; no headroom for selection (report, not a mechanism failure).")
    elif not (shuffreward_collapses and shuffgraph_collapses):
        verdict = "LEARNED_GATE_CONTROL_LEAK_SUSPECT"
        vmsg = (f"a MUST-FAIL control did NOT collapse toward baseline on split 0 "
                f"(shuffreward d_vs_A={split0.get('d_shuffreward_minus_A')} <= {SHUFFREWARD_MAX}? "
                f"{shuffreward_collapses}; shuffgraph d_vs_A={split0.get('d_shuffgraph_minus_A')} "
                f"<= {SHUFFGRAPH_MAX}? {shuffgraph_collapses}). Suspect leak/memorization -> the L vs "
                f"F_fixed contrast is not trustworthy until the control collapses.")
    elif sig_LF and d_LF >= HP_LF and sign_ok and d_LA >= HP_LA and arms_differ:
        verdict = "CREDIT_ASSIGNMENT_SPECIFIC_BENEFIT_ESTABLISHED"
        vmsg = (f"POOLED across {n_splits} splits (held-out Challenge n_pooled={n_pooled}): the LEARNED "
                f"credit-assignment gate BEATS the best FIXED non-learned selector F_fixed. "
                f"L={pooled_acc(L_all)} vs F_fixed={pooled_acc(Ffix_all)} (d={d_LF:+.4f} >= {HP_LF}); "
                f"pooled McNemar b={mc_LF['b_base_right_L_wrong']} c={mc_LF['c_base_wrong_L_right']} "
                f"p={p_LF} (< {ALPHA}); {n_splits_LF_pos}/{n_splits} splits positive (>= "
                f"{SIGN_FRAC}); vs F_struct d={mc_LFstr['d']:+.4f} (p={mc_LFstr['p_value']}); vs F_ppr "
                f"d={mc_LFppr['d']:+.4f}; vs G d={mc_LG['d']:+.4f}; vs A d={d_LA:+.4f} (>= {HP_LA}); "
                f"shuffreward+shuffgraph collapse. Learned VALUE (not any sensible fixed top-K) is the "
                f"precision lever.")
    elif not sig_LF:
        verdict = "HONEST_NEG_credit_assignment_specific_not_established"
        vmsg = (f"HONEST NEGATIVE (POWERED): across {n_splits} splits (held-out Challenge "
                f"n_pooled={n_pooled}), the LEARNED gate does NOT beat the best FIXED non-learned "
                f"selector at pooled significance. L={pooled_acc(L_all)} vs F_fixed="
                f"{pooled_acc(Ffix_all)} (d={d_LF:+.4f}); pooled McNemar b="
                f"{mc_LF['b_base_right_L_wrong']} c={mc_LF['c_base_wrong_L_right']} p={p_LF} "
                f"(>= {ALPHA}); {n_splits_LF_pos}/{n_splits} splits positive. The credit-assignment-"
                f"SPECIFIC increment is within noise -> only the GENERIC gate is real (F_fixed/G "
                f"already lift over A_baseline={pooled_acc(A_all)}; that is known). Learned re-weighting "
                f"over thin GloVe reps does not add a credit-assignment-specific lever; the fix is "
                f"grounded/learned MEANING, not a better selector (7x similarity-lineage root cause). "
                f"vs F_struct d={mc_LFstr['d']:+.4f}; vs F_ppr d={mc_LFppr['d']:+.4f}; vs G "
                f"d={mc_LG['d']:+.4f}; ceiling O.")
    else:
        verdict = "CREDIT_ASSIGNMENT_MIDDLE_BAND"
        vmsg = (f"MIDDLE: pooled L vs F_fixed significant (p={p_LF}) but a secondary gate failed -- "
                f"d(L-F_fixed)={d_LF:+.4f} (>= {HP_LF}? {d_LF >= HP_LF}); sign {n_splits_LF_pos}/"
                f"{n_splits} (ok? {sign_ok}); d(L-A)={d_LA:+.4f} (>= {HP_LA}? {d_LA >= HP_LA}); "
                f"arms_differ={arms_differ}. Learned selection helps but not decisively across all "
                f"gates; treat as inconclusive.")

    L_chal_pooled = pooled_acc(L_all)
    grade = arc._grade_proxy(None, L_chal_pooled)

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [POOLED held-out Chal n={n_pooled} over {n_splits} splits] "
                    f"L={L_chal_pooled} F_fixed={pooled_acc(Ffix_all)} F_struct={pooled_acc(Fstr_all)} "
                    f"F_ppr={pooled_acc(Fppr_all)} G={pooled_acc(G_all)} A={pooled_acc(A_all)} | "
                    f"PRIMARY d(L-F_fixed)={d_LF} pooled_McNemar_p={p_LF} "
                    f"({n_splits_LF_pos}/{n_splits} splits pos) | d(L-A)={d_LA} | "
                    f"shuffreward_dA={split0.get('d_shuffreward_minus_A')} "
                    f"shuffgraph_dA={split0.get('d_shuffgraph_minus_A')} | chance={round(chance,4)}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED, "n_epochs": n_epochs, "n_splits": n_splits,
        "expected_n_units": n_splits, "cardinality_ok": bool(cardinality_ok),
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_pooled_heldout_challenge": n_pooled,
        "chance_theoretical": round(chance, 4),
        "k_pool": K_POOL, "k_sel": K_SEL, "lr": LR, "l2": L2, "baseline_beta": BASELINE_BETA,
        "features": FEATURES,
        # PRIMARY pooled contrasts
        "pooled_acc": {"L": pooled_acc(L_all), "F_fixed": pooled_acc(Ffix_all),
                       "F_struct": pooled_acc(Fstr_all), "F_ppr": pooled_acc(Fppr_all),
                       "G": pooled_acc(G_all), "A": pooled_acc(A_all)},
        "pooled_mcnemar_L_vs_F_fixed": mc_LF,
        "pooled_mcnemar_L_vs_F_struct": mc_LFstr,
        "pooled_mcnemar_L_vs_F_ppr": mc_LFppr,
        "pooled_mcnemar_L_vs_G": mc_LG,
        "pooled_mcnemar_L_vs_A": mc_LA,
        "d_L_minus_F_fixed_pooled": d_LF,
        "d_L_minus_A_pooled": d_LA,
        "n_splits_L_gt_F_fixed": n_splits_LF_pos,
        "sign_ok": bool(sign_ok),
        "per_split": per_split,
        "split0_mustfail_controls": split0,
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band),
        "ag_saturated": bool(ag_saturated),
        "learn_fired_any": bool(learn_fired_any),
        "shuffreward_collapses": bool(shuffreward_collapses),
        "shuffgraph_collapses": bool(shuffgraph_collapses),
        "arms_differ_verified": bool(arms_differ),
        "arm_pooled_digests": digests,
        "bands": {"HP_LF": HP_LF, "HP_LA": HP_LA, "alpha": ALPHA, "sign_frac": SIGN_FRAC,
                  "shuffreward_max": SHUFFREWARD_MAX, "shuffgraph_max": SHUFFGRAPH_MAX,
                  "ag_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "v1_reference_MEASURED": {
            "source": "data/exp_arc_retrieval_selection_gate_learned_credit_v1/metrics.json",
            "A_chal": 0.3333, "G_chal": 0.3704, "L_chal": 0.4115, "O_chal": 0.7284,
            "d_L_minus_G": 0.0411, "single_split_mcnemar_L_vs_G_p": 0.19393},
        "wired_vs_stubbed": (
            "WIRED (v2 = v1 + the two VET-required additions): (1) MULTI-SPLIT pooled significance -- "
            "N_SPLITS independent stratified 50/50 splits, pooled paired McNemar over accumulated "
            "held-out-Challenge discordant pairs + a per-split sign-test. (2) F_fixed = the best FIXED "
            "NON-LEARNED selector (each per-fact feature as a sole top-K ranker, a-priori sign, + the "
            "hand-set G_simgate), CHOSEN on TRAIN Challenge accuracy, applied on held-out -- no learned "
            "weights, no RPE. PRIMARY = pooled L_learned vs F_fixed. Also reported: F_struct (best "
            "STRUCTURAL-only feature = the literal fixed-structural arm), F_ppr (raw top-K by PPR "
            "activation), G_simgate, A_baseline, O_oracle. Everything else (learned Go/NoGo credit-"
            "assignment gate, per-fact features, UNCHANGED PPR pool + bind+settle combiner) is imported "
            "UNCHANGED from v1. Must-fail controls (shuffreward, shuffgraph) run on split 0 and must "
            "collapse. NO-LEAK: gate + F_fixed selection use TRAIN correctness only; disjoint held-out "
            "eval; TRAIN-only standardization/feature-selection; answer-agnostic features. "
            "STUBBED/NOTED-NOT-BUILT: grounded/learned MEANING to replace thin GloVe fact reps (the "
            "honest-negative fix); controlled RE-RETRIEVAL (query reformulation + 2nd PPR pass)."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING",
        "compute_architecture": ("mixed CPU: batched GloVe encode + scipy.sparse batched PPR "
                                 "(imported, shared across splits) + cached UNCHANGED combiner picks "
                                 "(split-independent arms computed once) + REINFORCE per split; "
                                 "wall target < 9min foreground"),
        "storage_strategy": "sharded (each fact = own embedding + own graph node; no superposition)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": ("default_ok_for_this_regime (lr/epochs/L2 + bands author-set a priori, "
                              "NOT tuned to force a win; F_fixed is TUNED toward the eval stratum on "
                              "TRAIN so it is the STRONGEST fixed control; controls collapse toward "
                              "baseline by construction if there is no real signal)"),
    }
    _write_metrics_atomic(output_dir, metrics)

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
