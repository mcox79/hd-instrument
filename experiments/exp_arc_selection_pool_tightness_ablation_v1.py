"""arc_selection_pool_tightness_ablation_v1 -- POOL-TIGHTNESS ablation: falsify-or-confirm hypothesis C.

THE QUESTION (VET atom 29549): 7 consecutive selection HARD_FAILs. VET root-cause = (B) similarity !=
entailment (conf 0.72): from the WIDE 100-fact pool EVERY answer choice greedily assembles an equally
self-supporting set; winning sets were 0/12 built from any gold fact; setmargin_points_correct 0.29 ~=
chance despite gold_in_pool 0.91; correctness DECOUPLED from gold-reach. The ONE thing the VET could NOT do
off disk: run a tighter-POOL ablation (the pool was fixed at K_WIDE=100). So (C) pool-too-wide /
retrieval-granularity is DISFAVORED but NOT formally falsified. THIS CELL SETTLES IT.

Does making the candidate POOL tighter/higher-precision make selection INFORMATIVE (the correct answer's
support starts to stand out), or does 'every choice self-supports' persist wherever the gold is still
retained?

ONE VARIABLE = POOL TIGHTNESS/PRECISION. selection (A_TOPK) + combiner (agg.aggregate 'bundle') + the
TRAIN/TEST split are held FIXED (all imported UNCHANGED). The WIDE re-retrieval pool machinery
(mr.reformulate_seeds / _rownorm_scores / ppr, recall@100=0.69) is UNCHANGED; the ONLY change is a
pool-tightness knob applied to WHICH retrieved facts are eligible candidates for selection.

POOL ARMS (tighten the candidate pool the SAME A_TOPK selection draws from):
  POOL_100 -- top-100 by F_RR retrieval score (BASELINE ANCHOR; A_TOPK_LEARNED@POOL_100 MUST reproduce the
              29545 harness anchor ~0.3663 TEST Challenge)
  POOL_50  -- top-50 by F_RR
  POOL_20  -- top-20 by F_RR
  POOL_10  -- top-10 by F_RR
  POOL_PREC-- PRECISION-FILTERED: keep only facts with F_RR >= FRAC_OF_MAX * max(F_RR) among the 100 (a
              high relevance/retrieval-score threshold on the score the retriever ACTUALLY exposes)

SELECTION METHODS re-run over each pool (UNCHANGED per-fact top-K + UNCHANGED combiner):
  LEARNED -- 29545 answer-agnostic learned relevance, top-K_SEL among the arm's pool -> combiner argmax
             [PRIMARY; the current best / harness anchor]
  GEO     -- geometric question-relevance top-K_SEL among the arm's pool -> combiner argmax (no-train robustness)
  RND     -- random K_SEL from the arm's pool -> combiner argmax [MUST-FAIL per pool -> collapse toward chance]
  ORACLE  -- gold facts -> combiner argmax [pool-independent CEILING ~0.687]

DECISIVE DUAL-TRACK METRIC per pool arm (tracked TOGETHER -- the honesty guard):
  (1) gold-RECALL-in-pool  -- does the gold fact still survive the tightening? (Q-level gold_in_pool_frac +
      fact-level retention vs the wide-100 pool)
  (2) selection INFORMATIVE -- setmargin_points_correct (of gold-reachable TEST-Chal Qs, does the A_TOPK
      selection + combiner pick the correct answer? i.e. does the correct answer's support stand out?) +
      mean margin_correct (combiner score of correct choice minus best lure) + end-to-end TEST Challenge.

PRE-REGISTERED DECISIVE LOGIC (bands a priori; NO tuning to force either verdict). BOTH tracks measured as
a LIFT over the POOL_100 wide baseline (the decisive question is whether tightening IMPROVES over wide at
gold-retaining pools; an absolute floor is a META_RULE_L artifact since the A_TOPK baseline
setmargin_points_correct is already ~0.40). 'Retains gold' is RELATIVE to POOL_100's own gold reach
(gold_in_pool_frac[arm] >= RECALL_RETAIN_FRAC * gold_in_pool_frac[POOL_100]):
  C CONFIRMED (cheap fix exists): SOME GOLD-RETAINING pool arm lifts TEST Challenge by >= C_LIFT_HP over
    POOL_100 OR lifts setmargin_points_correct by >= INFORM_LIFT_HP over POOL_100 (the correct answer's
    support starts to stand out) toward oracle.
  C FALSIFIED (=> B confirmed; deep reframe justified): at EVERY gold-retaining pool arm, Challenge does not
    lift (< MB_LIFT) AND setmargin_points_correct does not lift (< INFORM_LIFT_MB); the only 'improvement'
    (if any) coincides with recall COLLAPSE (gold dropped below the retain threshold) -- NOT a fix.
  HONESTY GUARD: recall + informativeness tracked TOGETHER at every pool size. A Challenge 'win' that
    coincides with recall collapse is FLAGGED recall_collapse_false_positive and does NOT confirm C.

Report STRAIGHT which way it lands. A C-FALSIFICATION (B confirmed) is the expected, fully-reportable
outcome. Glass-box: at the TIGHTEST gold-retaining pool, on surface-trap lure TEST Qs, show whether the
correct answer's combiner support now out-scores the lures (C predicts) or still ties (B predicts).

Contract: INLINE-LOCAL foreground-to-completion (GloVe+WorldTree git-ignored/large -> NOT remote-portable;
inherits the 29544/29545/29546/set_level contract); NO push/remote-persist; ASCII-only; deterministic
(fixed seeds, numpy default_rng, sorted iteration, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL pool encode + REAL topk_from_scores +
#   REAL pool-restriction + UNCHANGED combiner; PLANTED discriminator: a WIDE pool where per-fact top-K by
#   relevance picks a strong lure (WRONG) but TIGHTENING drops the lure while RETAINING gold -> A_TOPK now
#   picks gold (RIGHT), proving the C-confirm mechanism CAN fire (cell is not can't-fail); a SECOND unit
#   test drives the decision logic with a recall-collapse table -> asserts the honesty guard flags it and
#   does NOT confirm C
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + anchor regression on LEARNED@POOL_100 TEST challenge (== 29545 anchor ~0.3663)
# - storage = SHARDED (each fact = own embedding + own graph node)
# - GLASS-BOX: correct-vs-lure combiner support at the tightest gold-retaining pool (dam-Q autopsy)
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

# reuse (UNCHANGED): the 29545 baseline features + glass-box learner + split, the WIDE RR pool, the
# bind+bundle combiner, PPR graph, fixed signals, arc helpers, encoder. (Same import spine as the
# set_level cell so the pool-100 anchor reproduces the 29545 harness behavior.)
from experiments import exp_arc_selection_learned_relevance_glassbox_v1 as learned  # noqa: E402
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr    # noqa: E402
from experiments import exp_arc_retrieval_max_recall_ksweep_reretrieval_v1 as mr   # noqa: E402
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as gate    # noqa: E402
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg         # noqa: E402
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc             # noqa: E402
from experiments import exp_arc_selection_precision_coherence_subset_v1 as fixedsel  # noqa: E402
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (                 # noqa: E402
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_selection_pool_tightness_ablation_v1"
SEED = 20260802

# ---- selection hyperparams (UNCHANGED pool + combiner; inherited from 29545/gate) ----
K_WIDE = learned.K_WIDE      # UNCHANGED wide re-retrieval pool the selector picks FROM (=100)
RR_TOP_T = learned.RR_TOP_T  # UNCHANGED re-retrieval reformulation depth
K_SEL = learned.K_SEL        # UNCHANGED clean-fact selection width (Cowan-4; =4)
MU_SUPP = learned.MU_SUPP
SETTLE_T = agg.SETTLE_T
SETTLE_EPS = agg.SETTLE_EPS
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# reuse the 29545 learner + baseline features EXACTLY (regression-anchors LEARNED@POOL_100 to 0.3663)
FLAT_FEATURE_NAMES = learned.FEATURE_NAMES
train_glassbox_relevance = learned.train_glassbox_relevance
learned_score = learned.learned_score
_minmax_cols = learned._minmax_cols
_neg_count = learned._neg_count
question_features_flat = learned.question_features
_topk_idx = learned._topk_idx

# ---- the ONE knob = pool tightness ----
POOL_ARMS = ("POOL_100", "POOL_50", "POOL_20", "POOL_10", "POOL_PREC")
K_BY_ARM = {"POOL_100": 100, "POOL_50": 50, "POOL_20": 20, "POOL_10": 10}  # POOL_PREC is threshold-based
FRAC_OF_MAX = 0.5        # POOL_PREC: keep facts with F_RR >= FRAC_OF_MAX * max(F_RR over the wide-100 pool)
SEL_METHODS = ("LEARNED", "GEO", "RND")
PRIMARY_METHOD = "LEARNED"

# ---- bands (author-designed a priori; NO tuning) ----
# "retains gold" is RELATIVE to the POOL_100 baseline's OWN gold reach (not an absolute 0.91 that a small
# slice may not hit): an arm retains gold iff it keeps >= RECALL_RETAIN_FRAC of the wide pool's Q-level reach.
RECALL_RETAIN_FRAC = 0.90  # retains_gold iff gold_in_pool_frac[arm] >= RECALL_RETAIN_FRAC * gold_in_pool_frac[POOL_100]
# Both tracks are measured as a LIFT over the POOL_100 wide baseline (the decisive question is whether
# tightening IMPROVES over wide at gold-retaining pools -- NOT an absolute floor, which the A_TOPK baseline
# setmargin_pc ~0.40 already clears, a META_RULE_L band-floor artifact).
C_LIFT_HP = 0.05          # C-CONFIRM: a gold-retaining arm's TEST-Chal lift over POOL_100 >= this
MB_LIFT = 0.02            # MIDDLE floor for a Challenge lift over POOL_100
INFORM_LIFT_HP = 0.08     # C-CONFIRM: setmargin_points_correct lift over POOL_100 >= this (correct support stands out)
INFORM_LIFT_MB = 0.03     # MIDDLE floor for a setmargin_points_correct lift over POOL_100
RANDOM_MAX = 0.02         # per-pool RND lift over POOL_100 baseline must be <= this (must-fail)
ANCHOR_CHAL = 0.3663      # 29545 answer-agnostic TEST Challenge (LEARNED@POOL_100 regression anchor)
ANCHOR_TOL_CHAL = 0.05    # WARN if |LEARNED@POOL_100 TEST challenge - ANCHOR_CHAL| > this
AG_BASELINE_SAT = 0.95    # POOL_100 challenge >= this -> vacuous (no headroom)

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
# the ONE new mechanism: pool-tightness membership + per-pool A_TOPK selection (combiner UNCHANGED)
# ---------------------------------------------------------------------------
def pool_members(frr_wide, arm):
    """Local indices (into the wide-pool arrays, which are sorted DESC by F_RR) that survive tightening.
      frr_wide: [P] F_RR scores of the wide pool (descending). arm in POOL_ARMS. Returns int64 array."""
    P = frr_wide.shape[0]
    if P == 0:
        return np.zeros(0, dtype=np.int64)
    if arm == "POOL_PREC":
        thr = FRAC_OF_MAX * float(frr_wide.max())
        mem = np.where(frr_wide >= thr)[0].astype(np.int64)
        if mem.size == 0:            # always keep at least the top-scored fact
            mem = np.array([0], dtype=np.int64)
        return mem
    k = K_BY_ARM[arm]
    return np.arange(min(k, P), dtype=np.int64)   # top-k by F_RR (wide already desc)


def select_topk_local(score_wide, members_local, k_sel):
    """Top-k_sel LOCAL indices (subset of members_local) by score_wide (descending, stable ties). The
    per-fact selection score is FIXED (computed on the native wide pool); ONLY membership varies -> the
    ONE variable is pool tightness, not the scoring function."""
    if members_local.size == 0:
        return np.zeros(0, dtype=np.int64)
    s = score_wide[members_local]
    order = np.argsort(-s, kind="stable")
    return members_local[order[:min(k_sel, members_local.size)]]


def combiner_scores(fh, q_rel, choice_hd, rng):
    """CALL the UNCHANGED combiner (agg.aggregate 'bundle') on a selected set -> score[C]. Empty -> zeros."""
    if fh.shape[0] == 0:
        sc, _ = agg.aggregate(np.zeros((0, choice_hd.shape[1]), np.float32),
                              np.zeros(0, np.float32), choice_hd, "bundle", rng=rng)
        return sc
    sc, _ = agg.aggregate(fh.astype(np.float32), np.maximum(q_rel, 0.0).astype(np.float32),
                          choice_hd, "bundle", rng=rng)
    return sc


# ---------------------------------------------------------------------------
# decision logic (unit-testable: the load-bearing C-confirm/C-falsify + honesty guard)
# ---------------------------------------------------------------------------
def classify_c(per_arm):
    """per_arm: dict arm -> {gold_in_pool_frac, challenge, setmargin_pc}. POOL_100 = the wide baseline.
    BOTH tracks measured as a LIFT over POOL_100; 'retains gold' is RELATIVE to POOL_100's own reach.
    C_CONFIRMED iff some GOLD-RETAINING arm lifts Challenge >= C_LIFT_HP OR setmargin_pc >= INFORM_LIFT_HP
    over the wide baseline. Honesty: the max-Challenge-lift arm, if it lifts >= C_LIFT_HP but does NOT
    retain gold, is flagged recall_collapse_false_positive and does NOT confirm C."""
    base_chal = per_arm["POOL_100"]["challenge"]
    base_inform = per_arm["POOL_100"]["setmargin_pc"] or 0.0
    base_gold = per_arm["POOL_100"]["gold_in_pool_frac"] or 0.0
    retain_thr = RECALL_RETAIN_FRAC * base_gold
    cand = [a for a in per_arm if a != "POOL_100"]

    chal_lifts = {a: round(per_arm[a]["challenge"] - base_chal, 4) for a in per_arm}
    inform_lifts = {a: (round((per_arm[a]["setmargin_pc"] or 0.0) - base_inform, 4)
                        if per_arm[a]["setmargin_pc"] is not None else None) for a in per_arm}
    retains = {a: bool(per_arm[a]["gold_in_pool_frac"] is not None
                       and per_arm[a]["gold_in_pool_frac"] >= retain_thr) for a in per_arm}

    # honesty guard: the biggest Challenge lift among candidates
    best_arm = max(cand, key=lambda a: chal_lifts[a]) if cand else None
    recall_collapse_fp = bool(best_arm is not None and chal_lifts[best_arm] >= C_LIFT_HP
                              and not retains[best_arm])

    def hp(a):
        return (chal_lifts[a] >= C_LIFT_HP
                or (inform_lifts[a] is not None and inform_lifts[a] >= INFORM_LIFT_HP))

    def mb(a):
        return (chal_lifts[a] >= MB_LIFT
                or (inform_lifts[a] is not None and inform_lifts[a] >= INFORM_LIFT_MB))

    confirm_arms = [a for a in cand if retains[a] and hp(a)]
    middle_arms = [a for a in cand if retains[a] and mb(a)]

    if confirm_arms:
        verdict = "C_CONFIRMED"
    elif middle_arms:
        verdict = "C_MIDDLE"
    else:
        verdict = "C_FALSIFIED"
    return {
        "verdict": verdict, "challenge_lifts": chal_lifts, "informativeness_lifts": inform_lifts,
        "retains_gold": retains, "retain_threshold_gold_in_pool": round(retain_thr, 4),
        "confirm_arms": confirm_arms, "middle_arms": middle_arms,
        "best_lift_arm": best_arm, "best_challenge_lift": (chal_lifts[best_arm] if best_arm else None),
        "recall_collapse_false_positive": recall_collapse_fp,
    }


# ---------------------------------------------------------------------------
# self-test: planted pool-tightness discriminator (tighten drops lure, keeps gold -> selection flips
# correct) + decision-logic honesty-guard unit test + real code path + determinism
# ---------------------------------------------------------------------------
def _planted_pool_tightness_discriminator(nd=512):
    """WIDE pool where per-fact top-K selection by relevance picks a LURE bundle (WRONG), but TIGHTENING the
    pool (top-F_RR) drops the lures while RETAINING the gold fact -> A_TOPK now selects gold -> CORRECT.
    Proves the C-confirm mechanism CAN fire (cell is NOT can't-fail)."""
    rng = np.random.default_rng(43)

    def unit(v):
        return (v / np.linalg.norm(v)).astype(np.float32)
    C = np.linalg.qr(rng.standard_normal((nd, 3)))[0].T.astype(np.float32)   # 3 orthonormal choices
    c0, c1, c2 = C[0], C[1], C[2]
    choice_hd = np.stack([c0, c1, c2]).astype(np.float32)                    # c0 correct

    g = unit(0.95 * c0)                          # GOLD: supports c0, moderate surface relevance, TOP F_RR
    L1 = unit(0.85 * c1 + 0.10 * c0)             # lures: support c1 (wrong), HIGH surface relevance, LOW F_RR
    L2 = unit(0.80 * c1)
    L3 = unit(0.78 * c1)
    fh_wide = np.stack([g, L1, L2, L3]).astype(np.float32)                   # wide pool
    # F_RR (retrieval) reaches gold at the TOP; lures well BELOW the precision threshold (0.5*max=0.5)
    frr_wide = np.array([1.00, 0.30, 0.25, 0.20], dtype=np.float32)
    # per-fact selection relevance: lures HIGH (surface), gold moderate -> combiner (relev-weighted) leans
    # to the lure BUNDLE in the wide pool
    relev = np.array([0.60, 0.90, 0.88, 0.86], dtype=np.float32)

    # WIDE pool (all 4): top-K_SEL=4 by relevance -> {L1,L2,L3,g}; combiner bundle leans c1 (lures dominate)
    mem_wide = pool_members(frr_wide, "POOL_100")
    sel_w = select_topk_local(relev, mem_wide, K_SEL)
    sc_w = combiner_scores(fh_wide[sel_w], relev[sel_w], choice_hd, np.random.default_rng(0))
    pick_w = agg._pick(sc_w, np.random.default_rng(0))
    assert pick_w == 1, f"planted: WIDE pool A_TOPK should be captured by the lure (c1), got {pick_w} ({sc_w})"

    # PRECISION-FILTER (a REAL arm): F_RR >= 0.5*max drops all lures, RETAINS gold -> combiner -> c0 CORRECT
    mem_t = pool_members(frr_wide, "POOL_PREC")
    assert mem_t.tolist() == [0], f"planted: POOL_PREC should keep only the gold fact, got {mem_t.tolist()}"
    sel_t = select_topk_local(relev, mem_t, K_SEL)
    sc_t = combiner_scores(fh_wide[sel_t], relev[sel_t], choice_hd, np.random.default_rng(0))
    pick_t = agg._pick(sc_t, np.random.default_rng(0))
    assert pick_t == 0, f"planted: TIGHT pool A_TOPK should recover c0 (gold retained), got {pick_t} ({sc_t})"
    assert 0 in mem_t.tolist(), "planted: tight pool must retain the gold fact (local idx 0)"
    return {"pick_wide": int(pick_w), "pick_tight": int(pick_t),
            "sc_wide": [round(float(x), 3) for x in sc_w],
            "sc_tight": [round(float(x), 3) for x in sc_t]}


def _honesty_guard_unit_test():
    """Drive classify_c with synthetic per-arm tables to prove: (1) a gold-retaining lift -> C_CONFIRMED;
    (2) a lift that coincides with recall collapse -> flagged + NOT confirmed (=> C_FALSIFIED/other)."""
    # case 1: POOL_20 retains gold (>= 0.9*0.91) AND lifts Challenge -> C_CONFIRMED
    t1 = {
        "POOL_100": {"gold_in_pool_frac": 0.91, "challenge": 0.36, "setmargin_pc": 0.40},
        "POOL_20":  {"gold_in_pool_frac": 0.85, "challenge": 0.45, "setmargin_pc": 0.52},
        "POOL_10":  {"gold_in_pool_frac": 0.50, "challenge": 0.40, "setmargin_pc": 0.44},
    }
    r1 = classify_c(t1)
    assert r1["verdict"] == "C_CONFIRMED", f"honesty unit: expected C_CONFIRMED, got {r1['verdict']}"
    assert not r1["recall_collapse_false_positive"], "honesty unit: case1 must NOT flag recall collapse"

    # case 2: the ONLY lift is at POOL_10 where recall COLLAPSED -> flagged + NOT confirmed. The
    # gold-retaining POOL_20 does NOT improve over the wide baseline -> C_FALSIFIED (the expected outcome).
    t2 = {
        "POOL_100": {"gold_in_pool_frac": 0.91, "challenge": 0.36, "setmargin_pc": 0.40},
        "POOL_20":  {"gold_in_pool_frac": 0.84, "challenge": 0.365, "setmargin_pc": 0.405},
        "POOL_10":  {"gold_in_pool_frac": 0.35, "challenge": 0.47, "setmargin_pc": 0.55},
    }
    r2 = classify_c(t2)
    assert r2["recall_collapse_false_positive"], "honesty unit: case2 MUST flag recall_collapse_false_positive"
    assert r2["verdict"] != "C_CONFIRMED", f"honesty unit: case2 must NOT confirm C, got {r2['verdict']}"
    return {"case1": r1["verdict"], "case2": r2["verdict"],
            "case2_flag": r2["recall_collapse_false_positive"]}


def self_test():
    print("[self-test] planted POOL-TIGHTNESS discriminator (wide->lure WRONG; tighten drops lure keeps "
          "gold->CORRECT) ...", flush=True)
    planted = _planted_pool_tightness_discriminator()
    print(f"[self-test]   planted: {planted}", flush=True)

    print("[self-test] honesty-guard decision-logic unit test (recall-collapse false-positive) ...", flush=True)
    hg = _honesty_guard_unit_test()
    print(f"[self-test]   honesty guard: {hg}", flush=True)

    print("[self-test] REAL SemanticHDEncoder + REAL pool encode + REAL topk_from_scores + pool-restriction "
          "+ UNCHANGED combiner ...", flush=True)
    exercised = set()
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv); exercised.add("SemanticHDEncoder")

    store_sents = [
        "moving water spins a turbine to generate hydroelectric power",
        "a dam holds back water in a reservoir",
        "burning coal heats water to make steam that spins a turbine",
        "a nuclear reactor heats water to make steam that spins a turbine",
        "iron is a kind of metal",
        "the sun emits light and heat",
    ]
    SV = arc._encode_store(enc, store_sents); exercised.add("arc._encode_store")   # [6, nd] unit
    q = {"stem": "What produces electricity at a hydroelectric dam?",
         "choices": ["moving water", "burning coal", "the moon"], "correct_index": 0}
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])   # [3, nd] unit

    # REAL retrieval-score proxy over the store (question relevance) + REAL topk_from_scores wide pool
    frr = np.maximum(SV @ QQ, 0.0).astype(np.float64)
    wide = ppr.topk_from_scores(frr, K_WIDE); exercised.add("ppr.topk_from_scores")   # global idx desc
    frr_wide = frr[wide].astype(np.float32)
    fh_wide = SV[wide]
    q_rel_wide = np.maximum(fh_wide @ QQ, 0.0).astype(np.float32)

    # exercise every POOL arm membership + per-pool A_TOPK selection + UNCHANGED combiner
    picks_by_arm = {}
    for arm in POOL_ARMS:
        mem = pool_members(frr_wide, arm); exercised.add("pool_members")
        sel_local = select_topk_local(q_rel_wide, mem, K_SEL); exercised.add("select_topk_local")
        sel_global = wide[sel_local]
        sc = combiner_scores(SV[sel_global], np.maximum(SV[sel_global] @ QQ, 0.0),
                             choice_hd, np.random.default_rng(0)); exercised.add("combiner_scores")
        picks_by_arm[arm] = int(agg._pick(sc, np.random.default_rng(0)))
    print(f"[self-test]   real per-arm picks: {picks_by_arm} (pool sizes shrink 100->10)", flush=True)

    # determinism: same call -> same members + selection
    m10a = pool_members(frr_wide, "POOL_10"); m10b = pool_members(frr_wide, "POOL_10")
    assert np.array_equal(m10a, m10b), "real: pool_members non-deterministic"
    s10a = select_topk_local(q_rel_wide, m10a, K_SEL); s10b = select_topk_local(q_rel_wide, m10b, K_SEL)
    assert np.array_equal(s10a, s10b), "real: select_topk_local non-deterministic"

    # real_code_path declaration (all real entrypoints exercised in self_test, not a synthetic-only branch)
    full_entrypoints = {"SemanticHDEncoder", "arc._encode_store", "ppr.topk_from_scores",
                        "pool_members", "select_topk_local", "combiner_scores"}
    missing = full_entrypoints - exercised
    assert not missing, f"real_code_path: FULL entrypoints not exercised in self-test: {sorted(missing)}"

    print(f"[self-test] PASS (planted pool-tightness discriminator fires; honesty guard catches recall "
          f"collapse; real encoder+retrieval+pool-tightness+combiner exercised {sorted(exercised)}; "
          f"determinism)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 120, "limit_chal": 140}
    return {"n_dim": 2048, "limit_easy": 500, "limit_chal": 600}


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
    train_mask, test_mask = learned._split_train_test(questions)
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f} "
          f"train={int(train_mask.sum())} test={int(test_mask.sum())}", flush=True)

    # ---- store = FULL tablestore (flat sentences UNCHANGED) ----
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

    # ---- encode store + terms + questions ONCE (UNCHANGED flat encodings) ----
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

    # ---- PASS A: per-question wide pool + flat baseline features (LEARNED) + gold ----
    _heartbeat(output_dir, "features")
    poolidx_list = [None] * nQ            # wide-100 global idx (desc by F_RR)
    frr_wide_list = [None] * nQ           # F_RR scores aligned to the wide pool (desc)
    Xn_flat = [None] * nQ                 # flat baseline features (LEARNED learner)
    lscore_wide = [None] * nQ             # precomputed learned score per wide-pool fact (native features)
    qrel_wide_list = [None] * nQ          # geometric relevance per wide-pool fact
    gold_rows_list = [None] * nQ
    lure_flags = np.zeros(nQ, dtype=bool)

    for qi, q in enumerate(questions):
        ci = q["correct_index"]
        stem_words = stem_words_per_q[qi]
        lure_flags[qi] = gate.is_lure_question(stem_words, q["choices"], ci)
        lure_set, _ = gate.standout_lure_choices(stem_words, q["choices"])

        pool_idx = ppr.topk_from_scores(F_RR[qi], K_WIDE)     # UNCHANGED wide pool
        poolidx_list[qi] = pool_idx
        frr_wide_list[qi] = F_RR[qi][pool_idx].astype(np.float64)
        fh_pool = SV_store[pool_idx]
        chd = choice_hd_map[qi]
        fw = [fact_word_sets[i] for i in pool_idx.tolist()]
        qrel_wide_list[qi] = np.maximum(fh_pool @ QQ[qi], 0.0).astype(np.float64)

        # FLAT baseline features (imported 29545 assembly, UNCHANGED) -> LEARNED learner
        gs = gate.gate_scores(fh_pool, fw, stem_words, STEM[qi], chd, lure_set)
        coh = fixedsel.coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ[qi], 0.0))
        rr_scores = F_RR[qi][pool_idx]
        degs = degrees_all[pool_idx]
        negs = neg_all[pool_idx]
        Xflat = question_features_flat(fh_pool, STEM[qi], chd, gs, coh, rr_scores, degs, negs)
        Xn_flat[qi] = _minmax_cols(Xflat)

        gold_rows_list[qi] = np.array([uid2fi[u] for u in q["gold_central"] if u in uid2fi], dtype=np.int64)

    # ---- TRAIN the LEARNED glass-box learner on TRAIN questions ONLY (label = is-gold) ----
    _heartbeat(output_dir, "train_learner")
    Xr, yr = [], []
    for qi in range(nQ):
        if not train_mask[qi]:
            continue
        gold_set = set(int(g) for g in gold_rows_list[qi].tolist())
        y = np.array([1.0 if int(gi) in gold_set else 0.0 for gi in poolidx_list[qi].tolist()], dtype=np.float64)
        Xr.append(Xn_flat[qi]); yr.append(y)
    Xt = np.concatenate(Xr, axis=0) if Xr else np.zeros((0, len(FLAT_FEATURE_NAMES)))
    yt = np.concatenate(yr, axis=0) if yr else np.zeros(0)
    n_train_rows = int(Xt.shape[0]); n_train_pos = int(yt.sum())
    w_flat, b_flat = train_glassbox_relevance(Xt, yt)
    flat_weights = {FLAT_FEATURE_NAMES[j]: round(float(w_flat[j]), 5) for j in range(len(w_flat))}
    print(f"[learned:LEARNED] rows={n_train_rows} pos={n_train_pos} weights={flat_weights}", flush=True)

    # precompute the FIXED per-fact selection scores over the wide pool (ONLY membership varies per pool arm)
    for qi in range(nQ):
        lscore_wide[qi] = learned_score(Xn_flat[qi], w_flat, b_flat).astype(np.float64)

    # ---- PASS B: per POOL arm x per selection method -> select + combiner argmax + track dual-track ----
    _heartbeat(output_dir, "pool_tightness_sweep")
    # picks[arm][method] -> [nQ]; ORACLE handled separately (pool-independent)
    picks = {arm: {m: np.full(nQ, -1, dtype=np.int64) for m in SEL_METHODS} for arm in POOL_ARMS}
    oracle_pick = np.full(nQ, -1, dtype=np.int64)
    # per-Q pool bookkeeping (method-independent membership)
    gold_in_arm = {arm: np.zeros(nQ, dtype=bool) for arm in POOL_ARMS}       # >=1 gold fact in arm pool
    gold_ret_arm = {arm: np.full(nQ, np.nan) for arm in POOL_ARMS}           # |gold in arm|/|gold in wide|
    poolsize_arm = {arm: np.zeros(nQ, dtype=np.int64) for arm in POOL_ARMS}
    # margin_correct[arm][method] -> [nQ] : combiner score of correct choice minus best lure (selected set)
    margin_correct = {arm: {m: np.full(nQ, np.nan) for m in SEL_METHODS} for arm in POOL_ARMS}

    for qi, q in enumerate(questions):
        pool_idx = poolidx_list[qi]
        frr_wide = frr_wide_list[qi].astype(np.float32)
        chd = choice_hd_map[qi]
        ci = q["correct_index"]
        C = chd.shape[0]
        gold_rows = gold_rows_list[qi]
        gold_set = set(int(g) for g in gold_rows.tolist())
        n_gold_in_wide = sum(1 for i in pool_idx.tolist() if i in gold_set)

        lscore = lscore_wide[qi]
        qrel = qrel_wide_list[qi]

        # ORACLE (gold facts -> combiner) : pool-independent ceiling
        if gold_rows.size:
            sc = combiner_scores(SV_store[gold_rows], np.maximum(SV_store[gold_rows] @ QQ[qi], 0.0),
                                 chd, np.random.default_rng(SEED + qi))
            oracle_pick[qi] = agg._pick(sc, np.random.default_rng(SEED + qi))
        else:
            oracle_pick[qi] = agg._pick(np.zeros(C, np.float32), np.random.default_rng(SEED + qi))

        for arm in POOL_ARMS:
            mem = pool_members(frr_wide, arm)                # local idx into wide pool
            poolsize_arm[arm][qi] = int(mem.size)
            mem_global = pool_idx[mem]
            n_gold_arm = sum(1 for i in mem_global.tolist() if i in gold_set)
            gold_in_arm[arm][qi] = n_gold_arm > 0
            if n_gold_in_wide > 0:
                gold_ret_arm[arm][qi] = n_gold_arm / n_gold_in_wide

            for m in SEL_METHODS:
                if m == "LEARNED":
                    sel_local = select_topk_local(lscore, mem, K_SEL)
                elif m == "GEO":
                    sel_local = select_topk_local(qrel, mem, K_SEL)
                else:  # RND
                    rng_r = np.random.default_rng(SEED + 7000 + qi + hash_arm(arm))
                    if mem.size:
                        perm = rng_r.permutation(mem.size)[:min(K_SEL, mem.size)]
                        sel_local = mem[perm]
                    else:
                        sel_local = np.zeros(0, dtype=np.int64)
                sel_global = pool_idx[sel_local]
                sc = combiner_scores(SV_store[sel_global],
                                     np.maximum(SV_store[sel_global] @ QQ[qi], 0.0),
                                     chd, np.random.default_rng(SEED + qi))
                picks[arm][m][qi] = agg._pick(sc, np.random.default_rng(SEED + qi))
                if C >= 2 and np.any(np.isfinite(sc)):
                    rivals = np.delete(sc, ci)
                    margin_correct[arm][m][qi] = float(sc[ci] - rivals.max())

        if (qi + 1) % 100 == 0:
            print(f"[progress] answered {qi+1}/{nQ}", flush=True)

    # ---- accuracies + dual-track per pool arm (TEST Challenge is PRIMARY) ----
    _heartbeat(output_dir, "aggregate")
    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    is_chal = ~is_easy
    test_chal = test_mask & is_chal
    test_easy = test_mask & is_easy
    tc_idx = [qi for qi in range(nQ) if test_chal[qi]]
    n_tc = len(tc_idx)

    def acc(mask, arr):
        m = arr[mask]
        return round(float(np.mean(m)), 4) if m.size else None

    corr = {arm: {m: np.array([int(picks[arm][m][qi] == questions[qi]["correct_index"])
                               for qi in range(nQ)], dtype=np.int64)
                  for m in SEL_METHODS} for arm in POOL_ARMS}
    oracle_corr = np.array([int(oracle_pick[qi] == questions[qi]["correct_index"]) for qi in range(nQ)],
                           dtype=np.int64)
    oracle_test_chal = acc(test_chal, oracle_corr)

    # per-arm dual-track table (PRIMARY method = LEARNED)
    per_arm = {}
    per_arm_full = {}
    for arm in POOL_ARMS:
        gip = [gold_in_arm[arm][qi] for qi in tc_idx]
        gold_in_pool_frac = round(float(np.mean(gip)), 4) if gip else None
        ret_vals = [gold_ret_arm[arm][qi] for qi in tc_idx if np.isfinite(gold_ret_arm[arm][qi])]
        gold_retention = round(float(np.mean(ret_vals)), 4) if ret_vals else None
        mean_psize = round(float(np.mean([poolsize_arm[arm][qi] for qi in tc_idx])), 2) if n_tc else None

        arm_methods = {}
        for m in SEL_METHODS:
            chal = acc(test_chal, corr[arm][m])
            easy = acc(test_easy, corr[arm][m])
            # informativeness: of GOLD-REACHABLE TEST-Chal Qs, does A_TOPK+combiner pick correct?
            reach = [qi for qi in tc_idx if gold_in_arm[arm][qi]]
            setmargin_pc = (round(float(np.mean([corr[arm][m][qi] for qi in reach])), 4)
                            if reach else None)
            mc = [margin_correct[arm][m][qi] for qi in tc_idx
                  if np.isfinite(margin_correct[arm][m][qi])]
            mc_reach_corr = [margin_correct[arm][m][qi] for qi in reach
                             if picks[arm][m][qi] == questions[qi]["correct_index"]
                             and np.isfinite(margin_correct[arm][m][qi])]
            mc_reach_wrong = [margin_correct[arm][m][qi] for qi in reach
                              if picks[arm][m][qi] != questions[qi]["correct_index"]
                              and np.isfinite(margin_correct[arm][m][qi])]
            arm_methods[m] = {
                "test_challenge": chal, "test_easy": easy,
                "setmargin_points_correct": setmargin_pc,
                "mean_margin_correct": round(float(np.mean(mc)), 5) if mc else None,
                "mean_margin_correct_when_right": round(float(np.mean(mc_reach_corr)), 5) if mc_reach_corr else None,
                "mean_margin_correct_when_wrong": round(float(np.mean(mc_reach_wrong)), 5) if mc_reach_wrong else None,
            }
        per_arm_full[arm] = {
            "gold_in_pool_frac": gold_in_pool_frac, "gold_retention_vs_wide": gold_retention,
            "mean_pool_size": mean_psize, "n_gold_reachable_tc": int(sum(gold_in_arm[arm][qi] for qi in tc_idx)),
            "by_method": arm_methods,
        }
        # compact table for the decision logic (PRIMARY method)
        per_arm[arm] = {
            "gold_in_pool_frac": gold_in_pool_frac,
            "challenge": arm_methods[PRIMARY_METHOD]["test_challenge"] or 0.0,
            "setmargin_pc": arm_methods[PRIMARY_METHOD]["setmargin_points_correct"],
        }
        print(f"[arm] {arm}: psize={mean_psize} gold_in_pool={gold_in_pool_frac} "
              f"retention={gold_retention} | LEARNED chal={per_arm[arm]['challenge']} "
              f"setmargin_pc={per_arm[arm]['setmargin_pc']}", flush=True)

    baseline_chal = per_arm["POOL_100"]["challenge"]

    # ---- must-fail: RND per pool must not lift over POOL_100 baseline ----
    rnd_lifts = {arm: round((per_arm_full[arm]["by_method"]["RND"]["test_challenge"] or 0.0) - baseline_chal, 4)
                 for arm in POOL_ARMS}
    max_rnd_lift = max(rnd_lifts.values())
    random_ok = max_rnd_lift <= RANDOM_MAX

    # ---- discriminator-fires: pool arms must actually CHANGE selection (else tightening is a no-op) ----
    digests = {arm: hashlib.sha256(picks[arm][PRIMARY_METHOD].tobytes()).hexdigest() for arm in POOL_ARMS}
    n_distinct = len(set(digests.values()))
    arms_differ = n_distinct >= 3   # POOL_100..POOL_10 should not all collapse to one pick vector
    # recall must vary across the sweep (tightening removes SOMETHING), else the ablation is vacuous
    recall_spread = round((per_arm["POOL_100"]["gold_in_pool_frac"] or 0.0)
                          - (per_arm["POOL_10"]["gold_in_pool_frac"] or 0.0), 4)
    poolsize_shrinks = bool((per_arm_full["POOL_100"]["mean_pool_size"] or 0)
                            > (per_arm_full["POOL_10"]["mean_pool_size"] or 0))
    discriminator_fired = bool(arms_differ and poolsize_shrinks)

    # ---- THE decisive C verdict (honesty guard tracks recall + informativeness together) ----
    _heartbeat(output_dir, "classify_c")
    cver = classify_c(per_arm)

    # ---- GLASS-BOX: correct-vs-lure combiner support at the TIGHTEST gold-retaining pool ----
    _heartbeat(output_dir, "glassbox")
    tight_order = ["POOL_10", "POOL_20", "POOL_50", "POOL_PREC", "POOL_100"]
    tightest_retaining = "POOL_100"
    _retain_thr = cver["retain_threshold_gold_in_pool"]
    for arm in tight_order:
        if per_arm[arm]["gold_in_pool_frac"] is not None and per_arm[arm]["gold_in_pool_frac"] >= _retain_thr:
            tightest_retaining = arm
            break
    glass = []
    for qi in tc_idx:
        if len(glass) >= 12:
            break
        if not (lure_flags[qi] and test_mask[qi]):
            continue
        arm = tightest_retaining
        pool_idx = poolidx_list[qi]
        frr_wide = frr_wide_list[qi].astype(np.float32)
        chd = choice_hd_map[qi]
        ci = questions[qi]["correct_index"]
        gold_set = set(int(g) for g in gold_rows_list[qi].tolist())
        mem = pool_members(frr_wide, arm)
        sel_local = select_topk_local(lscore_wide[qi], mem, K_SEL)
        sel_global = pool_idx[sel_local]
        sc = combiner_scores(SV_store[sel_global], np.maximum(SV_store[sel_global] @ QQ[qi], 0.0),
                             chd, np.random.default_rng(SEED + qi))
        rivals = np.delete(sc, ci)
        glass.append({
            "qid": questions[qi]["qid"], "stem": questions[qi]["stem"][:120],
            "choices": questions[qi]["choices"], "correct_index": ci,
            "pool_arm": arm, "pool_size": int(mem.size),
            "gold_in_arm_pool": int(any(int(i) in gold_set for i in pool_idx[mem].tolist())),
            "selected_facts": [uid2sent.get(uids[int(g)], "")[:70] for g in sel_global.tolist()],
            "selected_is_gold": [int(int(g) in gold_set) for g in sel_global.tolist()],
            "combiner_scores": [round(float(x), 4) for x in sc],
            "correct_support": round(float(sc[ci]), 4),
            "best_lure_support": round(float(rivals.max()), 4) if rivals.size else None,
            "correct_stands_out": int(sc[ci] > rivals.max()) if rivals.size else None,
            "pick": int(agg._pick(sc, np.random.default_rng(SEED + qi))),
        })

    # ---- integrity / anchor ----
    anchor_chal_ok = abs(baseline_chal - ANCHOR_CHAL) <= ANCHOR_TOL_CHAL
    ag_saturated = baseline_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < baseline_chal < 0.95

    grade = arc._grade_proxy(per_arm_full[tightest_retaining]["by_method"][PRIMARY_METHOD]["test_easy"],
                             per_arm_full[tightest_retaining]["by_method"][PRIMARY_METHOD]["test_challenge"])

    # ---- verdict assembly ----
    if ag_saturated:
        verdict = "POOL_TIGHTNESS_SATURATED"
        vmsg = f"LEARNED@POOL_100 TEST Challenge {baseline_chal} >= {AG_BASELINE_SAT}: no headroom (report)."
    elif not discriminator_fired:
        verdict = "POOL_TIGHTNESS_VACUOUS"
        vmsg = (f"tightening did not change selection (n_distinct_pick_vectors={n_distinct}, "
                f"poolsize_shrinks={poolsize_shrinks}); the ablation is a no-op -- do NOT interpret.")
    elif cver["verdict"] == "C_CONFIRMED":
        verdict = "POOL_TIGHTNESS_C_CONFIRMED"
        vmsg = (f"C CONFIRMED (cheap fix exists): a GOLD-RETAINING pool arm {cver['confirm_arms']} makes "
                f"selection informative -- LEARNED lifts TEST Challenge over POOL_100 {baseline_chal} "
                f"(chal_lifts={ {a: cver['challenge_lifts'][a] for a in cver['confirm_arms']} }, "
                f"inform_lifts={ {a: cver['informativeness_lifts'][a] for a in cver['confirm_arms']} }) "
                f"while gold_in_pool stays >= {cver['retain_threshold_gold_in_pool']}. "
                f"Tightening the candidate pool makes the correct answer's support STAND OUT -> the wall is "
                f"(partly) retrieval-granularity, not purely thin-meaning. recall_collapse_false_positive="
                f"{cver['recall_collapse_false_positive']}. RND must-fail ok={random_ok}.")
    elif cver["verdict"] == "C_MIDDLE":
        verdict = "POOL_TIGHTNESS_C_MIDDLE"
        vmsg = (f"MIDDLE: partial. A gold-retaining arm {cver['middle_arms']} nudges Challenge/informativeness "
                f"above the MIDDLE floor but below C-confirm (chal_lift < {C_LIFT_HP} and inform_lift < "
                f"{INFORM_LIFT_HP}). Tightening helps a little but is not a decisive fix. "
                f"chal_lifts={cver['challenge_lifts']} inform_lifts={cver['informativeness_lifts']}; "
                f"recall_collapse_false_positive={cver['recall_collapse_false_positive']}; RND ok={random_ok}.")
    else:
        verdict = "POOL_TIGHTNESS_C_FALSIFIED"
        vmsg = (f"C FALSIFIED (=> B confirmed; deep reframe justified): at EVERY gold-retaining pool arm the "
                f"correct answer's support does NOT stand out -- LEARNED TEST Challenge stays ~baseline "
                f"{baseline_chal} (chal_lifts={cver['challenge_lifts']}) AND setmargin_points_correct does "
                f"not lift (inform_lifts={cver['informativeness_lifts']}). Any Challenge lift coincides with "
                f"recall COLLAPSE (best_lift_arm={cver['best_lift_arm']} lift={cver['best_challenge_lift']}, "
                f"recall_collapse_false_positive={cver['recall_collapse_false_positive']}) -- NOT a real fix. "
                f"'Every choice self-supports' PERSISTS wherever the gold is still retained: the wall is "
                f"similarity!=entailment / thin meaning, not pool width. RND must-fail ok={random_ok}.")

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: baseline(POOL_100 LEARNED) chal={baseline_chal} oracle={oracle_test_chal} "
                    f"chance={round(chance,4)} | per-arm[LEARNED] "
                    + "; ".join(f"{a}:chal={per_arm[a]['challenge']},gold_in_pool="
                                f"{per_arm[a]['gold_in_pool_frac']},setmargin_pc={per_arm[a]['setmargin_pc']}"
                                for a in POOL_ARMS)
                    + f" | C_verdict={cver['verdict']} confirm_arms={cver['confirm_arms']} "
                    f"recall_collapse_fp={cver['recall_collapse_false_positive']} RND_ok={random_ok}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_train": int(train_mask.sum()), "n_test": int(test_mask.sum()),
        "n_test_challenge": int(n_tc), "chance_theoretical": round(chance, 4),
        "store_facts": nFacts, "graph_terms": nTerms,
        "n_train_rows": n_train_rows, "n_train_gold_pos": n_train_pos,
        # selection + combiner config (UNCHANGED)
        "k_wide": K_WIDE, "k_sel": K_SEL, "rr_top_t": RR_TOP_T, "mu_supp": MU_SUPP,
        "hops": HOPS, "damp": DAMP, "seed_cos": SEED_COS,
        "split_frac_train": learned.SPLIT_FRAC_TRAIN,
        # the ONE knob
        "pool_arms": list(POOL_ARMS), "k_by_arm": K_BY_ARM, "frac_of_max_precision": FRAC_OF_MAX,
        "sel_methods": list(SEL_METHODS), "primary_method": PRIMARY_METHOD,
        # GLASS-BOX: LEARNED weights (inspectable)
        "flat_feature_names": list(FLAT_FEATURE_NAMES), "learned_weights": flat_weights,
        # THE decisive dual-track table
        "per_arm_dual_track": per_arm_full,
        "baseline_pool100_learned_challenge": baseline_chal,
        "oracle_gold_test_challenge": oracle_test_chal,
        "selection_gap_to_oracle": round((oracle_test_chal or 0.0) - baseline_chal, 4),
        # the C decision + honesty guard
        "c_classification": cver,
        "recall_retain_frac": RECALL_RETAIN_FRAC,
        "recall_retain_threshold_gold_in_pool": cver["retain_threshold_gold_in_pool"],
        "tightest_gold_retaining_pool": tightest_retaining,
        # must-fail + integrity
        "rnd_lift_by_arm": rnd_lifts, "max_rnd_lift": max_rnd_lift, "random_control_ok": bool(random_ok),
        "arms_differ_verified": bool(arms_differ), "n_distinct_pick_vectors": int(n_distinct),
        "arm_pick_digests": digests, "recall_spread_100_to_10": recall_spread,
        "poolsize_shrinks": poolsize_shrinks, "discriminator_fired": discriminator_fired,
        "anchor_challenge_regression_ok": bool(anchor_chal_ok), "anchor_challenge_expected": ANCHOR_CHAL,
        "baseline_in_band": bool(baseline_in_band), "ag_saturated": bool(ag_saturated),
        "bands": {"RECALL_RETAIN_FRAC": RECALL_RETAIN_FRAC, "C_LIFT_HP": C_LIFT_HP, "MB_LIFT": MB_LIFT,
                  "INFORM_LIFT_HP": INFORM_LIFT_HP, "INFORM_LIFT_MB": INFORM_LIFT_MB, "RANDOM_MAX": RANDOM_MAX,
                  "anchor_chal": ANCHOR_CHAL, "ag_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: POOL TIGHTNESS is the ONLY variable. The WIDE re-retrieval pool (RR top-100, "
            "mr.reformulate_seeds/_rownorm_scores + ppr IMPORTED UNCHANGED, recall@100=0.69), the bind+bundle "
            "combiner (agg.aggregate 'bundle' IMPORTED UNCHANGED), the per-fact top-K A_TOPK selection "
            "(LEARNED = 29545's EXACT flat-cosine feature assembly + glass-box learner -> regression-anchor "
            "~0.3663 at POOL_100; GEO = geometric relevance top-K), and the TRAIN/TEST split "
            "(learned._split_train_test) are ALL held fixed. The ONLY change: pool_members() restricts WHICH "
            "retrieved facts are eligible candidates for selection (top-K by F_RR for K in {100,50,20,10}, "
            "plus a precision-filtered pool F_RR >= 0.5*max). The per-fact selection SCORE is precomputed ONCE "
            "on the native wide pool (lscore_wide/qrel_wide); only membership varies -> a clean one-variable "
            "sweep. DUAL-TRACK per arm: gold-recall-in-pool (Q-level gold_in_pool_frac + fact-level retention) "
            "AND informativeness (setmargin_points_correct on gold-reachable Qs + margin_correct + end-to-end "
            "TEST Challenge). HONESTY GUARD: classify_c tracks recall + informativeness together; a Challenge "
            "lift that coincides with recall collapse is flagged recall_collapse_false_positive and does NOT "
            "confirm C. RND per-pool must-fail + ORACLE ceiling anchor floor/ceiling. NO LEAK: TRAIN/TEST "
            "disjoint; gold used for LEARNED TRAIN label + ORACLE + eval only, NEVER in selection at test. "
            "STUBBED/NOTED-NOT-BUILT: richer/grounded meaning in the fact slots (the B-lever deep reframe, "
            "justified only if C FALSIFIED); learned relevance retrained per-pool (deliberately NOT done -- "
            "that would change the scoring function and break the one-variable design)."),
        "contract": ("INLINE-LOCAL foreground-to-completion; no push/remote-persist; NOT remote-portable "
                     "(GloVe+WorldTree git-ignored/large; inherits 29544/29545/29546/set_level contract); "
                     "VET-PENDING; FULL eval slice bounded (limit_easy=500 limit_chal=600, stratified "
                     "train/test) to fit one foreground call"),
        "compute_architecture": ("mixed CPU: batched GloVe encode (store + questions + choices) + scipy "
                                 "sparse batched PPR (2 passes, UNCHANGED) done ONCE; the pool-tightness sweep "
                                 "is cheap index-restriction + UNCHANGED combiner calls (5 pool arms x 3 sel "
                                 "methods x 1 aggregate/Q); wall target < 8min. No GPU speedup needed."),
        "storage_strategy": "sharded (each fact = own embedding + own graph node)",
        "progress_logging": "line_buffered_stdout",
        "crlb_n_a": ("geometric/learned selection over a deterministic per-pool candidate set; no learned "
                     "noise floor; MORE dims = LESS bundle/dot noise (~1/sqrt(N)) so signals SURVIVE scale by "
                     "construction; smoke runs at FULL n_dim=2048 (only question-limit reduced)"),
        "calibration_check": ("default_ok_for_this_regime (all selection scoring inherited UNCHANGED from "
                              "29545; pool-tightness knobs {K grid, FRAC_OF_MAX=0.5} + bands set a priori, NOT "
                              "tuned to force a verdict; RND per-pool must-fail + ORACLE ceiling + honesty "
                              "guard against recall-collapse false positives)"),
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


def hash_arm(arm):
    """Deterministic small int per pool arm (RND seed offset). NOT built-in hash() (PYTHONHASHSEED-salted)."""
    return int.from_bytes(hashlib.sha256(arm.encode("ascii")).digest()[:4], "big") % 100000


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    _T0[0] = time.perf_counter()
    output_dir = _out_dir()

    if args.self_test:
        ok = self_test()
        print(f"[self-test] {'PASS' if ok else 'FAIL'}", flush=True)
        sys.exit(0 if ok else 1)

    _write_start_marker(output_dir, args.mode)
    run(args.mode, output_dir)
    sys.exit(0)


if __name__ == "__main__":
    _output_dir_for_crash = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
