"""arc_combiner_confidence_gated_escalation_v1 -- reasoning-side ROBUSTNESS to imperfect facts.

The brain's confidence-gated, bounded ESCALATION LOOP wrapped around the UNCHANGED bind+settle (CI)
combiner. bind+settle scores ~0.690 ARC-Challenge on GOLD facts but ~0.341 on the best real
retrieved+selected pool (Director-supplied, HYPOTHESIZED@task -- MEASURED in-cell here). Retrieval is
recall-capped, so REASONING must become robust to imperfect facts. ONE variable = the escalation loop;
pool + selection gate + CI settle are UNCHANGED.

Loop (per question): run settle once -> GATE (margin >= conformal tau ? COMMIT) -> else escalate:
BRIDGE-if-premises-present (khop.traverse over a per-question mini-KG) OR DISCOUNTED gap-fill (inject a
plausible missing store fact at LOWER activation) -> re-settle ONCE -> else abstain / low-conf guess.

Primitives wired (both VERIFIED-ON-DISK):
- BRIDGING = substrate/khop.py traverse (FHRR unbind+cleanup; Merkle AuditChain) via NAMED adapter
  _pool_to_mini_kg (self-tested).
- CONFIDENCE GATE = conformal_tau (experiments/_substrate_refuse_gate_v8_conformal_v1_core.py):
  tau = alpha-quantile of settle-margins of CORRECTLY-answered CALIBRATION questions.

ARMS (settle mechanics identical; judged on the ANSWER):
  A baseline        -- selected pool -> settle once -> argmax (== the ~0.341 condition)
  B abstain_only    -- settle; if margin<tau ABSTAIN (value of knowing-when-not-to-guess)
  C bridge          -- on margin<tau: ONE khop bridge pass -> add fact -> re-settle -> argmax
  F bridge_random   -- MUST-FAIL: random in-pool pair bridged (must NOT beat A)
  D gapfill_disc    -- on margin<tau: inject top goal-relevant store fact at DISCOUNTED weight -> re-settle
  E gapfill_undisc  -- MUST-FAIL: identical to D but FULL weight (prediction: MORE confident-wrong => WORSE)
  G combined        -- gate; bridge-else-discounted-gapfill; terminal = low-conf guess; ONE escalation
  O oracle_gold     -- CONTEXT ceiling: gold central facts -> settle (~0.690)

Gap-fill source = the WorldTree tablestore (STORE), selected by ANSWER-AGNOSTIC goal_score (NEVER gold).
PRIMARY = end-to-end ARC accuracy on the TEST split, Easy + Challenge (esp Challenge); HARD-PASS = G
closes >= 20% of the IN-CELL Challenge gap (>= 0.02 absolute) on >= 2 seeds, random-bridge does NOT help,
undiscounted gap-fill is WORSE than discounted. Glass-box: escalation path per question + khop audit roots.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; NOT remote-portable
(GloVe+WorldTree git-ignored/large); ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted
iteration, no hash()); repo .venv; VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + PPR pool + selection + UNCHANGED settle +
#   khop.traverse (planted 2-hop bridge recovers a connecting concept) + conformal_tau; arms-differ
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration + stratified CAL split
#   by sorted-index modulus; no hash()
# - baseline_in_band + AG-guard on A challenge (headroom vs the O gold ceiling)
# - storage = SHARDED (each fact = own vector; each mini-KG concept = own FHRR codebook vector)
# - calibration_check = adaptive_with_discriminator_gate (conformal tau; escalation-fires check logged)
# - multi-seed smoke variance probe on A/D/E/G
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
import hashlib
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# UNCHANGED reuse: PPR pool, selection gate, CI settle combiner, arc helpers, semantic encoder
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as sel
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)
# CONFIDENCE GATE primitive (VERIFIED-ON-DISK)
from experiments._substrate_refuse_gate_v8_conformal_v1_core import conformal_tau
# BRIDGING primitive (VERIFIED-ON-DISK)
from substrate import khop

ANCHOR_NAME = "arc_combiner_confidence_gated_escalation_v1"

# ---- escalation-loop hyperparams (author-designed a priori; see pre-reg; NOT tuned to force a win) ----
K_POOL = sel.K_POOL          # UNCHANGED spreading pool (20)
K_SEL = sel.K_SEL            # UNCHANGED selection width (4)
ALPHA_GATE = 0.30            # conformal alpha: tau = 30th-pctile of correct-CAL margins (escalate low tail)
GAPFILL_DISCOUNT = 0.30      # discounted gap-fill injection weight = 0.30 * fact's natural relevance
BRIDGE_HOPS = 2              # khop bridge hop-cap
BRIDGE_CONF_MIN = 0.10       # min khop cleanup confidence to accept a bridged path
ESCALATION_BUDGET = 1        # bounded: ONE escalation attempt (SAM/REM stopping-rule precedent)
CAL_EVERY = 3               # stratified calibration split: every 3rd (by sorted pos) within each split -> CAL
SETTLE_MODE = "settle"       # the UNCHANGED CI bind+settle combiner (agg.aggregate)

# pool-construction constants (reused UNCHANGED)
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# ---- bands (author-designed a priori; PRIMARY = end-to-end Challenge on TEST split) ----
GAP_FRAC_HP = 0.20           # G closes >= 20% of the in-cell Challenge gap
GAP_FRAC_MB = 0.05           # MIDDLE band lower edge
ABS_G_MIN = 0.02             # absolute floor: G - A on Challenge
DISCOUNT_CW_MARGIN = 0.01    # E_confident_wrong - D_confident_wrong >= this (undiscounted MORE confident-wrong)
DISCOUNT_ACC_EPS = 0.005     # D_acc >= E_acc - this (discount does not hurt accuracy)
BRIDGE_RANDOM_MAX = 0.02     # F_chal - A_chal <= this (random-bridge does NOT help)
GAP_MIN_HEADROOM = 0.03      # gap < this -> INCONCLUSIVE (no headroom)
AG_BASELINE_SAT = 0.95       # A_chal >= this -> vacuous

FULL_SEEDS = [20260724, 20260725]
PROBE_SEEDS = [20260724, 20260725, 20260726]

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
# settle + confidence (UNCHANGED combiner; margin = confidence signal)
# ---------------------------------------------------------------------------
def settle_scores(fact_hd, q_rel, choice_hd):
    """UNCHANGED CI bind+settle DECISION scores. Returns (scores[C], margin, info). margin kept for
    diagnostics only -- it saturates to 1.0 (winner-take-all choice inhibition) and is NOT used as the
    gate confidence signal; see conf_signal()."""
    scores, info = agg.aggregate(fact_hd, q_rel, choice_hd, SETTLE_MODE, rng=np.random.default_rng(0))
    if scores.shape[0] >= 2:
        s = np.sort(scores.astype(np.float64))
        margin = float(s[-1] - s[-2])
    else:
        margin = float(scores.max()) if scores.shape[0] else 0.0
    return scores, margin, info


def conf_signal(fact_hd, q_rel, choice_hd):
    """GRADED confidence signal for the gate = separation of the relevance-weighted bundle choice-support
    (continuous in [-2,2]). The CI settle's own post-inhibition margin saturates to 1.0 (winner-take-all),
    unusable for a calibrated conformal gate; the bundle-support separation measures how far the facts
    push the top choice above the runner-up WITHOUT the winner-take-all collapse. Answer-agnostic; the CI
    settle remains UNCHANGED and still makes the DECISION. Higher = more confident."""
    b, _ = agg.aggregate(fact_hd, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    if b.shape[0] >= 2:
        s = np.sort(b.astype(np.float64))
        return float(s[-1] - s[-2])
    return float(b.max()) if b.shape[0] else 0.0


def _pick(scores, seed):
    return agg._pick(scores, np.random.default_rng(seed))


# ---------------------------------------------------------------------------
# BRIDGING: pool -> mini-KG adapter + khop.traverse (VERIFIED primitive)
# ---------------------------------------------------------------------------
def _cphasor_codebook(names, dim, rng):
    """FHRR unit-phasor codebook (khop format): name -> complex64 vector."""
    out = {}
    for n in sorted(names):
        ang = (rng.random(dim) * 2.0 - 1.0) * math.pi
        out[n] = np.exp(1j * ang).astype(np.complex64)
    return out


def _pool_to_mini_kg(fact_word_lists, dim, rng):
    """NAMED adapter (SHAPE_MISMATCH_adapter): build a per-question FHRR mini-KG from pool-fact content
    words. Entities = content words; ONE generic 'RELATES' relation; subject_memory[w_i] bundles
    bind(RELATES, w_j) for every co-occurring word w_j in the SAME fact -> co-occurrence chains so a
    khop 2-hop traverse recovers a transitive connecting concept. Returns (ents, rels, subject_memory)."""
    vocab = sorted({w for wl in fact_word_lists for w in wl})
    ents = _cphasor_codebook(vocab, dim, rng)
    rels = _cphasor_codebook(["RELATES"], dim, rng)
    r_v = rels["RELATES"]
    subject_memory = {}
    for wl in fact_word_lists:
        uniq = sorted(set(wl))
        for wi in uniq:
            for wj in uniq:
                if wi == wj:
                    continue
                contrib = r_v * ents[wj]
                subject_memory[wi] = subject_memory[wi] + contrib if wi in subject_memory else contrib
    return ents, rels, subject_memory


def _bridge_khop(fact_word_lists, stem_words, choice_word_sets, dim, rng):
    """khop bridge: build mini-KG from pool facts; traverse BRIDGE_HOPS from a stem-anchored entity; accept
    if the final concept is choice-relevant with cleanup confidence >= BRIDGE_CONF_MIN. Returns
    (bridge_sentence or None, audit_root or None, fired: bool). Uses substrate.khop.traverse UNCHANGED."""
    ents, rels, subject_memory = _pool_to_mini_kg(fact_word_lists, dim, rng)
    if not subject_memory:
        return None, None, False
    choice_words = set().union(*choice_word_sets) if choice_word_sets else set()
    starts = sorted([w for w in stem_words if w in subject_memory])
    if not starts:
        starts = sorted(subject_memory.keys())
    for start in starts:
        res = khop.traverse(start_entity=start, relation_path=["RELATES"] * BRIDGE_HOPS,
                            ent_codebook=ents, rel_codebook=rels, subject_memory=subject_memory,
                            query_id=f"bridge_{start}", top_k=3)
        final = res.final_entity
        if final is None or res.final_confidence < BRIDGE_CONF_MIN:
            continue
        # bridged fact must CONNECT to a choice (the missing link the settle lacked)
        pivot = res.hops[0].to_entity if res.hops else final
        if final in choice_words and final != start:
            sent = f"{start} {pivot} {final}"
            return sent, res.audit_chain.root, True
    return None, None, False


def _bridge_random(fact_sentences, rng):
    """MUST-FAIL control: compose a RANDOM pair of in-pool facts into a bridged sentence (no khop typing)."""
    n = len(fact_sentences)
    if n < 2:
        return None, False
    i, j = rng.choice(n, size=2, replace=False)
    sent = fact_sentences[int(i)] + " " + fact_sentences[int(j)]
    return sent, True


# ---------------------------------------------------------------------------
# self-test: real code path + planted bridge/discount discriminators + arms-differ + determinism
# ---------------------------------------------------------------------------
def _planted_khop_bridge_recovers_connection():
    """Planted mini-KG where a 2-hop traverse recovers a connecting concept absent from any single fact.
    facts: 'sunlight energy' , 'energy sugar'  -> pivot 'energy' bridges stem-word 'sunlight' to
    choice-word 'sugar'. Proves _pool_to_mini_kg + khop.traverse recover the transitive link."""
    dim = 512
    rng = np.random.default_rng(3)
    fact_word_lists = [["sunlight", "energy"], ["energy", "sugar"]]
    stem_words = {"sunlight"}
    choice_word_sets = [{"sugar"}, {"metal"}]
    sent, root, fired = _bridge_khop(fact_word_lists, stem_words, choice_word_sets, dim, rng)
    assert fired, "planted: khop bridge did not fire on a clean 2-hop chain"
    assert "sugar" in sent, f"planted: bridged sentence missing the connecting concept: {sent!r}"
    assert root is not None, "planted: missing khop AuditChain root"
    return True


def _planted_discount_reduces_confident_wrong():
    """Planted HD case: ONE weak correct pool fact; a plausible (NON-contradictory) but MISLEADING
    gap-fill fact supporting the WRONG choice at higher top-down relevance. At FULL weight the settle
    flips to the wrong choice (confident-wrong); at DISCOUNTED weight its pull is attenuated so the
    correct choice survives. The gap-fill is near-orthogonal to the pool fact so the CI settle's own
    contradiction handling does NOT already suppress it -- isolating the confidence-discount as the
    load-bearing variable under the UNCHANGED settle."""
    N = 512
    rng = np.random.default_rng(7)

    def orth(v, *against):
        for a in against:
            v = v - v.dot(a) * a
        return v / np.linalg.norm(v)

    def mk(v):
        return (v / np.linalg.norm(v)).astype(np.float32)

    t_dir = orth(rng.standard_normal(N))                    # correct choice
    w_dir = orth(rng.standard_normal(N), t_dir)             # wrong choice (orthogonal to correct)
    s_dir = orth(rng.standard_normal(N), t_dir, w_dir)      # shared TOPIC direction (fact-fact coherence)
    choice_hd = np.stack([t_dir, w_dir]).astype(np.float32)
    QQ = mk(t_dir + w_dir)
    # pool: ONE weak-correct fact carrying the shared topic (so injected facts cohere, not degenerate)
    f1 = mk(0.6 * t_dir + 0.6 * s_dir)
    pool = f1[None, :].astype(np.float32)
    q_rel = np.maximum(pool @ QQ, 0.0).astype(np.float32)
    # plausible but misleading gap-fill: supports the WRONG choice, coheres via topic, HIGHER relevance
    gf = mk(0.85 * w_dir + 0.55 * s_dir)
    gf_relnat = float(max(gf @ QQ, 0.0))

    base_scores, base_margin, _ = settle_scores(pool, q_rel, choice_hd)
    assert int(np.argmax(base_scores)) == 0, (
        f"planted: baseline should be correct pre-injection, got {int(np.argmax(base_scores))}")

    pu = np.vstack([pool, gf[None, :]])
    qu = np.concatenate([q_rel, np.array([gf_relnat], np.float32)])
    su, _, _ = settle_scores(pu, qu, choice_hd)
    pick_u = int(np.argmax(su))

    qd = np.concatenate([q_rel, np.array([GAPFILL_DISCOUNT * gf_relnat], np.float32)])
    sd, _, _ = settle_scores(pu, qd, choice_hd)
    pick_d = int(np.argmax(sd))

    assert pick_u == 1, f"planted: undiscounted gap-fill should flip to wrong, got {pick_u}"
    assert pick_d == 0, f"planted: discounted gap-fill should preserve the correct choice, got {pick_d}"
    return True


def self_test():
    print("[self-test] planted khop 2-hop bridge recovers a connecting concept ...", flush=True)
    _planted_khop_bridge_recovers_connection()
    print("[self-test] planted discount reduces confident-wrong under UNCHANGED settle ...", flush=True)
    _planted_discount_reduces_confident_wrong()

    # substrate-signature binds (base/portable kwargs only)
    import inspect
    inspect.signature(agg.aggregate).bind(np.zeros((1, 4), np.float32), np.zeros(1, np.float32),
                                          np.zeros((2, 4), np.float32), "settle", rng=None)
    inspect.signature(khop.traverse).bind(start_entity="a", relation_path=["RELATES"],
                                          ent_codebook={}, rel_codebook={}, subject_memory={})
    inspect.signature(conformal_tau).bind(np.zeros(3), 0.3)

    print("[self-test] REAL encoder + PPR pool + selection + UNCHANGED settle + conformal tau ...", flush=True)
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=20260724, use_wordnet=True, kv=kv)

    store_sents = [
        "green plants use sunlight to make sugar during photosynthesis",
        "photosynthesis produces oxygen as a byproduct for animals to breathe",
        "sunlight is a source of energy for plants",
        "energy from sunlight is stored as sugar in plants",
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

    q = {"stem": "What do green plants make using energy from sunlight?",
         "choices": ["iron metal", "sugar and oxygen", "the moon", "loud sound"], "correct_index": 1}
    stem_words = set(arc._content_words(q["stem"], MIN_TERM_LEN))
    q_words = sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
    q_word_vecs = arc._encode_store(enc, q_words)
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    STEM = arc._encode_store(enc, [q["stem"]])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
    choice_word_sets = [set(arc._content_words(c, MIN_TERM_LEN)) for c in q["choices"]]

    seeds = ppr.link_seeds([q_words], vocab, t2i, term_vecs, [q_word_vecs], SEED_COS)
    seed_mat = ppr.seeds_to_matrix(seeds, len(vocab))
    a = ppr.ppr_batch(seed_mat, M, HOPS, DAMP)
    fscore = ppr.fact_activation(a, Sft)[0]
    pool_idx = ppr.topk_from_scores(fscore, min(K_POOL, len(store_sents)))
    assert pool_idx.size > 0, "real: empty spreading pool"

    # UNCHANGED selection gate -> selected pool
    lure_set, _ = sel.standout_lure_choices(stem_words, q["choices"])
    fw = [fact_word_sets[i] for i in pool_idx]
    gs = sel.gate_scores(SV_store[pool_idx], fw, stem_words, STEM, choice_hd, lure_set)
    sel_local = sel._topk_idx(gs["gate"], K_SEL)
    sel_idx = pool_idx[sel_local]
    fh = SV_store[sel_idx]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)

    # UNCHANGED settle (decision) + GRADED conf signal (gate)
    scores, margin, info = settle_scores(fh, q_rel, choice_hd)
    conf = conf_signal(fh, q_rel, choice_hd)
    assert scores.shape[0] == len(q["choices"]), "real: settle shape mismatch"
    assert np.isfinite(conf), "real: conf signal not finite"

    # conformal tau on a tiny synthetic correct-conf calibration set
    tau = conformal_tau(np.array([conf, conf + 0.1, conf + 0.2]), ALPHA_GATE)
    assert np.isfinite(tau), "real: conformal tau not finite"

    # real khop bridge over the REAL selected pool (fires or honestly returns inert)
    sel_word_lists = [list(fact_word_sets[i]) for i in sel_idx]
    b_sent, b_root, b_fired = _bridge_khop(sel_word_lists, stem_words, choice_word_sets, nd,
                                           np.random.default_rng(20260724))
    # determinism of the settle margin
    _, margin2, _ = settle_scores(fh, q_rel, choice_hd)
    assert abs(margin - margin2) < 1e-9, "real: settle non-deterministic"

    print(f"[self-test] PASS (planted khop bridge + planted discount; real encoder+PPR+selection+"
          f"UNCHANGED settle conf={conf:.4f} tau={tau:.4f}; real bridge fired={b_fired})", flush=True)
    return True


# ---------------------------------------------------------------------------
# calibration split (deterministic, stratified, NO hash())
# ---------------------------------------------------------------------------
def _split_cal_test(questions):
    """Stratified CAL/TEST: within each of {easy, chal}, every CAL_EVERY-th (by sorted position) -> CAL.
    Deterministic (questions pre-sorted by qid); NO hash(), NO list(set())."""
    is_cal = np.zeros(len(questions), dtype=bool)
    pos_e = pos_c = 0
    for i, q in enumerate(questions):
        if q["source"].startswith("ARC-Easy"):
            if pos_e % CAL_EVERY == 0:
                is_cal[i] = True
            pos_e += 1
        else:
            if pos_c % CAL_EVERY == 0:
                is_cal[i] = True
            pos_c += 1
    return is_cal


# ---------------------------------------------------------------------------
# one seed: encode -> pool -> selection -> calibrate -> arms
# ---------------------------------------------------------------------------
def run_seed(seed, cfg, output_dir, tag):
    nd = cfg["n_dim"]
    _heartbeat(output_dir, f"{tag}:load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=nd, seed=seed, use_wordnet=True, kv=kv)

    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    is_cal = _split_cal_test(questions)
    nQ = len(questions)

    # store = FULL tablestore (closed-book curriculum; gold facts are curriculum sentences, not labels)
    uid2sent = agg.parse_tablestore()
    uids = sorted(uid2sent.keys())
    sents = [uid2sent[u] for u in uids]
    uid2fi = {u: i for i, u in enumerate(uids)}
    nFacts = len(uids)
    _heartbeat(output_dir, f"{tag}:store", {"n_facts": nFacts, "nQ": nQ})

    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in sents]
    fact_word_sets = [set(t) for t in fact_terms]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = ppr.build_incidence(fact_terms, vocab)
    nTerms = len(vocab)
    M, Sft, idf = ppr.build_transition(A, df, use_idf=True)

    _heartbeat(output_dir, f"{tag}:encode_store", {"n": nFacts})
    t_enc = time.perf_counter()
    SV_store = arc._encode_store(enc, sents)
    print(f"[{tag}] encode store {nFacts} facts in {time.perf_counter()-t_enc:.1f}s", flush=True)
    term_vecs = arc._encode_store(enc, vocab)

    _heartbeat(output_dir, f"{tag}:encode_questions")
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"]) for q in questions])
    STEM = arc._encode_store(enc, [q["stem"] for q in questions])
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]) for q in questions]
    stem_words_per_q = [set(arc._content_words(q["stem"], MIN_TERM_LEN)) for q in questions]
    choice_words_per_q = [[set(arc._content_words(c, MIN_TERM_LEN)) for c in q["choices"]] for q in questions]
    q_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
                     for q in questions]
    uniq_words = sorted({w for ws in q_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}
    q_word_vecs_per_q = [uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)
                         for ws in q_words_per_q]

    # UNCHANGED PPR pool (arm B), batched
    _heartbeat(output_dir, f"{tag}:ppr")
    seeds = ppr.link_seeds(q_words_per_q, vocab, t2i, term_vecs, q_word_vecs_per_q, SEED_COS)
    seed_mat = ppr.seeds_to_matrix(seeds, nTerms)
    a_real = ppr.ppr_batch(seed_mat, M, HOPS, DAMP)
    FB = ppr.fact_activation(a_real, Sft)

    # ---- per-question: build selected pool + escalation context ----
    _heartbeat(output_dir, f"{tag}:select")
    per_q = []   # dict per question with sel_hd, q_rel_sel, choice_hd, base scores/margin, gapfill fact, etc.
    for qi, q in enumerate(questions):
        stem_words = stem_words_per_q[qi]
        lure_set, _ = sel.standout_lure_choices(stem_words, q["choices"])
        pool_idx = ppr.topk_from_scores(FB[qi], K_POOL)
        fw = [fact_word_sets[i] for i in pool_idx]
        gs = sel.gate_scores(SV_store[pool_idx], fw, stem_words, STEM[qi], choice_hd_map[qi], lure_set)
        sel_local = sel._topk_idx(gs["gate"], K_SEL)
        sel_idx = pool_idx[sel_local]
        fh = SV_store[sel_idx]
        q_rel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        scores, margin, _ = settle_scores(fh, q_rel, choice_hd_map[qi])
        conf = conf_signal(fh, q_rel, choice_hd_map[qi])

        # gap-fill candidate = top goal-relevant STORE fact NOT already in the selected pool
        goal = gs["goal"]
        pool_set = set(int(x) for x in sel_idx.tolist())
        gf_fi = None
        order = np.argsort(-FB[qi])
        for fi in order[:200]:
            if int(fi) not in pool_set:
                gf_fi = int(fi)
                break

        per_q.append({
            "qi": qi, "ci": q["correct_index"], "sel_idx": sel_idx, "fh": fh, "q_rel": q_rel,
            "choice_hd": choice_hd_map[qi], "scores": scores, "margin": margin, "conf": conf,
            "gf_fi": gf_fi, "sel_words": [list(fact_word_sets[i]) for i in sel_idx],
            "sel_sents": [sents[i] for i in sel_idx], "stem_words": stem_words,
            "choice_word_sets": choice_words_per_q[qi], "QQ": QQ[qi],
            "gold_rows": [uid2fi[u] for u in q["gold_central"] if u in uid2fi],
        })

    # ---- calibrate conformal tau on CAL: graded conf of correctly-answered CAL questions ----
    cal_correct_confs = []
    for d in per_q:
        if is_cal[d["qi"]]:
            pk = _pick(d["scores"], seed + d["qi"])
            if pk == d["ci"]:
                cal_correct_confs.append(d["conf"])
    cal_arr = np.array(cal_correct_confs, dtype=np.float64) if cal_correct_confs else np.array([0.0])
    tau = conformal_tau(cal_arr, ALPHA_GATE)
    _heartbeat(output_dir, f"{tag}:tau", {"tau": round(float(tau), 5), "n_cal_correct": len(cal_correct_confs)})

    # ---- escalation ops (produce re-settled decision scores + the NEW graded conf) ----
    def resettle_with_extra(d, extra_vec, extra_relweight):
        fh2 = np.vstack([d["fh"], extra_vec[None, :].astype(np.float32)])
        q2 = np.concatenate([d["q_rel"], np.array([extra_relweight], np.float32)])
        s2, _, _ = settle_scores(fh2, q2, d["choice_hd"])
        c2 = conf_signal(fh2, q2, d["choice_hd"])
        return s2, c2

    def op_gapfill(d, discount):
        if d["gf_fi"] is None:
            return d["scores"], d["conf"], False
        gvec = SV_store[d["gf_fi"]]
        natural = float(max(gvec @ d["QQ"], 0.0))
        s2, c2 = resettle_with_extra(d, gvec, discount * natural if discount < 1.0 else natural)
        return s2, c2, True

    def op_bridge(d, rng, khop_mode):
        if khop_mode:
            sent, root, fired = _bridge_khop(d["sel_words"], d["stem_words"], d["choice_word_sets"],
                                             nd, rng)
        else:
            sent, fired = _bridge_random(d["sel_sents"], rng)
            root = None
        if not fired or not sent:
            return d["scores"], d["conf"], False, None
        bvec = arc._encode_store(enc, [sent])[0]
        natural = float(max(bvec @ d["QQ"], 0.0))
        s2, c2 = resettle_with_extra(d, bvec, natural)
        return s2, c2, True, root

    # ---- run all arms ----
    _heartbeat(output_dir, f"{tag}:arms", {"tau": round(float(tau), 5)})
    ARMS = ("A", "B", "C", "D", "E", "F", "G", "O")
    picks = {k: np.full(nQ, -1, dtype=np.int64) for k in ARMS}      # -1 = abstain (only B uses it)
    fmargin = {k: np.zeros(nQ, dtype=np.float64) for k in ARMS}
    escalated = {k: np.zeros(nQ, dtype=bool) for k in ARMS}
    path_counts = {"committed": 0, "bridged": 0, "gap_filled": 0, "abstained": 0, "guess_lowconf": 0}
    bridge_fire = {"C": 0, "F": 0, "G_bridge": 0}
    audit_roots = []

    for d in per_q:
        qi = d["qi"]
        base_pick = _pick(d["scores"], seed + qi)
        low = d["conf"] < tau                 # gate on the GRADED confidence signal
        # A baseline
        picks["A"][qi] = base_pick
        fmargin["A"][qi] = d["conf"]
        # O oracle-gold
        if d["gold_rows"]:
            gfh = SV_store[d["gold_rows"]]
            gq = np.maximum(gfh @ d["QQ"], 0.0).astype(np.float32)
            gscores, _, _ = settle_scores(gfh, gq, d["choice_hd"])
            picks["O"][qi] = _pick(gscores, seed + qi)
            fmargin["O"][qi] = conf_signal(gfh, gq, d["choice_hd"])
        else:
            picks["O"][qi] = base_pick
            fmargin["O"][qi] = d["conf"]
        # B abstain-only
        if low:
            picks["B"][qi] = -1
            path_counts["abstained"] += 1
        else:
            picks["B"][qi] = base_pick
            path_counts["committed"] += 1
        fmargin["B"][qi] = d["conf"]
        # C bridge (khop)
        if low:
            s2, m2, fired, root = op_bridge(d, np.random.default_rng(seed + 1000 + qi), khop_mode=True)
            picks["C"][qi] = _pick(s2, seed + qi); fmargin["C"][qi] = m2; escalated["C"][qi] = fired
            if fired:
                bridge_fire["C"] += 1
                if root and len(audit_roots) < 8:
                    audit_roots.append(root)
        else:
            picks["C"][qi] = base_pick; fmargin["C"][qi] = d["conf"]
        # F bridge-random (must-fail)
        if low:
            s2, m2, fired, _ = op_bridge(d, np.random.default_rng(seed + 2000 + qi), khop_mode=False)
            picks["F"][qi] = _pick(s2, seed + qi); fmargin["F"][qi] = m2; escalated["F"][qi] = fired
            if fired:
                bridge_fire["F"] += 1
        else:
            picks["F"][qi] = base_pick; fmargin["F"][qi] = d["conf"]
        # D gap-fill discounted
        if low:
            s2, m2, fired = op_gapfill(d, GAPFILL_DISCOUNT)
            picks["D"][qi] = _pick(s2, seed + qi); fmargin["D"][qi] = m2; escalated["D"][qi] = fired
        else:
            picks["D"][qi] = base_pick; fmargin["D"][qi] = d["conf"]
        # E gap-fill undiscounted (must-fail)
        if low:
            s2, m2, fired = op_gapfill(d, 1.0)
            picks["E"][qi] = _pick(s2, seed + qi); fmargin["E"][qi] = m2; escalated["E"][qi] = fired
        else:
            picks["E"][qi] = base_pick; fmargin["E"][qi] = d["conf"]
        # G combined: gate -> bridge-if-fires else discounted gap-fill else low-conf guess
        if low:
            s2, m2, bfired, root = op_bridge(d, np.random.default_rng(seed + 1000 + qi), khop_mode=True)
            if bfired:
                picks["G"][qi] = _pick(s2, seed + qi); fmargin["G"][qi] = m2; escalated["G"][qi] = True
                path_counts["bridged"] += 1; bridge_fire["G_bridge"] += 1
            else:
                s3, m3, gfired = op_gapfill(d, GAPFILL_DISCOUNT)
                if gfired:
                    picks["G"][qi] = _pick(s3, seed + qi); fmargin["G"][qi] = m3; escalated["G"][qi] = True
                    path_counts["gap_filled"] += 1
                else:
                    picks["G"][qi] = base_pick; fmargin["G"][qi] = d["conf"]
                    path_counts["guess_lowconf"] += 1
        else:
            picks["G"][qi] = base_pick; fmargin["G"][qi] = d["conf"]

    # ---- accuracy by split (TEST split only for arm evaluation; O + A also reported over TEST) ----
    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    is_test = ~is_cal
    test_easy = is_test & is_easy
    test_chal = is_test & ~is_easy
    correct = {k: np.array([1 if (picks[k][qi] >= 0 and picks[k][qi] == questions[qi]["correct_index"]) else 0
                            for qi in range(nQ)], dtype=np.int64) for k in ARMS}
    answered = {k: np.array([1 if picks[k][qi] >= 0 else 0 for qi in range(nQ)], dtype=np.int64) for k in ARMS}

    def acc_full(mask, k):
        m = correct[k][mask]
        return round(float(np.mean(m)), 4) if m.size else None

    def acc_answered(mask, k):
        ans = answered[k][mask].astype(bool)
        if ans.sum() == 0:
            return None
        return round(float(np.mean(correct[k][mask][ans])), 4)

    def coverage(mask, k):
        a = answered[k][mask]
        return round(float(np.mean(a)), 4) if a.size else None

    def conf_wrong_rate(mask, k, tau_):
        # answered-and-wrong with FINAL margin >= tau  (over answered items)
        idxs = np.where(mask & (answered[k] == 1))[0]
        if idxs.size == 0:
            return None
        cw = sum(1 for i in idxs if correct[k][i] == 0 and fmargin[k][i] >= tau_)
        return round(cw / idxs.size, 4)

    accs = {}
    for k in ARMS:
        accs[k] = {"easy": acc_full(test_easy, k), "challenge": acc_full(test_chal, k),
                   "acc_answered_chal": acc_answered(test_chal, k),
                   "coverage_chal": coverage(test_chal, k),
                   "conf_wrong_chal": conf_wrong_rate(test_chal, k, tau)}
    A_chal = accs["A"]["challenge"] or 0.0
    O_chal = accs["O"]["challenge"] or 0.0
    G_chal = accs["G"]["challenge"] or 0.0

    return {
        "seed": seed, "tag": tag, "n_dim": nd,
        "n_questions": nQ, "n_test": int(is_test.sum()),
        "n_test_easy": int(test_easy.sum()), "n_test_chal": int(test_chal.sum()),
        "n_cal_correct": len(cal_correct_confs), "tau": round(float(tau), 5),
        "acc": accs, "A_chal": A_chal, "O_chal": O_chal, "G_chal": G_chal,
        "gap": round(O_chal - A_chal, 4),
        "path_counts": path_counts, "bridge_fire": bridge_fire,
        "audit_roots_sample": audit_roots,
        "n_low_conf": int(sum(1 for d in per_q if is_test[d["qi"]] and d["conf"] < tau)),
        "picks_digest": {k: hashlib.sha256(picks[k].tobytes()).hexdigest()[:16] for k in ARMS},
    }


# ---------------------------------------------------------------------------
# aggregate seeds + verdict
# ---------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(float(np.mean(xs)), 4) if xs else None


def aggregate_and_verdict(seed_results, mode, output_dir):
    A = _mean([r["acc"]["A"]["challenge"] for r in seed_results])
    O = _mean([r["acc"]["O"]["challenge"] for r in seed_results])
    G = _mean([r["acc"]["G"]["challenge"] for r in seed_results])
    C = _mean([r["acc"]["C"]["challenge"] for r in seed_results])
    D = _mean([r["acc"]["D"]["challenge"] for r in seed_results])
    E = _mean([r["acc"]["E"]["challenge"] for r in seed_results])
    F = _mean([r["acc"]["F"]["challenge"] for r in seed_results])
    B_acc_ans = _mean([r["acc"]["B"]["acc_answered_chal"] for r in seed_results])
    B_cov = _mean([r["acc"]["B"]["coverage_chal"] for r in seed_results])
    D_cw = _mean([r["acc"]["D"]["conf_wrong_chal"] for r in seed_results])
    E_cw = _mean([r["acc"]["E"]["conf_wrong_chal"] for r in seed_results])
    gap = round((O or 0.0) - (A or 0.0), 4)
    g_minus_a = round((G or 0.0) - (A or 0.0), 4)
    gap_frac = round(g_minus_a / gap, 4) if gap > 1e-9 else None

    # per-seed replication of the HP arithmetic
    per_seed_hp = []
    for r in seed_results:
        a = r["acc"]["A"]["challenge"] or 0.0
        o = r["acc"]["O"]["challenge"] or 0.0
        g = r["acc"]["G"]["challenge"] or 0.0
        gp = o - a
        per_seed_hp.append(gp >= GAP_MIN_HEADROOM and (g - a) >= GAP_FRAC_HP * gp and (g - a) >= ABS_G_MIN)
    replicated = all(per_seed_hp) and len(per_seed_hp) >= 2

    bridge_guard = ((C is not None and F is not None) and (C - F) >= 0.0
                    and (F - (A or 0.0)) <= BRIDGE_RANDOM_MAX)
    discount_guard = ((E_cw is not None and D_cw is not None) and (E_cw - D_cw) >= DISCOUNT_CW_MARGIN
                      and (D is not None and E is not None) and (D >= E - DISCOUNT_ACC_EPS))

    total_bridge_C = sum(r["bridge_fire"]["C"] for r in seed_results)
    total_lowconf = sum(r["n_low_conf"] for r in seed_results)
    escalation_fired = total_lowconf > 0

    if not escalation_fired:
        verdict = "ESCALATION_DISCRIMINATOR_INERT"
        vmsg = (f"gate never fired (n_low_conf=0 across seeds): tau below every settle margin -> the "
                f"escalation loop was never exercised. Re-spec ALPHA_GATE or the margin signal; NOT a "
                f"mechanism result. A_chal={A} O_chal={O}.")
    elif gap < GAP_MIN_HEADROOM or (A or 0.0) >= AG_BASELINE_SAT:
        verdict = "ESCALATION_INCONCLUSIVE_NO_HEADROOM"
        vmsg = (f"in-cell Challenge gap O-A={gap} < {GAP_MIN_HEADROOM} (or A saturated {A}>= "
                f"{AG_BASELINE_SAT}): no headroom for reasoning-robustness to close. Baseline already "
                f"near the gold ceiling on this pool/seed set; report, not a mechanism failure.")
    elif (g_minus_a >= GAP_FRAC_HP * gap and g_minus_a >= ABS_G_MIN and replicated
          and bridge_guard and discount_guard):
        verdict = "ESCALATION_HARD_PASS"
        vmsg = (f"CONFIDENCE-GATED ESCALATION closes the gap ON THE ANSWER: Challenge G={G} vs A={A} "
                f"(lift {g_minus_a:+.4f} = {gap_frac} of the O-A gap {gap}; >= {GAP_FRAC_HP} and >= "
                f"{ABS_G_MIN}; replicated {len(per_seed_hp)} seeds). Ceiling O={O}. MUST-FAIL controls hold: "
                f"random-bridge F={F} (F-A={round((F or 0)-(A or 0),4)} <= {BRIDGE_RANDOM_MAX}), khop-bridge "
                f"C={C} (C-F={round((C or 0)-(F or 0),4)} >= 0); undiscounted gap-fill confident-wrong "
                f"E_cw={E_cw} > D_cw={D_cw} (discount load-bearing), D_acc={D} >= E_acc={E}. Abstain arm B: "
                f"acc-when-answered={B_acc_ans} at coverage={B_cov}.")
    elif g_minus_a >= GAP_FRAC_MB * gap:
        verdict = "ESCALATION_MIDDLE_BAND"
        vmsg = (f"MIDDLE: Challenge G-A={g_minus_a:+.4f} = {gap_frac} of gap {gap} (in [{GAP_FRAC_MB}, "
                f"{GAP_FRAC_HP}) OR a guard/replication unmet: replicated={replicated} bridge_guard="
                f"{bridge_guard} (C={C} F={F}) discount_guard={discount_guard} (D_cw={D_cw} E_cw={E_cw} "
                f"D={D} E={E}). Escalation helps but not decisively. O ceiling={O}.")
    else:
        verdict = "ESCALATION_HARD_FAIL"
        vmsg = (f"HARD_FAIL: confidence-gated escalation does NOT beat plain settle on the answer "
                f"(Challenge G={G} vs A={A}, lift {g_minus_a:+.4f} < {GAP_FRAC_MB}*gap). Reasoning-side "
                f"robustness is NOT the lever on real pools -> redirect to retrieval quality (per the "
                f"drill's own HARD-FAIL-1 recommendation). O gold ceiling={O} (headroom exists but the "
                f"escalation loop cannot use it). bridge C={C} F={F}; gap-fill D={D} E={E} "
                f"(D_cw={D_cw} E_cw={E_cw}); n_low_conf(total)={total_lowconf} bridge_fires_C={total_bridge_C}.")

    grade = arc._grade_proxy(_mean([r["acc"]["G"]["easy"] for r in seed_results]), G)
    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [Chal TEST] A={A} G={G} O={O} gap={gap} G-A={g_minus_a} "
                    f"({gap_frac} of gap) | bridge C={C} F={F} | gapfill D={D} E={E} "
                    f"cw(D/E)={D_cw}/{E_cw} | abstain B acc_ans={B_acc_ans} cov={B_cov} | "
                    f"replicated={replicated} bridge_guard={bridge_guard} discount_guard={discount_guard}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_seeds": len(seed_results),
        # PRIMARY: challenge accuracy by arm (TEST split)
        "chal_A_baseline": A, "chal_G_combined": G, "chal_O_oracle_gold": O,
        "chal_C_bridge": C, "chal_F_bridge_random": F,
        "chal_D_gapfill_disc": D, "chal_E_gapfill_undisc": E,
        "in_cell_gap_O_minus_A": gap, "G_minus_A": g_minus_a, "gap_fraction_closed": gap_frac,
        "per_seed_hp_replicated": bool(replicated), "per_seed_hp_flags": per_seed_hp,
        # controls / secondary
        "bridge_guard_ok": bool(bridge_guard), "discount_guard_ok": bool(discount_guard),
        "confident_wrong_D_disc": D_cw, "confident_wrong_E_undisc": E_cw,
        "abstain_acc_when_answered_chal": B_acc_ans, "abstain_coverage_chal": B_cov,
        # gate / firing
        "escalation_fired": bool(escalation_fired),
        "n_low_conf_total": total_lowconf, "bridge_fires_C_total": total_bridge_C,
        "path_counts_seed0": seed_results[0]["path_counts"],
        "bridge_fire_seed0": seed_results[0]["bridge_fire"],
        "audit_roots_seed0": seed_results[0]["audit_roots_sample"],
        "tau_per_seed": [r["tau"] for r in seed_results],
        # bands
        "bands": {"GAP_FRAC_HP": GAP_FRAC_HP, "GAP_FRAC_MB": GAP_FRAC_MB, "ABS_G_MIN": ABS_G_MIN,
                  "DISCOUNT_CW_MARGIN": DISCOUNT_CW_MARGIN, "DISCOUNT_ACC_EPS": DISCOUNT_ACC_EPS,
                  "BRIDGE_RANDOM_MAX": BRIDGE_RANDOM_MAX, "GAP_MIN_HEADROOM": GAP_MIN_HEADROOM,
                  "AG_BASELINE_SAT": AG_BASELINE_SAT, "ALPHA_GATE": ALPHA_GATE,
                  "GAPFILL_DISCOUNT": GAPFILL_DISCOUNT, "K_SEL": K_SEL, "K_POOL": K_POOL},
        # per-arm full detail per seed
        "per_seed": [{"seed": r["seed"], "n_test_chal": r["n_test_chal"], "tau": r["tau"],
                      "n_low_conf": r["n_low_conf"], "gap": r["gap"],
                      "acc": {k: r["acc"][k] for k in ("A", "B", "C", "D", "E", "F", "G", "O")},
                      "picks_digest": r["picks_digest"]} for r in seed_results],
        "grade_proxy": grade,
        "hyperparams_note": ("author-set a priori: ALPHA_GATE=0.30 conformal, GAPFILL_DISCOUNT=0.30, "
                             "BRIDGE_HOPS=2, ESCALATION_BUDGET=1, K_SEL=4, K_POOL=20; NOT tuned to force a win"),
        "wired_vs_stubbed": (
            "WIRED: confidence-gated bounded ESCALATION LOOP around the UNCHANGED CI bind+settle "
            "(agg.aggregate mode='settle') over the UNCHANGED PPR pool + UNCHANGED selection gate "
            "(sel.gate_scores B_gate). CONFIDENCE GATE = conformal_tau (refuse-gate v8 core) on the "
            "settle choice-margin, calibrated on correct CALIBRATION-split questions. BRIDGE = "
            "substrate.khop.traverse over a per-question FHRR mini-KG (_pool_to_mini_kg adapter; "
            "Merkle AuditChain roots logged). DISCOUNTED gap-fill = inject the top ANSWER-AGNOSTIC "
            "goal-relevant store fact NOT in the pool at 0.30x natural weight; UNDISCOUNTED = full "
            "weight (must-fail). Arms A/B/C/D/E/F/G/O; PRIMARY = end-to-end Challenge accuracy on the "
            "held-out TEST split; gap measured IN-CELL (O gold ceiling - A selected-pool baseline). "
            "STUBBED/NOTED-NOT-BUILT: controlled RE-RETRIEVAL (query reformulation) -- deferred; "
            "principled discount MAGNITUDE (default-logic defeasibility) -- author-set 0.30, a follow-up "
            "drill sharpens it if D-vs-E lands."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree); VET-PENDING",
        "compute_architecture": ("mixed CPU: batched GloVe encode + scipy.sparse PPR (imported) + cheap "
                                 "per-question CI settle + escalation re-settles on low-conf subset + tiny "
                                 "per-question khop mini-KG; sequential-CPU (settle IS the primitive)"),
        "storage_strategy": "sharded (each fact = own embedding; each mini-KG concept = own FHRR vector)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": ("adaptive_with_discriminator_gate: conformal tau on held-out CAL correct "
                              "margins (NOT hand-set); discriminator-fires = escalation fired on "
                              f"{total_lowconf} low-conf TEST items across seeds (logged)"),
    }
    _write_metrics_atomic(output_dir, metrics)
    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)
    return metrics


# ---------------------------------------------------------------------------
# smoke multi-seed variance probe (A/D/E/G signals must not vanish across seeds)
# ---------------------------------------------------------------------------
def _variance_probe(output_dir):
    cfg = {"n_dim": 512, "limit_easy": 60, "limit_chal": 60}
    rs = []
    for s in PROBE_SEEDS:
        rs.append(run_seed(s, cfg, output_dir, tag=f"probe_s{s}"))
    ga = [(r["acc"]["G"]["challenge"] or 0.0) - (r["acc"]["A"]["challenge"] or 0.0) for r in rs]
    de_cw = [((r["acc"]["E"]["conf_wrong_chal"] or 0.0) - (r["acc"]["D"]["conf_wrong_chal"] or 0.0)) for r in rs]
    probe = {"seeds": PROBE_SEEDS, "G_minus_A_per_seed": [round(x, 4) for x in ga],
             "E_minus_D_confwrong_per_seed": [round(x, 4) for x in de_cw],
             "G_minus_A_mean": round(float(np.mean(ga)), 4), "G_minus_A_std": round(float(np.std(ga)), 4),
             "n_low_conf_per_seed": [r["n_low_conf"] for r in rs]}
    print(f"[probe] G-A per seed={probe['G_minus_A_per_seed']} (mean={probe['G_minus_A_mean']} "
          f"std={probe['G_minus_A_std']}); E-D confwrong={probe['E_minus_D_confwrong_per_seed']}; "
          f"n_low_conf={probe['n_low_conf_per_seed']}", flush=True)
    with open(os.path.join(output_dir, "variance_probe.json"), "w", encoding="utf-8") as f:
        json.dump(probe, f, indent=2)
    return probe


# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 200, "limit_chal": 200, "seeds": [FULL_SEEDS[0]]}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None, "seeds": FULL_SEEDS}


def run(mode, output_dir):
    cfg = _config(mode)
    if mode == "smoke":
        _heartbeat(output_dir, "variance_probe_start")
        _variance_probe(output_dir)
    seed_results = []
    for s in cfg["seeds"]:
        seed_results.append(run_seed(s, {"n_dim": cfg["n_dim"], "limit_easy": cfg["limit_easy"],
                                          "limit_chal": cfg["limit_chal"]}, output_dir, tag=f"seed{s}"))
    return aggregate_and_verdict(seed_results, mode, output_dir)


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
