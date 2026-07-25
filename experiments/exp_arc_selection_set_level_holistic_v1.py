"""arc_selection_set_level_holistic_v1 -- SET-LEVEL / HOLISTIC selection vs PER-FACT top-K selection.

The selection wall (VET atom 29548 + the answer-conditioned drill + fair re-tests): retrieval REACHES
the facts (wide RR pool recall@100=0.69), the bundle COMBINER USES them (oracle gold->bundle Challenge
~0.687), but SELECTION cannot ISOLATE the gold from the contains-gold pool. EVERY per-fact signal has
failed (relevance / coherence / structure / content / answer-conditioned single-fact; precision ~0.15 vs
oracle 0.97). VET KEY RESULT: the answer signal is a SET-LEVEL / BUNDLE property of the thin-meaning gold
facts -- the answer-AGNOSTIC bundle combiner over the gold SET reads the correct answer at ORACLE ~0.687
>> chance -- but NO single fact carries it (single-fact conditioned differential ~= noise ~1/sqrt(2048)).
So do the discrimination at the BUNDLE (set) level where the readout is strong, NOT per-fact where it is
noise. A working SET-LEVEL answer-readout ALREADY EXISTS: the bundle combiner (agg.aggregate 'bundle').

BRAIN GROUNDING (deep-brain-analysis -> accurate-duplication): COALITION FORMATION / global workspace (a
winning COALITION of units wins together; the diagnostic value is a property of the coalition, not any
member); Kintsch CONSTRUCTION-INTEGRATION (the network is CONSTRUCTED then INTEGRATED, settling on the
mutually-supporting SUBSET); READOUT-GUIDED CONSTRUCTIVE LOOP grown COMPETITIVELY across candidate answers
(each choice grows its best-supported set; the strongest-supported wins) -- the competition is the guard
against the CONFIRMATION TRAP (do not grow a set that confidently supports a WRONG choice).

ONE VARIABLE = selection GRANULARITY (per-fact top-K vs set-level construction). The WIDE RR pool
(recall@100=0.69; mr.reformulate_seeds/_rownorm_scores IMPORTED UNCHANGED), the bind+bundle COMBINER
(agg.aggregate 'bundle' IMPORTED UNCHANGED, used as the set-readout with the SAME answer-agnostic q_rel
weight for every arm), retrieval, and the TRAIN/TEST split are held FIXED. The ONLY difference across the
spine arms is WHICH facts the selection stage picks.

SET-LEVEL MECHANISM (the ONE new thing = greedy set construction over the UNCHANGED combiner readout):
  combiner_score_i(S) = normalize(sum_{f in S} relu(q_rel_f) * fact_f) . choice_hd_i   [agg 'bundle', UNCHANGED]
  margin_i(S)         = combiner_score_i(S) - max_{j!=i} combiner_score_j(S)             [set-level discrimination]
  PER-CHOICE competitive construction: for each choice i, greedily grow S_i (up to K_SEL facts from the
  pool) by adding the fact that most RAISES margin_i(S_i), stopping when no fact improves it. Answer =
  argmax_i margin_i(S_i) (competitive across choices; the confirmation-trap guard: every choice builds its
  best set, the strongest-supported wins). This does the answer-conditioning / contrast at the BUNDLE
  (set) level where the readout is strong, NOT at the single-fact level where it is noise.
  The greedy candidate search is a VECTORIZED incremental of the SAME combiner (b_raw += relu(q_rel_f)*f;
  the combiner's L2-norm absorbs the w/w.sum rescale, so the fast path is bit-equal to agg.aggregate --
  ASSERTED in self_test); the FINAL per-choice margin is recomputed by CALLING agg.aggregate (combiner-
  faithful).

ARMS (spine = A_TOPK_LEARNED -> A_TOPK_GEO -> SET_AGNOSTIC -> B_SETLEVEL; all feed the SAME bundle combiner):
  A_TOPK_LEARNED -- 29545 learned answer-agnostic relevance top-K_SEL -> combiner argmax [PRIMARY BASELINE +
                    HARNESS REGRESSION ANCHOR ~0.1865 insample-prec / ~0.3663 TEST Challenge]
  A_TOPK_GEO     -- geometric question-relevance top-K_SEL -> combiner argmax (matched no-train per-fact)
  SET_AGNOSTIC   -- ONE greedy set maximizing the PEAK cross-choice margin (which-choice AGNOSTIC) ->
                    combiner argmax [isolates set-CONSTRUCTION from per-choice conditioning]
  B_SETLEVEL     -- PER-CHOICE competitive greedy set construction; answer = argmax_i margin_i [TEST ARM]
  RND_SUBSET     -- random K_SEL subset -> combiner argmax [MUST-FAIL -> collapse toward chance]
  ORACLE         -- gold facts -> combiner argmax [CEILING ~0.687 / precision ~0.97]

PRIMARY = end-to-end TEST Challenge (B_SETLEVEL vs A_TOPK_LEARNED ~0.3663, toward oracle ~0.687) + McNemar;
SECONDARY = TEST sel_gold_precision (toward 0.97) + chal_lure surface-trap subset. HARD_PASS = B_SETLEVEL
materially beats A_TOPK_LEARNED (>=+0.05 Challenge) AND raises sel_gold_precision AND McNemar-sig AND
RND_SUBSET collapses; (bonus) B beats SET_AGNOSTIC => per-choice conditioning at bundle-level adds value.
HARD_FAIL = set-level ~= per-fact top-K (lift < +0.02) -> report STRAIGHT + residual sub-diagnosis (is it
the construction objective, the greedy locality, or a deeper thin-meaning wall? glass-box the per-choice
set growth to see whether the correct choice's set out-discriminates the lures' sets). CONFIRMATION-TRAP
CHECK: pick distribution + winning-margin-vs-correctness informativeness; a degenerate single-choice winner
is a must-catch (SET_LEVEL_DEGENERATE_WINNER). NO tuning to force a win; a clean HARD_FAIL is reportable.

Contract: INLINE-LOCAL foreground-to-completion (GloVe+WorldTree git-ignored/large -> NOT remote-portable;
inherits the 29544/29545/29546 contract); NO push/remote-persist; ASCII-only; deterministic (fixed seeds,
numpy default_rng, sorted iteration, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL pool encode + REAL greedy set
#   construction + UNCHANGED combiner; PLANTED discriminator asserts a set whose BUNDLE discriminates
#   (per-fact top-K by q_rel picks a strong lure and the combiner leans WRONG; set-level greedy toward the
#   correct choice builds the gold bundle achieving the top margin -> right); combiner-equivalence
#   (fast incremental == agg.aggregate 'bundle'); arms-differ; determinism
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-guard on A_TOPK_LEARNED TEST challenge (headroom to the ~0.687 ceiling)
# - storage = SHARDED (each fact = own embedding + own graph node)
# - GLASS-BOX: per-choice constructed set + margin growth on surface-trap TEST Qs (dam-Q autopsy)
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
# bind+bundle combiner, PPR graph, fixed signals, arc helpers, encoder.
from experiments import exp_arc_selection_learned_relevance_glassbox_v1 as learned  # noqa: E402
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr    # noqa: E402
from experiments import exp_arc_retrieval_max_recall_ksweep_reretrieval_v1 as mr   # noqa: E402
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as gate    # noqa: E402
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg         # noqa: E402
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc             # noqa: E402
from experiments import exp_arc_selection_precision_coherence_subset_v1 as fixedsel  # noqa: E402
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (                 # noqa: E402
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_selection_set_level_holistic_v1"
SEED = 20260801

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

# reuse the 29545 learner + baseline features EXACTLY (regression-anchors A_TOPK_LEARNED to 0.1865/0.3663)
FLAT_FEATURE_NAMES = learned.FEATURE_NAMES
train_glassbox_relevance = learned.train_glassbox_relevance
learned_score = learned.learned_score
_minmax_cols = learned._minmax_cols
_neg_count = learned._neg_count
question_features_flat = learned.question_features
_topk_idx = learned._topk_idx

# ---- bands (author-designed a priori) ----
SET_LIFT_HP = 0.05        # PRIMARY HARD-PASS: B_SETLEVEL - A_TOPK_LEARNED on TEST Challenge >= this
MB_SET_LIFT = 0.02        # MIDDLE band floor (positive but sub-HP)
RANDOM_MAX = 0.02         # RND_SUBSET - A_TOPK_LEARNED on Challenge must be <= this (must-fail)
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95    # A_TOPK_LEARNED challenge >= this -> vacuous (no headroom)
DEGENERATE_WINNER_FRAC = 0.90  # B_SETLEVEL winning-choice single-index frequency >= this -> degenerate
ANCHOR_PREC = 0.1865      # 29545 answer-agnostic in-sample precision (regression anchor)
ANCHOR_CHAL = 0.3663      # 29545 answer-agnostic TEST Challenge (regression anchor)
ANCHOR_TOL_PREC = 0.03    # WARN if |A_learn insample precision - ANCHOR_PREC| > this
ANCHOR_TOL_CHAL = 0.05    # WARN if |A_learn TEST challenge   - ANCHOR_CHAL| > this (bundle-combiner variant)

_T0 = [0.0]

# combiner-argmax arms (single fixed set -> combiner argmax); B_SETLEVEL + ORACLE handled separately
COMBINER_ARMS = ("A_TOPK_LEARNED", "A_TOPK_GEO", "SET_AGNOSTIC", "RND_SUBSET")
ARMS = COMBINER_ARMS + ("B_SETLEVEL", "ORACLE")


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
# set-level greedy construction over the UNCHANGED bundle combiner (the ONE new mechanism)
# ---------------------------------------------------------------------------
def _margin_toward(sc, i):
    """sc: [..., C] combiner scores. margin toward choice i = sc[...,i] - max_{j!=i} sc[...,j]. -> [...]."""
    C = sc.shape[-1]
    if C == 1:
        return np.asarray(sc[..., 0])
    rivals = np.delete(sc, i, axis=-1)
    return sc[..., i] - rivals.max(axis=-1)


def _cand_bundle_scores(b_raw, add_vecs, add_w, choice_hd):
    """For each candidate row f: normalize(b_raw + relu(add_w_f)*add_vecs_f) . choice_hd. This is the
    VECTORIZED incremental of agg.aggregate 'bundle' (the L2-norm absorbs the combiner's w/w.sum rescale,
    so it is bit-equal to calling the combiner on the resulting set -- ASSERTED in self_test).
      b_raw: [N] ; add_vecs: [A, N] ; add_w: [A] ; choice_hd: [C, N]. Returns [A, C]."""
    w = np.maximum(add_w.astype(np.float64), 0.0)
    B = b_raw[None, :] + w[:, None] * add_vecs.astype(np.float64)   # [A, N]
    nb = np.linalg.norm(B, axis=1)
    nb[nb <= 0.0] = 1.0
    return (B / nb[:, None]) @ choice_hd.T.astype(np.float64)       # [A, C]


def greedy_set_toward(fh_pool, q_rel, choice_hd, i, k_sel):
    """PER-CHOICE competitive construction: greedily grow S_i (up to k_sel pool facts) adding the fact
    that most RAISES margin_i(bundle(S_i)); stop when no fact improves margin_i. Returns (local_idx list,
    achieved_margin). Empty pool -> ([], -inf)."""
    P, N = fh_pool.shape
    if P == 0:
        return [], float("-inf")
    sel = []
    b_raw = np.zeros(N, dtype=np.float64)
    cur = float("-inf")
    avail = list(range(P))
    for _ in range(min(k_sel, P)):
        av = np.asarray(avail, dtype=np.int64)
        sc = _cand_bundle_scores(b_raw, fh_pool[av], q_rel[av], choice_hd)   # [A, C]
        marg = _margin_toward(sc, i)                                         # [A]
        bi = int(np.argmax(marg))
        if not np.isfinite(marg[bi]) or marg[bi] <= cur + 1e-9:              # no improvement -> stop
            break
        f = int(av[bi])
        sel.append(f)
        b_raw = b_raw + max(float(q_rel[f]), 0.0) * fh_pool[f].astype(np.float64)
        cur = float(marg[bi])
        avail.remove(f)
    return sel, cur


def greedy_set_agnostic(fh_pool, q_rel, choice_hd, k_sel):
    """ONE set maximizing the PEAK cross-choice margin (which-choice AGNOSTIC): greedily add the fact that
    most raises max_i margin_i(bundle(S)). Isolates set-CONSTRUCTION from per-choice conditioning.
    Returns (local_idx list, achieved_peak_margin)."""
    P, N = fh_pool.shape
    C = choice_hd.shape[0]
    if P == 0 or C == 0:
        return [], float("-inf")
    sel = []
    b_raw = np.zeros(N, dtype=np.float64)
    cur = float("-inf")
    avail = list(range(P))
    for _ in range(min(k_sel, P)):
        av = np.asarray(avail, dtype=np.int64)
        sc = _cand_bundle_scores(b_raw, fh_pool[av], q_rel[av], choice_hd)   # [A, C]
        peak = np.stack([_margin_toward(sc, ii) for ii in range(C)], axis=0).max(axis=0)  # [A]
        bi = int(np.argmax(peak))
        if not np.isfinite(peak[bi]) or peak[bi] <= cur + 1e-9:
            break
        f = int(av[bi])
        sel.append(f)
        b_raw = b_raw + max(float(q_rel[f]), 0.0) * fh_pool[f].astype(np.float64)
        cur = float(peak[bi])
        avail.remove(f)
    return sel, cur


def combiner_scores(fh, q_rel, choice_hd, rng):
    """CALL the UNCHANGED combiner (agg.aggregate 'bundle') on a selected set -> score[C]. Empty -> zeros."""
    if fh.shape[0] == 0:
        sc, _ = agg.aggregate(np.zeros((0, fh.shape[1] if fh.ndim == 2 else choice_hd.shape[1]), np.float32),
                              np.zeros(0, np.float32), choice_hd, "bundle", rng=rng)
        return sc
    sc, _ = agg.aggregate(fh.astype(np.float32), np.maximum(q_rel, 0.0).astype(np.float32),
                          choice_hd, "bundle", rng=rng)
    return sc


# ---------------------------------------------------------------------------
# self-test: planted set-level discriminator (bundle discriminates where per-fact top-K fails) +
# combiner-equivalence + real code path + arms-differ + determinism
# ---------------------------------------------------------------------------
def _planted_set_level_discriminator(nd=512):
    """Case where the SET/BUNDLE discriminates but PER-FACT top-K (by q_rel) fails:
      - a strong LURE fact L (high q_rel) points at the WRONG choice c1;
      - two GOLD facts g1,g2 (low q_rel) each only weakly favor c0 individually, but their BUNDLE cancels
        their off-axis parts and points STRONGLY at c0.
    A_TOPK (top-K by q_rel) picks the lure -> combiner leans c1 (WRONG). B_SETLEVEL greedy toward c0 builds
    {g1,g2} achieving the top margin -> argmax_i margin_i = c0 (CORRECT)."""
    rng = np.random.default_rng(41)

    def unit(v):
        return (v / np.linalg.norm(v)).astype(np.float32)
    # 3 near-orthonormal choices + an off-axis direction u1 perp to all
    C = np.linalg.qr(rng.standard_normal((nd, 4)))[0].T.astype(np.float32)  # 4 orthonormal rows
    c0, c1, c2, u1 = C[0], C[1], C[2], C[3]
    choice_hd = np.stack([c0, c1, c2]).astype(np.float32)                   # [3, nd] readout targets

    L = unit(0.85 * c1 + 0.20 * c0)          # strong lure -> c1 (wrong)
    g1 = unit(0.55 * c0 + 0.62 * u1)         # weak c0 + off-axis
    g2 = unit(0.55 * c0 - 0.62 * u1)         # weak c0 - off-axis (bundle cancels u1 -> strong c0)
    n1 = unit(rng.standard_normal(nd))       # noise
    fh_pool = np.stack([L, g1, g2, n1]).astype(np.float32)                  # pool order [L, g1, g2, n1]
    q_rel = np.array([1.00, 0.30, 0.28, 0.20], dtype=np.float32)           # lure has the highest relevance

    # combiner-equivalence: fast incremental (b_raw from empty over {g1,g2}) == agg.aggregate 'bundle'
    S = [1, 2]
    b_raw = np.zeros(nd, dtype=np.float64)
    for f in S:
        b_raw = b_raw + max(float(q_rel[f]), 0.0) * fh_pool[f].astype(np.float64)
    nb = np.linalg.norm(b_raw)
    fast = (b_raw / (nb if nb > 0 else 1.0)) @ choice_hd.T.astype(np.float64)
    ref, _ = agg.aggregate(fh_pool[S], q_rel[S], choice_hd, "bundle", rng=np.random.default_rng(0))
    assert np.allclose(fast, ref, atol=1e-5), f"planted: fast incremental != agg 'bundle' ({fast} vs {ref})"

    # A_TOPK by q_rel -> combiner argmax should pick the WRONG choice (lure dominates)
    sel_a = _topk_idx(q_rel.astype(np.float64), 2)
    sc_a, _ = agg.aggregate(fh_pool[sel_a], q_rel[sel_a], choice_hd, "bundle", rng=np.random.default_rng(0))
    a_pick = agg._pick(sc_a, np.random.default_rng(0))
    assert a_pick == 1, f"planted: A_TOPK should be captured by the lure (pick c1), got {a_pick} ({sc_a})"

    # B_SETLEVEL: per-choice sets -> argmax_i margin_i should pick c0
    margins = []
    sets = []
    for i in range(3):
        s_i, _ = greedy_set_toward(fh_pool, q_rel, choice_hd, i, K_SEL)
        sc_i = combiner_scores(fh_pool[np.asarray(s_i, dtype=np.int64)] if s_i else fh_pool[:0],
                               q_rel[np.asarray(s_i, dtype=np.int64)] if s_i else np.zeros(0, np.float32),
                               choice_hd, np.random.default_rng(0))
        margins.append(float(_margin_toward(sc_i, i)))
        sets.append(s_i)
    b_pick = int(np.argmax(margins))
    assert b_pick == 0, f"planted: B_SETLEVEL should pick c0 via set-level margin, got {b_pick} (margins={margins}, sets={sets})"
    assert set(sets[0]) == {1, 2}, f"planted: c0 set should be the gold pair {{1,2}}, got {sets[0]}"
    assert margins[0] > margins[1] + 0.05, f"planted: correct margin not above lure margin ({margins})"
    return {"a_pick": a_pick, "b_pick": b_pick, "margins": [round(m, 4) for m in margins], "sets": sets}


def self_test():
    print("[self-test] planted SET-LEVEL discriminator (bundle discriminates where per-fact top-K fails; "
          "combiner-equivalence; per-choice competition picks correct) ...", flush=True)
    planted = _planted_set_level_discriminator()
    print(f"[self-test]   planted: {planted}", flush=True)

    print("[self-test] REAL SemanticHDEncoder + REAL pool encode + REAL greedy set construction + "
          "UNCHANGED combiner ...", flush=True)
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    store_sents = [
        "moving water spins a turbine to generate hydroelectric power",
        "a dam holds back water in a reservoir",
        "burning coal heats water to make steam that spins a turbine",
        "iron is a kind of metal",
    ]
    SV = arc._encode_store(enc, store_sents)                     # [4, nd] unit
    q = {"stem": "What produces electricity at a hydroelectric dam?",
         "choices": ["moving water", "burning coal", "the moon"], "correct_index": 0}
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])   # [3, nd] unit
    q_rel = np.maximum(SV @ QQ, 0.0).astype(np.float32)

    # real combiner-equivalence over a greedy-selected set
    s0, _ = greedy_set_toward(SV, q_rel, choice_hd, 0, K_SEL)
    assert len(s0) >= 1, "real: greedy built an empty set"
    sidx = np.asarray(s0, dtype=np.int64)
    b_raw = np.zeros(nd, dtype=np.float64)
    for f in s0:
        b_raw = b_raw + max(float(q_rel[f]), 0.0) * SV[f].astype(np.float64)
    nb = np.linalg.norm(b_raw)
    fast = (b_raw / (nb if nb > 0 else 1.0)) @ choice_hd.T.astype(np.float64)
    ref, _ = agg.aggregate(SV[sidx], q_rel[sidx], choice_hd, "bundle", rng=np.random.default_rng(0))
    assert np.allclose(fast, ref, atol=1e-5), f"real: fast incremental != agg 'bundle' ({fast} vs {ref})"

    # determinism
    s0b, _ = greedy_set_toward(SV, q_rel, choice_hd, 0, K_SEL)
    assert s0 == s0b, "real: greedy set construction non-deterministic"

    # arms-differ: set-level selection != per-fact top-K selection (in general)
    sel_topk = set(_topk_idx(q_rel.astype(np.float64), K_SEL).tolist())
    sa, _ = greedy_set_agnostic(SV, q_rel, choice_hd, K_SEL)
    print(f"[self-test]   real: set_toward_c0={sorted(s0)} set_agnostic={sorted(sa)} topk={sorted(sel_topk)}",
          flush=True)

    # SET_AGNOSTIC + B decision run end-to-end on the tiny real question
    margins = []
    for i in range(choice_hd.shape[0]):
        s_i, _ = greedy_set_toward(SV, q_rel, choice_hd, i, K_SEL)
        sc_i = combiner_scores(SV[np.asarray(s_i, dtype=np.int64)] if s_i else SV[:0],
                               q_rel[np.asarray(s_i, dtype=np.int64)] if s_i else np.zeros(0, np.float32),
                               choice_hd, np.random.default_rng(0))
        margins.append(float(_margin_toward(sc_i, i)))
    assert len(margins) == choice_hd.shape[0], "real: per-choice margin vector wrong length"
    print(f"[self-test] PASS (planted set-level discriminator fires; fast==combiner; real greedy "
          f"construction; determinism; arms-differ; real per-choice margins={np.round(margins,3).tolist()})",
          flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 120, "limit_chal": 120}
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

    # ---- PASS A: per-question wide pool + flat baseline features (A_TOPK_LEARNED) + gold ----
    _heartbeat(output_dir, "features")
    poolidx_list = [None] * nQ
    Xn_flat = [None] * nQ                 # flat baseline features (A_TOPK_LEARNED learner)
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

        # FLAT baseline features (imported 29545 assembly, UNCHANGED) -> A_TOPK_LEARNED learner
        gs = gate.gate_scores(fh_pool, fw, stem_words, STEM[qi], chd, lure_set)
        coh = fixedsel.coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ[qi], 0.0))
        rr_scores = F_RR[qi][pool_idx]
        degs = degrees_all[pool_idx]
        negs = neg_all[pool_idx]
        Xflat = question_features_flat(fh_pool, STEM[qi], chd, gs, coh, rr_scores, degs, negs)
        Xn_flat[qi] = _minmax_cols(Xflat)

        gold_rows_list[qi] = np.array([uid2fi[u] for u in q["gold_central"] if u in uid2fi], dtype=np.int64)

    # ---- TRAIN the A_TOPK_LEARNED glass-box learner on TRAIN questions ONLY (label = is-gold) ----
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
    print(f"[learned:A_TOPK_LEARNED] rows={n_train_rows} pos={n_train_pos} weights={flat_weights}", flush=True)

    # ---- PASS B: select + answer per arm ----
    _heartbeat(output_dir, "select_and_answer")
    picks = {name: np.full(nQ, -1, dtype=np.int64) for name in ARMS}
    sel_gold_hit = {name: [None] * nQ for name in ARMS}
    b_win_choice = np.full(nQ, -1, dtype=np.int64)     # B_SETLEVEL winning choice index
    b_win_margin = np.full(nQ, np.nan, dtype=np.float64)   # its achieved margin
    b_margin_gap = np.full(nQ, np.nan, dtype=np.float64)   # winning margin - 2nd-best margin
    b_setsize = np.full(nQ, 0, dtype=np.int64)          # winning set size
    glass = []

    def gold_prec(sel_global, gold_set):
        if sel_global.size == 0:
            return 0.0
        return sum(1 for g in sel_global.tolist() if g in gold_set) / min(K_SEL, sel_global.size)

    for qi, q in enumerate(questions):
        pool_idx = poolidx_list[qi]
        fh_pool = SV_store[pool_idx]
        chd = choice_hd_map[qi]
        gold_rows = gold_rows_list[qi]
        gold_set = set(int(g) for g in gold_rows.tolist())
        q_rel_pool = np.maximum(fh_pool @ QQ[qi], 0.0).astype(np.float32)
        rng_q = np.random.default_rng(SEED + qi)
        C = chd.shape[0]

        # ---- A_TOPK_LEARNED (learned flat) ----
        sel_learn = pool_idx[_topk_idx(learned_score(Xn_flat[qi], w_flat, b_flat), K_SEL)]
        sc = combiner_scores(SV_store[sel_learn], np.maximum(SV_store[sel_learn] @ QQ[qi], 0.0),
                             chd, np.random.default_rng(SEED + qi))
        picks["A_TOPK_LEARNED"][qi] = agg._pick(sc, np.random.default_rng(SEED + qi))
        sel_gold_hit["A_TOPK_LEARNED"][qi] = gold_prec(sel_learn, gold_set)

        # ---- A_TOPK_GEO (geometric question relevance top-K) ----
        sel_geo = pool_idx[_topk_idx(q_rel_pool.astype(np.float64), K_SEL)]
        sc = combiner_scores(SV_store[sel_geo], np.maximum(SV_store[sel_geo] @ QQ[qi], 0.0),
                             chd, np.random.default_rng(SEED + qi))
        picks["A_TOPK_GEO"][qi] = agg._pick(sc, np.random.default_rng(SEED + qi))
        sel_gold_hit["A_TOPK_GEO"][qi] = gold_prec(sel_geo, gold_set)

        # ---- SET_AGNOSTIC (one set maximizing peak cross-choice margin) ----
        sa_local, _ = greedy_set_agnostic(fh_pool, q_rel_pool, chd, K_SEL)
        sel_sa = pool_idx[np.asarray(sa_local, dtype=np.int64)] if sa_local else pool_idx[:0]
        sc = combiner_scores(SV_store[sel_sa], np.maximum(SV_store[sel_sa] @ QQ[qi], 0.0),
                             chd, np.random.default_rng(SEED + qi))
        picks["SET_AGNOSTIC"][qi] = agg._pick(sc, np.random.default_rng(SEED + qi))
        sel_gold_hit["SET_AGNOSTIC"][qi] = gold_prec(sel_sa, gold_set)

        # ---- RND_SUBSET (must-fail) ----
        rng_r = np.random.default_rng(SEED + 7000 + qi)
        rnd_local = rng_r.permutation(pool_idx.size)[:min(K_SEL, pool_idx.size)]
        sel_rnd = pool_idx[rnd_local]
        sc = combiner_scores(SV_store[sel_rnd], np.maximum(SV_store[sel_rnd] @ QQ[qi], 0.0),
                             chd, np.random.default_rng(SEED + qi))
        picks["RND_SUBSET"][qi] = agg._pick(sc, np.random.default_rng(SEED + qi))
        sel_gold_hit["RND_SUBSET"][qi] = gold_prec(sel_rnd, gold_set)

        # ---- B_SETLEVEL (per-choice competitive set construction; answer = argmax_i margin_i) ----
        per_choice_sets = []
        per_choice_margin = np.full(C, -np.inf, dtype=np.float64)
        for i in range(C):
            s_i, _ = greedy_set_toward(fh_pool, q_rel_pool, chd, i, K_SEL)
            per_choice_sets.append(s_i)
            si = np.asarray(s_i, dtype=np.int64)
            sc_i = combiner_scores(fh_pool[si] if s_i else fh_pool[:0],
                                   q_rel_pool[si] if s_i else np.zeros(0, np.float32),
                                   chd, np.random.default_rng(SEED + qi))
            per_choice_margin[i] = float(_margin_toward(sc_i, i))
        b_pick = int(np.argmax(per_choice_margin))
        picks["B_SETLEVEL"][qi] = b_pick
        b_win_choice[qi] = b_pick
        b_win_margin[qi] = float(per_choice_margin[b_pick])
        srt = np.sort(per_choice_margin)[::-1]
        b_margin_gap[qi] = float(srt[0] - srt[1]) if C >= 2 else float(srt[0])
        win_set = pool_idx[np.asarray(per_choice_sets[b_pick], dtype=np.int64)] if per_choice_sets[b_pick] else pool_idx[:0]
        b_setsize[qi] = int(win_set.size)
        sel_gold_hit["B_SETLEVEL"][qi] = gold_prec(win_set, gold_set)

        # ---- ORACLE (gold facts -> combiner) ----
        if gold_rows.size:
            sc = combiner_scores(SV_store[gold_rows], np.maximum(SV_store[gold_rows] @ QQ[qi], 0.0),
                                 chd, np.random.default_rng(SEED + qi))
            picks["ORACLE"][qi] = agg._pick(sc, np.random.default_rng(SEED + qi))
            sel_gold_hit["ORACLE"][qi] = 1.0
        else:
            picks["ORACLE"][qi] = agg._pick(np.zeros(C, np.float32), np.random.default_rng(SEED + qi))
            sel_gold_hit["ORACLE"][qi] = 0.0

        # ---- GLASS-BOX (dam-Q autopsy): per-choice constructed set + margin, on TEST lure questions ----
        if len(glass) < 12 and lure_flags[qi] and test_mask[qi]:
            per_choice = {}
            for i in range(C):
                s_i = per_choice_sets[i]
                per_choice[str(i)] = {
                    "choice": q["choices"][i], "is_correct": int(i == q["correct_index"]),
                    "margin": round(float(per_choice_margin[i]), 4),
                    "set": [uid2sent.get(uids[int(pool_idx[j])], "")[:70] for j in s_i],
                    "set_gold": [int(int(pool_idx[j]) in gold_set) for j in s_i]}
            glass.append({
                "qid": q["qid"], "stem": q["stem"][:120], "choices": q["choices"],
                "correct_index": q["correct_index"], "split": "test",
                "gold_in_wide_pool": sum(1 for i in pool_idx.tolist() if i in gold_set),
                "B_win_choice": b_pick, "B_win_is_correct": int(b_pick == q["correct_index"]),
                "picks": {name: int(picks[name][qi]) for name in ARMS},
                "per_choice_constructed_set": per_choice})

        if (qi + 1) % 100 == 0:
            print(f"[progress] answered {qi+1}/{nQ}", flush=True)

    # ---- accuracies + precision ----
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
            "insample_train_precision": selprec(train_chal, name),
            "test_sel_gold_precision": selprec(test_chal, name),
        }
        print(f"[acc] {name}: insample_prec={accs[name]['insample_train_precision']} "
              f"test_prec={accs[name]['test_sel_gold_precision']} "
              f"test_chal={accs[name]['test_challenge']}", flush=True)

    # ---- CONFIRMATION-TRAP diagnostics (must-catch degenerate / non-informative winner) ----
    _heartbeat(output_dir, "confirmation_trap")
    tc_idx = [qi for qi in range(nQ) if test_chal[qi]]
    # winning-choice distribution on TEST Challenge
    win_counts = {}
    for qi in tc_idx:
        k = int(b_win_choice[qi])
        win_counts[k] = win_counts.get(k, 0) + 1
    n_tc = len(tc_idx)
    max_win_frac = round(max(win_counts.values()) / n_tc, 4) if n_tc else 0.0
    degenerate_winner = bool(n_tc and max_win_frac >= DEGENERATE_WINNER_FRAC)
    # winning-margin informativeness: mean winning margin on correct vs incorrect (TEST Challenge)
    m_corr = [b_win_margin[qi] for qi in tc_idx if picks["B_SETLEVEL"][qi] == questions[qi]["correct_index"]
              and np.isfinite(b_win_margin[qi])]
    m_wrong = [b_win_margin[qi] for qi in tc_idx if picks["B_SETLEVEL"][qi] != questions[qi]["correct_index"]
               and np.isfinite(b_win_margin[qi])]
    mean_margin_correct = round(float(np.mean(m_corr)), 5) if m_corr else None
    mean_margin_wrong = round(float(np.mean(m_wrong)), 5) if m_wrong else None
    margin_informative = bool(mean_margin_correct is not None and mean_margin_wrong is not None
                              and mean_margin_correct > mean_margin_wrong)
    mean_win_margin_gap = round(float(np.nanmean([b_margin_gap[qi] for qi in tc_idx])), 5) if n_tc else 0.0
    mean_b_setsize = round(float(np.mean([b_setsize[qi] for qi in tc_idx])), 3) if n_tc else 0.0

    # ---- residual diagnosis: does the SET-LEVEL margin point at the correct choice when gold in pool? ----
    _heartbeat(output_dir, "residual_diagnosis")
    n_reach = n_reach_correct = n_tc2 = 0
    for qi in tc_idx:
        n_tc2 += 1
        pool_idx = poolidx_list[qi]
        gold_set = set(int(g) for g in gold_rows_list[qi].tolist())
        if not any(int(i) in gold_set for i in pool_idx.tolist()):
            continue
        n_reach += 1
        if int(b_win_choice[qi]) == questions[qi]["correct_index"]:
            n_reach_correct += 1
    gold_in_pool_frac = round(n_reach / n_tc2, 4) if n_tc2 else None
    setmargin_points_correct_frac = round(n_reach_correct / n_reach, 4) if n_reach else None
    print(f"[diag] test_chal={n_tc2} gold_in_pool={gold_in_pool_frac} "
          f"setmargin_points_correct(of reachable)={setmargin_points_correct_frac}", flush=True)

    # ---- PRIMARY: end-to-end B_SETLEVEL vs A_TOPK_LEARNED; controls ----
    A_learn_chal = accs["A_TOPK_LEARNED"]["test_challenge"] or 0.0
    A_geo_chal = accs["A_TOPK_GEO"]["test_challenge"] or 0.0
    sa_chal = accs["SET_AGNOSTIC"]["test_challenge"] or 0.0
    B_chal = accs["B_SETLEVEL"]["test_challenge"] or 0.0
    rnd_chal = accs["RND_SUBSET"]["test_challenge"] or 0.0
    oracle_chal = accs["ORACLE"]["test_challenge"] or 0.0

    set_lift = round(B_chal - A_learn_chal, 4)              # PRIMARY lift (vs the harness anchor baseline)
    set_lift_geo = round(B_chal - A_geo_chal, 4)
    set_vs_agnostic = round(B_chal - sa_chal, 4)           # bonus: per-choice conditioning adds over set-build
    gap = round(oracle_chal - A_learn_chal, 4)
    gap_frac_closed = round(set_lift / gap, 4) if gap > 1e-9 else None
    rnd_lift = round(rnd_chal - A_learn_chal, 4)

    A_test_prec = accs["A_TOPK_LEARNED"]["test_sel_gold_precision"] or 0.0
    B_test_prec = accs["B_SETLEVEL"]["test_sel_gold_precision"] or 0.0
    prec_rises = bool(B_test_prec > A_test_prec)

    mc_b, mc_c, mc_stat, mc_p = gate.mcnemar(correct["A_TOPK_LEARNED"][test_chal],
                                             correct["B_SETLEVEL"][test_chal])
    sig = (mc_p is not None) and (mc_p < MCNEMAR_ALPHA)
    random_ok = rnd_lift <= RANDOM_MAX

    # ---- integrity gates ----
    A_insample = accs["A_TOPK_LEARNED"]["insample_train_precision"] or 0.0
    anchor_prec_ok = abs(A_insample - ANCHOR_PREC) <= ANCHOR_TOL_PREC
    anchor_chal_ok = abs(A_learn_chal - ANCHOR_CHAL) <= ANCHOR_TOL_CHAL
    ag_saturated = A_learn_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_learn_chal < 0.95
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest() for name in ARMS}
    n_distinct = len(set(digests[n] for n in ("A_TOPK_LEARNED", "A_TOPK_GEO", "SET_AGNOSTIC",
                                              "B_SETLEVEL", "RND_SUBSET")))
    arms_differ = n_distinct >= 4
    discriminator_fired = bool(mean_b_setsize > 0.0 and mean_win_margin_gap > 1e-5 and arms_differ)

    hp_lift = set_lift >= SET_LIFT_HP
    hard_pass = bool(hp_lift and prec_rises and sig and random_ok and (not degenerate_winner))
    middle = bool((not hard_pass) and set_lift >= MB_SET_LIFT and random_ok and (not degenerate_winner))
    hard_fail = bool(set_lift < MB_SET_LIFT)

    # ---- residual sub-diagnosis (meaningful on HARD_FAIL) ----
    sub_diag = None
    if hard_fail:
        if gold_in_pool_frac is not None and gold_in_pool_frac < 0.4:
            sub_diag = (f"retrieval-cut: the discriminating gold fact is often NOT in the wide pool "
                        f"(gold_in_pool_frac={gold_in_pool_frac}); redirect = retrieval recall, not "
                        f"set-level selection.")
        elif setmargin_points_correct_frac is not None and setmargin_points_correct_frac < 0.4:
            sub_diag = (f"objective-wall: gold reaches the pool (gold_in_pool_frac={gold_in_pool_frac}) but "
                        f"the SET-LEVEL bundle-margin points at the CORRECT choice only "
                        f"{setmargin_points_correct_frac} of the time -- the greedy set-construction "
                        f"objective (raise the bundle's margin) does not separate the correct choice's best "
                        f"set from the lures' best sets on this thin GloVe/WordNet content; redirect = "
                        f"richer/grounded meaning in the set slots (the deeper lever), not the construction "
                        f"granularity.")
        else:
            sub_diag = (f"aggregation/readout: gold reaches the pool AND the set-margin points correct "
                        f"(setmargin_points_correct_frac={setmargin_points_correct_frac}) but the end-to-end "
                        f"accuracy does not lift over per-fact top-K -- suspect the combiner readout scale or "
                        f"the argmax mapping, not the set-construction signal.")

    grade = arc._grade_proxy(accs["B_SETLEVEL"]["test_easy"], accs["B_SETLEVEL"]["test_challenge"])

    # ---- verdict ----
    if ag_saturated:
        verdict = "SET_LEVEL_SATURATED"
        vmsg = f"A_TOPK_LEARNED TEST Challenge {A_learn_chal} >= {AG_BASELINE_SAT}: no headroom (report)."
    elif not arms_differ:
        verdict = "SET_LEVEL_ARMS_IDENTICAL_META_RULE_AF"
        vmsg = (f"selection arms produced < 4 distinct pick-vectors (n_distinct={n_distinct}); arm bug -- "
                f"do NOT trust the comparison.")
    elif not discriminator_fired:
        verdict = "SET_LEVEL_DISCRIMINATOR_VACUOUS"
        vmsg = (f"set construction degenerate (mean_win_setsize={mean_b_setsize}, mean_win_margin_gap="
                f"{mean_win_margin_gap}); the per-choice sets do not differentiate at this regime.")
    elif degenerate_winner:
        verdict = "SET_LEVEL_DEGENERATE_WINNER"
        vmsg = (f"CONFIRMATION-TRAP CATCH: B_SETLEVEL winning choice collapses onto a single index "
                f"{max_win_frac} >= {DEGENERATE_WINNER_FRAC} of TEST Challenge questions; the per-choice "
                f"competition is a no-op / one choice trivially inflates margin -- do NOT credit the "
                f"mechanism (margin_informative={margin_informative}).")
    elif hard_pass:
        verdict = "SET_LEVEL_HARD_PASS"
        vmsg = (f"SET-LEVEL / HOLISTIC selection BEATS per-fact top-K: B_SETLEVEL TEST Challenge {B_chal} vs "
                f"A_TOPK_LEARNED {A_learn_chal} (lift {set_lift:+.4f} >= {SET_LIFT_HP}, {gap_frac_closed} of "
                f"the {gap} oracle gap); TEST precision {B_test_prec} > A {A_test_prec}; McNemar p={mc_p} < "
                f"{MCNEMAR_ALPHA}; RND lift {rnd_lift:+.4f} (<= {RANDOM_MAX}); vs SET_AGNOSTIC {set_vs_agnostic:+.4f} "
                f"(per-choice conditioning {'adds' if set_vs_agnostic > 0 else 'does not add'}); winner not "
                f"degenerate ({max_win_frac}); margin_informative={margin_informative}. Discriminating at the "
                f"BUNDLE (set) level is the missing brain-shape (coalition/CI-construction).")
    elif middle:
        verdict = "SET_LEVEL_MIDDLE_BAND"
        vmsg = (f"MIDDLE: real-but-partial. B_SETLEVEL TEST Challenge {B_chal} vs A_TOPK_LEARNED {A_learn_chal} "
                f"(lift {set_lift:+.4f} in [{MB_SET_LIFT},{SET_LIFT_HP})); prec_rises={prec_rises} "
                f"({B_test_prec} vs {A_test_prec}); McNemar p={mc_p} sig={sig}; vs SET_AGNOSTIC "
                f"{set_vs_agnostic:+.4f}; RND lift {rnd_lift:+.4f} (ok={random_ok}). Set-level helps but is not "
                f"decisive -> residual: gold_in_pool={gold_in_pool_frac}, setmargin_points_correct="
                f"{setmargin_points_correct_frac}.")
    else:
        verdict = "SET_LEVEL_HARD_FAIL"
        vmsg = (f"HONEST: SET-LEVEL selection ~= per-fact top-K. B_SETLEVEL TEST Challenge {B_chal} vs "
                f"A_TOPK_LEARNED {A_learn_chal} (lift {set_lift:+.4f} < {MB_SET_LIFT}); A_TOPK_GEO {A_geo_chal}, "
                f"SET_AGNOSTIC {sa_chal}, RND {rnd_chal}, ORACLE {oracle_chal}; TEST prec B {B_test_prec} vs A "
                f"{A_test_prec}. Doing the discrimination at the BUNDLE (set) level does NOT break the "
                f"gold-vs-lure symmetry in THIS pipeline. Sub-diagnosis: {sub_diag}")

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [TEST Chal] A_learn={A_learn_chal} A_geo={A_geo_chal} SET_AGN={sa_chal} "
                    f"B_SETLEVEL={B_chal} RND={rnd_chal} ORACLE={oracle_chal}; set_lift={set_lift:+.4f} "
                    f"({gap_frac_closed} of {gap} gap) McNemar_p={mc_p}; vs_agnostic={set_vs_agnostic:+.4f}; "
                    f"rnd_lift={rnd_lift:+.4f}; [prec] A={A_test_prec} B={B_test_prec}; "
                    f"gold_in_pool={gold_in_pool_frac} setmargin_points_correct={setmargin_points_correct_frac}; "
                    f"win_frac={max_win_frac} margin_informative={margin_informative} | chance={round(chance,4)}"),
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
        # selection + combiner config (UNCHANGED)
        "k_wide": K_WIDE, "k_sel": K_SEL, "rr_top_t": RR_TOP_T, "mu_supp": MU_SUPP,
        "settle_t": SETTLE_T, "settle_eps": SETTLE_EPS, "hops": HOPS, "damp": DAMP, "seed_cos": SEED_COS,
        "l2_reg": learned.L2_REG, "gd_iters": learned.GD_ITERS, "gd_lr": learned.GD_LR,
        "split_frac_train": learned.SPLIT_FRAC_TRAIN,
        # GLASS-BOX: A_TOPK_LEARNED learned weights (inspectable)
        "flat_feature_names": list(FLAT_FEATURE_NAMES),
        "A_topk_learned_weights": flat_weights,
        # end-to-end accuracy by arm
        "acc_by_arm": accs,
        "A_TOPK_LEARNED_test_challenge": A_learn_chal, "A_TOPK_GEO_test_challenge": A_geo_chal,
        "SET_AGNOSTIC_test_challenge": sa_chal, "B_SETLEVEL_test_challenge": B_chal,
        "RND_SUBSET_test_challenge": rnd_chal, "oracle_gold_test_challenge": oracle_chal,
        "primary_baseline": "A_TOPK_LEARNED", "primary_arm": "B_SETLEVEL",
        "set_lift_challenge": set_lift, "set_lift_vs_geo": set_lift_geo,
        "set_vs_agnostic_challenge": set_vs_agnostic,
        "selection_gap": gap, "gap_fraction_closed": gap_frac_closed,
        "random_lift_challenge": rnd_lift, "random_control_ok": bool(random_ok),
        # precision
        "test_sel_gold_precision_by_arm": {n: accs[n]["test_sel_gold_precision"] for n in ARMS},
        "insample_train_precision_by_arm": {n: accs[n]["insample_train_precision"] for n in ARMS},
        "A_insample_precision": A_insample,
        "A_test_sel_gold_precision": A_test_prec, "B_test_sel_gold_precision": B_test_prec,
        "primary_precision_rises": prec_rises,
        # McNemar
        "mcnemar_challenge": {"baseline": "A_TOPK_LEARNED", "arm": "B_SETLEVEL",
                              "b_A_right_arm_wrong": mc_b, "c_A_wrong_arm_right": mc_c,
                              "stat": None if mc_stat is None else round(mc_stat, 4),
                              "p_value": None if mc_p is None else round(mc_p, 5),
                              "significant": bool(sig)},
        # CONFIRMATION-TRAP diagnostics
        "confirmation_trap": {
            "b_win_choice_distribution": {str(k): win_counts[k] for k in sorted(win_counts)},
            "max_win_choice_frac": max_win_frac, "degenerate_winner": degenerate_winner,
            "mean_win_margin_correct": mean_margin_correct, "mean_win_margin_wrong": mean_margin_wrong,
            "margin_informative": margin_informative,
            "mean_win_margin_gap_to_second": mean_win_margin_gap,
            "mean_winning_set_size": mean_b_setsize},
        # residual diagnosis (retrieval-reach vs set-objective-wall)
        "gold_in_pool_frac": gold_in_pool_frac,
        "setmargin_points_correct_frac": setmargin_points_correct_frac,
        "hard_fail_sub_diagnosis": sub_diag,
        # anchor regression
        "anchor_precision_regression_ok": bool(anchor_prec_ok),
        "anchor_challenge_regression_ok": bool(anchor_chal_ok),
        "anchor_precision_expected": ANCHOR_PREC, "anchor_challenge_expected": ANCHOR_CHAL,
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band), "ag_saturated": bool(ag_saturated),
        "arms_differ_verified": bool(arms_differ), "n_distinct_pick_vectors": int(n_distinct),
        "arm_pick_digests": digests,
        "discriminator_fired": discriminator_fired,
        "hard_pass": hard_pass, "middle_band": middle, "hard_fail": hard_fail,
        "bands": {"SET_LIFT_HP": SET_LIFT_HP, "MB_SET_LIFT": MB_SET_LIFT, "RANDOM_MAX": RANDOM_MAX,
                  "mcnemar_alpha": MCNEMAR_ALPHA, "ag_baseline_sat": AG_BASELINE_SAT,
                  "degenerate_winner_frac": DEGENERATE_WINNER_FRAC,
                  "anchor_prec": ANCHOR_PREC, "anchor_chal": ANCHOR_CHAL},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: the SELECTION GRANULARITY is the ONLY variable. The WIDE re-retrieval pool (RR top-100, "
            "mr.reformulate_seeds/_rownorm_scores IMPORTED UNCHANGED, recall@100=0.69) and the bind+bundle "
            "combiner (agg.aggregate 'bundle' IMPORTED UNCHANGED, used AS the set-readout with the SAME "
            "answer-agnostic q_rel=relu(cos(fact,QQ)) weight for every arm) are held fixed. A_TOPK_LEARNED "
            "reuses 29545's EXACT flat-cosine feature assembly + glass-box learner (imported) -> regression-"
            "anchor to ~0.1865 in-sample / ~0.3663 TEST Challenge. B_SETLEVEL does PER-CHOICE competitive "
            "greedy set construction: for each choice i, grow S_i (up to K_SEL) by adding the pool fact that "
            "most raises margin_i(S_i)=combiner_score_i(bundle(S_i))-max_{j!=i} combiner_score_j; answer = "
            "argmax_i margin_i (the competition = the confirmation-trap guard). The greedy candidate search is "
            "a VECTORIZED incremental of the SAME combiner (b_raw += relu(q_rel_f)*f; L2-norm absorbs the "
            "w/w.sum rescale -> bit-equal to agg.aggregate, ASSERTED in self_test); the FINAL per-choice "
            "margin CALLS agg.aggregate (combiner-faithful). SET_AGNOSTIC builds ONE set maximizing the peak "
            "cross-choice margin (isolates set-CONSTRUCTION from per-choice conditioning). A_TOPK_GEO = "
            "geometric per-fact top-K (matched no-train). RND_SUBSET (must-fail) + ORACLE (ceiling) anchor "
            "floor/ceiling. CONFIRMATION-TRAP diagnostics: winning-choice distribution (degenerate catch) + "
            "winning-margin informativeness (correct vs wrong). NO LEAK: TRAIN/TEST disjoint "
            "(learned._split_train_test); the set-level arms are UNTRAINED geometry (gold never enters "
            "selection); gold used for A-learner TRAIN label + ORACLE + eval only. "
            "STUBBED/NOTED-NOT-BUILT: richer/grounded meaning in the set slots (the deeper lever if the "
            "set-objective-wall is the residual); iterative/beam settle (greedy add is the first constructive "
            "loop; a full Kintsch relaxation over the constructed set is the next refinement)."),
        "contract": ("INLINE-LOCAL foreground-to-completion; no push/remote-persist; NOT remote-portable "
                     "(GloVe+WorldTree git-ignored/large; inherits 29544/29545/29546 contract); VET-PENDING; "
                     "FULL eval slice bounded (limit_easy=500 limit_chal=600, stratified train/test) to fit "
                     "one foreground call"),
        "compute_architecture": ("mixed CPU: batched GloVe encode (store + questions + choices) + scipy "
                                 "sparse batched PPR (2 passes, UNCHANGED) + per-question VECTORIZED greedy "
                                 "set construction (b_raw increment + normalize + choice matmul; C choices x "
                                 "K_SEL steps x P<=100 candidates) + UNCHANGED combiner calls for the final "
                                 "margins; wall target < 8min. No GPU speedup needed (matmuls small)."),
        "storage_strategy": "sharded (each fact = own embedding + own graph node)",
        "progress_logging": "line_buffered_stdout",
        "crlb_n_a": ("geometric selection, no learned noise floor; the set-level bundle margin is a "
                     "deterministic per-pool quantity -> a fixed geometric signal, MORE dims = LESS bundle/dot "
                     "noise (~1/sqrt(N)) so it SURVIVES scale by construction; smoke runs at FULL n_dim=2048 "
                     "(only question-limit reduced)"),
        "calibration_check": ("default_ok_for_this_regime (all set-level scoring is geometric over the "
                              "UNCHANGED combiner + author-set a priori; A_TOPK_LEARNED hyperparams inherited "
                              "from 29545 L2=1.0/iters=400/lr=0.5; NOT tuned to force a win; RND_SUBSET "
                              "must-fail + SET_AGNOSTIC isolation + confirmation-trap degenerate-catch present; "
                              "bands set a priori)"),
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
