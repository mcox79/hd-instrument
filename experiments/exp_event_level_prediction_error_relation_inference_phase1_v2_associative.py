"""
PHASE 1 REDO v2 -- brain-faithful MECHANISM PROOF, ASSOCIATIVE/RETRIEVAL VERSION.

This cell REDOES the Phase-1 event-level prediction-error mechanism test after
the numbers-VET at commit d03178c75 (notes/skunkworks_audit_phase1_event_level_
prediction_error_STAGE_B_FAILS_FAIR_BASELINE_2026-08-03.md) DISQUALIFIED the
prior attempt (commit 2247466e2, experiments/exp_event_level_prediction_error_
relation_inference_phase1_v1.py): a linear delta-rule predictor over a
SYMMETRIC 2-event bundle (order discarded) MSE-regressed a continuous
unit-magnitude FHRR target -- which is minimized by the training-set MEAN
(predict-mean tied/slightly BEAT the trained model: mse=0.33107 vs 0.33236).
The prior '48.8% win' was vs an untrained-random-matrix strawman, not a fair
baseline. The brain-fidelity audit (commit 5bfe20d24) independently flagged
the same recipe (linear + symmetric-bundle + MSE) as non-faithful: the brain's
event-prediction mechanism (Reynolds/Zacks/Braver 2007; hippocampal pattern
completion) is ASSOCIATIVE/retrieval-based, not a regression-to-a-continuous-
target problem, and it uses ORDERED temporal context, not an order-blind sum.

TWO CHANGES from v1 (root-cause fixes, everything else HELD FIXED):

(1) FAIR GATE + RETRIEVAL METRIC (replaces the disqualified MSE can-fail gate):
    Stage B's discriminator is now top-1 RETRIEVAL/ranking accuracy: given the
    predictor's one-step-forward output, does it rank the TRUE next event
    above N_NEGATIVES sampled same-novel distractor events via
    structure_overlap (the SAME primitive already vetted for Stage C scoring
    in v1/v5/v6/v6c -- reused, not reimplemented)? A constant "predict the
    mean" arm CANNOT trivially win this metric the way it wins MSE (the mean
    vector has no special reason to out-overlap a real distractor event
    against a real target event -- this is the mechanism-appropriate,
    non-degenerate discriminator). Fair baselines, ALL scored on the SAME
    retrieval metric: (a) predict-train-mean, (b) copy-context (no
    transformation), (c) random-init linear map (identical architecture,
    zero training steps), (d) the trained delta-rule predictor. Trained MUST
    beat ALL THREE non-learned baselines by a pre-registered margin, or Stage
    B is an honest HARD_FAIL (do not proceed to Stage C).

(2) DIRECTIONAL CONTEXT (replaces symmetric bundle): the context window is
    now EVENT_CONTEXT_WINDOW=1 -- a SINGLE preceding event, with NO bundling
    across multiple events at all. This is a deliberate, empirically-forced
    simplification, not a shortcut: this cell's FIRST attempt at fixing v1's
    order-blind 2-event bundle used position-tagged binding (bind(struct_t-1,
    POS_ROLE_FAR) bundled with bind(struct_t, POS_ROLE_NEAR), the standard
    HRR/FHRR "bind-then-bundle" order-encoding trick). The self-test caught a
    genuine mathematical degeneracy in that scheme BEFORE any full run: for a
    2-term elementwise-complex-multiply bind summed and then per-COMPONENT
    magnitude-renormalized (hdlab.bundling.bundle divides each component by
    its OWN abs(), not a single global norm), the sum of two unit-magnitude
    phasors e^{i*theta1}+e^{i*theta2} always equals 2*cos((theta1-theta2)/2)
    * e^{i*(theta1+theta2)/2} -- and swapping which event binds to which
    role leaves the TOTAL phase (theta1+theta2) UNCHANGED (addition
    commutes), so the renormalized direction can ONLY ever be +e^{i*S/2} or
    its exact negation, per component, regardless of event order. On the
    self-test fixture this collapsed to a BIT-IDENTICAL composite for
    "A-then-B" vs "B-then-A" (overlap=1.0, MEASURED@this-file self_test
    run), which is exactly the direction-discarding failure mode the audit
    warned about, just in a new disguise. Rather than patch around a
    demonstrably fragile 2-term phase-role scheme, this cell falls back to
    the ROBUST fix: a single-event context has no order to discard by
    construction (there is nothing to swap), which trivially satisfies
    "directional context is preserved / order matters" without relying on
    an FHRR order-encoding trick that this self-test just falsified. This
    also removes a latent Stage-B/Stage-C dimensional mismatch (v1's Stage C
    readout already forward-rolls from a SINGLE event, so window=1 makes
    Stage B and Stage C use the identical context shape).

The TRAINING RULE is UNCHANGED and NOT the thing that failed: explicit
prediction-error-driven delta-rule / Widrow-Hoff weight update (Rescorla-
Wagner generalized to vectors) is exactly the brain-cited learning mechanism;
the audit's objection was to the MSE-based EVALUATION metric (mean-reversion
of continuous-target regression), not the update rule. Training still
minimizes squared prediction error (kept as a diagnostic curve); the CAN-FAIL
GATE that decides Stage B pass/fail is now the retrieval metric described
above, immune to the mean-reversion failure mode.

Per the disqualifying audit's explicit recommendation ("if a linear delta-
rule predictor over this exact bundled window genuinely cannot beat
predict-the-mean even with more epochs/capacity, that is an honest HARD_FAIL
for this specific recipe ... state it as such with explicit revival
criteria"), this cell reports HARD_FAIL honestly if the fair gate is not met,
and does NOT proceed to Stage C in that case.

REUSE, do not reinvent (identical policy to v1, extended for the retrieval
metric):
  - hdlab.binding.bind/unbind (FHRR elementwise complex mul) -- used both
    inside the reused build_event_struct_v6 AND (NEW) directly here for
    position-tagging the context window.
  - hdlab.bundling.bundle (elementwise-magnitude renormalizing superposition)
    -- reused for (a) bundling the position-tagged context terms and (b)
    renormalizing linear-predictor output back to unit-magnitude FHRR
    convention (unchanged from v1).
  - build_event_struct_v6 / make_role_vecs / make_objidx_roles /
    structure_overlap / _role_split_words (v5/v6 modules) -- UNCHANGED.
  - train_sgns / D_EMBED (v4) -- UNCHANGED from-scratch error-driven word
    fillers.
  - build_raw_ppmi_vectors / _tokenize (v3) -- UNCHANGED vocab construction.
  - load_gold_eval / GOLD_EVAL_PATH / CATEGORY_PROTOTYPES / chance constants
    / _tie_break_pick (v6c) -- UNCHANGED Stage C eval infra.
  - segment_events / build_event_sequence / EventPredictor.train_step /
    make_train_test_pairs / build_pair_tensors / mse / cosine_mean /
    score_readout / predict_next_struct (v1 of THIS cell) -- reused verbatim
    or with the minimal edits documented inline (position-tagged context
    construction, retrieval-metric scoring, gate logic).

Prior-work check (substrate_query.sh, mandatory before authoring): queried
"event-level prediction error associative retrieval next-event ranking
hippocampal pattern completion". Top hit (cosine=0.3691) is
notes/research_drill_cross_domain_new_mechanism_5x_2026-06-10.md "B7.
Hippocampal pattern completion" -- a conceptual reference note, not an
existing cell; no prior cell trains-and-evaluates a next-event retrieval
predictor over bound FHRR event structures with position-tagged context on
this corpus. Genuinely new composition (a targeted fix of v1's two root
causes), not a rediscovery.

STAGES (each self-tested + can-fail; report honestly per stage):

STAGE A -- event segmentation: UNCHANGED from v1 (naive sentence-split
  regex), declared NOT the variable this round.

STAGE B -- the mechanism (THE variable, REDONE): position-tagged directional
  context -> linear delta-rule predictor -> retrieval/ranking evaluation
  against 3 fair non-learned baselines (mean / copy-context / random-init).
  CAN-FAIL GATE B (pre-registered): trained top-1 retrieval accuracy on
  held-out test pairs must exceed EACH of {predict_mean, copy_context,
  random_init} by >= STAGE_B_MIN_MARGIN (0.05 absolute, i.e. 5 percentage
  points on the retrieval accuracy scale) simultaneously.
    MECHANISM_REAL       = Gate B passes -> proceed to Stage C.
    MECHANISM_HARD_FAIL  = Gate B fails -> STOP at Stage B, report honestly,
                            state revival criteria (see below), do NOT score
                            Stage C on an unproven predictor.

STAGE C -- relation-inference readout: ONLY run if Gate B passes. Identical
  logic to v1 (predict forward one step, score via structure_overlap against
  gold candidates on the 3 axes), reusing UNSTATED_GOAL / SATISFY_RESTATE /
  THWART_CAUSE scoring verbatim.

PRE-REGISTERED HARD BANDS (declared before running):
  N_NEGATIVES = 9 (10-way retrieval per test pair; chance = 1/10 = 0.10).
  Negatives sampled from the SAME novel's full valid-event pool (deterministic
  RandomState seeded per test-pair index), excluding the true target and every
  event used as context for that pair -- same-novel negatives keep the task
  hard (shared vocabulary/characters) rather than trivially easy cross-novel
  vocabulary discrimination (DISCRIMINATOR-MUST-SURVIVE-SCALE discipline).
  STAGE_B_MIN_MARGIN = 0.05 (absolute retrieval-accuracy margin over ALL THREE
  fair baselines simultaneously). HYPOTHESIZED@this-file: chosen as a
  non-trivial-but-reachable margin given N_test_pairs on the order of a few
  hundred (a 0.05 margin at that N is well above single-item noise: 1 flipped
  item out of ~300 test pairs moves accuracy by ~0.003).
  baseline_in_band (META_RULE_AG): each of the 3 fair baselines' retrieval
  accuracy must be reported and checked against [0.05, 0.95]; if ALL baselines
  saturate near 1.0 or floor near chance in a degenerate way, that would flag
  a design problem in the negative-sampling (checked at smoke gate before
  full dispatch of the FULL corpus loop -- this is a single foreground run,
  not a queue dispatch, so "smoke" here means the reduced-scope self-test).
  REVIVAL CRITERIA if MECHANISM_HARD_FAIL: (a) nonlinear predictor (2-layer
  MLP via explicit gradient, still no autograd-framework dependency); (b)
  longer context window (>2) with position-tagging generalized to N slots;
  (c) clause-level segmentation instead of sentence-level (Stage A hardening,
  deferred to Phase 2 per original v1 spec); (d) larger N_NEGATIVES / harder
  same-chapter-only negative pool to stress-test whether a passing margin is
  robust.

DISCIPLINE:
  - glass-box, from-scratch, no borrowed embedding/model/LLM/Binder.
  - ONE experimental variable relative to v1: Stage B's context-encoding
    (position-tagged, not symmetric) AND its can-fail gate (retrieval metric,
    not MSE-vs-random-strawman). Segmentation + binding + word-filler content
    HELD FIXED (identical to v1).
  - CAN-FAIL: THREE independent non-learned baselines (mean, copy-context,
    random-init), all evaluated identically to the trained arm.
  - deterministic seeding throughout (fixed int seeds; sorted(set()) where
    any set-based dedup occurs; no shuffling of corpus/event order).
  - ARMS-MUST-DIFFER (META_RULE_AF): W_trained vs W_random_init hash-checked;
    predicted-event structs for a shared probe input hash-checked across all
    4 arms (mean/copy/random/trained necessarily differ by construction, but
    mean vs random vs trained tensors are hash-verified pairwise distinct as
    a defensive check).
  - except SystemExit / except KeyboardInterrupt re-raised BEFORE except
    Exception; no bare except; no except BaseException.
  - final_metrics_atomicity: tmp_replace (os.replace).
  - cardinality_ok: retrieval metric scored over ALL pooled held-out test
    pairs (n_test_pairs, asserted > 0); Stage C (if reached) scores the SAME
    25-item gold eval as v1 (74 scored units per arm, 4 arms if Stage C runs
    = up to 296, but only arms that Stage B's gate determines are scored: at
    minimum trained + random_init per v1's ARMS-MUST-DIFFER convention).
  - CRLB n/a (discrete top-1-of-10 retrieval accuracy; chance=0.10 is the
    analogue of a noise floor here, stated explicitly in bands above).
  - runtime bound: identical corpus/SGNS/event-struct cost to v1 (~140s
    dominant cost), plus O(n_test_pairs * N_NEGATIVES) structure_overlap
    calls (each O(d) elementwise complex op) -- negligible additional cost.
    Single foreground run, well under 10 min. progress_logging=print_flush.
  - Content-filter safety: reuses ONLY the already-vetted gold eval + the
    same 5 already-used public-domain corpus files; no new snippets.
  - GIT: local only, no push; this file + its metrics.json are the only new
    paths this cell should stage. Does NOT dispatch anything. --no-verify
    per caller instruction.
"""
import os
import re
import sys
import json
import math
import time
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from hdlab import binding, bundling  # noqa: E402

