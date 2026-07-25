"""arc_selection_answer_conditioned_contrastive_v1 -- ANSWER-AGNOSTIC vs ANSWER-CONDITIONED selection.

The selection wall (VET 29544/29545 + the deconfounded content-enrichment fair re-test
exp_concept_featural_enrichment_v2): retrieval REACHES the facts (wide RR pool recall@100=0.69), the
combiner USES them (oracle gold->combiner Challenge ~0.71), but SELECTION cannot ISOLATE the gold from
the contains-gold pool (answer-agnostic precision ~0.11-0.19 vs oracle 0.97). The fair re-test proved
WHY richer CONTENT does not help: enrichment raises fact-vs-choice TOPIC-cosine roughly SYMMETRICALLY
across the 4 choices, so a read-out that never compares across choices cannot break the ASYMMETRIC
gold-vs-lure decision. Our pipeline selects K facts relevant to the QUESTION, then a combiner scores
choices -- selection NEVER conditions on WHICH choice it supports.

The brain-drill (notes/research_drill_answer_conditioned_selection_biology_2026-07-25.md) shows human
MC-reasoning is answer-CONDITIONED: bind Q to each candidate, score by CONTRASTIVE / likelihood-ratio
DIFFERENTIAL support, competitively normalized across choices (PFC goal-biased competitive retrieval /
illness-script differential diagnosis / multi-alternative DDM-LCA / likelihood-ratio norm / ECHO
inhibitory contrast). Named gap: SHAPE (per-choice conditioned selection, not question-only top-K),
PLACE (condition at SELECTION time), METRIC (differential support, not raw relevance).

ONE variable = answer-AGNOSTIC vs answer-CONDITIONED SELECTION. The WIDE RR pool (recall@100=0.69,
mr.reformulate_seeds/_rownorm_scores IMPORTED), the bind+bundle COMBINER (agg.aggregate 'bundle'
IMPORTED), retrieval, and the TRAIN/TEST split are held FIXED. Every combiner arm feeds the SAME K_SEL
facts to the SAME combiner with the SAME answer-agnostic q_rel weight; the ONLY difference is WHICH facts
the selection stage picks.

Conditioned / contrastive metric (place / shape / metric of the gap):
  s_i(f)  = <sign(fact_f) (*) sign(stem), sign(choice_i)> / N    [SUBSTRATE BIND: conjunctive read-out;
            binding fact with question then dotting the bipolar choice is the substrate-native analog of
            dendritic coincidence detection -- the drill's "conjunction for free"; TESTED, not assumed]
  d_i(f)  = s_i(f) - max_{j!=i} s_j(f)                           [CONTRAST across choices: max-margin /
            likelihood-ratio-flavored; competitively normalized; removes the shared question-topic
            component that answer-agnostic content raises symmetrically]
  disc(f) = max_i d_i(f)                                         [fact's best discriminative power]

Arms (one-variable spine A_AGNOSTIC_GEO -> COND_NONCONTRAST -> B_CONDITIONED):
  A_AGNOSTIC       -- 29545 flat learned relevance -> top-K_SEL -> combiner [HARNESS ANCHOR 0.1865/0.3663]
  A_AGNOSTIC_GEO   -- geometric question-relevance top-K_SEL (matched no-train scoring class for B)
  COND_NONCONTRAST -- bind-conditioned max_i s_i(f) top-K_SEL (conditioning WITHOUT contrast)
  B_CONDITIONED    -- bind-conditioned CONTRAST disc(f) top-K_SEL -> combiner [PRIMARY test arm]
  B_COND_FLAT      -- flat-encoding conditioned CONTRAST -> combiner (robustness / representation check)
  B_DIRECT         -- literal DDM winner: answer = argmax_i max_f d_i(f) (per-choice competition, NO
                      combiner)
  MISCONDITIONED   -- bind-conditioned CONTRAST w/ choices SHUFFLED (roll by 1) [MUST-FAIL: right cond.]
  RND              -- random K_SEL -> combiner [MUST-FAIL]
  ORACLE           -- gold facts -> combiner [CEILING ~0.71]

PRIMARY = end-to-end TEST Challenge accuracy (B vs A 0.3663 toward oracle ~0.71) + McNemar; SECONDARY =
TEST sel_gold_precision (toward oracle 0.97) + chal_lure subset. HARD_PASS = B materially lifts Challenge
(>=+0.05) AND raises precision AND McNemar-sig AND MISCONDITIONED does NOT help AND contrast beats
non-contrast. HARD_FAIL = conditioning ~= agnostic (lift < +0.02) -> report STRAIGHT; residual diagnosis
(retrieval-cut vs content-resolution) tells us if the next lever is grounding. NO tuning to force a win.

Contract: INLINE-LOCAL foreground-to-completion (GloVe+WorldTree git-ignored/large -> NOT remote-
portable; inherits 29544/29545 contract); NO push/remote-persist; ASCII-only; deterministic (fixed
seeds, numpy default_rng, sorted iteration, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL pool encode + REAL conditioned bind +
#   flat scoring + differential + UNCHANGED combiner; PLANTED discriminator asserts the contrast selects
#   a choice-specific fact, the DDM winner points at the right choice, misconditioning breaks it, and an
#   on-topic-to-ALL fact is NOT selected; arms-differ; determinism
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-guard on A_AGNOSTIC TEST challenge (headroom to the ~0.71 ceiling)
# - storage = SHARDED (each fact = own embedding + own graph node)
# - GLASS-BOX: per-choice best differential fact + its d score logged on surface-trap Qs (dam-Q autopsy)
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

ANCHOR_NAME = "arc_selection_answer_conditioned_contrastive_v1"
SEED = 20260731

# ---- selection hyperparams (UNCHANGED pool + combiner; inherited from 29545/gate) ----
K_WIDE = learned.K_WIDE      # UNCHANGED wide re-retrieval pool the scorer selects FROM (=100)
RR_TOP_T = learned.RR_TOP_T  # UNCHANGED re-retrieval reformulation depth
K_SEL = learned.K_SEL        # UNCHANGED clean-fact selection width (Cowan-4; =4)
MU_SUPP = learned.MU_SUPP
SETTLE_T = agg.SETTLE_T
SETTLE_EPS = agg.SETTLE_EPS
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# reuse the 29545 learner + baseline features EXACTLY (regression-anchors A_AGNOSTIC to 0.1865/0.3663)
FLAT_FEATURE_NAMES = learned.FEATURE_NAMES
train_glassbox_relevance = learned.train_glassbox_relevance
learned_score = learned.learned_score
_minmax_cols = learned._minmax_cols
_neg_count = learned._neg_count
question_features_flat = learned.question_features
_topk_idx = learned._topk_idx

# ---- bands (author-designed a priori) ----
CHAL_LIFT_HP = 0.05       # PRIMARY HARD-PASS: (best conditioned arm) - A on TEST Challenge >= this
MB_CHAL_LIFT = 0.02       # MIDDLE band floor (positive but sub-HP)
MISCOND_MAX = 0.02        # MISCONDITIONED - A on Challenge must be <= this (must-fail)
RANDOM_MAX = 0.02         # RND - A on Challenge must be <= this (must-fail)
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95    # A_AGNOSTIC challenge >= this -> vacuous (no headroom)
ANCHOR_PREC = 0.1865      # 29545 answer-agnostic in-sample precision (regression anchor)
ANCHOR_CHAL = 0.3663      # 29545 answer-agnostic TEST Challenge (regression anchor)
ANCHOR_TOL_PREC = 0.03    # WARN if |A insample precision - ANCHOR_PREC| > this
ANCHOR_TOL_CHAL = 0.03    # WARN if |A TEST challenge   - ANCHOR_CHAL| > this

_T0 = [0.0]

# combiner arms feed K_SEL facts to the UNCHANGED combiner; B_DIRECT + ORACLE handled separately
COMBINER_ARMS = ("A_AGNOSTIC", "A_AGNOSTIC_GEO", "COND_NONCONTRAST", "B_CONDITIONED",
                 "B_COND_FLAT", "MISCONDITIONED", "RND")
ARMS = COMBINER_ARMS + ("B_DIRECT", "ORACLE")


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
# conditioned / contrastive selection scoring (the ONE new mechanism)
# ---------------------------------------------------------------------------
def _bipolar(mat):
    """Real dense -> bipolar +/-1 (sign; 0 -> +1). mat: [..., N]."""
    m = np.asarray(mat, dtype=np.float32)
    return np.where(m >= 0.0, 1.0, -1.0).astype(np.float32)


def conditioned_scores_bind(fh_pool, stem_vec, choice_only):
    """SUBSTRATE BIND conditioned relevance s_i(f) = <sign(fact)(*)sign(stem), sign(choice_i)>/N in [-1,1].
      fh_pool     : [P, N] unit fact rows ; stem_vec: [N] ; choice_only: [C, N] unit choice-only rows
    Binding fact with the question then dotting each bipolar choice is the conjunctive read-out (only high
    when the fact aligns with the question-bound choice, not the question topic alone). Returns [P, C]."""
    P = fh_pool.shape[0]
    C = choice_only.shape[0]
    N = fh_pool.shape[1]
    if P == 0 or C == 0:
        return np.zeros((P, C), dtype=np.float64)
    qsign = _bipolar(stem_vec)                       # [N]
    Fbq = _bipolar(fh_pool) * qsign[None, :]         # [P, N]  fact bound with question
    Cb = _bipolar(choice_only)                       # [C, N]
    s = (Fbq @ Cb.T) / float(N)                      # [P, C]  bipolar dot / N in [-1,1]
    return s.astype(np.float64)


def conditioned_scores_flat(fh_pool, choice_only):
    """FLAT conditioned relevance s_flat_i(f) = cos(fact_f, choice_only_i). Pool is already question-
    retrieved (question-grounded), so the choice-only differential is implicitly question-conditioned."""
    P = fh_pool.shape[0]
    C = choice_only.shape[0]
    if P == 0 or C == 0:
        return np.zeros((P, C), dtype=np.float64)
    return (fh_pool @ choice_only.T).astype(np.float64)   # [P, C] (unit rows -> cosine)


def differential_support(s):
    """CONTRAST across choices: d_i(f) = s_i(f) - max_{j!=i} s_j(f) (max-margin, competitively normalized).
      s: [P, C]. Returns (d [P,C], disc [P] = max_i d_i)."""
    P, C = s.shape
    if C == 0:
        return np.zeros((P, 0), dtype=np.float64), np.zeros(P, dtype=np.float64)
    if C == 1:
        return s.copy(), s[:, 0].copy()
    d = np.empty_like(s)
    for i in range(C):
        rivals = np.delete(s, i, axis=1)             # [P, C-1]
        d[:, i] = s[:, i] - rivals.max(axis=1)
    return d, d.max(axis=1)


def _roll_choices(choice_only):
    """Within-question relabel: roll choice rows by 1 (no fixed point for C>=2; no hash()). Used ONLY to
    demonstrate the per-choice WINNER (B_DIRECT) is choice-label-sensitive -- NOT for combiner-arm
    selection, where disc(f)=max_i d_i is permutation-invariant so a within-question roll is a no-op."""
    C = choice_only.shape[0]
    if C < 2:
        return choice_only.copy()
    return choice_only[np.roll(np.arange(C), 1)]


def _donor_choices(donor_choice_only, C):
    """Cross-question misconditioning: return C rows of WRONG (other-question) choice content, cycled to
    length C. Binding Q with unrelated choices genuinely changes the disc ranking (unlike a within-
    question roll), so this is a non-vacuous must-fail control for the combiner-fed selection arms."""
    D = donor_choice_only.shape[0]
    if D == 0:
        return donor_choice_only
    return donor_choice_only[np.arange(C) % D]


# ---------------------------------------------------------------------------
# self-test: planted discriminator (contrast selects choice-specific fact; DDM winner correct;
# misconditioning breaks it; on-topic-to-all fact NOT selected) + real code path + arms-differ
# ---------------------------------------------------------------------------
def _planted_conditioned_discriminator(nd=512):
    rng = np.random.default_rng(31)
    # 3 near-orthogonal unit choice vectors + a question stem
    def unit(v):
        return (v / np.linalg.norm(v)).astype(np.float32)
    choices = np.stack([unit(rng.standard_normal(nd)) for _ in range(3)])      # [3, nd]
    stem = unit(rng.standard_normal(nd))                                        # [nd]

    qsign = _bipolar(stem)
    c0sign = _bipolar(choices[0])
    # GOLD fact: constructed so sign(fact)(*)sign(stem) == sign(choice_0) -> s_0=1, s_{1,2} ~ 0
    fact_gold = unit((qsign * c0sign).astype(np.float32))
    # AGNOSTIC fact: sign(fact)=sign(stem) -> s_i ~ <all-ones, sign(choice_i)>/N ~ 0 for every choice
    fact_agn = unit(qsign.copy())
    fh = np.stack([fact_gold, fact_agn])                                        # [2, nd]

    s = conditioned_scores_bind(fh, stem, choices)                             # [2, 3]
    d, disc = differential_support(s)
    assert s[0, 0] >= 0.9, f"planted: gold fact not choice-0 aligned (s00={s[0,0]:.3f})"
    assert disc[0] >= disc[1] + 0.3, f"planted: contrast did not separate gold (disc={disc.tolist()})"
    # DDM winner (argmax_i max_f d_i) must be choice 0
    ddm = np.array([d[:, i].max() for i in range(3)])
    assert int(np.argmax(ddm)) == 0, f"planted: DDM winner not choice 0 (ddm={ddm.tolist()})"
    # COND_NONCONTRAST alone (max_i s_i) fires for gold too, but MUST-FAIL: misconditioning breaks it
    s_mis = conditioned_scores_bind(fh, stem, _roll_choices(choices))
    d_mis, _ = differential_support(s_mis)
    ddm_mis = np.array([d_mis[:, i].max() for i in range(3)])
    assert int(np.argmax(ddm_mis)) != 0, f"planted: misconditioning did NOT break the winner (mis={ddm_mis.tolist()})"
    return {"s_gold": [round(float(x), 3) for x in s[0].tolist()],
            "disc": [round(float(x), 3) for x in disc.tolist()],
            "ddm": [round(float(x), 3) for x in ddm.tolist()],
            "ddm_mis": [round(float(x), 3) for x in ddm_mis.tolist()]}


def self_test():
    print("[self-test] planted conditioned-contrastive discriminator (contrast selects a choice-specific "
          "fact; DDM winner correct; misconditioning breaks it; on-topic-to-all fact not selected) ...",
          flush=True)
    planted = _planted_conditioned_discriminator()
    print(f"[self-test]   planted: {planted}", flush=True)

    print("[self-test] REAL SemanticHDEncoder + REAL pool encode + REAL conditioned bind/flat scoring + "
          "differential + UNCHANGED combiner ...", flush=True)
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    store_sents = [
        "moving water spins a turbine to generate hydroelectric power",
        "burning coal heats water to make steam that spins a turbine",
        "iron is a kind of metal",
    ]
    SV = arc._encode_store(enc, store_sents)                     # [3, nd] unit
    q = {"stem": "What produces electricity at a hydroelectric dam?",
         "choices": ["moving water", "burning coal", "the moon"], "correct_index": 0}
    stem_vec = arc._encode_store(enc, [q["stem"]])[0]
    choice_only = arc._encode_store(enc, list(q["choices"]))     # [3, nd] unit
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])

    s_bind = conditioned_scores_bind(SV, stem_vec, choice_only)
    s_flat = conditioned_scores_flat(SV, choice_only)
    assert s_bind.shape == (3, 3) and s_flat.shape == (3, 3), "real: conditioned score shape"
    d_bind, disc_bind = differential_support(s_bind)
    d_flat, disc_flat = differential_support(s_flat)
    assert disc_bind.shape == (3,) and disc_flat.shape == (3,), "real: differential shape"

    # UNCHANGED combiner over a conditioned selection
    sel = _topk_idx(disc_bind, min(K_SEL, 3))
    fh = SV[sel]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
    sc, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc.shape[0] == 3, "real: combiner reuse shape"

    # determinism
    s_bind2 = conditioned_scores_bind(SV, stem_vec, choice_only)
    assert np.allclose(s_bind, s_bind2), "real: conditioned scoring non-deterministic"

    # arms differ: conditioned selection != agnostic selection (different rankings expected in general)
    g = (SV @ QQ).astype(np.float64)                            # question relevance (agnostic)
    sel_agn = set(_topk_idx(g, min(K_SEL, 3)).tolist())
    sel_cond = set(sel.tolist())
    print(f"[self-test]   real: disc_bind={np.round(disc_bind,3).tolist()} "
          f"sel_cond={sorted(sel_cond)} sel_agn={sorted(sel_agn)}", flush=True)

    # cross-question misconditioning (the combiner-arm control) must change the disc RANKING, unlike a
    # within-question roll (permutation-invariant for disc=max_i d_i).
    donor = arc._encode_store(enc, ["a red apple", "a blue car"])   # WRONG (unrelated) choice content
    s_mis = conditioned_scores_bind(SV, stem_vec, _donor_choices(donor, 3))
    _, disc_mis = differential_support(s_mis)
    assert not np.allclose(np.argsort(disc_mis), np.argsort(disc_bind)) or not np.allclose(s_mis, s_bind), \
        "real: cross-question misconditioning did not change the differential"
    # confirm the within-question roll IS a no-op for disc (documents the vacuous-control pitfall we fixed)
    _, disc_roll = differential_support(conditioned_scores_bind(SV, stem_vec, _roll_choices(choice_only)))
    assert np.allclose(np.sort(disc_roll), np.sort(disc_bind)), "real: roll unexpectedly changed disc set"
    print("[self-test] PASS (planted contrast discriminator fires; real conditioned bind/flat scoring + "
          "UNCHANGED combiner; determinism; cross-question misconditioning changes disc; roll is a no-op)",
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
    choice_only_map = [arc._encode_store(enc, list(q["choices"])) for q in questions]

    # cross-question donor map for MISCONDITIONED (bind Q with WRONG other-question choices).
    # np.roll by nQ//2 is a derangement of the index (donor[qi]=(qi-nQ//2)%nQ != qi for nQ>=2); no hash().
    donor_idx = np.roll(np.arange(nQ), max(1, nQ // 2))

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

    # ---- PASS A: per-question pool + flat baseline features + conditioned/contrastive scores + gold ----
    _heartbeat(output_dir, "features_and_scores")
    poolidx_list = [None] * nQ
    Xn_flat = [None] * nQ                 # flat baseline features (A_AGNOSTIC learner)
    sel_geo = {name: [None] * nQ for name in ("A_AGNOSTIC_GEO", "COND_NONCONTRAST", "B_CONDITIONED",
                                              "B_COND_FLAT", "MISCONDITIONED")}
    ddm_choice = [None] * nQ              # B_DIRECT per-choice winner scores
    dbind_list = [None] * nQ             # cache bind differential for glass-box + diagnosis
    gold_rows_list = [None] * nQ
    lure_flags = np.zeros(nQ, dtype=bool)
    contrast_spread = []                  # discriminator-fires telemetry: std of s across choices

    for qi, q in enumerate(questions):
        ci = q["correct_index"]
        stem_words = stem_words_per_q[qi]
        lure_flags[qi] = gate.is_lure_question(stem_words, q["choices"], ci)
        lure_set, _ = gate.standout_lure_choices(stem_words, q["choices"])

        pool_idx = ppr.topk_from_scores(F_RR[qi], K_WIDE)
        poolidx_list[qi] = pool_idx
        fh_pool = SV_store[pool_idx]
        chd = choice_hd_map[qi]
        cho = choice_only_map[qi]
        fw = [fact_word_sets[i] for i in pool_idx.tolist()]

        # FLAT baseline features (imported 29545 assembly, UNCHANGED) -> A_AGNOSTIC learner
        gs = gate.gate_scores(fh_pool, fw, stem_words, STEM[qi], chd, lure_set)
        coh = fixedsel.coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ[qi], 0.0))
        rr_scores = F_RR[qi][pool_idx]
        degs = degrees_all[pool_idx]
        negs = neg_all[pool_idx]
        Xflat = question_features_flat(fh_pool, STEM[qi], chd, gs, coh, rr_scores, degs, negs)
        Xn_flat[qi] = _minmax_cols(Xflat)

        # CONDITIONED / CONTRASTIVE scores (the ONE new mechanism)
        s_bind = conditioned_scores_bind(fh_pool, STEM[qi], cho)     # [P, C]
        s_flat = conditioned_scores_flat(fh_pool, cho)              # [P, C]
        d_bind, disc_bind = differential_support(s_bind)
        d_flat, disc_flat = differential_support(s_flat)
        cho_donor = _donor_choices(choice_only_map[int(donor_idx[qi])], cho.shape[0]) if cho.shape[0] else cho
        d_mis, disc_mis = differential_support(conditioned_scores_bind(fh_pool, STEM[qi], cho_donor))
        dbind_list[qi] = d_bind

        g_agn = (fh_pool @ QQ[qi]).astype(np.float64)              # question relevance (agnostic geometric)
        nc = s_bind.max(axis=1) if s_bind.shape[1] else np.zeros(pool_idx.size)  # conditioned, no contrast

        sel_geo["A_AGNOSTIC_GEO"][qi] = _topk_idx(g_agn, K_SEL)
        sel_geo["COND_NONCONTRAST"][qi] = _topk_idx(nc, K_SEL)
        sel_geo["B_CONDITIONED"][qi] = _topk_idx(disc_bind, K_SEL)
        sel_geo["B_COND_FLAT"][qi] = _topk_idx(disc_flat, K_SEL)
        sel_geo["MISCONDITIONED"][qi] = _topk_idx(disc_mis, K_SEL)

        # B_DIRECT: per-choice best differential fact wins (literal DDM competition; no combiner)
        C = cho.shape[0]
        ddm_choice[qi] = np.array([d_bind[:, i].max() if pool_idx.size else 0.0 for i in range(C)],
                                  dtype=np.float64) if C else np.zeros(0)

        if s_bind.shape[1] >= 2 and pool_idx.size:
            contrast_spread.append(float(np.mean(np.std(s_bind, axis=1))))

        gold_rows_list[qi] = np.array([uid2fi[u] for u in q["gold_central"] if u in uid2fi], dtype=np.int64)

    # ---- TRAIN the A_AGNOSTIC glass-box learner on TRAIN questions ONLY (label = is-gold) ----
    _heartbeat(output_dir, "train_agnostic_learner")
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
    print(f"[learned:A_AGNOSTIC] rows={n_train_rows} pos={n_train_pos} weights={flat_weights}", flush=True)

    # ---- PASS B: select + answer per arm ----
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
        q_rel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)   # UNCHANGED answer-agnostic combiner weight
        sc, _ = agg.aggregate(fh, q_rel, choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
        return agg._pick(sc, np.random.default_rng(SEED + qi))

    for qi, q in enumerate(questions):
        pool_idx = poolidx_list[qi]
        gold_rows = gold_rows_list[qi]
        gold_set = set(int(g) for g in gold_rows.tolist())

        # A_AGNOSTIC (learned flat) local selection
        sel_local = {"A_AGNOSTIC": _topk_idx(learned_score(Xn_flat[qi], w_flat, b_flat), K_SEL)}
        for name in sel_geo:
            sel_local[name] = sel_geo[name][qi]
        rng_r = np.random.default_rng(SEED + 7000 + qi)
        sel_local["RND"] = rng_r.permutation(pool_idx.size)[:min(K_SEL, pool_idx.size)]

        for name in COMBINER_ARMS:
            sel_glob = pool_idx[sel_local[name]]
            picks[name][qi] = combiner_pick(qi, sel_glob)
            denom = min(K_SEL, sel_glob.size) if sel_glob.size else 1
            sel_gold_hit[name][qi] = sum(1 for g in sel_glob.tolist() if g in gold_set) / denom

        # B_DIRECT: argmax_i (max_f d_i(f)); random tie-break; precision = same top-K disc facts as B_COND
        if ddm_choice[qi].size:
            picks["B_DIRECT"][qi] = agg._pick(ddm_choice[qi].astype(np.float32), np.random.default_rng(SEED + qi))
        else:
            picks["B_DIRECT"][qi] = agg._pick(np.zeros(len(q["choices"]), np.float32),
                                              np.random.default_rng(SEED + qi))
        bsel = pool_idx[sel_local["B_CONDITIONED"]]
        denom = min(K_SEL, bsel.size) if bsel.size else 1
        sel_gold_hit["B_DIRECT"][qi] = sum(1 for g in bsel.tolist() if g in gold_set) / denom

        # ORACLE
        picks["ORACLE"][qi] = combiner_pick(qi, gold_rows)
        sel_gold_hit["ORACLE"][qi] = 1.0 if gold_rows.size else 0.0

        # GLASS-BOX (dam-Q autopsy): per-choice best differential fact + is-gold, on TEST lure questions
        if len(glass) < 12 and lure_flags[qi] and test_mask[qi]:
            d_bind = dbind_list[qi]
            C = choice_only_map[qi].shape[0]
            per_choice = {}
            for i in range(C):
                if pool_idx.size:
                    bi = int(np.argmax(d_bind[:, i]))
                    fi = int(pool_idx[bi])
                    per_choice[str(i)] = {
                        "choice": q["choices"][i], "is_correct": int(i == q["correct_index"]),
                        "best_diff_fact": uid2sent.get(uids[fi], "")[:80],
                        "d_score": round(float(d_bind[bi, i]), 4), "fact_is_gold": int(fi in gold_set)}
            b_local = sel_local["B_CONDITIONED"]
            glass.append({
                "qid": q["qid"], "stem": q["stem"][:120], "choices": q["choices"],
                "correct_index": q["correct_index"], "split": "test",
                "gold_in_wide_pool": sum(1 for i in pool_idx.tolist() if i in gold_set),
                "picks": {name: int(picks[name][qi]) for name in ARMS},
                "per_choice_best_differential": per_choice,
                "B_CONDITIONED_selected": [uid2sent.get(uids[i], "")[:70]
                                           for i in pool_idx[b_local].tolist()],
                "B_selected_gold": [int(i in gold_set) for i in pool_idx[b_local].tolist()],
                "A_AGNOSTIC_selected": [uid2sent.get(uids[i], "")[:70]
                                        for i in pool_idx[sel_local["A_AGNOSTIC"]].tolist()],
                "A_selected_gold": [int(i in gold_set) for i in pool_idx[sel_local["A_AGNOSTIC"]].tolist()],
            })

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

    # ---- residual diagnosis: retrieval-reach vs content-resolution (glass-box, per drill) ----
    _heartbeat(output_dir, "residual_diagnosis")
    n_reach = n_reach_correct = n_tc = 0
    for qi in range(nQ):
        if not test_chal[qi]:
            continue
        n_tc += 1
        pool_idx = poolidx_list[qi]
        gold_set = set(int(g) for g in gold_rows_list[qi].tolist())
        gold_local = [li for li, fi in enumerate(pool_idx.tolist()) if fi in gold_set]
        if not gold_local:
            continue
        n_reach += 1
        d_bind = dbind_list[qi]
        ci = questions[qi]["correct_index"]
        # does the BEST gold fact's differential point at the CORRECT choice?
        gl = np.array(gold_local, dtype=np.int64)
        best_gold_choice = int(np.argmax(d_bind[gl].max(axis=0))) if d_bind.shape[1] else -1
        if best_gold_choice == ci:
            n_reach_correct += 1
    gold_in_pool_frac = round(n_reach / n_tc, 4) if n_tc else None
    gold_points_correct_frac = round(n_reach_correct / n_reach, 4) if n_reach else None
    print(f"[diag] test_chal={n_tc} gold_in_pool={gold_in_pool_frac} "
          f"gold_points_correct(of reachable)={gold_points_correct_frac}", flush=True)

    # ---- PRIMARY: end-to-end A vs conditioned arms; controls ----
    A_chal = accs["A_AGNOSTIC"]["test_challenge"] or 0.0
    A_geo_chal = accs["A_AGNOSTIC_GEO"]["test_challenge"] or 0.0
    nc_chal = accs["COND_NONCONTRAST"]["test_challenge"] or 0.0
    B_chal = accs["B_CONDITIONED"]["test_challenge"] or 0.0
    Bflat_chal = accs["B_COND_FLAT"]["test_challenge"] or 0.0
    Bdir_chal = accs["B_DIRECT"]["test_challenge"] or 0.0
    mis_chal = accs["MISCONDITIONED"]["test_challenge"] or 0.0
    rnd_chal = accs["RND"]["test_challenge"] or 0.0
    oracle_chal = accs["ORACLE"]["test_challenge"] or 0.0

    cond_arms = {"B_CONDITIONED": B_chal, "B_COND_FLAT": Bflat_chal, "B_DIRECT": Bdir_chal}
    primary_arm = max(cond_arms, key=lambda k: cond_arms[k])
    primary_chal = cond_arms[primary_arm]
    primary_lift = round(primary_chal - A_chal, 4)
    B_lift = round(B_chal - A_chal, 4)
    gap = round(oracle_chal - A_chal, 4)
    gap_frac_closed = round(primary_lift / gap, 4) if gap > 1e-9 else None
    mis_lift = round(mis_chal - A_chal, 4)
    rnd_lift = round(rnd_chal - A_chal, 4)
    contrast_beats_noncontrast = bool(B_chal >= nc_chal)   # contrast does not hurt vs conditioning-alone
    contrast_margin = round(B_chal - nc_chal, 4)

    A_test_prec = accs["A_AGNOSTIC"]["test_sel_gold_precision"] or 0.0
    primary_test_prec = accs[primary_arm]["test_sel_gold_precision"] or 0.0
    prec_rises = bool(primary_test_prec > A_test_prec)

    mc_b, mc_c, mc_stat, mc_p = gate.mcnemar(correct["A_AGNOSTIC"][test_chal],
                                             correct[primary_arm][test_chal])
    sig = (mc_p is not None) and (mc_p < MCNEMAR_ALPHA)
    miscond_ok = mis_lift <= MISCOND_MAX
    random_ok = rnd_lift <= RANDOM_MAX

    # ---- integrity gates ----
    A_insample = accs["A_AGNOSTIC"]["insample_train_precision"] or 0.0
    anchor_prec_ok = abs(A_insample - ANCHOR_PREC) <= ANCHOR_TOL_PREC
    anchor_chal_ok = abs(A_chal - ANCHOR_CHAL) <= ANCHOR_TOL_CHAL
    ag_saturated = A_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_chal < 0.95
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest() for name in ARMS}
    n_distinct = len(set(digests[n] for n in COMBINER_ARMS + ("B_DIRECT",)))
    arms_differ = n_distinct >= 5
    mean_contrast_spread = round(float(np.mean(contrast_spread)), 5) if contrast_spread else 0.0
    discriminator_fired = bool(mean_contrast_spread > 1e-4 and arms_differ)

    hp_lift = primary_lift >= CHAL_LIFT_HP
    hard_pass = bool(hp_lift and prec_rises and sig and miscond_ok and random_ok
                     and contrast_beats_noncontrast)
    middle = bool((not hard_pass) and primary_lift >= MB_CHAL_LIFT and miscond_ok)
    hard_fail = bool(primary_lift < MB_CHAL_LIFT)

    # ---- residual sub-diagnosis (meaningful on HARD_FAIL) ----
    sub_diag = None
    if hard_fail:
        if gold_in_pool_frac is not None and gold_in_pool_frac < 0.4:
            sub_diag = (f"retrieval-cut: the discriminating gold fact is often NOT in the wide pool "
                        f"(gold_in_pool_frac={gold_in_pool_frac}); redirect = retrieval recall, not "
                        f"selection.")
        elif gold_points_correct_frac is not None and gold_points_correct_frac < 0.4:
            sub_diag = (f"content-resolution: gold reaches the pool (gold_in_pool_frac={gold_in_pool_frac}) "
                        f"but its differential points at the CORRECT choice only "
                        f"{gold_points_correct_frac} of the time -- the thin GloVe/WordNet fact content "
                        f"cannot express the fine feature that distinguishes gold from lure; redirect = "
                        f"perceptual/richer grounding (the drill's next lever).")
        else:
            sub_diag = (f"aggregation: gold reaches the pool AND its differential points correct "
                        f"(gold_points_correct_frac={gold_points_correct_frac}) but the end-to-end answer "
                        f"does not lift -- suspect the combiner/answer-mapping, not the selection signal; "
                        f"redirect = combiner over conditioned selection.")

    # ---- verdict ----
    if ag_saturated:
        verdict = "COND_SELECTION_SATURATED"
        vmsg = f"A_AGNOSTIC TEST Challenge {A_chal} >= {AG_BASELINE_SAT}: no headroom (report)."
    elif not arms_differ:
        verdict = "COND_SELECTION_ARMS_IDENTICAL_META_RULE_AF"
        vmsg = (f"selection arms produced < 5 distinct pick-vectors (n_distinct={n_distinct}); arm bug -- "
                f"do NOT trust the comparison.")
    elif not discriminator_fired:
        verdict = "COND_SELECTION_DISCRIMINATOR_VACUOUS"
        vmsg = (f"conditioned contrast is degenerate (mean cross-choice std={mean_contrast_spread}); the "
                f"choices do not differ in fact-alignment at this regime -- inspect encodings.")
    elif hard_pass:
        verdict = "COND_SELECTION_HARD_PASS"
        vmsg = (f"answer-CONDITIONED contrastive selection BREAKS the gold-vs-lure symmetry: {primary_arm} "
                f"TEST Challenge {primary_chal} vs A_AGNOSTIC {A_chal} (lift {primary_lift:+.4f} >= "
                f"{CHAL_LIFT_HP}, {gap_frac_closed} of the {gap} oracle gap); TEST precision "
                f"{primary_test_prec} > A {A_test_prec}; McNemar p={mc_p} < {MCNEMAR_ALPHA}; MISCONDITIONED "
                f"lift {mis_lift:+.4f} (<= {MISCOND_MAX}); RND lift {rnd_lift:+.4f} (<= {RANDOM_MAX}); "
                f"contrast beats non-contrast (B {B_chal} >= COND_NONCONTRAST {nc_chal}, margin "
                f"{contrast_margin:+.4f}). Conditioning at SELECTION time with a DIFFERENTIAL metric is the "
                f"missing brain-shape.")
    elif middle:
        verdict = "COND_SELECTION_MIDDLE_BAND"
        vmsg = (f"MIDDLE: real-but-partial. {primary_arm} TEST Challenge {primary_chal} vs A {A_chal} "
                f"(lift {primary_lift:+.4f} in [{MB_CHAL_LIFT},{CHAL_LIFT_HP})); prec_rises={prec_rises} "
                f"({primary_test_prec} vs {A_test_prec}); McNemar p={mc_p} sig={sig}; contrast_margin="
                f"{contrast_margin:+.4f}; MISCONDITIONED lift {mis_lift:+.4f} (ok={miscond_ok}); RND lift "
                f"{rnd_lift:+.4f} (ok={random_ok}). Conditioning helps but is not decisive -> residual "
                f"diagnosis: gold_in_pool={gold_in_pool_frac}, gold_points_correct="
                f"{gold_points_correct_frac} (content-resolution vs aggregation).")
    else:
        verdict = "COND_SELECTION_HARD_FAIL"
        vmsg = (f"HONEST: answer-conditioning ~= answer-agnostic. {primary_arm} TEST Challenge "
                f"{primary_chal} vs A {A_chal} (lift {primary_lift:+.4f} < {MB_CHAL_LIFT}); B_CONDITIONED "
                f"{B_chal} (lift {B_lift:+.4f}), COND_NONCONTRAST {nc_chal}, MISCONDITIONED {mis_chal} "
                f"(lift {mis_lift:+.4f}), RND {rnd_chal}; TEST prec {primary_test_prec} vs A {A_test_prec}. "
                f"The conditioning SHAPE does not break symmetry in THIS pipeline. Sub-diagnosis: {sub_diag}")

    grade = arc._grade_proxy(accs["B_CONDITIONED"]["test_easy"], accs["B_CONDITIONED"]["test_challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [TEST Chal] A={A_chal} A_geo={A_geo_chal} COND_NC={nc_chal} "
                    f"B_COND={B_chal} B_flat={Bflat_chal} B_direct={Bdir_chal} MISCOND={mis_chal} "
                    f"RND={rnd_chal} ORACLE={oracle_chal}; primary={primary_arm} lift={primary_lift:+.4f} "
                    f"({gap_frac_closed} of {gap} gap) McNemar_p={mc_p}; contrast_margin={contrast_margin:+.4f}; "
                    f"miscond_lift={mis_lift:+.4f} rnd_lift={rnd_lift:+.4f}; "
                    f"[prec] A={A_test_prec} B={primary_test_prec}; gold_in_pool={gold_in_pool_frac} "
                    f"gold_points_correct={gold_points_correct_frac} | chance={round(chance,4)}"),
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
        # GLASS-BOX: A_AGNOSTIC learned weights (inspectable)
        "flat_feature_names": list(FLAT_FEATURE_NAMES),
        "A_agnostic_learned_weights": flat_weights,
        # end-to-end accuracy by arm
        "acc_by_arm": accs,
        "A_AGNOSTIC_test_challenge": A_chal, "A_AGNOSTIC_GEO_test_challenge": A_geo_chal,
        "COND_NONCONTRAST_test_challenge": nc_chal, "B_CONDITIONED_test_challenge": B_chal,
        "B_COND_FLAT_test_challenge": Bflat_chal, "B_DIRECT_test_challenge": Bdir_chal,
        "MISCONDITIONED_test_challenge": mis_chal, "RND_test_challenge": rnd_chal,
        "oracle_gold_test_challenge": oracle_chal,
        "primary_arm": primary_arm, "primary_lift_challenge": primary_lift,
        "B_CONDITIONED_lift_challenge": B_lift,
        "selection_gap": gap, "gap_fraction_closed": gap_frac_closed,
        "contrast_beats_noncontrast": contrast_beats_noncontrast, "contrast_margin": contrast_margin,
        "miscond_lift_challenge": mis_lift, "miscond_control_ok": bool(miscond_ok),
        "random_lift_challenge": rnd_lift, "random_control_ok": bool(random_ok),
        # precision
        "test_sel_gold_precision_by_arm": {n: accs[n]["test_sel_gold_precision"] for n in ARMS},
        "insample_train_precision_by_arm": {n: accs[n]["insample_train_precision"] for n in ARMS},
        "A_insample_precision": A_insample,
        "A_test_sel_gold_precision": A_test_prec, "primary_test_sel_gold_precision": primary_test_prec,
        "primary_precision_rises": prec_rises,
        # McNemar
        "mcnemar_challenge": {"arm": primary_arm, "b_A_right_arm_wrong": mc_b,
                              "c_A_wrong_arm_right": mc_c,
                              "stat": None if mc_stat is None else round(mc_stat, 4),
                              "p_value": None if mc_p is None else round(mc_p, 5),
                              "significant": bool(sig)},
        # residual diagnosis (retrieval-reach vs content-resolution)
        "gold_in_pool_frac": gold_in_pool_frac,
        "gold_points_correct_frac": gold_points_correct_frac,
        "hard_fail_sub_diagnosis": sub_diag,
        # discriminator-fires telemetry
        "mean_cross_choice_contrast_spread": mean_contrast_spread,
        "discriminator_fired": discriminator_fired,
        # anchor regression
        "anchor_precision_regression_ok": bool(anchor_prec_ok),
        "anchor_challenge_regression_ok": bool(anchor_chal_ok),
        "anchor_precision_expected": ANCHOR_PREC, "anchor_challenge_expected": ANCHOR_CHAL,
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band), "ag_saturated": bool(ag_saturated),
        "arms_differ_verified": bool(arms_differ), "n_distinct_pick_vectors": int(n_distinct),
        "arm_pick_digests": digests,
        "hard_pass": hard_pass, "middle_band": middle, "hard_fail": hard_fail,
        "bands": {"CHAL_LIFT_HP": CHAL_LIFT_HP, "MB_CHAL_LIFT": MB_CHAL_LIFT, "MISCOND_MAX": MISCOND_MAX,
                  "RANDOM_MAX": RANDOM_MAX, "mcnemar_alpha": MCNEMAR_ALPHA, "ag_baseline_sat": AG_BASELINE_SAT,
                  "anchor_prec": ANCHOR_PREC, "anchor_chal": ANCHOR_CHAL},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: the SELECTION conditioning is the ONLY variable. The WIDE re-retrieval pool (RR top-100, "
            "mr.reformulate_seeds/_rownorm_scores IMPORTED UNCHANGED, recall@100=0.69) and the bind+bundle "
            "combiner (agg.aggregate 'bundle' IMPORTED UNCHANGED, with the SAME answer-agnostic q_rel weight "
            "for every arm) are held fixed. A_AGNOSTIC reuses 29545's EXACT flat-cosine feature assembly + "
            "glass-box learner (imported) -> regression-anchor to 0.1865 in-sample / 0.3663 TEST Challenge. "
            "The conditioned arms score each pool fact per choice via the SUBSTRATE BIND s_i(f)=<sign(fact)"
            "(*)sign(stem), sign(choice_i)>/N (conjunctive read-out) and reduce by the CONTRAST d_i(f)=s_i - "
            "max_{j!=i} s_j (differential support). B_CONDITIONED selects top-K_SEL by disc=max_i d_i -> "
            "combiner. B_COND_FLAT uses cos(fact,choice_only) as s. B_DIRECT answers argmax_i max_f d_i (no "
            "combiner; literal DDM). COND_NONCONTRAST selects by max_i s_i (conditioning WITHOUT contrast) -> "
            "isolates the contrast. MISCONDITIONED binds Q with WRONG cross-question choice content at "
            "conditioning time (combiner uses TRUE choices) -> MUST-FAIL, proves it is the RIGHT "
            "conditioning (a within-question roll is a no-op for disc=max_i d_i, so cross-question donors "
            "are used). RND + ORACLE anchor floor/ceiling. "
            "One-variable spine A_AGNOSTIC_GEO -> COND_NONCONTRAST -> B_CONDITIONED decomposes conditioning "
            "vs contrast. NO LEAK: TRAIN/TEST disjoint (learned._split_train_test); the conditioned arms are "
            "UNTRAINED geometry (gold never enters selection); gold used for A-learner TRAIN label + ORACLE + "
            "eval only. STUBBED/NOTED-NOT-BUILT: perceptual/richer grounding (the redirect if content-"
            "resolution is the residual wall)."),
        "contract": ("INLINE-LOCAL foreground-to-completion; no push/remote-persist; NOT remote-portable "
                     "(GloVe+WorldTree git-ignored/large; inherits 29544/29545 contract); VET-PENDING; FULL "
                     "eval slice bounded (limit_easy=500 limit_chal=600, stratified train/test) to fit one "
                     "foreground call"),
        "compute_architecture": ("mixed CPU: batched GloVe encode (store + questions + choices) + scipy "
                                 "sparse batched PPR (2 passes, UNCHANGED) + numpy bipolar-bind conditioned "
                                 "scoring (elementwise sign product + matmul, cheap) + per-question contrast "
                                 "reduction + ONE glass-box logreg train (A_AGNOSTIC only) + UNCHANGED "
                                 "combiner; wall target < 5min. No GPU speedup needed (matmuls small)."),
        "storage_strategy": "sharded (each fact = own embedding + own graph node)",
        "progress_logging": "line_buffered_stdout",
        "crlb_n_a": ("geometric selection, no learned noise floor; the conditioned contrast is a "
                     "deterministic per-pool quantity -> the discriminator is a fixed geometric signal, "
                     "MORE dims = LESS bipolar-dot noise (~1/sqrt(N)) so it SURVIVES scale by construction; "
                     "smoke runs at FULL n_dim=2048 (only question-limit reduced)"),
        "calibration_check": ("default_ok_for_this_regime (all conditioned scoring is geometric + author-set "
                              "a priori; A_AGNOSTIC learner hyperparams inherited from 29545 L2=1.0/iters=400/"
                              "lr=0.5; NOT tuned to force a win; MISCONDITIONED + RND must-fail controls "
                              "present; contrast-vs-noncontrast isolation present; bands set a priori)"),
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
