#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exp_read_xsent_coref_learned_centering_cb_continuity_v1

LEARNED DISCOURSE-CENTERING coref (the self-drive "learned / flexible-improving /
learning-curve" directive applied to the same-gender coref wall). The same-gender wall
(29513-29517: cross-sentence pronoun misses dominated by >=2 same-gender competitors) was
triangulated as DISCOURSE CENTERING, not knowledge. Our banked coref readers use recency +
subject-role-mass + first-mention primacy + phi-filter but NOT the explicit backward-looking-
center (Cb) CONTINUITY signal (prefer the candidate the prior utterance was 'about'). This
cell LEARNS the feature weights of a glass-box linear centering ranker IN-SUBSTRATE and adds
Cb-continuity as a NEW feature, then measures the LEARNING CURVE + a clean Cb ablation.

BRAIN MECHANISM (Centering Theory Grosz/Joshi/Weinstein 1995 + Lappin-Leass 1994 recency;
drill notes/research_drill_hrr_context_bind_disambiguator_Q2_coreference_2026-06-28.md):
pronoun resolution = (1) backward-looking center Cb (entity the prior utterance was about),
(2) forward-looking centers Cf ranked by grammatical role subject>object>oblique (with a
first-mention / subject-position advantage), (3) recency weights, (4) gender/number filter.

FEATURES per candidate (brain-faithful centering, glass-box; nominal-mention derived, no gold):
  x_role     role-prominence = subject-role-weighted mention mass (Cf-rank; subject weighs
             CENTER_SUBJECT_W, oblique 1.0). Global topicality mass.
  x_recency  exp(-lam * mention-distance) to the candidate's most-recent mention (Lappin-Leass).
  x_cb       NEW: Cb-CONTINUITY = 1 iff the candidate was the backward-looking center of the
             PRIOR utterance (the specific-character subject the last sentence was about). LOCAL
             continuity -- can DISAGREE with global role-mass and with recency.
  x_phi      phi-agreement confidence = 1 iff the candidate has a KNOWN cue-gender. NEAR-CONSTANT
             on the same-gender subset by construction (phi is EXHAUSTED there -- exactly WHY the
             subset is the wall). Its learned weight is expected ~0 (honest, reported).
  x_primacy  first-mention primacy = pool-normalized earliest-introduction (1=earliest, 0=latest;
             the Centering Cf first-mention/subject advantage that the banked hand-rule uses as
             its tie-break). Included so the learner can FAIRLY represent the hand-rule.

LEARNING (in-substrate, glass-box): the LEARNER MODULE (hdlab/learner, 29487) is an MDL
two-part-code CLASSIFICATION / rule-induction engine (mdl_select over estimation/ruleind
plugins); it has NO pairwise-ranking-loss plugin and cannot express argmax-over-a-variable-
candidate-pool cleanly. So per the cell-author escape hatch we use the simplest in-substrate
learned linear ranker: a SOFTMAX RANKING model (multinomial-logistic over the candidate pool),
fit by deterministic full-batch gradient descent with small L2 (zero init, fixed lr/epochs). The
learned weight vector IS a glass-box JSON-serializable hypothesis (honors the learner module's
glass_box_assert invariant), just fitted by a ranking loss rather than the MDL gate. Reported
honestly.

TRAIN/TEST: LitBank coref gold, HELD-OUT BOOKS (no train/test book leakage; deterministic
sorted split, TEST = every 3rd book). Learning curve = TEST accuracy vs # training books.

SUBSET (difficulty ON, apples-to-apples with the banked 0.4523): the 29513/29514 wall =
cross-sentence (xsent) targets with backbone suppressed-pool n_pool >= 2 (>=2 same-gender
specific competitors). The banked hand-rule recency_centrality scores 0.4523 there; local_window
0.4070; single_sentence 0.0000 (reproduced in-cell as positive controls). The learned reader is
a full per-target arm: it overrides the base topical pick ONLY on same-gender ties (agreement-
narrowed tpool >= 2), so on the rest it equals local_window (forced/identical) -- clean isolation.

DISCRIMINATORS (pre-registered, can-fail, ONE variable):
  D1  learned-centering vs the HAND-RULE recency-centrality baseline (banked 0.4523 backbone
      subset, reproduced in-cell). BEAT (learning helps) OR PLATEAU / UNDER (hand-rules already
      capture centering = ceiling confirmed VIA a learning curve). Either is informative + honest.
  D2  Cb-CONTINUITY ABLATION: learned_full [role,recency,cb,phi,primacy] vs learned_nocb
      [role,recency,phi,primacy]. Does the NEW Cb feature lift accuracy? If not, the residual is
      not classic-centering either (reported honestly).

PRE-REGISTERED bands (HYPOTHESIZED@this file; set BEFORE the final run):
  HARD_PASS  = validity holds (single_sentence xsent ~0) AND positive-control reproduces the
               banked recency-centrality 0.4523 (|full - 0.4523| <= 0.03) AND learned_full TEST
               subset >= recency_centrality TEST subset + BEAT_MARGIN (0.02) with sign_stability
               >= 0.90 AND cb_delta (full - nocb) >= CB_MARGIN (0.01). = learning BEATS the
               hand-rule AND Cb-continuity is the load-bearing lever.
  MIDDLE_BAND = valid + positive-control holds AND the learner is sane (learned_full TEST >=
               SANITY_FLOOR 0.15, well above the 1/n_cands random floor) BUT learned_full does
               NOT beat the hand-rule by the margin (PLATEAU / UNDER = ceiling confirmed via a
               learning curve). Reports whether Cb ADDS (cb_delta >= CB_MARGIN) separately. A
               learning curve to a proven bound is a real clean result -- reported plainly.
  HARD_FAIL  = validity fails, OR (full mode) positive-control fails to reproduce 0.4523
               (invocation/regime mismatch -- downstream suspect), OR the learned ranker is
               BROKEN (learned_full TEST < SANITY_FLOOR 0.15 = below any single real feature /
               near the random floor = the ranker/features are miswired).

Numbers tagged MEASURED@disk / HYPOTHESIZED@this file / CITED@prior; reported numbers are
MEASURED@ the metrics.json this run writes.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at gate (META_RULE_AF): learned_full / learned_nocb / recency
#   correctness patterns differ on the test subset (asserted; identical learned_full==recency
#   pattern -> flagged as the learner-did-nothing case).
# - final_metrics_atomicity: tmp_replace (single-shot; metrics.json.tmp + os.replace).
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: symbolic accuracy metric over a glass-box linear ranker; no matmul noise floor on
#   accuracy. Reachability shown empirically: single_sentence xsent ~0 leaves headroom; the
#   1/n_cands random floor (~0.08 at mean n_cands~12) is far below the reported numbers.
# - baseline_in_band: recency_centrality subset ~0.45 (0.05<b<0.95); single_sentence ~0 by
#   validity design (the discriminator baseline, intentionally at floor).
# - discriminator survives scale: full = 25 books; smoke = first 8, asserts test subset
#   non-empty, the learner fits (non-trivial weights), arms differ, direction sane. The learned-
#   vs-handrule contrast is measured at FULL scale on the reproduced-0.4523 backbone subset.
# - HARD_PASS strictly above the hand-rule by BEAT_MARGIN (META_RULE_L) + sign-stable.
# - cardinality: EXPECTED_N_UNITS = n_books usable; verdict counts per-book coverage.
# - per-unit failure-class instrumentation; no bare except.
# - calibration_check: default_ok_for_this_regime (overlay/centering constants ported VERBATIM
#   from hdlab.coref/state_of_mind; CENTER_SUBJECT_W a general role prominence; lam=0.1 the
#   banked overlay decay; EPOCHS/LR/L2/split FIXED, not tuned for PASS).
# - real_code_path: self-test builds a real temp conll, runs parse + baseline readers + the
#   learned reader end-to-end via evaluate_book, asserts the learned reader reproduces its own
#   base topical pick with weights=None, that the Cb feature CHANGES the pick when decisive, and
#   that the softmax learner fits a cb-decisive example.
# - deterministic_seeding: true. Softmax GD zero-init full-batch fixed epochs; split by sorted
#   book index (no hash()-seeded RNG, no list(set()) ordering). Bootstrap uses a FIXED
#   np.random.default_rng seed.
# - progress_logging: print_flush_true (wall < ~5min; heartbeat EXEMPT, timeout_s < 1800).
"""

import argparse
import glob
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.coref import (  # noqa: E402
    CENTER_SUBJECT_W,
    CorefReader,
    build_pronoun_targets,
    load_name_gender,
    name_content_tokens,
    parse_litbank_conll,
    sent_dist_bucket,
)
from hdlab.coref_distractor_suppress import (  # noqa: E402
    GenericDistractorFilter,
    SuppressReader,
    build_ever_subject_heads,
)
from hdlab.scene_segment import (  # noqa: E402
    SceneProtagonistReader,
    TOPICAL_SLOT_HEADS,
    parse_conll_sentences,
)
from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader  # noqa: E402
from hdlab.state_of_mind import PRONOUN_SCOPE, TARGET_PRONOUNS  # noqa: E402

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ANCHOR_NAME = "read_xsent_coref_learned_centering_cb_continuity_v1"
CORPUS_DIR = os.path.join(REPO_ROOT, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 8
LOCAL_WINDOW = 5
MEM_SEED = 7
FEATURE_NAMES = ["role", "recency", "cb", "phi", "primacy"]
N_FEAT = 5
CB_IDX = 2
PRIMACY_IDX = 4
EPOCHS = 300
LR = 0.5
L2 = 1e-3
TEST_EVERY = 3             # deterministic held-out split: TEST = sorted-book index % 3 == 2

# Banked hand-rule numbers to reproduce (positive controls, Gate D).
# MEASURED@data/exp_read_xsent_coref_event_centrality_v1/metrics.json:same_gender_subset_acc.*
RECENCY_CENTRALITY_BANKED = 0.45226130653266333
LOCAL_WINDOW_BANKED = 0.40703517587939697
BACKBONE_BANKED = 0.24623115577889448

# Bands (pre-registered; HYPOTHESIZED@this file).
VALIDITY_GATE_MAX = 0.10
POSCTRL_EPS = 0.03            # |recency_centrality full backbone-subset - 0.4523| <= this
BEAT_MARGIN = 0.02           # learned_full >= recency + this  (D1 beat)
CB_MARGIN = 0.01             # learned_full - learned_nocb >= this  (D2 cb lift)
HP_SIGN_STABILITY = 0.90
SANITY_FLOOR = 0.15          # learned_full below this = broken ranker (well below any single feat)
N_BOOTSTRAP = 2000
BOOTSTRAP_SEED = 20260724
MIN_TEST_SUBSET = 30
MIN_TRAIN_EX = 30

SUP_KW = dict(suppress_generic=True, use_nonref=True, use_struct=True,
              chain_pronouns=True, use_gazetteer=True)
XSENT_BUCKETS = ("plus1", "plus2", "long")


def _p(msg):
    print(msg, flush=True)


def _f(x):
    return "None" if x is None else ("%.4f" % x)


def is_xsent(bucket):
    return bucket in XSENT_BUCKETS


# ----------------------------------------------------------------------------
# LEARNED CENTERING READER. Identical pool construction to the banked readers
# (SceneProtagonistReader tpool); the same-gender pick is a LEARNED softmax rank over
# glass-box centering features (or the base topical pick when weights=None). chain_pronouns
# is held OFF so features are pick-independent + deterministic; the candidate SET (tpool) is
# chain-independent (pronouns create no entities), so it matches what the hand-rule readers see
# -> the head-to-head is apples-to-apples. For tpool < 2 the pick is forced (== local_window).
# ----------------------------------------------------------------------------
class LearnedCenteringReader(SceneProtagonistReader):
    """SceneProtagonistReader pool + a LEARNED softmax-ranking centering pick on same-gender ties.

    resolve_stream(..., weights=None) -> base topical pick (local-window faithful) + stashes
      per-target candidate FEATURE dumps (5 features) in self.last_features (for training/eval).
    resolve_stream(..., weights=w, feat_mean, feat_std, feat_mask) -> pick argmax(w . std(x)) on
      same-gender ties (n_cands>=2); base topical pick otherwise. Also stashes features.

    Pronoun-chaining is applied to the deterministic BASE decision (topical pick / adaptive pick),
    NOT the learned override, so the role-mass feature is (a) strong (chained, like the banked
    readers) and (b) pick-independent -> identical between feature-extraction and learned-apply.
    """

    @staticmethod
    def _feat_row(e, now, cb_head, lam, midx_to_role, primacy):
        role = 0.0
        for mx in e.mention_midxs:
            role += CENTER_SUBJECT_W if midx_to_role.get(mx, 99) == 0 else 1.0
        rec = math.exp(-lam * (now - e.last_midx))
        cb = 1.0 if (cb_head is not None and e.head == cb_head) else 0.0
        phi = 1.0 if e.gender in ("masc", "fem") else 0.0
        return [role, rec, cb, phi, primacy]

    def resolve_stream(self, mentions, targets, *, scene_ids=None,
                       topical_mode="rolemass", topical_heads=None,
                       use_gazetteer=True, suppress_generic=True,
                       use_nonref=True, use_struct=True,
                       weights=None, feat_mean=None, feat_std=None, feat_mask=None):
        if topical_heads is None:
            topical_heads = TOPICAL_SLOT_HEADS
        if scene_ids is None:
            raise ValueError("LearnedCenteringReader requires scene_ids (fixed-window baseline)")
        ever_subj = build_ever_subject_heads(mentions)
        filt = GenericDistractorFilter(ever_subj, use_nonref=use_nonref, use_struct=use_struct)
        midx_to_role = {m["midx"]: m.get("sent_role_rank", 99) for m in mentions}
        target_by_midx = {t["target"]["midx"]: t for t in targets}

        scene_of_midx = {}
        scene_to_midxs = defaultdict(set)
        for m in mentions:
            si = m.get("sent_idx", 0)
            sc = scene_ids[si] if 0 <= si < len(scene_ids) else -1
            scene_of_midx[m["midx"]] = sc
            scene_to_midxs[sc].add(m["midx"])

        lam = self._lam
        w = None if weights is None else np.asarray(weights, dtype=float)
        mean = None if feat_mean is None else np.asarray(feat_mean, dtype=float)
        std = None if feat_std is None else np.asarray(feat_std, dtype=float)
        mask = np.ones(N_FEAT) if feat_mask is None else np.asarray(feat_mask, dtype=float)

        overlay = self._new_overlay()
        head_to_cluster = {}
        records = []
        feats_out = []

        cur_sent = mentions[0]["sent_idx"] if mentions else 0
        cb_head = None       # backward-looking center inherited from the PRIOR utterance
        cur_subj = None      # first specific-character subject seen in the CURRENT sentence

        for m in mentions:
            if m["sent_idx"] != cur_sent:
                if cur_subj is not None:      # carry-forward continuity if this sentence had none
                    cb_head = cur_subj
                cur_subj = None
                cur_sent = m["sent_idx"]

            resolved_ent = None
            base_decision = None       # deterministic base pick, used for chaining (pick-independent)
            pool_empty = False
            suppressed_any = False
            topical_fired = False
            learned_fired = False
            if m["is_pronoun"] and m["head"] in TARGET_PRONOUNS:
                now = overlay.n_observed
                sc = PRONOUN_SCOPE[m["head"]]
                cands = overlay._compatible_entities(sc["gender"], sc["number"])
                trank = midx_to_role.get(m["midx"], 99)
                if suppress_generic:
                    pool = [c for c in cands if not filt.is_generic(c)]
                    suppressed_any = len(pool) < len(cands)
                else:
                    pool = cands
                if pool:
                    do_topical = (m["head"] in topical_heads)
                    if do_topical:
                        tpool = self._agreement_narrow(pool, sc["gender"])
                        cur_scene = scene_of_midx.get(m["midx"], -1)
                        scene_midxs = scene_to_midxs.get(cur_scene)
                        base_pick = self._topical_pick(tpool, scene_midxs, midx_to_role,
                                                       topical_mode)
                        if base_pick is None:
                            base_pick = self._topical_pick(tpool, None, midx_to_role,
                                                           topical_mode)
                        resolved_ent = base_pick
                        base_decision = base_pick
                        topical_fired = True
                        if len(tpool) >= 2:
                            tp = sorted(tpool, key=lambda e: e.mention_midxs[0])
                            n = len(tp)
                            X = np.array([self._feat_row(
                                e, now, cb_head, lam, midx_to_role,
                                (1.0 - (j / (n - 1))) if n > 1 else 0.0)
                                for j, e in enumerate(tp)], dtype=float)
                            gold_idx = -1
                            for j, e in enumerate(tp):
                                if head_to_cluster.get(e.head) == m["cluster"]:
                                    gold_idx = j
                                    break
                            if w is not None:
                                Xs = X if mean is None else (X - mean) / std
                                scores = (Xs * mask) @ (w * mask)
                                resolved_ent = tp[int(np.argmax(scores))]
                                learned_fired = True
                            if m["midx"] in target_by_midx:
                                tinfo = target_by_midx[m["midx"]]
                                feats_out.append({
                                    "target_midx": m["midx"], "pronoun": m["head"],
                                    "gold_cluster": m["cluster"],
                                    "sent_dist": tinfo["sent_dist"],
                                    "bucket": sent_dist_bucket(tinfo["sent_dist"]),
                                    "n_cands": n, "gold_idx": gold_idx,
                                    "cand_heads": [e.head for e in tp],
                                    "X_raw": X.tolist(), "cb_head": cb_head})
                    else:
                        resolved_ent = self._adaptive_pick(pool, now, trank, midx_to_role)
                        base_decision = resolved_ent
                else:
                    pool_empty = True
                    resolved_ent = self._adaptive_pick(cands, now, trank, midx_to_role)
                    base_decision = resolved_ent

                if m["midx"] in target_by_midx:
                    tinfo = target_by_midx[m["midx"]]
                    if resolved_ent is None:
                        rec = dict(resolved_head=None, resolved_cluster=None,
                                   attempted=False, correct=False)
                    else:
                        rc = head_to_cluster.get(resolved_ent.head)
                        rec = dict(resolved_head=resolved_ent.head, resolved_cluster=rc,
                                   attempted=True,
                                   correct=(rc is not None and rc == m["cluster"]))
                    rec.update(target_midx=m["midx"], gold_cluster=m["cluster"],
                               sent_dist=tinfo["sent_dist"],
                               bucket=sent_dist_bucket(tinfo["sent_dist"]),
                               pool_empty=pool_empty, suppressed_any=suppressed_any,
                               topical_fired=topical_fired, learned_fired=learned_fired,
                               n_cands=len(cands), n_pool=len(pool))
                    records.append(rec)

            # advance the mention stream. Chain the DETERMINISTIC base decision (not the learned
            # override) so the role-mass feature is strong (chained) AND pick-independent.
            if m["is_pronoun"]:
                overlay.observe(m["head"], is_pronoun=True,
                                gender=m["gender"], number=m["number"])
                if base_decision is not None:
                    base_decision.mention_midxs.append(m["midx"])
            else:
                eff_gender = m["gender"]
                if eff_gender is None and use_gazetteer:
                    eff_gender = m.get("name_gender")
                is_named = bool(name_content_tokens(m.get("span_toks", [m["head"]])))
                overlay.observe(m["head"], gender=eff_gender, number=m["number"],
                                is_proper_name=is_named)
                head_to_cluster[m["head"].lower()] = m["cluster"]
                is_specific = (m.get("gender") is not None) or (m.get("name_gender") is not None)
                if is_specific and m.get("sent_role_rank", 99) == 0 and cur_subj is None:
                    cur_subj = m["head"].lower()

        self.last_features = feats_out
        return records


# ----------------------------------------------------------------------------
# In-substrate LEARNED softmax-ranking model (deterministic full-batch GD; glass-box weights).
# ----------------------------------------------------------------------------
def standardize_stats(examples):
    """Feature mean/std over pooled candidate rows of the (gold-in-pool, n>=2) examples. Constant
    features (std==0, e.g. phi saturated on the same-gender subset) get std=1 -> standardized to 0
    -> contribute nothing to the rank (weight indeterminate but harmless)."""
    rows = []
    for ex in examples:
        if ex["gold_idx"] >= 0 and ex["n_cands"] >= 2:
            rows.extend(ex["X_raw"])
    if not rows:
        return np.zeros(N_FEAT), np.ones(N_FEAT)
    A = np.asarray(rows, dtype=float)
    mean = A.mean(axis=0)
    std = A.std(axis=0)
    std = np.where(std < 1e-9, 1.0, std)
    return mean, std


def train_softmax_ranker(examples, mask, mean, std, epochs=EPOCHS, lr=LR, l2=L2):
    """Softmax (multinomial-logistic) RANKING learner over standardized candidate features, fit by
    deterministic full-batch gradient descent. Loss = mean over examples of -log softmax(gold).
    grad_w = mean_ex sum_i (p_i - 1{i=gold}) x_i + l2*w. Returns (w*mask, n_examples)."""
    mask = np.asarray(mask, dtype=float)
    data = []
    for ex in examples:
        if ex["gold_idx"] < 0 or ex["n_cands"] < 2:
            continue
        X = (np.asarray(ex["X_raw"], dtype=float) - mean) / std
        data.append((X * mask, ex["gold_idx"]))
    w = np.zeros(N_FEAT)
    if not data:
        return w, 0
    for _ep in range(epochs):
        g = np.zeros(N_FEAT)
        for X, gi in data:
            s = X @ w
            s = s - s.max()
            p = np.exp(s)
            p = p / p.sum()
            oh = np.zeros(len(X))
            oh[gi] = 1.0
            g += X.T @ (p - oh)
        g = g / len(data) + l2 * w
        w = w - lr * g
    return w * mask, len(data)


def predict_correct(ex, w, mean, std, mask):
    """Learned pick over a feature-dump example; correct iff argmax index == gold_idx."""
    X = (np.asarray(ex["X_raw"], dtype=float) - mean) / std
    scores = (X * mask) @ (w * mask)
    pick = int(np.argmax(scores))
    return (1 if (ex["gold_idx"] >= 0 and pick == ex["gold_idx"]) else 0), pick


# ----------------------------------------------------------------------------
# corpus + per-book evaluation
# ----------------------------------------------------------------------------
def list_books(run_mode):
    paths = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.conll")))
    usable = [p for p in paths if os.path.getsize(p) > 1000]
    if run_mode == "smoke":
        usable = usable[:SMOKE_N]
    return usable


def fixed_window_scenes(n_sents, size):
    return [i // size for i in range(n_sents)]


def evaluate_book(path, gaz, reader_coref, reader_sup, reader_scene, reader_ec, reader_learn):
    """Run the baseline arms + the learned reader's feature extract on one book. Returns
    (base_records, feature_dumps). base_records carry per-target correctness for single_sentence
    / backbone / local_window / recency_centrality + n_pool(backbone) + has_tpool2."""
    mentions, n_sentences = parse_litbank_conll(path, name_gender_map=gaz)
    sents = parse_conll_sentences(path)
    if len(sents) != n_sentences:
        raise RuntimeError("SENTENCE_MISALIGN: parse_litbank=%d parse_conll_sentences=%d"
                           % (n_sentences, len(sents)))
    targets = build_pronoun_targets(mentions)
    if not targets:
        return [], []
    sid_fixed = fixed_window_scenes(n_sentences, LOCAL_WINDOW)

    ss = reader_coref.resolve_stream(mentions, targets, reset_per_sentence=True,
                                     strategy="maintained")
    bk = reader_sup.resolve_stream(mentions, targets, **SUP_KW)
    lw = reader_scene.resolve_stream(mentions, targets, prefer_topical=True, per_scene=True,
                                     scene_ids=sid_fixed, topical_mode="rolemass", **SUP_KW)
    rc = reader_ec.resolve_stream(mentions, targets, scene_ids=sid_fixed,
                                  topical_mode="rolemass", query_memory=True,
                                  centrality_mode="recency", **SUP_KW)
    _ = reader_learn.resolve_stream(mentions, targets, scene_ids=sid_fixed,
                                    topical_mode="rolemass", weights=None)
    feats = list(reader_learn.last_features)
    tpool2 = {f["target_midx"] for f in feats if f["n_cands"] >= 2}

    base = []
    for i in range(len(targets)):
        tm = ss[i]["target_midx"]
        base.append({
            "target_midx": tm, "sent_dist": ss[i]["sent_dist"], "bucket": ss[i]["bucket"],
            "gold_cluster": ss[i]["gold_cluster"],
            "n_pool_backbone": bk[i].get("n_pool", -1),
            "has_tpool2": tm in tpool2,
            "correct": {
                "single_sentence": ss[i]["correct"], "backbone": bk[i]["correct"],
                "local_window": lw[i]["correct"], "recency_centrality": rc[i]["correct"],
            },
        })
    return base, feats


# ----------------------------------------------------------------------------
# metrics helpers
# ----------------------------------------------------------------------------
def acc(vals):
    return (sum(vals) / len(vals)) if vals else None


def sign_stability(mech, base, n_boot=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
    if len(mech) < 2 or len(mech) != len(base):
        return None
    rng = np.random.default_rng(seed)
    a = np.asarray(mech, dtype=float)
    b = np.asarray(base, dtype=float)
    n = len(a)
    pos = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if a[idx].mean() - b[idx].mean() > 0:
            pos += 1
    return pos / n_boot


def digest_bools(vals):
    return hashlib.sha256(bytes([1 if v else 0 for v in vals])).hexdigest()


# ----------------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------------
def run(run_mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data",
                           "exp_%s%s" % (ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, run_mode, 0)

    gaz = load_name_gender()
    books = list_books(run_mode)
    if len(books) < 3:
        raise RuntimeError("CORPUS_UNAVAILABLE: only %d books in %s" % (len(books), CORPUS_DIR))

    reader_coref = CorefReader()
    reader_sup = SuppressReader()
    reader_scene = SceneProtagonistReader()
    reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
    reader_learn = LearnedCenteringReader()

    book_base = {}     # book -> list of base records
    book_feat = {}     # book -> list of feature dumps
    per_book = {}
    book_failures = []
    for path in books:
        b = os.path.basename(path)
        try:
            base_recs, feats = evaluate_book(path, gaz, reader_coref, reader_sup,
                                             reader_scene, reader_ec, reader_learn)
            book_base[b] = base_recs
            book_feat[b] = feats
            per_book[b] = {"n_targets": len(base_recs), "n_feat_dumps": len(feats)}
            _p("[book] %-46s targets=%d feat_dumps=%d" % (b[:46], len(base_recs), len(feats)))
        except Exception as e:  # noqa: BLE001 -- per-book failure-class recorded, not silent
            book_failures.append({"book": b, "failure_class": type(e).__name__,
                                  "msg": str(e)[:160]})
            _p("[book-FAIL] %s : %s: %s" % (b, type(e).__name__, str(e)[:120]))

    ok_books = [os.path.basename(p) for p in books if os.path.basename(p) in book_base]
    if len(ok_books) < 3:
        raise RuntimeError("TOO_FEW_BOOKS_PARSED: %d" % len(ok_books))

    dump_by_key = {}
    for b in ok_books:
        for ex in book_feat[b]:
            dump_by_key[(b, ex["target_midx"])] = ex

    # ---- validity (single_sentence xsent acc, all books) ----
    ss_xsent = [r["correct"]["single_sentence"] for b in ok_books for r in book_base[b]
                if is_xsent(r["bucket"])]
    validity_acc = acc(ss_xsent)

    # ---- backbone n_pool>=2 xsent subset keys (the banked wall definition) ----
    def backbone_subset_keys(book_list):
        keys = []
        for b in book_list:
            for r in book_base[b]:
                if is_xsent(r["bucket"]) and r["n_pool_backbone"] >= 2:
                    keys.append((b, r["target_midx"]))
        return keys

    base_by_key = {(b, r["target_midx"]): r for b in ok_books for r in book_base[b]}

    all_keys = backbone_subset_keys(ok_books)
    recency_full_subset = acc([base_by_key[k]["correct"]["recency_centrality"] for k in all_keys])
    localwindow_full_subset = acc([base_by_key[k]["correct"]["local_window"] for k in all_keys])
    backbone_full_subset = acc([base_by_key[k]["correct"]["backbone"] for k in all_keys])

    # ---- held-out book split (deterministic: sorted index % TEST_EVERY == 2) ----
    train_books = [b for i, b in enumerate(ok_books) if i % TEST_EVERY != (TEST_EVERY - 1)]
    test_books = [b for i, b in enumerate(ok_books) if i % TEST_EVERY == (TEST_EVERY - 1)]
    if not train_books or not test_books:
        raise RuntimeError("SPLIT_DEGENERATE: train=%d test=%d" % (len(train_books), len(test_books)))

    def train_dumps(book_list):
        out = []
        for b in book_list:
            for ex in book_feat.get(b, []):
                if is_xsent(ex["bucket"]) and ex["n_cands"] >= 2 and ex["gold_idx"] >= 0:
                    out.append(ex)
        return out

    train_ex = train_dumps(train_books)

    # learned correctness for a key given trained weights: use the dump pick if tpool>=2 dump
    # exists (the learned decision), else the base local_window pick (forced/identical).
    def learned_correct_key(k, w, mean, std, mask):
        ex = dump_by_key.get(k)
        if ex is not None and is_xsent(ex["bucket"]) and ex["n_cands"] >= 2:
            c, _pk = predict_correct(ex, w, mean, std, mask)
            return c
        return base_by_key[k]["correct"]["local_window"]

    def learned_acc(keys, w, mean, std, mask):
        return acc([learned_correct_key(k, w, mean, std, mask) for k in keys])

    test_keys = backbone_subset_keys(test_books)
    recency_test = acc([base_by_key[k]["correct"]["recency_centrality"] for k in test_keys])
    localwindow_test = acc([base_by_key[k]["correct"]["local_window"] for k in test_keys])

    mask_full = np.ones(N_FEAT)
    mask_nocb = np.ones(N_FEAT)
    mask_nocb[CB_IDX] = 0.0

    small = (len(test_keys) < MIN_TEST_SUBSET or len(train_ex) < MIN_TRAIN_EX)

    # ---- LEARN via MODEL SELECTION (faithful to the LEARNER MODULE mdl_select ethos): fit
    # several candidate linear rankers on a FIT slice of the train books + SELECT the one that
    # GENERALIZES best on a held-out VALIDATION slice of the train books; refit the selected
    # config on ALL train books. Candidates = softmax rankers at several L2 + single-feature
    # rankers + a role-primary rule. This makes "does learning help" a FAIR test (the selected
    # model is at least as good on validation as the best simple rule) and keeps the Cb ablation
    # clean (nocb removes cb from EVERY candidate). Deterministic (fixed sub-split, zero-init GD).
    L2_GRID = [1e-3, 1e-2, 1e-1]

    def fit_and_select(tbooks, mask):
        if len(tbooks) >= 3:
            fit_b = [b for i, b in enumerate(tbooks) if i % 3 != 2]
            val_b = [b for i, b in enumerate(tbooks) if i % 3 == 2]
        else:
            fit_b, val_b = tbooks, tbooks     # too few to split -> select on train itself
        fit_ex = train_dumps(fit_b)
        full_ex = train_dumps(tbooks)
        if not fit_ex or not full_ex:
            return np.zeros(N_FEAT), np.zeros(N_FEAT), np.ones(N_FEAT), "none", None
        fm, fs = standardize_stats(fit_ex)
        val_keys = backbone_subset_keys(val_b)
        cands = {}
        for l2 in L2_GRID:
            wl, _ = train_softmax_ranker(fit_ex, mask, fm, fs, l2=l2)
            cands["softmax_l2_%g" % l2] = wl
        for fi in range(N_FEAT):
            if mask[fi] > 0:
                wf = np.zeros(N_FEAT); wf[fi] = 1.0
                cands["single_%s" % FEATURE_NAMES[fi]] = wf
        wr = np.zeros(N_FEAT); wr[0] = 1.0; wr[PRIMACY_IDX] = 0.05 * mask[PRIMACY_IDX]
        cands["role_primary"] = wr
        best_name, best_acc = None, -1.0
        for name in sorted(cands):     # sorted -> deterministic tie-break
            av = learned_acc(val_keys, cands[name], fm, fs, mask)
            if av is not None and av > best_acc:
                best_acc, best_name = av, name
        fmean, fstd = standardize_stats(full_ex)
        if best_name.startswith("softmax_l2_"):
            l2v = float(best_name[len("softmax_l2_"):])
            w_final, _ = train_softmax_ranker(full_ex, mask, fmean, fstd, l2=l2v)
        elif best_name.startswith("single_"):
            fi = FEATURE_NAMES.index(best_name[len("single_"):])
            w_final = np.zeros(N_FEAT); w_final[fi] = 1.0
        else:
            w_final = np.zeros(N_FEAT); w_final[0] = 1.0
            w_final[PRIMACY_IDX] = 0.05 * mask[PRIMACY_IDX]
        return w_final, fmean, fstd, best_name, best_acc

    w_full, mean, std, sel_full, val_full = fit_and_select(train_books, mask_full)
    w_nocb, mean_nc, std_nc, sel_nocb, val_nocb = fit_and_select(train_books, mask_nocb)
    n_used = len(train_ex)
    learned_full_test = learned_acc(test_keys, w_full, mean, std, mask_full)
    learned_nocb_test = learned_acc(test_keys, w_nocb, mean_nc, std_nc, mask_nocb)

    # paired correctness arrays on the test subset (for stability + autopsy)
    corr_full = [learned_correct_key(k, w_full, mean, std, mask_full) for k in test_keys]
    corr_nocb = [learned_correct_key(k, w_nocb, mean_nc, std_nc, mask_nocb) for k in test_keys]
    corr_rec = [base_by_key[k]["correct"]["recency_centrality"] for k in test_keys]

    # ---- FAIR internal reference: fixed role-primary hand-rule over the IDENTICAL features
    # (role primary + tiny primacy tie-break; the linear centering rule the learner CAN represent).
    # Isolates "does LEARNING the weights help" from the banked readers' extra mechanisms
    # (scene-scoping / pronoun-chain-to-own-pick / HD event-memory not representable per-candidate).
    w_rolefix = np.zeros(N_FEAT); w_rolefix[0] = 1.0; w_rolefix[PRIMACY_IDX] = 0.05
    handrule_fixed_test = learned_acc(test_keys, w_rolefix, mean, std, mask_full)
    single_feat_test = {}
    for fi in range(N_FEAT):
        wf = np.zeros(N_FEAT); wf[fi] = 1.0
        single_feat_test[FEATURE_NAMES[fi]] = learned_acc(test_keys, wf, mean, std, mask_full)
    best_single_feat_test = max((v for v in single_feat_test.values() if v is not None),
                                default=None)
    learned_beats_fixed = (None if (learned_full_test is None or handrule_fixed_test is None)
                           else learned_full_test - handrule_fixed_test)

    # ---- LEARNING CURVE: TEST backbone-subset acc vs # training books ----
    n_tr = len(train_books)
    sizes = sorted(set([s for s in [1, 2, 4, 8, 12, 16, n_tr] if 1 <= s <= n_tr]))
    learning_curve = []
    for k in sizes:
        kex = train_dumps(train_books[:k])
        if len(kex) < 1:
            learning_curve.append({"n_books": k, "n_train_ex": 0, "test_acc": None,
                                   "selected": "none"})
            continue
        wk, mk, sk, sel_k, _v = fit_and_select(train_books[:k], mask_full)
        ak = learned_acc(test_keys, wk, mk, sk, mask_full)
        learning_curve.append({"n_books": k, "n_train_ex": len(kex), "test_acc": ak,
                               "selected": sel_k})
    curve_first = next((c["test_acc"] for c in learning_curve if c["test_acc"] is not None), None)
    curve_last = next((c["test_acc"] for c in reversed(learning_curve)
                       if c["test_acc"] is not None), None)
    curve_rise = (None if (curve_first is None or curve_last is None)
                  else curve_last - curve_first)

    # ---- discriminators ----
    beat_delta = (None if (learned_full_test is None or recency_test is None)
                  else learned_full_test - recency_test)
    cb_delta = (None if (learned_full_test is None or learned_nocb_test is None)
                else learned_full_test - learned_nocb_test)
    stability = (sign_stability(corr_full, corr_rec) if not small else None)

    # ---- glass-box weights (standardized-space importance) ----
    def importance(w):
        aw = np.abs(np.asarray(w, dtype=float))
        s = aw.sum()
        return {FEATURE_NAMES[i]: (float(aw[i] / s) if s > 0 else 0.0) for i in range(N_FEAT)}
    weights_glass = {
        "feature_names": FEATURE_NAMES,
        "w_full": [float(x) for x in w_full], "w_nocb": [float(x) for x in w_nocb],
        "feat_mean": [float(x) for x in mean], "feat_std": [float(x) for x in std],
        "importance_full": importance(w_full), "importance_nocb": importance(w_nocb),
        "selected_full": sel_full, "selected_nocb": sel_nocb,
        "val_acc_full": val_full, "val_acc_nocb": val_nocb,
        "n_train_used": n_used,
    }

    # ---- glass-box traces: 2 correct + 2 incorrect learned_full test decisions (tpool>=2) ----
    def trace(ex, pk):
        cands = []
        for j, h in enumerate(ex["cand_heads"]):
            xr = ex["X_raw"][j]
            xs = ((np.asarray(xr) - mean) / std)
            cands.append({"head": h,
                          "x_raw": {FEATURE_NAMES[i]: round(xr[i], 3) for i in range(N_FEAT)},
                          "score": round(float((xs * mask_full) @ (w_full * mask_full)), 3),
                          "is_gold": (j == ex["gold_idx"]), "is_pick": (j == pk)})
        return {"pronoun": ex["pronoun"], "cb_head": ex["cb_head"],
                "gold_cluster": ex["gold_cluster"], "gold_idx": ex["gold_idx"], "pick_idx": pk,
                "correct": bool(ex["gold_idx"] >= 0 and pk == ex["gold_idx"]),
                "candidates": cands}
    traces = []
    nc = nw = 0
    for k in test_keys:
        ex = dump_by_key.get(k)
        if ex is None or ex["n_cands"] < 2:
            continue
        c, pk = predict_correct(ex, w_full, mean, std, mask_full)
        if c and nc < 2:
            traces.append(trace(ex, pk)); nc += 1
        elif (not c) and nw < 2:
            traces.append(trace(ex, pk)); nw += 1
        if nc >= 2 and nw >= 2:
            break

    # ---- per-item autopsy on the test subset ----
    def fixed_broke(mech, base):
        fx = sum(1 for a, b in zip(mech, base) if a and not b)
        bk = sum(1 for a, b in zip(mech, base) if b and not a)
        return fx, bk
    fx_rc, bk_rc = fixed_broke(corr_full, corr_rec)
    fx_cb, bk_cb = fixed_broke(corr_full, corr_nocb)
    n_gold_absent = sum(1 for k in test_keys
                        if (dump_by_key.get(k) is not None and dump_by_key[k]["n_cands"] >= 2
                            and dump_by_key[k]["gold_idx"] < 0))
    n_decision = sum(1 for k in test_keys
                     if (dump_by_key.get(k) is not None and dump_by_key[k]["n_cands"] >= 2))
    autopsy = {
        "learned_vs_recency_fixed": fx_rc, "learned_vs_recency_broke": bk_rc,
        "learned_net_vs_recency": fx_rc - bk_rc,
        "cb_vs_nocb_fixed": fx_cb, "cb_vs_nocb_broke": bk_cb, "cb_net": fx_cb - bk_cb,
        "n_test_subset": len(test_keys), "n_learned_decisions_tpool2": n_decision,
        "n_gold_absent_from_pool": n_gold_absent,
    }

    # ---- arms-must-differ (test-subset correctness patterns) ----
    dig = {"learned_full": digest_bools(corr_full), "learned_nocb": digest_bools(corr_nocb),
           "recency_centrality": digest_bools(corr_rec)}
    arms_differ = (dig["learned_full"] != dig["recency_centrality"])
    learner_fit = (n_used > 0 and float(np.abs(w_full).sum()) > 1e-6)

    # ---- gates + verdict ----
    validity_ok = (validity_acc is not None and validity_acc <= VALIDITY_GATE_MAX)
    posctrl_ok = (recency_full_subset is not None
                  and abs(recency_full_subset - RECENCY_CENTRALITY_BANKED) <= POSCTRL_EPS)
    posctrl_gate = posctrl_ok if run_mode == "full" else True
    broken = (learned_full_test is not None and learned_full_test < SANITY_FLOOR)
    beat = (beat_delta is not None and beat_delta >= BEAT_MARGIN
            and stability is not None and stability >= HP_SIGN_STABILITY)
    cb_helps = (cb_delta is not None and cb_delta >= CB_MARGIN)

    if small:
        verdict = "UNKNOWN"
        verdict_msg = ("test subset / train too small (test_subset=%d, train_ex=%d)"
                       % (len(test_keys), len(train_ex)))
    elif not validity_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("VALIDITY GATE FAILED: single_sentence xsent acc=%s > %.2f (cross-sentence "
                       "memory not load-bearing)" % (_f(validity_acc), VALIDITY_GATE_MAX))
    elif not posctrl_gate:
        verdict = "HARD_FAIL"
        verdict_msg = ("POSITIVE-CONTROL FAILED: recency_centrality full backbone-subset=%s vs "
                       "banked 0.4523 (eps=%.3f) -- invocation/regime mismatch, downstream suspect"
                       % (_f(recency_full_subset), POSCTRL_EPS))
    elif not learner_fit:
        verdict = "HARD_FAIL"
        verdict_msg = ("LEARNER INERT: n_train_used=%d, |w|=%.3g -- the ranker never fit (bug)."
                       % (n_used, float(np.abs(w_full).sum())))
    elif broken:
        verdict = "HARD_FAIL"
        verdict_msg = ("LEARNED RANKER BROKEN: learned_full test=%s < sanity floor %.2f (below any "
                       "single real feature / near the 1/n_cands random floor) -- ranker/features "
                       "miswired." % (_f(learned_full_test), SANITY_FLOOR))
    elif beat and cb_helps:
        verdict = "HARD_PASS"
        verdict_msg = (
            "LEARNING BEATS THE HAND-RULE AND Cb-CONTINUITY IS THE LEVER: learned_full test "
            "backbone-subset=%s vs recency_centrality test=%s (beat delta=+%s, sign_stability=%s) "
            "AND Cb-ablation learned_nocb=%s (cb_delta=+%s >= %.2f). Learning curve %s->%s (rise "
            "%s). Net vs recency fixed=%d broke=%d. Importance(full)=%s."
            % (_f(learned_full_test), _f(recency_test), _f(beat_delta), _f(stability),
               _f(learned_nocb_test), _f(cb_delta), CB_MARGIN, _f(curve_first), _f(curve_last),
               _f(curve_rise), fx_rc, bk_rc, json.dumps(weights_glass["importance_full"])))
    else:
        rel = ("PLATEAUS AT" if (beat_delta is not None and abs(beat_delta) < BEAT_MARGIN)
               else ("beats-but-not-stable" if (beat_delta is not None and beat_delta >= BEAT_MARGIN)
                     else "is UNDER"))
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            "CLEAN LEARNING-CURVE-TO-A-BOUND (honest): valid + positive-control reproduces the "
            "banked 0.4523 (recency full backbone-subset=%s, local_window=%s, backbone=%s). The "
            "learned centering ranker %s the hand-rule: learned_full test=%s vs recency_centrality "
            "test=%s (beat delta=%s; HP needs >=+%.2f w/ stability>=%.2f, stability=%s). Cb-"
            "ablation: learned_nocb=%s (cb_delta=%s; needs >=+%.2f) => Cb-continuity %s. Learning "
            "curve %s->%s (rise %s). Net vs recency fixed=%d broke=%d. Importance(full)=%s. The "
            "same-gender residual is %s classic-centering (per the ablation)."
            % (_f(recency_full_subset), _f(localwindow_full_subset), _f(backbone_full_subset),
               rel, _f(learned_full_test), _f(recency_test), _f(beat_delta), BEAT_MARGIN,
               HP_SIGN_STABILITY, _f(stability), _f(learned_nocb_test), _f(cb_delta), CB_MARGIN,
               ("ADDS a real lift" if cb_helps else "adds ~nothing"),
               _f(curve_first), _f(curve_last), _f(curve_rise), fx_rc, bk_rc,
               json.dumps(weights_glass["importance_full"]),
               ("consistent with" if cb_helps else "NOT")))

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "%s: %s" % (ANCHOR_NAME, verdict),
        "elapsed_s": round(elapsed, 3), "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "corpus": {"source": "LitBank coref (dbamman/litbank), CC-BY 4.0",
                   "corpus_dir": CORPUS_DIR, "n_books_usable": len(books),
                   "n_books_parsed": len(ok_books)},
        "config": {
            "feature_names": FEATURE_NAMES, "cb_feature_idx": CB_IDX,
            "learner": "softmax_ranking_GD (in-substrate, glass-box); LEARNER MODULE "
                       "(hdlab/learner) is MDL classification/rule-induction, no ranking-loss "
                       "plugin -> escape-hatch linear ranker per cell-author discipline",
            "epochs": EPOCHS, "lr": LR, "l2": L2, "local_window": LOCAL_WINDOW,
            "test_every": TEST_EVERY, "n_train_books": len(train_books),
            "n_test_books": len(test_books),
            "subset_def": "xsent AND backbone suppressed-pool n_pool>=2 (the 29513/29514 wall)",
            "recency_centrality_banked": RECENCY_CENTRALITY_BANKED,
            "local_window_banked": LOCAL_WINDOW_BANKED, "backbone_banked": BACKBONE_BANKED,
            "bands": {"validity_gate_max": VALIDITY_GATE_MAX, "posctrl_eps": POSCTRL_EPS,
                      "beat_margin": BEAT_MARGIN, "cb_margin": CB_MARGIN,
                      "hp_sign_stability": HP_SIGN_STABILITY, "sanity_floor": SANITY_FLOOR},
            "pass_criterion": "valid AND posctrl reproduces 0.4523 AND learned_full >= recency "
                              "+ 0.02 (stability>=0.90) AND cb_delta >= 0.01",
        },
        "n_train_examples": len(train_ex), "n_test_subset": len(test_keys),
        "n_full_backbone_subset": len(all_keys),
        "validity_single_sentence_xsent_acc": validity_acc,
        "recency_centrality_full_subset_acc": recency_full_subset,
        "local_window_full_subset_acc": localwindow_full_subset,
        "backbone_full_subset_acc": backbone_full_subset,
        "recency_centrality_test_subset_acc": recency_test,
        "local_window_test_subset_acc": localwindow_test,
        "learned_full_test_subset_acc": learned_full_test,
        "learned_nocb_test_subset_acc": learned_nocb_test,
        "handrule_fixed_rolerule_test_subset_acc": handrule_fixed_test,
        "single_feature_test_subset_acc": single_feat_test,
        "best_single_feature_test_subset_acc": best_single_feat_test,
        "learned_beats_fixed_rolerule": learned_beats_fixed,
        "beat_delta_learned_minus_recency": beat_delta,
        "cb_delta_full_minus_nocb": cb_delta,
        "sign_stability_learned_vs_recency": stability,
        "learning_curve": learning_curve, "learning_curve_rise": curve_rise,
        "weights_glassbox": weights_glass, "glass_box_traces": traces, "autopsy": autopsy,
        "arms_differ_digests": dig, "arms_differ_verified": arms_differ, "learner_fit": learner_fit,
        "validity_ok": validity_ok, "posctrl_ok": posctrl_ok, "beat": beat, "cb_helps": cb_helps,
        "broken": broken,
        "per_book": per_book, "book_failures": book_failures,
        "train_books": train_books, "test_books": test_books,
        "expected_n_units": len(books),
        "cardinality_ok": (len(per_book) == len(books) - len(book_failures)),
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics, out_dir


# ----------------------------------------------------------------------------
# markers / crash-diagnostic (atomic)
# ----------------------------------------------------------------------------
def _write_start_marker(out_dir, run_mode, expected_n):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n, "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_crash_metrics(out_dir, exc):
    os.makedirs(out_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "anchor_name": ANCHOR_NAME,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ----------------------------------------------------------------------------
# SELF-TEST (real code path)
# ----------------------------------------------------------------------------
def _mk(head, cluster, is_pron, sent, midx, gender, role_rank, number="singular",
        name_gender=None):
    return {"head": head, "cluster": cluster, "is_pronoun": is_pron,
            "sent_idx": sent, "midx": midx, "gender": gender, "number": number,
            "name_gender": name_gender, "sent_role_rank": role_rank,
            "is_subject": (role_rank == 0), "span_toks": [head]}


def self_test():
    # A cb-decisive doc: anna = global protagonist (subject mass); bella = subject of the PRIOR
    # sentence (the Cb); gold = bella (continuity). role -> anna, cb -> bella.
    mentions, mi = [], 0
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 1, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("anna", 1, False, 2, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("bella", 2, False, 3, mi, "fem", 0, name_gender="fem")); mi += 1  # prior-sent subject
    mentions.append(_mk("she", 2, True, 4, mi, "fem", 0)); mi += 1     # gold=bella (Cb continuity)
    targets = build_pronoun_targets(mentions)
    assert len(targets) == 1, "expected 1 target"
    n_sents = max(m["sent_idx"] for m in mentions) + 1
    sid = fixed_window_scenes(n_sents, LOCAL_WINDOW)

    lr = LearnedCenteringReader()
    recs = lr.resolve_stream(mentions, targets, scene_ids=sid, topical_mode="rolemass",
                             weights=None)
    assert len(recs) == 1 and lr.last_features, "no records/features from learned reader"
    fd = lr.last_features[0]
    assert fd["n_cands"] == 2, "expected 2 same-gender cands, got %d" % fd["n_cands"]
    heads = fd["cand_heads"]
    ai, bi = heads.index("anna"), heads.index("bella")
    assert fd["X_raw"][bi][CB_IDX] == 1.0 and fd["X_raw"][ai][CB_IDX] == 0.0, "cb should flag bella"
    assert fd["X_raw"][ai][0] > fd["X_raw"][bi][0], "anna should have more role-mass"
    assert fd["gold_idx"] == bi, "gold should be bella"
    _p("[self-test] learned reader pool + 5 features (cb flags prior-sentence subject bella): OK")

    # cb-only weights CHANGE the pick vs role-only (the one variable).
    mean = np.zeros(N_FEAT); std = np.ones(N_FEAT); mask = np.ones(N_FEAT)
    w_role = np.zeros(N_FEAT); w_role[0] = 1.0
    w_cb = np.zeros(N_FEAT); w_cb[CB_IDX] = 1.0
    r_role = lr.resolve_stream(mentions, targets, scene_ids=sid, topical_mode="rolemass",
                               weights=w_role, feat_mean=mean, feat_std=std, feat_mask=mask)
    r_cb = lr.resolve_stream(mentions, targets, scene_ids=sid, topical_mode="rolemass",
                             weights=w_cb, feat_mean=mean, feat_std=std, feat_mask=mask)
    assert r_role[0]["resolved_head"] == "anna", "role-only must pick anna"
    assert r_cb[0]["resolved_head"] == "bella", "cb-only must pick bella"
    assert r_cb[0]["correct"] and not r_role[0]["correct"], "cb right, role wrong here"
    _p("[self-test] Cb feature is decision-load-bearing (cb-only->bella beats role-only->anna)")

    # softmax ranker LEARNS to solve the cb-decisive example.
    exs = [dict(fd)]
    m2, s2 = standardize_stats(exs)
    w_learned, n_used = train_softmax_ranker(exs, mask, m2, s2, epochs=300)
    assert n_used == 1, "expected 1 training example"
    c, _pk = predict_correct(exs[0], w_learned, m2, s2, mask)
    assert c == 1, "learned ranker should solve the cb-decisive training example"
    assert w_learned[CB_IDX] > 0, "learned cb weight should be positive on a cb-decisive example"
    _p("[self-test] softmax ranker fits + learns positive cb weight (%.3f)" % w_learned[CB_IDX])

    # REAL code path: temp conll -> parse + baseline readers + learned reader via evaluate_book.
    import tempfile

    def tok(tidx, word, coref="_"):
        return "selftest\t0\t%d\t%s\t_\t_\t_\t_\t_\t_\t_\t_\t%s" % (tidx, word, coref)
    lines = ["#begin document (selftest); part 0"]
    lines += [tok(0, "Anna", "(1)"), tok(1, "summoned"), tok(2, "the"),
              tok(3, "servants", "(2)"), tok(4, "."), ""]
    lines += [tok(0, "She", "(1)"), tok(1, "left"), tok(2, "."), ""]
    with tempfile.NamedTemporaryFile("w", suffix=".conll", delete=False, encoding="utf-8") as tf:
        tf.write("\n".join(lines) + "\n")
        tmp_path = tf.name
    try:
        gaz = load_name_gender()
        base_recs, feats = evaluate_book(tmp_path, gaz, CorefReader(), SuppressReader(),
                                         SceneProtagonistReader(),
                                         EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED),
                                         LearnedCenteringReader())
        assert base_recs, "no base records from evaluate_book"
        ss_acc = acc([r["correct"]["single_sentence"] for r in base_recs])
        assert ss_acc is not None and ss_acc <= VALIDITY_GATE_MAX, "validity gate: %.3f" % ss_acc
        _p("[self-test] real code path: temp conll + baselines + learned reader via evaluate_book OK")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    _p("[self-test] PASS (glass-box, deterministic, no network)")
    return 0


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    run_mode = "smoke" if args.smoke else "full"
    metrics, out_dir = run(run_mode)
    _p("[%s] verdict=%s" % (run_mode, metrics["verdict"]))
    _p(metrics["verdict_msg"])
    _p("validity(single_sentence xsent)=%s" % _f(metrics["validity_single_sentence_xsent_acc"]))
    _p("posctrl full backbone-subset: recency=%s (banked 0.4523) local=%s backbone=%s"
       % (_f(metrics["recency_centrality_full_subset_acc"]),
          _f(metrics["local_window_full_subset_acc"]), _f(metrics["backbone_full_subset_acc"])))
    _p("TEST backbone-subset (n=%d): learned_full=%s learned_nocb=%s recency=%s local=%s"
       % (metrics["n_test_subset"], _f(metrics["learned_full_test_subset_acc"]),
          _f(metrics["learned_nocb_test_subset_acc"]), _f(metrics["recency_centrality_test_subset_acc"]),
          _f(metrics["local_window_test_subset_acc"])))
    _p("selected model: full=%s (val=%s)  nocb=%s (val=%s)"
       % (metrics["weights_glassbox"]["selected_full"], _f(metrics["weights_glassbox"]["val_acc_full"]),
          metrics["weights_glassbox"]["selected_nocb"], _f(metrics["weights_glassbox"]["val_acc_nocb"])))
    _p("fair internal ref: fixed role-rule (identical features)=%s  best_single_feat=%s  "
       "learned_beats_fixed=%s"
       % (_f(metrics["handrule_fixed_rolerule_test_subset_acc"]),
          _f(metrics["best_single_feature_test_subset_acc"]),
          _f(metrics["learned_beats_fixed_rolerule"])))
    _p("D1 beat_delta(learned-recency)=%s  D2 cb_delta(full-nocb)=%s  stability=%s"
       % (_f(metrics["beat_delta_learned_minus_recency"]), _f(metrics["cb_delta_full_minus_nocb"]),
          _f(metrics["sign_stability_learned_vs_recency"])))
    _p("learning curve: %s" % json.dumps([(c["n_books"], _f(c["test_acc"]))
                                          for c in metrics["learning_curve"]]))
    _p("importance(full)=%s" % json.dumps(metrics["weights_glassbox"]["importance_full"]))
    _p("autopsy=%s" % json.dumps(metrics["autopsy"]))
    _p("metrics -> %s" % os.path.join(out_dir, "metrics.json"))


if __name__ == "__main__":
    _out = os.path.join(REPO_ROOT, "data", "exp_%s" % ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- crash-diag then re-raise (no BaseException)
        _write_crash_metrics(_out, e)
        raise