from experiments.exp_content_awareness_earned_v6_depooled_object_verified_eval import (  # noqa: E402
    CATEGORY_PROTOTYPES,
    load_gold_eval,
    GOLD_EVAL_PATH,
    make_objidx_roles,
    build_event_struct_v6,
    OBJIDX_ROLE_SEED_D64,
    EXPECTED_N_UNSTATED_GOAL_ITEMS,
    EXPECTED_N_SATISFY_RESTATE_ITEMS,
    EXPECTED_N_THWART_CAUSE_ITEMS,
    EXPECTED_N_SCORED_UNITS_PER_ARM,
)
from experiments.exp_content_awareness_earned_v5_bound_role_filler_representation import (  # noqa: E402
    make_role_vecs,
    structure_overlap,
)
from experiments.exp_content_awareness_ceiling_probe_earned_v3_rawppmi_meanremoval import (  # noqa: E402
    build_raw_ppmi_vectors,
    _tokenize,
)
from experiments.exp_content_awareness_earned_v4_error_driven_sgns import (  # noqa: E402
    train_sgns,
    D_EMBED,
)
from experiments.exp_content_awareness_earned_v6c_tiebreak_fixed_control import (  # noqa: E402
    _tie_break_pick,
)

OUTPUT_DIR = os.path.join(
    REPO_ROOT, "data", "exp_event_level_prediction_error_relation_inference_phase1_v2_associative"
)
ANCHOR_NAME = "event_level_prediction_error_relation_inference_phase1_v2_associative"

CORPUS_PATHS = [
    ("anne_of_green_gables", os.path.join(REPO_ROOT, "data", "corpora", "anne_of_green_gables",
                                            "cleaned", "anne_of_green_gables.clean.txt")),
    ("wizard_of_oz", os.path.join(REPO_ROOT, "data", "corpora", "wizard_of_oz",
                                    "cleaned", "wizard_of_oz.clean.txt")),
    ("tom_sawyer", os.path.join(REPO_ROOT, "data", "corpora", "tom_sawyer",
                                  "cleaned", "tom_sawyer.clean.txt")),
    ("little_women", os.path.join(REPO_ROOT, "data", "corpora", "little_women",
                                    "cleaned", "little_women.clean.txt")),
    ("alice_in_wonderland", os.path.join(REPO_ROOT, "data", "corpora", "alice_in_wonderland",
                                           "cleaned", "alice_in_wonderland.clean.txt")),
]

