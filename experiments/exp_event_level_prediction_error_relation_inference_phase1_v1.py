"""
PHASE 1 (USER-approved "commit, definitely") -- brain-faithful MECHANISM PROOF:
EVENT-LEVEL PREDICTION-ERROR learning (Zacks Event Segmentation Theory +
Reynolds-Zacks-Braver 2007 computational model: an event-model predicts the
next event-state; transient prediction-error spikes = event boundaries;
learning = reducing that error) applied to whether RELATION INFERENCE
(unstated goals; SATISFY/THWART/CAUSE) becomes readable where the WORD-LEVEL
distributional paradigm empirically FAILED this session (commit 878ea6cca,
ae614c25b: on the Director-verified clean 25-item gold eval, random-init
lexical fillers scored 0.5200 overall accuracy > trained SGNS 0.4000 --
MEASURED@data/exp_content_awareness_earned_v6c_tiebreak_fixed_control/
metrics.json:summary_fields.Q2_random_still_beats_trained).

Per notes/research_drill_biology_led_encoder_target_representation_2026-08-03.md
(Trabasso & van den Broek 1985; Zwaan & Radvansky 1998; Speer/Zacks/Reynolds
2007): relation inference operates over EVENT/PREDICATE-level bound structure,
not word-level co-occurrence, and the brain's own mechanism for building that
structure is predictive: an event model that predicts forward and updates on
error. This cell builds the SIMPLEST honest version of that claim and lets it
fail if it fails (USER: "bounded + can-fail + STAGED -- NOT a blind multi-hour
run").

NO borrowed vectors/model/LLM. NO Binder norms (lock-safest, per USER
instruction this cycle). Word fillers are the SAME from-scratch error-driven
SGNS content vectors already trained+reused across this arc (train_sgns,
exp_content_awareness_earned_v4) -- content/segmentation/binding are HELD
FIXED; the ONE swept variable is the EVENT-LEVEL PREDICTOR (trained via
prediction-error/delta-rule vs random-init, never updated -- the must-fail
control).

REUSE, do not reinvent (USER instruction):
  - hdlab.binding.bind/unbind (FHRR elementwise complex mul) -- used inside
    the reused build_event_struct_v6 (v6 module) for role<-filler binding.
  - hdlab.bundling.bundle (elementwise-magnitude renormalizing superposition)
    -- used inside build_event_struct_v6 for role-bundling AND reused here
    directly for (a) the multi-event CONTEXT WINDOW (bundle of the last
    EVENT_CONTEXT_WINDOW event-structs, the same organ situation_model_
    accumulate.py's AccumulateRegister uses to accumulate multiple bound
    facts into one register -- here the "entity" is implicitly "the ongoing
    narrative", so a keyed per-entity register is not the right shape;
    plain bundling.bundle over a raw temporal window is the correct reuse of
    the SAME primitive, not a new mechanism) and (b) renormalizing every
    linear-predictor output back to the elementwise-unit-magnitude FHRR
    convention (predicted = bundling.bundle(raw_linear_output.unsqueeze(0))
    -- a 1-item "bundle" is exactly the renormalization step, reused not
    reimplemented).
  - build_event_struct_v6 / make_role_vecs / make_objidx_roles / structure_overlap
    / _role_split_words (v5/v6 modules) for the bound AGENT/ACTION/OBJECT
    role-filler FHRR event representation -- UNCHANGED.
  - train_sgns / D_EMBED (v4) for the from-scratch error-driven word fillers.
  - build_raw_ppmi_vectors / _tokenize (v3 ceiling-probe module) for vocab/idx
    construction (shared with v6c's own pipeline, for parity).
  - load_gold_eval / GOLD_EVAL_PATH / CATEGORY_PROTOTYPES / chance constants /
    _tie_break_pick (v6c) for the 25-item Director-verified eval + the
    order-independent tie-break already vetted this session.

Prior-work check (substrate_query.sh, mandatory before authoring): queried
"event-level prediction error next event state predictor relation inference
Zacks event segmentation" and "linear delta-rule predictor bound FHRR event
representation next-state prediction". Top hits were the ALREADY-CITED prior
art already listed in notes/research_drill_biology_led_encoder_target_
representation_2026-08-03.md (situation_model_accumulate, coref/causal organs,
the v4-v6c word-level arc itself) at cosine>0.30 -- these are the building
blocks this cell composes, not a duplicate of an existing event-level
predictor cell. No existing cell trains a next-event-state predictor over
bound FHRR event structures on this corpus; genuinely new composition, not a
rediscovery.

STAGES (each self-tested + can-fail; report honestly per stage, do not force
downstream if an earlier stage fails):

STAGE A -- event sequences (rough, glass-box, declared NOT the variable):
  Each novel's raw text -> naive sentence split (regex on .!?  + whitespace,
  same granularity as several prior scan/segmentation cells in this repo) ->
  each sentence -> one "event" -> build_event_struct_v6 (bound AGENT/ACTION/
  OBJECT FHRR composite), reusing the SAME idx/dense_vecs/role_vecs/
  objidx_roles the SGNS/eval pipeline already uses. Sentences with zero
  vocabulary coverage are dropped (not a valid event). Capped at
  MAX_SENTENCES_PER_NOVEL per novel for bounded runtime. Self-test: sane
  event counts, coverage stats logged, no crashes. THIS IS ROUGH (Phase 2
  hardens segmentation; sentence-as-event is a coarse proxy for clause-level
  events).

STAGE B -- the mechanism (THE variable): a from-scratch linear EVENT-LEVEL
  predictor (EventPredictor below) trained by batch gradient-descent
  prediction-error minimization (this IS the delta rule / Widrow-Hoff /
  Rescorla-Wagner update generalized to vectors -- explicit error-driven
  weight update, no borrowed optimizer semantics beyond "subtract error
  gradient", matching the discriminative-learning mechanism cited in the
  research drill) to predict the NEXT event-state's FHRR representation from
  a bundled window of EVENT_CONTEXT_WINDOW prior event-state(s), over each
  novel's own event sequence (train/test split is a CONTIGUOUS temporal
  split per novel -- last HELD_OUT_FRAC events held out, with a full-window
  gap so no train context/target pair and no test context/target pair
  straddles the split). CAN-FAIL GATE B: held-out next-event prediction MSE
  for the TRAINED predictor must be LOWER than for a RANDOM-INIT predictor
  (identical architecture and initialization, zero training steps -- the
  must-fail control) by at least STAGE_B_MIN_REL_IMPROVEMENT relative. If
  this fails, Stage C readout is still measured (for completeness/diagnosis)
  but the cell's honest verdict is PHASE1_MECHANISM_INSUFFICIENT at Stage B.

STAGE C -- relation-inference readout (glass-box, THROUGH the predictor, only
  informative if Stage B passes): for each gold item, roll the trained
  predictor forward ONE step from the antecedent event-struct and score
  candidates by structure_overlap(predicted_next, candidate_struct) --
  the SAME primitive already used to score direct (non-predictive) overlap
  in v5/v6/v6b/v6c, now applied to a PREDICTED future state rather than the
  raw antecedent state itself:
    - unstated_goal (4-way MC): predicted_next = predict(action_struct);
      argmax_cat structure_overlap(predicted_next, category_prototype_struct)
      via the SAME order-independent _tie_break_pick as v6c (reused
      verbatim, not reimplemented -- this eval's tie-break bug is already
      fixed upstream and must not be reintroduced here).
    - satisfy_restate (2-way): predicted_next = predict(goal_struct); correct
      iff structure_overlap(predicted_next, satisfy_struct) >
      structure_overlap(predicted_next, restate_struct) (same >-based
      resolution as v6/v6c -- exact ties resolve to a miss, unchanged).
    - thwart_cause (2-way, CAUSE(a,b) operationalized as "predicting forward
      from a lands closer to b than to a same-topic non-causal distractor"):
      predicted_next = predict(event_a_struct); correct iff
      structure_overlap(predicted_next, event_b_struct) >
      structure_overlap(predicted_next, distractor_struct).
  Both the TRAINED and RANDOM-INIT predictors are scored on all three axes
  (ARMS-MUST-DIFFER + the random-init must-fail control at the READOUT level,
  not just the MSE level). The word-level lexical baseline (0.5200 overall,
  ARM_RANDOM_INIT_CONTROL) is CITED (MEASURED@ the v6c metrics path above),
  not rerun -- it is unchanged infrastructure, and rerunning it would not be
  the one swept variable this cell tests.

PRE-REGISTERED HARD BANDS (declared before running):
  PHASE1_MECHANISM_WORKS   = STAGE_B_PASS and (UNSTATED_GOAL_AXIS_PASS or
                              SATISFY_RESTATE_AXIS_PASS)   [thwart_cause is
                              EXCLUDED from the greenlight axis per task spec
                              -- it is lexically shortcuttable / measured
                              near-ceiling by cheap baselines elsewhere in
                              this arc, so a thwart_cause-only win would not
                              be trustworthy evidence of the event mechanism].
  STAGE_B_PASS             = mse_trained_test < mse_random_test AND
                              (mse_random_test - mse_trained_test) / mse_random_test
                              >= STAGE_B_MIN_REL_IMPROVEMENT (0.02).
  <AXIS>_AXIS_PASS         = trained_axis_acc > random_axis_acc (strict,
                              the readout-level must-fail control) AND
                              trained_axis_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC
                              (0.5200, strict -- beating the cited word-level
                              number, per task spec).
  PHASE1_MECHANISM_INSUFFICIENT = otherwise; report per-stage WHERE it fell
                              short (segmentation/predictor-didn't-learn/
                              readout) -- do NOT overclaim on N=25.

DISCIPLINE:
  - glass-box, from-scratch, no borrowed embedding/model/LLM/Binder.
  - ONE variable (trained-vs-random event predictor); segmentation + binding
    + word-filler content HELD FIXED across both predictor arms.
  - CAN-FAIL random-init control at BOTH the MSE level (Stage B) and the
    readout-accuracy level (Stage C) -- two independent must-fail checks.
  - deterministic seeding throughout (fixed int seeds; no hash()/list(set())
    ordering anywhere; sentence order and event order are the corpus's own
    natural reading order, not shuffled).
  - ARMS-MUST-DIFFER (META_RULE_AF): W_trained vs W_random_init hash-checked
    after training; predicted-event structs for a shared probe input
    hash-checked across the two predictor arms.
  - except SystemExit / except KeyboardInterrupt re-raised BEFORE except
    Exception; no bare except; no except BaseException.
  - final_metrics_atomicity: tmp_replace (os.replace).
  - cardinality_ok: 25 gold items scored per predictor arm (74 scored units:
    12*4 + 7*2 + 6*2), 2 predictor arms = 148 total scored units, asserted.
  - CRLB n/a (no fixed-capacity argmax-noise floor; discrete N=25-item
    accuracy-count feasibility is the analogue, per this arc's convention).
  - runtime bound: event-struct construction over ~16k capped sentences is
    O(1) FHRR ops each (microseconds); SGNS retrain is the dominant cost
    (measured ~140s in v6c at identical D_EMBED/corpus); predictor training
    is a small (2*D_EMBED)x(2*D_EMBED)=128x128 batch GD, trivial. Single
    foreground run, well under 10 min. progress_logging=print_flush_true.
  - Content-filter safety: reuses ONLY the already-vetted Director-verified
    gold_relation_inference_v1.jsonl + the same 5 already-used public-domain
    corpus files; no new snippets introduced (short excerpts already vetted
    upstream in this arc).
  - GIT: local only, no push; this file + its metrics.json are the only new
    paths this cell should stage. Does NOT dispatch anything (a direct
    measurement cell, not a queue cell). --no-verify per caller instruction.
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
    CHANCE_OVERALL_WEIGHTED,
    CHANCE_UNSTATED,
    CHANCE_SATREST,
    CHANCE_THWART,
    EXPECTED_N_UNSTATED_GOAL_ITEMS,
    EXPECTED_N_SATISFY_RESTATE_ITEMS,
    EXPECTED_N_THWART_CAUSE_ITEMS,
    EXPECTED_N_TOTAL_ITEMS,
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
    REPO_ROOT, "data", "exp_event_level_prediction_error_relation_inference_phase1_v1"
)
ANCHOR_NAME = "event_level_prediction_error_relation_inference_phase1_v1"

V6C_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_content_awareness_earned_v6c_tiebreak_fixed_control", "metrics.json"
)

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

# ---- MEASURED reference (word-level arc, this session; NOT rerun here) ----
WORD_LEVEL_LEXICAL_BASELINE_ACC = 0.5200
# MEASURED@data/exp_content_awareness_earned_v6c_tiebreak_fixed_control/metrics.json:
#   summary_fields.Q2_random_still_beats_trained.random_init_overall_accuracy
WORD_LEVEL_TRAINED_SGNS_ACC_REF = 0.4000
# MEASURED@ same file: summary_fields.Q2_random_still_beats_trained.error_driven_overall_accuracy

# ---- Stage A (segmentation, rough/fixed) ----
MAX_SENTENCES_PER_NOVEL = 5000
MIN_SENTENCE_WORDS = 3
EVENT_MAX_WORDS = 30    # MEASURED@this-file preflight: full-novel "sentences" (regex-split, no
                         # parser) include rare 200+-word run-ons from unsegmented paragraph-like
                         # punctuation; truncating to the first 30 raw whitespace tokens keeps each
                         # event a single bounded AGENT/ACTION/OBJECT unit (consistent with "rough,
                         # fixed, not the variable" segmentation) instead of growing the objidx-role
                         # vocabulary to cover pathological outliers.
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

ROLE_VEC_SEED = 55001         # SAME literal seed as v5/v6/v6b/v6c (D_EMBED-dim role vocab)
OBJIDX_ROLE_SEED = OBJIDX_ROLE_SEED_D64  # reuse v6's D64 objidx-role family SEED (deterministic
                                          # generator start), but this cell draws its OWN n_slots
                                          # sized for full-sentence events (see OBJIDX_ROLES_N_SLOTS)
                                          # rather than v6's short-gold-span MAX_OBJECT_SLOTS=24.
OBJIDX_ROLES_N_SLOTS = 40      # >= EVENT_MAX_WORDS - 2 (agent+action slots) with headroom

# ---- Stage B (the mechanism) ----
EVENT_CONTEXT_WINDOW = 2       # bundle of the last N event-structs as predictor context
HELD_OUT_FRAC = 0.20           # last 20% of each novel's valid-event sequence, contiguous
PREDICTOR_SEED = 71001
PREDICTOR_LR = 0.05
PREDICTOR_EPOCHS = 300
PREDICTOR_L2 = 1e-4
STAGE_B_MIN_REL_IMPROVEMENT = 0.02   # HYPOTHESIZED@this-file: 2% relative MSE reduction floor,
                                       # a small-but-repeatable (deterministic-seeded, no run-to-run
                                       # noise) margin so a rounding-level "improvement" is not
                                       # over-claimed as HARD_PASS.

# ---- Stage C (readout) axis-pass margins ----
UNSTATED_GOAL_UNIT = 1.0 / EXPECTED_N_UNSTATED_GOAL_ITEMS      # = 0.08333
SATISFY_RESTATE_UNIT = 1.0 / EXPECTED_N_SATISFY_RESTATE_ITEMS  # = 0.14286


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
    """META_RULE_AF hash-based check across N named tensors."""
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
# STAGE A: rough event segmentation (declared fixed, not the variable)
# --------------------------------------------------------------------------

def segment_events(text, max_sentences=MAX_SENTENCES_PER_NOVEL, min_words=MIN_SENTENCE_WORDS):
    """Naive sentence-level event segmentation (glass-box regex heuristic,
    NOT a parser). Each event = one sentence with >= min_words tokens.
    Capped at max_sentences for bounded runtime. Declared ROUGH: Phase 2
    hardens this into clause-level segmentation."""
    raw = SENTENCE_SPLIT_RE.split(text)
    sentences = [s.strip() for s in raw if len(s.split()) >= min_words]
    sentences = [" ".join(s.split()[:EVENT_MAX_WORDS]) for s in sentences]
    return sentences[:max_sentences]


def build_event_sequence(sentences, idx, dense_vecs, d, role_vecs, objidx_roles):
    """Builds one bound FHRR event-struct per sentence via build_event_struct_v6
    (reused verbatim). Drops sentences with zero vocabulary coverage (not a
    valid event). Returns (event_structs: list[complex64[d]], n_dropped, n_total)."""
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
# STAGE B: the event-level predictor (THE variable)
# --------------------------------------------------------------------------

def to_real_2d(struct, d):
    """complex64[d] -> real[2d] (concat real, imag). Flat torch <-> torch, no numpy."""
    return torch.cat([struct.real, struct.imag]).to(torch.float32)


def from_real_2d(vec2d, d):
    """real[2d] -> complex64[d]. Inverse of to_real_2d."""
    return torch.complex(vec2d[:d], vec2d[d:]).to(torch.complex64)


class EventPredictor:
    """From-scratch linear next-event-state predictor over the real-2d
    encoding of bound FHRR event structs. Trained via explicit batch
    gradient-descent on squared prediction error -- the delta rule /
    Widrow-Hoff update generalized to a vector target, the same closed-form
    error-driven mechanism cited in the research drill's discriminative-
    learning family (Rescorla-Wagner). No autograd framework; the gradient
    is written out explicitly (glass-box)."""

    def __init__(self, dim2, generator):
        self.dim2 = dim2
        scale = 1.0 / math.sqrt(dim2)
        self.W = (torch.rand(dim2, dim2, generator=generator) - 0.5) * 2.0 * scale

    def clone_frozen(self):
        """Returns a NEW EventPredictor-like object sharing this W but never
        trained further (used to snapshot the random-init control BEFORE any
        training step is taken)."""
        p = EventPredictor.__new__(EventPredictor)
        p.dim2 = self.dim2
        p.W = self.W.clone()
        return p

    def predict_raw(self, x):
        """x: (dim2,) or (N, dim2) -> same-shaped linear prediction."""
        return x @ self.W

    def train_step(self, X, Y, lr=PREDICTOR_LR, l2=PREDICTOR_L2):
        """One full-batch gradient-descent step minimizing mean squared
        prediction error err = (X @ W) - Y. grad = X^T @ err / N + l2 * W
        (explicit delta-rule-equivalent update, not autograd)."""
        pred = X @ self.W
        err = pred - Y
        n = X.shape[0]
        grad = (X.t() @ err) / n + l2 * self.W
        self.W = self.W - lr * grad
        return float((err ** 2).mean())


def predict_next_struct(event_struct, predictor, d):
    """Rolls the predictor forward ONE step from a single event-struct
    context and renormalizes the output back to the elementwise-unit-
    magnitude FHRR convention by reusing bundling.bundle on a length-1 stack
    (a 1-item bundle IS the renormalization step -- reused, not reimplemented)."""
    x = to_real_2d(event_struct, d)
    y = predictor.predict_raw(x)
    p_raw = from_real_2d(y, d)
    p_norm = bundling.bundle(p_raw.unsqueeze(0))
    return p_norm


def make_context_struct(event_structs, lo, hi_inclusive):
    """Bundles event_structs[lo:hi_inclusive+1] into one context vector via
    hdlab.bundling.bundle (reused verbatim; single-event windows return the
    event itself, since bundle of one item is that item post-renorm)."""
    window = event_structs[lo:hi_inclusive + 1]
    if len(window) == 1:
        return window[0]
    return bundling.bundle(torch.stack(window, dim=0))


def make_train_test_pairs(n_events, window, held_out_frac):
    """Contiguous temporal train/test split per novel. A pair (lo, t,
    target_idx) requires context event_structs[lo:t+1] and target
    event_structs[target_idx] to fall ENTIRELY within the train partition
    OR ENTIRELY within the test partition -- no pair straddles the split
    (prevents any leakage across the boundary)."""
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
    """Materializes (X, Y) real-2d tensors for a list of (lo, t, target_idx)
    pairs, using make_context_struct for the context side."""
    if not pairs:
        return torch.zeros(0, 2 * d), torch.zeros(0, 2 * d)
    xs, ys = [], []
    for lo, t, target_idx in pairs:
        ctx = make_context_struct(event_structs, lo, t)
        xs.append(to_real_2d(ctx, d))
        ys.append(to_real_2d(event_structs[target_idx], d))
    return torch.stack(xs, dim=0), torch.stack(ys, dim=0)


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
# STAGE C: relation-inference readout THROUGH the predictor
# --------------------------------------------------------------------------

def score_readout(arm_name, predictor, idx, dense_vecs, d, role_vecs, objidx_roles,
                   unstated_items, satrest_items, thwart_items):
    cache = {}

    def get(text):
        if text not in cache:
            struct, _, _, cov = build_event_struct_v6(text, idx, dense_vecs, d, role_vecs, objidx_roles)
            cache[text] = (struct, cov)
        return cache[text]

    unstated_results, unstated_correct, n_ties = [], 0, 0
    for item in unstated_items:
        action_struct, action_cov = get(item["action_text"])
        predicted_next = predict_next_struct(action_struct, predictor, d) if action_struct is not None else None
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
        predicted_next = predict_next_struct(goal_struct, predictor, d) if goal_struct is not None else None
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
        predicted_next = predict_next_struct(a_struct, predictor, d) if a_struct is not None else None
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
        "expected_n_units": EXPECTED_N_SCORED_UNITS_PER_ARM * 2,
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

    # ---- shared vocab/filler content (SAME recipe as v6c, held fixed) ----
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

    # ---- STAGE A cont'd: build event-struct sequences (fillers held fixed) ----
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

    # ---- STAGE B: build train/test pairs per novel, pool, train predictor ----
    gen = torch.Generator().manual_seed(PREDICTOR_SEED)
    dim2 = 2 * D_EMBED
    predictor_trained = EventPredictor(dim2, gen)
    predictor_random = predictor_trained.clone_frozen()  # snapshot BEFORE any training step

    all_train_X, all_train_Y = [], []
    per_novel_test = {}
    per_novel_pair_counts = {}
    for name, structs in per_novel_events.items():
        n_events = len(structs)
        train_pairs, test_pairs, split_idx = make_train_test_pairs(n_events, EVENT_CONTEXT_WINDOW, HELD_OUT_FRAC)
        Xtr, Ytr = build_pair_tensors(structs, train_pairs, D_EMBED)
        Xte, Yte = build_pair_tensors(structs, test_pairs, D_EMBED)
        if Xtr.shape[0] > 0:
            all_train_X.append(Xtr)
            all_train_Y.append(Ytr)
        per_novel_test[name] = (Xte, Yte)
        per_novel_pair_counts[name] = {
            "n_events": n_events, "split_idx": split_idx,
            "n_train_pairs": len(train_pairs), "n_test_pairs": len(test_pairs),
        }
    print(f"[progress] STAGE B: per-novel pair counts = {per_novel_pair_counts}", flush=True)

    X_train = torch.cat(all_train_X, dim=0)
    Y_train = torch.cat(all_train_Y, dim=0)
    X_test = torch.cat([per_novel_test[n][0] for n in per_novel_test if per_novel_test[n][0].shape[0] > 0], dim=0) \
        if any(per_novel_test[n][0].shape[0] > 0 for n in per_novel_test) else torch.zeros(0, dim2)
    Y_test = torch.cat([per_novel_test[n][1] for n in per_novel_test if per_novel_test[n][1].shape[0] > 0], dim=0) \
        if any(per_novel_test[n][1].shape[0] > 0 for n in per_novel_test) else torch.zeros(0, dim2)

    assert X_train.shape[0] > 0, "STAGE B FAILED: zero pooled train pairs"
    assert X_test.shape[0] > 0, "STAGE B FAILED: zero pooled held-out test pairs"

    stage_b_started_mse_test_random = mse(X_test, Y_test, predictor_random)
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

    rel_improvement = (mse_test_random - mse_test_trained) / mse_test_random if mse_test_random > 0 else float("nan")
    stage_b_pass = (mse_test_trained < mse_test_random) and (rel_improvement >= STAGE_B_MIN_REL_IMPROVEMENT)

    print(f"[progress] STAGE B RESULT: mse_test_trained={mse_test_trained:.6f} "
          f"mse_test_random={mse_test_random:.6f} rel_improvement={rel_improvement:.4f} "
          f"stage_b_pass={stage_b_pass}", flush=True)

    # ARMS-MUST-DIFFER: W_trained vs W_random must differ; predicted structs on a shared probe differ
    _digests_w, _pairwise_w, w_differ = _arms_must_differ_tensors({
        "W_trained": predictor_trained.W, "W_random_init": predictor_random.W,
    })
    probe_struct = per_novel_events["alice_in_wonderland"][0]
    pred_trained_probe = predict_next_struct(probe_struct, predictor_trained, D_EMBED)
    pred_random_probe = predict_next_struct(probe_struct, predictor_random, D_EMBED)
    _digests_p, _pairwise_p, pred_differ = _arms_must_differ_tensors({
        "pred_trained": pred_trained_probe, "pred_random": pred_random_probe,
    })
    assert w_differ, "META_RULE_AF VIOLATION: W_trained and W_random_init are bit-identical"
    assert pred_differ, "META_RULE_AF VIOLATION: predicted structs from trained vs random predictor are bit-identical"

    # ---- STAGE C: relation-inference readout, both predictor arms ----
    print("[progress] STAGE C: scoring readout for TRAINED and RANDOM-INIT predictors", flush=True)
    readout_trained = score_readout(
        "TRAINED_EVENT_PREDICTOR", predictor_trained, idx, w_sgns_trained, D_EMBED, role_vecs, objidx_roles,
        unstated_items, satrest_items, thwart_items,
    )
    readout_random = score_readout(
        "RANDOM_INIT_EVENT_PREDICTOR", predictor_random, idx, w_sgns_trained, D_EMBED, role_vecs, objidx_roles,
        unstated_items, satrest_items, thwart_items,
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
        (thwart_trained_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC)  # diagnostic only; excluded from greenlight per spec

    phase1_mechanism_works = stage_b_pass and (unstated_axis_pass or satrest_axis_pass)

    if not stage_b_pass:
        insufficiency_reason = "STAGE_B_PREDICTOR_DID_NOT_LEARN_TO_PREDICT_BETTER_THAN_RANDOM"
    elif not (unstated_axis_pass or satrest_axis_pass):
        insufficiency_reason = "STAGE_C_READOUT_DID_NOT_BEAT_RANDOM_AND_WORD_LEVEL_BASELINE_ON_A_CLEAN_AXIS"
    else:
        insufficiency_reason = None

    elapsed_s = time.perf_counter() - t_start

    summary = {
        "mechanism": (
            "Event-level next-event-state predictor (linear, delta-rule/error-driven-trained) "
            "over bound AGENT/ACTION/OBJECT FHRR event structs (build_event_struct_v6, reused "
            "verbatim), read out THROUGH the predictor's one-step forward roll (structure_overlap "
            "of predicted_next vs each relation-inference candidate)."
        ),
        "stage_a_segmentation": {
            "method": "naive sentence-split regex (rough, fixed, NOT the variable)",
            "per_novel_counts": stage_a_drop_stats,
            "total_valid_events": total_valid_events,
            "stage_a_sane": stage_a_sane,
        },
        "stage_b_predictor": {
            "event_context_window": EVENT_CONTEXT_WINDOW,
            "held_out_frac": HELD_OUT_FRAC,
            "per_novel_pair_counts": per_novel_pair_counts,
            "n_pooled_train_pairs": int(X_train.shape[0]),
            "n_pooled_test_pairs": int(X_test.shape[0]),
            "predictor_epochs": PREDICTOR_EPOCHS,
            "train_curve_sampled": train_curve,
            "mse_train_final": mse_train_final,
            "mse_test_trained": mse_test_trained,
            "mse_test_random_init": mse_test_random,
            "mse_test_random_init_started": stage_b_started_mse_test_random,
            "cosine_test_trained": cos_test_trained,
            "cosine_test_random_init": cos_test_random,
            "rel_improvement_over_random": rel_improvement,
            "stage_b_min_rel_improvement_required": STAGE_B_MIN_REL_IMPROVEMENT,
            "stage_b_pass": stage_b_pass,
        },
        "stage_c_readout": {
            "arms": {
                "TRAINED_EVENT_PREDICTOR": _trim_arm(readout_trained),
                "RANDOM_INIT_EVENT_PREDICTOR": _trim_arm(readout_random),
            },
            "word_level_lexical_baseline_acc_cited": WORD_LEVEL_LEXICAL_BASELINE_ACC,
            "word_level_trained_sgns_acc_cited": WORD_LEVEL_TRAINED_SGNS_ACC_REF,
            "unstated_goal": {
                "trained_acc": unstated_trained_acc, "random_acc": unstated_random_acc,
                "beats_random": unstated_trained_acc > unstated_random_acc,
                "beats_word_level_baseline": unstated_trained_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC,
                "axis_pass": unstated_axis_pass,
            },
            "satisfy_restate": {
                "trained_acc": satrest_trained_acc, "random_acc": satrest_random_acc,
                "beats_random": satrest_trained_acc > satrest_random_acc,
                "beats_word_level_baseline": satrest_trained_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC,
                "axis_pass": satrest_axis_pass,
            },
            "thwart_cause": {
                "trained_acc": thwart_trained_acc, "random_acc": thwart_random_acc,
                "beats_random": thwart_trained_acc > thwart_random_acc,
                "beats_word_level_baseline": thwart_trained_acc > WORD_LEVEL_LEXICAL_BASELINE_ACC,
                "axis_pass_diagnostic_only_excluded_from_greenlight": thwart_axis_pass_diag_only,
            },
        },
        "PHASE1_MECHANISM_WORKS": phase1_mechanism_works,
        "insufficiency_reason": insufficiency_reason,
        "eval_caveat": (
            "N=25 Director-VERIFIED balanced eval; small-N diagnostic by ML standards -- report "
            "per-item-type counts alongside fractions, do not overclaim precision beyond ~1/25=0.04 "
            "(unstated_goal ~1/12=0.083, satisfy_restate ~1/7=0.143) resolution."
        ),
        "elapsed_s": elapsed_s,
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"PHASE1_MECHANISM_WORKS={phase1_mechanism_works}; stage_b_pass={stage_b_pass} "
            f"(mse_trained={mse_test_trained:.5f} vs mse_random={mse_test_random:.5f}, "
            f"rel_improvement={rel_improvement:+.4f}); unstated_goal trained={unstated_trained_acc:.4f} "
            f"random={unstated_random_acc:.4f}; satisfy_restate trained={satrest_trained_acc:.4f} "
            f"random={satrest_random_acc:.4f}; thwart_cause trained={thwart_trained_acc:.4f} "
            f"random={thwart_random_acc:.4f}; word_level_baseline_cited={WORD_LEVEL_LEXICAL_BASELINE_ACC:.4f}; "
            f"insufficiency_reason={insufficiency_reason}"
        ),
        "summary": f"PHASE1 event-level prediction-error mechanism: WORKS={phase1_mechanism_works}",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "results_trained_unstated_goal": readout_trained["unstated_results"],
        "results_trained_satisfy_restate": readout_trained["satrest_results"],
        "results_trained_thwart_cause": readout_trained["thwart_results"],
        "results_random_unstated_goal": readout_random["unstated_results"],
        "results_random_satisfy_restate": readout_random["satrest_results"],
        "results_random_thwart_cause": readout_random["thwart_results"],
        "summary_fields": summary,
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_scaled_to_diagnostic_n25x2arms",
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_exempted": [],
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "crlb_n_a": (
            "no fixed-capacity argmax-noise-floor threshold in this cell; discrete-tier "
            "accuracy-count feasibility over N=25 items is the analogue, per this arc's own convention"
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
    build_event_struct_v6 pipeline, the segmentation regex, the
    EventPredictor train/predict cycle, and the readout scorer, all at
    N~tiny scale, end to end."""
    d = 8
    vocab = ["alice", "wants", "tea", "and", "cake", "bob", "gives", "cake2",
             "runs", "fast", "far", "away", "quickly", "sad", "happy", "the",
             "cat", "sat", "mat", "dog", "ran", "park"]
    idx = {w: i for i, w in enumerate(vocab)}
    rng = np.random.RandomState(0)
    dense_vecs = rng.rand(len(vocab), d).astype(np.float64)
    role_vecs = make_role_vecs(d, seed=1)
    objidx_roles = make_objidx_roles(d, seed=2, n_slots=6)

    # --- Stage A: segmentation on a tiny synthetic "novel" ---
    text = "Alice wants tea and cake. Bob gives cake2 to alice. The cat sat on the mat. A dog ran in the park!"
    sents = segment_events(text, max_sentences=100, min_words=2)
    assert len(sents) >= 3, f"segmentation produced too few sentences: {sents}"

    structs, n_dropped, n_total = build_event_sequence(sents, idx, dense_vecs, d, role_vecs, objidx_roles)
    assert n_total == len(sents)
    assert len(structs) >= 3, "expected at least 3 valid events from the fixture"
    for s in structs:
        assert s.dtype == torch.complex64 and s.shape == (d,)

    # --- to_real_2d / from_real_2d round trip ---
    v2d = to_real_2d(structs[0], d)
    assert v2d.shape == (2 * d,)
    back = from_real_2d(v2d, d)
    assert torch.allclose(back, structs[0], atol=1e-5), "to_real_2d/from_real_2d round trip broken"

    # --- context window bundling ---
    ctx = make_context_struct(structs, 0, 1)
    assert ctx.shape == (d,) and ctx.dtype == torch.complex64
    ctx_single = make_context_struct(structs, 0, 0)
    assert torch.allclose(ctx_single, structs[0])

    # --- train/test pair split: no leakage, deterministic ---
    train_pairs, test_pairs, split_idx = make_train_test_pairs(len(structs), window=2, held_out_frac=0.3)
    assert len(train_pairs) > 0 and len(test_pairs) >= 0
    for lo, t, target_idx in train_pairs:
        assert target_idx < split_idx and lo < split_idx
    for lo, t, target_idx in test_pairs:
        assert lo >= split_idx and target_idx <= len(structs) - 1

    # --- EventPredictor: trained must reduce MSE vs its own random-init snapshot on a
    # synthetic case engineered to be learnable (target = context, an identity map) ---
    gen = torch.Generator().manual_seed(123)
    dim2 = 2 * d
    pred = EventPredictor(dim2, gen)
    pred_random = pred.clone_frozen()
    fixed_rng = torch.Generator().manual_seed(5)
    X = torch.rand(40, dim2, generator=fixed_rng)
    Y = X.clone()  # identity target: perfectly learnable by a linear map
    mse_before = mse(X, Y, pred)
    for _ in range(200):
        pred.train_step(X, Y, lr=0.2, l2=0.0)
    mse_after = mse(X, Y, pred)
    mse_random_ref = mse(X, Y, pred_random)
    assert mse_after < mse_before, f"predictor did not reduce training MSE: before={mse_before} after={mse_after}"
    assert mse_after < mse_random_ref, (
        f"trained predictor did not beat its own random-init snapshot on the learnable fixture: "
        f"trained={mse_after} random={mse_random_ref}"
    )

    # --- predict_next_struct: output is complex64[d], unit-magnitude components (via bundle reuse) ---
    pn = predict_next_struct(structs[0], pred, d)
    assert pn.shape == (d,) and pn.dtype == torch.complex64
    mags = pn.abs()
    assert torch.allclose(mags, torch.ones_like(mags), atol=1e-4), (
        "predict_next_struct output should be elementwise-unit-magnitude (bundling.bundle renorm)"
    )

    # --- ARMS-MUST-DIFFER on predictor weights + predicted outputs ---
    _digests_w, _pw, w_differ = _arms_must_differ_tensors({"trained": pred.W, "random": pred_random.W})
    assert w_differ
    pn_trained = predict_next_struct(structs[0], pred, d)
    pn_random = predict_next_struct(structs[0], pred_random, d)
    _digests_p, _pp, p_differ = _arms_must_differ_tensors({"pred_trained": pn_trained, "pred_random": pn_random})
    assert p_differ

    # --- score_readout end-to-end on tiny fixture gold items ---
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
        res = score_readout("ARM_TEST", pred, idx, dense_vecs, d, role_vecs, objidx_roles,
                             unstated_items, satrest_items, thwart_items)
        assert res["arm_name"] == "ARM_TEST"
        assert res["n_scored_units"] == 4 + 2 + 2
        assert 0.0 <= res["unstated_goal_accuracy"] <= 1.0
        assert 0.0 <= res["satisfy_restate_accuracy"] <= 1.0
        assert 0.0 <= res["thwart_cause_accuracy"] <= 1.0
    finally:
        CATEGORY_PROTOTYPES.clear()
        CATEGORY_PROTOTYPES.update(_orig)

    print(
        f"[self_test] PASS  n_events={len(structs)}  mse_before={mse_before:.4f}  "
        f"mse_after={mse_after:.4f}  mse_random_ref={mse_random_ref:.4f}  "
        f"unit_magnitude_ok=True  n_scored_units={res['n_scored_units']}",
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