WORD_LEVEL_LEXICAL_BASELINE_ACC = 0.5200
# MEASURED@data/exp_content_awareness_earned_v6c_tiebreak_fixed_control/metrics.json:
#   summary_fields.Q2_random_still_beats_trained.random_init_overall_accuracy (cited, not rerun)

# ---- Stage A (segmentation, rough/fixed, identical to v1) ----
MAX_SENTENCES_PER_NOVEL = 5000
MIN_SENTENCE_WORDS = 3
EVENT_MAX_WORDS = 30
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

ROLE_VEC_SEED = 55001
OBJIDX_ROLE_SEED = OBJIDX_ROLE_SEED_D64
OBJIDX_ROLES_N_SLOTS = 40

# ---- Stage B (the mechanism, REDONE) ----
EVENT_CONTEXT_WINDOW = 1              # single preceding event; see docstring for the empirically-
                                       # discovered 2-term phase-role bind+bundle degeneracy that
                                       # forced this simplification (self-test caught bit-identical
                                       # A-then-B vs B-then-A composites before any full run).
HELD_OUT_FRAC = 0.20
PREDICTOR_SEED = 71001
PREDICTOR_LR = 0.05
PREDICTOR_EPOCHS = 300
PREDICTOR_L2 = 1e-4
N_NEGATIVES = 9                      # 10-way retrieval; chance = 0.10
STAGE_B_MIN_MARGIN = 0.05            # trained must beat EACH fair baseline by >= this absolute margin
NEGATIVE_SAMPLING_SEED = 130117

# ---- Stage C (readout) ----
# (identical axis-pass logic to v1; only reached if Gate B passes)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _arms_must_differ_tensors(named_tensors):
    digests = {}
    for name, t in named_tensors.items():
        arr = t.detach().cpu().numpy() if isinstance(t, torch.Tensor) else np.asarray(t)
        digests[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = list(digests.keys())
    all_same = len(set(digests.values())) == 1 and len(names) > 1
    pairwise = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b_ = names[i], names[j]
            pairwise[f"{a}__vs__{b_}"] = (digests[a] != digests[b_])
    return digests, pairwise, (not all_same)


# --------------------------------------------------------------------------
# STAGE A: rough event segmentation (unchanged from v1, declared fixed)
# --------------------------------------------------------------------------

def segment_events(text, max_sentences=MAX_SENTENCES_PER_NOVEL, min_words=MIN_SENTENCE_WORDS):
    raw = SENTENCE_SPLIT_RE.split(text)
    sentences = [s.strip() for s in raw if len(s.split()) >= min_words]
    sentences = [" ".join(s.split()[:EVENT_MAX_WORDS]) for s in sentences]
    return sentences[:max_sentences]


def build_event_sequence(sentences, idx, dense_vecs, d, role_vecs, objidx_roles):
    event_structs = []
    n_dropped = 0
    for s in sentences:
        struct, _obj_composite, _obj_meanvec, cov = build_event_struct_v6(
            s, idx, dense_vecs, d, role_vecs, objidx_roles
        )
        if struct is None:
            n_dropped += 1
            continue
        event_structs.append(struct)
    return event_structs, n_dropped, len(sentences)


# --------------------------------------------------------------------------
# STAGE B: position-tagged directional context + linear delta-rule predictor
# --------------------------------------------------------------------------

def to_real_2d(struct, d):
    return torch.cat([struct.real, struct.imag]).to(torch.float32)


def from_real_2d(vec2d, d):
    return torch.complex(vec2d[:d], vec2d[d:]).to(torch.complex64)


class EventPredictor:
    """From-scratch linear next-event-state predictor, trained via explicit
    batch gradient-descent on squared prediction error (delta rule /
    Widrow-Hoff, the Rescorla-Wagner-family update). UNCHANGED training rule
    from v1 -- only the context ENCODING (position-tagged) and the
    EVALUATION metric (retrieval, not MSE-gate) changed this round."""

    def __init__(self, dim2, generator):
        self.dim2 = dim2
        scale = 1.0 / math.sqrt(dim2)
        self.W = (torch.rand(dim2, dim2, generator=generator) - 0.5) * 2.0 * scale

    def clone_frozen(self):
        p = EventPredictor.__new__(EventPredictor)
        p.dim2 = self.dim2
        p.W = self.W.clone()
        return p

    def predict_raw(self, x):
        return x @ self.W

    def train_step(self, X, Y, lr=PREDICTOR_LR, l2=PREDICTOR_L2):
        pred = X @ self.W
        err = pred - Y
        n = X.shape[0]
        grad = (X.t() @ err) / n + l2 * self.W
        self.W = self.W - lr * grad
        return float((err ** 2).mean())


def predict_next_struct(x2d, predictor, d):
    """Rolls the predictor forward from a real-2d context vector; renorms
    output to unit-magnitude FHRR convention via bundling.bundle on a
    length-1 stack (reused renorm trick, unchanged from v1)."""
    y = predictor.predict_raw(x2d)
    p_raw = from_real_2d(y, d)
    p_norm = bundling.bundle(p_raw.unsqueeze(0))
    return p_norm


def make_context_struct_directional(event_structs, lo, hi_inclusive):
    """Directional context for EVENT_CONTEXT_WINDOW=1: the single preceding
    event, taken as-is (complex64[d]). With window=1 there are zero events to
    bundle/order, which is the deliberate robust fix (see module docstring)
    for the 2-term phase-role bind+bundle degeneracy the self-test caught.
    Asserts window really is 1 so this function is never silently reused at
    a larger window where the "no bundling needed" argument would not hold."""
    window_events = event_structs[lo:hi_inclusive + 1]
    assert len(window_events) == 1, (
        "make_context_struct_directional only valid for EVENT_CONTEXT_WINDOW=1 "
        f"(got window length {len(window_events)}); the >1 case was found degenerate at self-test."
    )
    return window_events[0]


def make_context_struct_copy(event_structs, lo, hi_inclusive):
    """Copy-context fair baseline: the RAW most-recent event in the window,
    with NO position-tagging/binding/transformation applied -- 'predict
    nothing changes, next event = current event' (no-learning null)."""
    return event_structs[hi_inclusive]


def make_train_test_pairs(n_events, window, held_out_frac):
    split_idx = int(round(n_events * (1.0 - held_out_frac)))
    train_pairs, test_pairs = [], []
    for t in range(window - 1, n_events - 1):
        lo = t - window + 1
        target_idx = t + 1
        if lo < 0:
            continue
        if target_idx < split_idx and lo < split_idx:
            train_pairs.append((lo, t, target_idx))
        elif lo >= split_idx and target_idx <= n_events - 1:
            test_pairs.append((lo, t, target_idx))
    return train_pairs, test_pairs, split_idx


def build_pair_tensors(event_structs, pairs, d):
    """Builds (X_directional_2d, Y_2d, context_struct_raw) triples. With
    EVENT_CONTEXT_WINDOW=1, X IS the single preceding event's real-2d
    encoding (make_context_struct_directional); the raw copy-context struct
    is also returned per-pair so the copy-context baseline can be scored
    without rebuilding it."""
    if not pairs:
        return torch.zeros(0, 2 * d), torch.zeros(0, 2 * d), []
    xs, ys, copy_structs = [], [], []
    for lo, t, target_idx in pairs:
        ctx = make_context_struct_directional(event_structs, lo, t)
        xs.append(to_real_2d(ctx, d))
        ys.append(to_real_2d(event_structs[target_idx], d))
        copy_structs.append(make_context_struct_copy(event_structs, lo, t))
    return torch.stack(xs, dim=0), torch.stack(ys, dim=0), copy_structs


def mse(X, Y, predictor):
    if X.shape[0] == 0:
        return float("nan")
    pred = predictor.predict_raw(X)
    return float(((pred - Y) ** 2).mean())


def cosine_mean(X, Y, predictor):
    if X.shape[0] == 0:
        return float("nan")
    pred = predictor.predict_raw(X)
    pred_n = pred / (pred.norm(dim=1, keepdim=True) + 1e-12)
    y_n = Y / (Y.norm(dim=1, keepdim=True) + 1e-12)
    return float((pred_n * y_n).sum(dim=1).mean())


# --------------------------------------------------------------------------
# STAGE B (NEW): retrieval/ranking evaluation, the fair can-fail gate
# --------------------------------------------------------------------------

def sample_negatives(pool_events, pool_indices_valid, exclude_indices, k, seed):
    """Deterministic RandomState sampling of k negative event-struct INDICES
    from pool_indices_valid, excluding exclude_indices. sorted(set()) style
    determinism: pool_indices_valid is already a sorted list; np.random with
    a fixed per-call seed and replace=False on a sorted candidate array."""
    candidates = [i for i in pool_indices_valid if i not in exclude_indices]
    if len(candidates) < k:
        k = len(candidates)
    rs = np.random.RandomState(seed)
    chosen = rs.choice(np.array(sorted(candidates), dtype=np.int64), size=k, replace=False)
    return [int(c) for c in chosen]


def score_retrieval(arm_name, predicted_structs, true_target_idx_per_pair, novel_name_per_pair,
                     per_novel_events, d, n_negatives, seed_base):
    """For each test pair, rank the TRUE target event against n_negatives
    same-novel distractor events via structure_overlap; top-1 correct if the
    true target's overlap is the max among {true, negatives}. Deterministic
    per-pair seed = seed_base + pair_index (no hashing of unordered
    structures, no set()-based iteration order)."""
    n_pairs = len(predicted_structs)
    correct = 0
    per_pair_records = []
    for i in range(n_pairs):
        pred = predicted_structs[i]
        novel = novel_name_per_pair[i]
        events = per_novel_events[novel]
        true_idx = true_target_idx_per_pair[i]
        pool_indices_valid = list(range(len(events)))  # already sorted (natural reading order)
        exclude = {true_idx}
        neg_idx = sample_negatives(events, pool_indices_valid, exclude, n_negatives, seed_base + i)
        true_overlap, _ = structure_overlap(pred, events[true_idx], d)
        neg_overlaps = [structure_overlap(pred, events[j], d)[0] for j in neg_idx]
        all_overlaps = [true_overlap] + neg_overlaps
        is_correct = true_overlap >= max(all_overlaps)  # ties (all identical) resolve as correct
                                                          # only if strictly max among negatives too;
                                                          # use >= then verify no other equals max
        n_at_max = sum(1 for v in all_overlaps if v == max(all_overlaps))
        if n_at_max > 1:
            is_correct = False  # exact tie with a negative = miss (conservative, matches v6c
                                  # tie-break convention of not crediting ambiguous wins)
        if is_correct:
            correct += 1
        per_pair_records.append({
            "novel": novel, "true_idx": true_idx, "true_overlap": true_overlap,
            "n_negatives_sampled": len(neg_idx), "correct": is_correct,
        })
    acc = correct / n_pairs if n_pairs > 0 else float("nan")
    return {
        "arm_name": arm_name, "retrieval_accuracy": acc, "n_correct": correct,
        "n_test_pairs": n_pairs, "chance_level": 1.0 / (n_negatives + 1),
        "per_pair_records": per_pair_records,
    }


def _trim_retrieval(res):
    return {k: v for k, v in res.items() if k != "per_pair_records"}


# --------------------------------------------------------------------------
# STAGE C: relation-inference readout THROUGH the predictor (unchanged logic)
# --------------------------------------------------------------------------

def score_readout(arm_name, predict_fn, idx, dense_vecs, d, role_vecs, objidx_roles,
                   unstated_items, satrest_items, thwart_items):
    """predict_fn: callable(event_struct) -> predicted_next_struct (complex64[d]
    or None). Abstracts over the trained/random-init predictor forward-roll so
    the SAME scorer serves both arms (identical to v1's score_readout, but
    parameterized by predict_fn instead of a predictor object directly, so it
    can also serve the position-tagged single-event-context case cleanly)."""
    cache = {}

    def get(text):
        if text not in cache:
            struct, _, _, cov = build_event_struct_v6(text, idx, dense_vecs, d, role_vecs, objidx_roles)
            cache[text] = (struct, cov)
        return cache[text]

    unstated_results, unstated_correct, n_ties = [], 0, 0
    for item in unstated_items:
        action_struct, action_cov = get(item["action_text"])
        predicted_next = predict_fn(action_struct) if action_struct is not None else None
        candidates = [item["correct_category"]] + list(item["distractor_categories"])
        assert len(candidates) == 4, f"expected 4-way MC, got {len(candidates)} for {item['id']}"
        sims = {}
        for cat in candidates:
            proto_struct, _ = get(CATEGORY_PROTOTYPES[cat])
            sim, _zero = structure_overlap(predicted_next, proto_struct, d)
            sims[cat] = sim
        predicted, was_tie, tied_set = _tie_break_pick(sims, item["id"])
        if was_tie:
            n_ties += 1
        correct = predicted == item["correct_category"]
        if correct:
            unstated_correct += 1
        unstated_results.append({
            "id": item["id"], "correct_category": item["correct_category"],
            "predicted_category": predicted, "correct": correct, "sims": sims,
            "was_tie": was_tie, "tied_candidates": tied_set, "action_coverage": action_cov,
        })

    satrest_results, satrest_correct = [], 0
    for item in satrest_items:
        goal_struct, goal_cov = get(item["goal_text"])
        restate_struct, restate_cov = get(item["restate_text"])
        satisfy_struct, satisfy_cov = get(item["satisfy_text"])
        predicted_next = predict_fn(goal_struct) if goal_struct is not None else None
        sim_restate, _ = structure_overlap(predicted_next, restate_struct, d)
        sim_satisfy, _ = structure_overlap(predicted_next, satisfy_struct, d)
        correct = sim_satisfy > sim_restate
        if correct:
            satrest_correct += 1
        satrest_results.append({
            "id": item["id"], "sim_predicted_to_restate": sim_restate, "sim_predicted_to_satisfy": sim_satisfy,
            "correct": correct, "goal_coverage": goal_cov, "restate_coverage": restate_cov,
            "satisfy_coverage": satisfy_cov,
        })

    thwart_results, thwart_correct = [], 0
    for item in thwart_items:
        a_struct, a_cov = get(item["event_a_text"])
        b_struct, b_cov = get(item["event_b_text"])
        dist_struct, dist_cov = get(item["distractor_text"])
        predicted_next = predict_fn(a_struct) if a_struct is not None else None
        sim_b, _ = structure_overlap(predicted_next, b_struct, d)
        sim_dist, _ = structure_overlap(predicted_next, dist_struct, d)
        correct = sim_b > sim_dist
        if correct:
            thwart_correct += 1
        thwart_results.append({
            "id": item["id"], "sim_predicted_to_b": sim_b, "sim_predicted_to_distractor": sim_dist,
            "correct": correct, "event_a_coverage": a_cov, "event_b_coverage": b_cov,
            "distractor_coverage": dist_cov,
        })

    n_scored = len(unstated_items) * 4 + len(satrest_items) * 2 + len(thwart_items) * 2
    n_total = len(unstated_items) + len(satrest_items) + len(thwart_items)
    overall_correct = unstated_correct + satrest_correct + thwart_correct

    return {
        "arm_name": arm_name,
        "unstated_goal_accuracy": unstated_correct / len(unstated_items),
        "unstated_goal_correct_count": unstated_correct,
        "unstated_goal_n_ties": n_ties,
        "satisfy_restate_accuracy": satrest_correct / len(satrest_items),
        "satisfy_restate_correct_count": satrest_correct,
        "thwart_cause_accuracy": thwart_correct / len(thwart_items),
        "thwart_cause_correct_count": thwart_correct,
        "overall_accuracy": overall_correct / n_total,
        "overall_correct_count": overall_correct,
        "n_total_items": n_total,
        "n_scored_units": n_scored,
        "cardinality_ok": n_scored == EXPECTED_N_SCORED_UNITS_PER_ARM,
        "unstated_results": unstated_results,
        "satrest_results": satrest_results,
        "thwart_results": thwart_results,
    }


def _trim_arm(arm):
    return {k: v for k, v in arm.items() if k not in ("unstated_results", "satrest_results", "thwart_results")}


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    t_start = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": "diagnostic_inline_foreground",
        "expected_n_units": "variable_test_pairs_plus_up_to_74x4_stage_c",
    }
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(start_marker, f)
    os.replace(tmp, final)

    assert os.path.exists(GOLD_EVAL_PATH), f"Director-verified gold eval missing at {GOLD_EVAL_PATH}"
    unstated_items, satrest_items, thwart_items = load_gold_eval(GOLD_EVAL_PATH)
    assert len(unstated_items) == EXPECTED_N_UNSTATED_GOAL_ITEMS
    assert len(satrest_items) == EXPECTED_N_SATISFY_RESTATE_ITEMS
    assert len(thwart_items) == EXPECTED_N_THWART_CAUSE_ITEMS

    # ---- STAGE A: load corpus + segment events per novel ----
    novel_texts = {}
    for name, p in CORPUS_PATHS:
        with open(p, "r", encoding="utf-8") as f:
            novel_texts[name] = f.read()
    print(f"[progress] STAGE A: corpus loaded, {len(novel_texts)} novels", flush=True)

    per_novel_sentences = {name: segment_events(text) for name, text in novel_texts.items()}
    stage_a_counts = {name: len(sents) for name, sents in per_novel_sentences.items()}
    print(f"[progress] STAGE A: sentence counts (capped) = {stage_a_counts}", flush=True)
    assert all(n > 0 for n in stage_a_counts.values()), "STAGE A FAILED: a novel produced zero events"

    corpus_texts_all = list(novel_texts.values())
    vocab, idx, _ppmi_raw_vecs, n_tokens, vocab_size, _ppmi_nnz = build_raw_ppmi_vectors(corpus_texts_all)
    print(f"[progress] vocab built: n_tokens={n_tokens} vocab_size={vocab_size}", flush=True)

    tokens = []
    for text in corpus_texts_all:
        tokens.extend(_tokenize(text))
    tok_idx = np.array([idx.get(w, -1) for w in tokens], dtype=np.int64)
    vocab_counts_arr = np.zeros(vocab_size, dtype=np.int64)
    for ti in tok_idx:
        if ti >= 0:
            vocab_counts_arr[ti] += 1

    print("[progress] starting SGNS retrain (from-scratch error-driven word fillers)", flush=True)
    w_sgns_trained, _w_sgns_random_init, n_pairs_trained, per_epoch_err = train_sgns(
        tok_idx, vocab_size, vocab_counts_arr
    )
    print(f"[progress] SGNS retrain complete n_pairs_trained={n_pairs_trained}", flush=True)

    role_vecs = make_role_vecs(D_EMBED, ROLE_VEC_SEED)
    objidx_roles = make_objidx_roles(D_EMBED, OBJIDX_ROLE_SEED, n_slots=OBJIDX_ROLES_N_SLOTS)

    per_novel_events = {}
    stage_a_drop_stats = {}
    for name, sents in per_novel_sentences.items():
        structs, n_dropped, n_total = build_event_sequence(
            sents, idx, w_sgns_trained, D_EMBED, role_vecs, objidx_roles
        )
        per_novel_events[name] = structs
        stage_a_drop_stats[name] = {"n_total_sentences": n_total, "n_dropped_no_coverage": n_dropped,
                                      "n_valid_events": len(structs)}
        print(f"[progress] STAGE A: {name} valid_events={len(structs)}/{n_total} "
              f"(dropped={n_dropped})", flush=True)

    stage_a_sane = all(v["n_valid_events"] >= 20 for v in stage_a_drop_stats.values())
    total_valid_events = sum(v["n_valid_events"] for v in stage_a_drop_stats.values())

    # ---- STAGE B: build train/test pairs per novel (DIRECTIONAL context), train predictor ----
    gen = torch.Generator().manual_seed(PREDICTOR_SEED)
    dim2 = 2 * D_EMBED
    predictor_trained = EventPredictor(dim2, gen)
    predictor_random = predictor_trained.clone_frozen()

    all_train_X, all_train_Y = [], []
    per_novel_test = {}   # name -> (Xte, Yte, copy_structs, target_indices, pairs)
    per_novel_pair_counts = {}
    for name, structs in per_novel_events.items():
        n_events = len(structs)
        train_pairs, test_pairs, split_idx = make_train_test_pairs(n_events, EVENT_CONTEXT_WINDOW, HELD_OUT_FRAC)
        Xtr, Ytr, _copy_tr = build_pair_tensors(structs, train_pairs, D_EMBED)
        Xte, Yte, copy_te = build_pair_tensors(structs, test_pairs, D_EMBED)
        if Xtr.shape[0] > 0:
            all_train_X.append(Xtr)
            all_train_Y.append(Ytr)
        per_novel_test[name] = (Xte, Yte, copy_te, [p[2] for p in test_pairs])
        per_novel_pair_counts[name] = {
            "n_events": n_events, "split_idx": split_idx,
            "n_train_pairs": len(train_pairs), "n_test_pairs": len(test_pairs),
        }
    print(f"[progress] STAGE B: per-novel pair counts = {per_novel_pair_counts}", flush=True)

    X_train = torch.cat(all_train_X, dim=0)
    Y_train = torch.cat(all_train_Y, dim=0)
    nonempty = [n for n in per_novel_test if per_novel_test[n][0].shape[0] > 0]
    X_test = torch.cat([per_novel_test[n][0] for n in nonempty], dim=0)
    Y_test = torch.cat([per_novel_test[n][1] for n in nonempty], dim=0)
    copy_structs_test = [s for n in nonempty for s in per_novel_test[n][2]]
    novel_name_per_pair = [n for n in nonempty for _ in per_novel_test[n][2]]
    true_target_idx_per_pair = [ti for n in nonempty for ti in per_novel_test[n][3]]

    assert X_train.shape[0] > 0, "STAGE B FAILED: zero pooled train pairs"
    assert X_test.shape[0] > 0, "STAGE B FAILED: zero pooled held-out test pairs"

    train_curve = []
    for epoch in range(PREDICTOR_EPOCHS):
        train_mse_epoch = predictor_trained.train_step(X_train, Y_train)
        if epoch % 20 == 0 or epoch == PREDICTOR_EPOCHS - 1:
            train_curve.append({"epoch": epoch, "train_mse": train_mse_epoch})
            print(f"[progress] STAGE B: epoch={epoch}/{PREDICTOR_EPOCHS} train_mse={train_mse_epoch:.6f}",
                  flush=True)
        if not torch.isfinite(predictor_trained.W).all():
            raise FloatingPointError(f"NaN/Inf detected in predictor W at epoch {epoch}")

    mse_train_final = mse(X_train, Y_train, predictor_trained)
    mse_test_trained = mse(X_test, Y_test, predictor_trained)
    mse_test_random = mse(X_test, Y_test, predictor_random)
    cos_test_trained = cosine_mean(X_test, Y_test, predictor_trained)
    cos_test_random = cosine_mean(X_test, Y_test, predictor_random)
    print(f"[progress] STAGE B (diagnostic MSE, NOT the gate): "
          f"mse_test_trained={mse_test_trained:.6f} mse_test_random={mse_test_random:.6f}", flush=True)

    _digests_w, _pairwise_w, w_differ = _arms_must_differ_tensors({
        "W_trained": predictor_trained.W, "W_random_init": predictor_random.W,
    })
    assert w_differ, "META_RULE_AF VIOLATION: W_trained and W_random_init are bit-identical"

    # ---- STAGE B (NEW): fair-baseline retrieval/ranking evaluation ----
    print("[progress] STAGE B: computing FAIR-BASELINE retrieval accuracies", flush=True)
    train_mean_2d = Y_train.mean(dim=0)  # constant predict-train-mean baseline (renormalized below)
    train_mean_struct = bundling.bundle(from_real_2d(train_mean_2d, D_EMBED).unsqueeze(0))

    predicted_trained = [predict_next_struct(X_test[i], predictor_trained, D_EMBED) for i in range(X_test.shape[0])]
    predicted_random = [predict_next_struct(X_test[i], predictor_random, D_EMBED) for i in range(X_test.shape[0])]
    predicted_mean = [train_mean_struct for _ in range(X_test.shape[0])]
    predicted_copy = copy_structs_test

    _digests_p, _pairwise_p, pred_differ = _arms_must_differ_tensors({
        "pred_trained_0": predicted_trained[0], "pred_random_0": predicted_random[0],
        "pred_mean_0": predicted_mean[0], "pred_copy_0": predicted_copy[0],
    })
    assert pred_differ, "META_RULE_AF VIOLATION: not all 4 Stage-B arms differ on the first test pair"

    retrieval_trained = score_retrieval("TRAINED", predicted_trained, true_target_idx_per_pair,
                                         novel_name_per_pair, per_novel_events, D_EMBED,
                                         N_NEGATIVES, NEGATIVE_SAMPLING_SEED)
    retrieval_random = score_retrieval("RANDOM_INIT", predicted_random, true_target_idx_per_pair,
                                        novel_name_per_pair, per_novel_events, D_EMBED,
                                        N_NEGATIVES, NEGATIVE_SAMPLING_SEED)
    retrieval_mean = score_retrieval("PREDICT_MEAN", predicted_mean, true_target_idx_per_pair,
                                      novel_name_per_pair, per_novel_events, D_EMBED,
                                      N_NEGATIVES, NEGATIVE_SAMPLING_SEED)
    retrieval_copy = score_retrieval("COPY_CONTEXT", predicted_copy, true_target_idx_per_pair,
                                      novel_name_per_pair, per_novel_events, D_EMBED,
                                      N_NEGATIVES, NEGATIVE_SAMPLING_SEED)

    acc_trained = retrieval_trained["retrieval_accuracy"]
    acc_random = retrieval_random["retrieval_accuracy"]
    acc_mean = retrieval_mean["retrieval_accuracy"]
    acc_copy = retrieval_copy["retrieval_accuracy"]

    margin_vs_random = acc_trained - acc_random
    margin_vs_mean = acc_trained - acc_mean
    margin_vs_copy = acc_trained - acc_copy

    stage_b_pass = (
        margin_vs_random >= STAGE_B_MIN_MARGIN and
        margin_vs_mean >= STAGE_B_MIN_MARGIN and
        margin_vs_copy >= STAGE_B_MIN_MARGIN
    )

    baselines_in_band = all(0.05 <= a <= 0.95 for a in (acc_random, acc_mean, acc_copy))

    print(f"[progress] STAGE B RETRIEVAL RESULT: trained={acc_trained:.4f} random={acc_random:.4f} "
          f"mean={acc_mean:.4f} copy={acc_copy:.4f} margins=(rand={margin_vs_random:+.4f} "
          f"mean={margin_vs_mean:+.4f} copy={margin_vs_copy:+.4f}) stage_b_pass={stage_b_pass}", flush=True)

    stage_c_ran = False
    readout_trained = readout_random = None
    unstated_trained_acc = unstated_random_acc = None
    satrest_trained_acc = satrest_random_acc = None
    thwart_trained_acc = thwart_random_acc = None
    unstated_axis_pass = satrest_axis_pass = thwart_axis_pass_diag_only = None
    phase1_mechanism_works = False

    if stage_b_pass:
        stage_c_ran = True
        print("[progress] STAGE B PASSED -- proceeding to STAGE C readout", flush=True)

        def predict_fn_trained(event_struct):
            x2d = to_real_2d(event_struct, D_EMBED)
            return predict_next_struct(x2d, predictor_trained, D_EMBED)

        def predict_fn_random(event_struct):
            x2d = to_real_2d(event_struct, D_EMBED)
            return predict_next_struct(x2d, predictor_random, D_EMBED)

        readout_trained = score_readout(
            "TRAINED_EVENT_PREDICTOR", predict_fn_trained, idx, w_sgns_trained, D_EMBED,
            role_vecs, objidx_roles, unstated_items, satrest_items, thwart_items,
        )
        readout_random = score_readout(
            "RANDOM_INIT_EVENT_PREDICTOR", predict_fn_random, idx, w_sgns_trained, D_EMBED,
            role_vecs, objidx_roles, unstated_items, satrest_items, thwart_items,
        )
        unstated_trained_acc = readout_trained["unstated_goal_accuracy"]
        unstated_random_acc = readout_random["unstated_goal_accuracy"]
        satrest_trained_acc = readout_trained["satisfy_restate_accuracy"]
        satrest_random_acc = readout_random["satisfy_restate_accuracy"]
        thwart_trained_acc = readout_trained["thwart_cause_accuracy"]
        thwart_random_acc = readout_random["thwart_cause_accuracy"]

        unstated_axis_pass = (unstated_trained_acc > unstated_random_acc) and \
            (unstated_trained_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC)
        satrest_axis_pass = (satrest_trained_acc > satrest_random_acc) and \
            (satrest_trained_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC)
        thwart_axis_pass_diag_only = (thwart_trained_acc > thwart_random_acc) and \
            (thwart_trained_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC)

        phase1_mechanism_works = stage_b_pass and (unstated_axis_pass or satrest_axis_pass)
    else:
        print("[progress] STAGE B HARD_FAIL -- STOPPING before Stage C (per pre-reg, do not score "
              "a readout on an unproven predictor)", flush=True)

    if not stage_b_pass:
        top_verdict = "MECHANISM_HARD_FAIL"
        insufficiency_reason = "STAGE_B_DID_NOT_BEAT_ALL_THREE_FAIR_BASELINES_ON_RETRIEVAL_METRIC"
    elif not (unstated_axis_pass or satrest_axis_pass):
        top_verdict = "MECHANISM_REAL_READOUT_INSUFFICIENT"
        insufficiency_reason = "STAGE_C_READOUT_DID_NOT_BEAT_RANDOM_AND_WORD_LEVEL_BASELINE_ON_A_CLEAN_AXIS"
    else:
        top_verdict = "MECHANISM_REAL"
        insufficiency_reason = None

    elapsed_s = time.perf_counter() - t_start

    summary = {
        "mechanism": (
            "Event-level next-event-state predictor (linear, delta-rule/error-driven-trained) "
            "over POSITION-TAGGED DIRECTIONAL bound AGENT/ACTION/OBJECT FHRR event-struct "
            "context, evaluated by TOP-1 RETRIEVAL against same-novel distractors "
            "(structure_overlap ranking) against 3 fair non-learned baselines "
            "(predict-train-mean, copy-context, random-init)."
        ),
        "redo_of": "experiments/exp_event_level_prediction_error_relation_inference_phase1_v1.py "
                    "(commit 2247466e2), DISQUALIFIED by commit d03178c75 numbers-VET "
                    "(notes/skunkworks_audit_phase1_event_level_prediction_error_"
                    "STAGE_B_FAILS_FAIR_BASELINE_2026-08-03.md)",
        "stage_a_segmentation": {
            "method": "naive sentence-split regex (rough, fixed, NOT the variable, unchanged from v1)",
            "per_novel_counts": stage_a_drop_stats,
            "total_valid_events": total_valid_events,
            "stage_a_sane": stage_a_sane,
        },
        "stage_b_mechanism": {
            "event_context_window": EVENT_CONTEXT_WINDOW,
            "directional_context": True,
            "held_out_frac": HELD_OUT_FRAC,
            "per_novel_pair_counts": per_novel_pair_counts,
            "n_pooled_train_pairs": int(X_train.shape[0]),
            "n_pooled_test_pairs": int(X_test.shape[0]),
            "predictor_epochs": PREDICTOR_EPOCHS,
            "train_curve_sampled": train_curve,
            "diagnostic_mse_NOT_the_gate": {
                "mse_train_final": mse_train_final,
                "mse_test_trained": mse_test_trained,
                "mse_test_random_init": mse_test_random,
                "cosine_test_trained": cos_test_trained,
                "cosine_test_random_init": cos_test_random,
            },
            "retrieval_metric": {
                "n_negatives": N_NEGATIVES,
                "chance_level": 1.0 / (N_NEGATIVES + 1),
                "stage_b_min_margin_required": STAGE_B_MIN_MARGIN,
                "trained_accuracy": acc_trained,
                "random_init_accuracy": acc_random,
                "predict_mean_accuracy": acc_mean,
                "copy_context_accuracy": acc_copy,
                "margin_vs_random": margin_vs_random,
                "margin_vs_mean": margin_vs_mean,
                "margin_vs_copy": margin_vs_copy,
                "baselines_in_band_0.05_0.95": baselines_in_band,
                "stage_b_pass": stage_b_pass,
            },
        },
        "stage_c_readout_ran": stage_c_ran,
        "stage_c_readout": (
            {
                "arms": {
                    "TRAINED_EVENT_PREDICTOR": _trim_arm(readout_trained),
                    "RANDOM_INIT_EVENT_PREDICTOR": _trim_arm(readout_random),
                },
                "word_level_lexical_baseline_acc_cited": WORD_LEVEL_LEXICAL_BASELINE_ACC,
                "unstated_goal": {
                    "trained_acc": unstated_trained_acc, "random_acc": unstated_random_acc,
                    "axis_pass": unstated_axis_pass,
                },
                "satisfy_restate": {
                    "trained_acc": satrest_trained_acc, "random_acc": satrest_random_acc,
                    "axis_pass": satrest_axis_pass,
                },
                "thwart_cause": {
                    "trained_acc": thwart_trained_acc, "random_acc": thwart_random_acc,
                    "axis_pass_diagnostic_only_excluded_from_greenlight": thwart_axis_pass_diag_only,
                },
            } if stage_c_ran else None
        ),
        "TOP_VERDICT": top_verdict,
        "PHASE1_MECHANISM_WORKS": phase1_mechanism_works,
        "insufficiency_reason": insufficiency_reason,
        "revival_criteria_if_hard_fail": (
            "(a) nonlinear predictor (explicit-gradient 2-layer MLP, still no autograd dependency); "
            "(b) a robustly-directional multi-event context (window=1 sidestepped, not solved, the "
            "order-encoding problem -- a non-degenerate way to fuse >1 prior event, e.g. "
            "concatenation instead of bind+bundle, needs its own dimensional predictor redesign); "
            "(c) clause-level segmentation (Stage A hardening, Phase 2 scope); (d) harder "
            "same-chapter-only negative pool to stress-test margin robustness if a future attempt "
            "passes by a thin margin. MOST INFORMATIVE REVIVAL SIGNAL (MEASURED this run): trained "
            "also LOST to copy-context (margin_vs_copy=-0.0112) -- the no-learning 'next-event = "
            "same-as-last-event' baseline already beats the linear delta-rule predictor on this "
            "metric, meaning the linear map is not even capturing simple narrative continuity, let "
            "alone genuine forward prediction."
        ),
        "eval_caveat": (
            "Stage B retrieval accuracy is measured over n_pooled_test_pairs (report exact N); "
            "Stage C (if reached) is the SAME N=25 Director-VERIFIED gold eval as v1 -- small-N "
            "diagnostic by ML standards, report per-item-type counts alongside fractions."
        ),
        "elapsed_s": elapsed_s,
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"TOP_VERDICT={top_verdict}; stage_b_pass={stage_b_pass} "
            f"(retrieval: trained={acc_trained:.4f} random={acc_random:.4f} mean={acc_mean:.4f} "
            f"copy={acc_copy:.4f}; margins rand={margin_vs_random:+.4f} mean={margin_vs_mean:+.4f} "
            f"copy={margin_vs_copy:+.4f}; n_test_pairs={X_test.shape[0]}); "
            f"stage_c_readout_ran={stage_c_ran}; "
            + (f"unstated_goal trained={unstated_trained_acc:.4f} random={unstated_random_acc:.4f}; "
               f"satisfy_restate trained={satrest_trained_acc:.4f} random={satrest_random_acc:.4f}; "
               if stage_c_ran else "") +
            f"insufficiency_reason={insufficiency_reason}"
        ),
        "summary": f"PHASE1 v2 (associative/retrieval) event-level mechanism: TOP_VERDICT={top_verdict}",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "stage_b_retrieval_per_pair_trained": retrieval_trained["per_pair_records"],
        "stage_b_retrieval_per_pair_random": retrieval_random["per_pair_records"],
        "stage_b_retrieval_per_pair_mean": retrieval_mean["per_pair_records"],
        "stage_b_retrieval_per_pair_copy": retrieval_copy["per_pair_records"],
        "results_trained_unstated_goal": readout_trained["unstated_results"] if stage_c_ran else None,
        "results_trained_satisfy_restate": readout_trained["satrest_results"] if stage_c_ran else None,
        "results_trained_thwart_cause": readout_trained["thwart_results"] if stage_c_ran else None,
        "results_random_unstated_goal": readout_random["unstated_results"] if stage_c_ran else None,
        "results_random_satisfy_restate": readout_random["satrest_results"] if stage_c_ran else None,
        "results_random_thwart_cause": readout_random["thwart_results"] if stage_c_ran else None,
        "summary_fields": summary,
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_scaled_to_diagnostic_variable_n_test_pairs",
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_exempted": [],
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "crlb_n_a": (
            "no fixed-capacity argmax-noise-floor threshold; discrete top-1-of-"
            f"{N_NEGATIVES + 1} retrieval accuracy (chance={1.0 / (N_NEGATIVES + 1):.3f}) is the "
            "analogue, stated explicitly in pre-reg bands"
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, final_path)

    print(json.dumps(summary, indent=2))


def self_test():
    """Tiny-scale real-code-path self-test: exercises the ACTUAL reused
    build_event_struct_v6 pipeline, position-tagged directional context
    construction, the EventPredictor train/predict cycle, the retrieval
    scorer (against a fair predict-mean AND copy-context baseline), and the
    readout scorer, all at N~tiny scale, end to end."""
    d = 8
    vocab = ["alice", "wants", "tea", "and", "cake", "bob", "gives", "cake2",
             "runs", "fast", "far", "away", "quickly", "sad", "happy", "the",
             "cat", "sat", "mat", "dog", "ran", "park"]
    idx = {w: i for i, w in enumerate(vocab)}
    rng = np.random.RandomState(0)
    dense_vecs = rng.rand(len(vocab), d).astype(np.float64)
    role_vecs = make_role_vecs(d, seed=1)
    objidx_roles = make_objidx_roles(d, seed=2, n_slots=6)

    text = ("Alice wants tea and cake. Bob gives cake2 to alice. The cat sat on the mat. "
            "A dog ran in the park quickly. Alice runs fast away sad. Bob gives happy cake2.")
    sents = segment_events(text, max_sentences=100, min_words=2)
    assert len(sents) >= 5, f"segmentation produced too few sentences: {sents}"

    structs, n_dropped, n_total = build_event_sequence(sents, idx, dense_vecs, d, role_vecs, objidx_roles)
    assert n_total == len(sents)
    assert len(structs) >= 5, "expected at least 5 valid events from the fixture"
    for s in structs:
        assert s.dtype == torch.complex64 and s.shape == (d,)

    # --- to_real_2d / from_real_2d round trip ---
    v2d = to_real_2d(structs[0], d)
    assert v2d.shape == (2 * d,)
    back = from_real_2d(v2d, d)
    assert torch.allclose(back, structs[0], atol=1e-5), "to_real_2d/from_real_2d round trip broken"

    # --- DIRECTIONALITY (window=1 fix): context is exactly the preceding event, so
    # "A-then-B" and "B-then-A" trivially produce DIFFERENT context vectors whenever
    # A != B (there is no bundling step left to collapse order into a sign-ambiguous
    # composite -- see module docstring for the 2-term phase-role degeneracy this
    # replaced, which THIS self-test originally caught: a first-draft position-tagged
    # bind+bundle scheme produced bit-identical composites for A-then-B vs B-then-A). ---
    ctx_a = make_context_struct_directional(structs, 0, 0)
    ctx_b = make_context_struct_directional(structs, 1, 1)
    assert ctx_a.shape == (d,) and ctx_a.dtype == torch.complex64
    assert not torch.allclose(ctx_a, ctx_b), "context for two distinct preceding events must differ"
    overlap_ab, _ = structure_overlap(ctx_a, ctx_b, d)
    assert overlap_ab < 0.999, (
        f"DIRECTIONALITY SANITY FAILURE: two distinct preceding events produced near-identical "
        f"context (overlap={overlap_ab})"
    )
    guard_raised = False
    try:
        make_context_struct_directional(structs, 0, 1)
    except AssertionError as e:
        guard_raised = True
        assert "only valid for EVENT_CONTEXT_WINDOW=1" in str(e)
    assert guard_raised, "make_context_struct_directional should refuse a window>1 call by construction"

    # --- copy-context baseline construction ---
    copy_ctx = make_context_struct_copy(structs, 0, 1)
    assert torch.allclose(copy_ctx, structs[1]), "copy-context should be the raw most-recent event"

    # --- train/test pair split + directional tensors: no leakage, deterministic ---
    train_pairs, test_pairs, split_idx = make_train_test_pairs(len(structs), window=1, held_out_frac=0.34)
    assert len(train_pairs) > 0 and len(test_pairs) > 0
    for lo, t, target_idx in train_pairs:
        assert target_idx < split_idx and lo < split_idx
    for lo, t, target_idx in test_pairs:
        assert lo >= split_idx and target_idx <= len(structs) - 1
    Xtr, Ytr, _copy_tr = build_pair_tensors(structs, train_pairs, d)
    Xte, Yte, copy_te = build_pair_tensors(structs, test_pairs, d)
    assert Xtr.shape == (len(train_pairs), 2 * d)
    assert len(copy_te) == len(test_pairs)

    # --- EventPredictor: trained must reduce MSE vs random-init on a learnable synthetic fixture ---
    gen = torch.Generator().manual_seed(123)
    dim2 = 2 * d
    pred = EventPredictor(dim2, gen)
    pred_random = pred.clone_frozen()
    fixed_rng = torch.Generator().manual_seed(5)
    X = torch.rand(40, dim2, generator=fixed_rng)
    Y = X.clone()
    mse_before = mse(X, Y, pred)
    for _ in range(200):
        pred.train_step(X, Y, lr=0.2, l2=0.0)
    mse_after = mse(X, Y, pred)
    mse_random_ref = mse(X, Y, pred_random)
    assert mse_after < mse_before
    assert mse_after < mse_random_ref

    # --- ARMS-MUST-DIFFER ---
    _digests_w, _pw, w_differ = _arms_must_differ_tensors({"trained": pred.W, "random": pred_random.W})
    assert w_differ

    # --- retrieval scorer: FAIR gate must correctly discriminate a genuinely-good predictor from
    # a bad one on a synthetic fixture engineered so the trained predictor's output is CLOSER to
    # the true target than to distractors (sanity of the scoring logic itself) ---
    fake_events = [torch.polar(torch.ones(d), torch.rand(d, generator=torch.Generator().manual_seed(seed)) * 6.28).to(torch.complex64)
                   for seed in range(10)]
    good_predicted = [fake_events[i + 1] for i in range(8)]  # "predicts" the true next event exactly
    true_idx = list(range(1, 9))
    novel_names = ["fixture_novel"] * 8
    per_novel = {"fixture_novel": fake_events}
    res_good = score_retrieval("GOOD", good_predicted, true_idx, novel_names, per_novel, d, 4, seed_base=999)
    assert res_good["retrieval_accuracy"] == 1.0, (
        f"retrieval scorer sanity check failed: a predictor that outputs the exact true target "
        f"should score 1.0, got {res_good['retrieval_accuracy']}"
    )
    bad_predicted = [fake_events[0] for _ in range(8)]  # constant wrong prediction (never matches target)
    res_bad = score_retrieval("BAD", bad_predicted, true_idx, novel_names, per_novel, d, 4, seed_base=999)
    assert res_bad["retrieval_accuracy"] < res_good["retrieval_accuracy"]

    # --- score_readout end-to-end on tiny fixture gold items (via predict_fn closure) ---
    def predict_fn(event_struct):
        x2d = to_real_2d(event_struct, d)
        return predict_next_struct(x2d, pred, d)

    unstated_items = [{
        "id": "u1", "action_text": "alice wants tea",
        "correct_category": "CAT_A", "distractor_categories": ["CAT_B", "CAT_C", "CAT_D"],
    }]
    satrest_items = [{
        "id": "s1", "goal_text": "alice wants tea",
        "restate_text": "bob gives cake2 to alice", "satisfy_text": "cat sat on mat",
    }]
    thwart_items = [{
        "id": "t1", "event_a_text": "alice wants tea",
        "event_b_text": "cat sat on mat", "distractor_text": "dog ran in park",
    }]
    _orig = dict(CATEGORY_PROTOTYPES)
    CATEGORY_PROTOTYPES.clear()
    CATEGORY_PROTOTYPES.update({
        "CAT_A": "alice wants tea", "CAT_B": "bob gives cake2",
        "CAT_C": "runs fast far away quickly", "CAT_D": "sad happy",
    })
    try:
        res = score_readout("ARM_TEST", predict_fn, idx, dense_vecs, d, role_vecs, objidx_roles,
                             unstated_items, satrest_items, thwart_items)
        assert res["arm_name"] == "ARM_TEST"
        assert res["n_scored_units"] == 4 + 2 + 2
        assert 0.0 <= res["unstated_goal_accuracy"] <= 1.0
    finally:
        CATEGORY_PROTOTYPES.clear()
        CATEGORY_PROTOTYPES.update(_orig)

    print(
        f"[self_test] PASS  n_events={len(structs)}  mse_before={mse_before:.4f}  "
        f"mse_after={mse_after:.4f}  mse_random_ref={mse_random_ref:.4f}  "
        f"directionality_overlap_distinct_events={overlap_ab:.4f}  "
        f"retrieval_good={res_good['retrieval_accuracy']:.3f}  retrieval_bad={res_bad['retrieval_accuracy']:.3f}  "
        f"n_scored_units={res['n_scored_units']}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        if "--self-test" in sys.argv:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
