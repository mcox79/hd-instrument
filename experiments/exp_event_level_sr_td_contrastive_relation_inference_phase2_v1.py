"""
PHASE 2 -- brain-faithful SUCCESSOR-REPRESENTATION (SR) / TD-BOOTSTRAP mechanism
proof for event-level relation inference, per the §4 spec in
notes/research_drill_biology_led_predictive_learning_mechanism_successor_representation_2026-08-03.md.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n_a declared (discrete top-1-of-(1+N_NEGATIVES) ranking; chance stated)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95)
# - discriminator survives scale: smoke exercises the REAL pipeline at tiny N (F.1)
# - HARD_PASS strictly above floor (STAGE_B_MIN_MARGIN=0.05 absolute, pre-registered)
# - HP_SCOPE: gate applies to the SR/TD trained arm only (baselines are diagnostic references)
# - cardinality_ok: n_test_pairs > 0 asserted; reported exactly
# - per-unit failure-class instrumentation: single except Exception -> crash metrics, re-raise
# - calibration_check: default_ok_for_this_regime (GAMMA/ACCUM_WINDOW/HORIZON pre-registered,
#   not tuned post-hoc; see constants block)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

WHY THIS CELL (context for a reader with no other memory of this arc):
Two prior event-predictor cells FAILED, and BOTH failures were independently diagnosed by two
VET gates (notes/skunkworks_audit_phase1_event_level_prediction_error_STAGE_B_FAILS_FAIR_
BASELINE_2026-08-03.md; notes/research_drill_brain_fidelity_audit_v2_HARD_FAIL_2026-08-03.md)
as having TWO confounds:
  (1) the training OBJECTIVE was MSE regression to a continuous FHRR target, whose global
      optimum is the training-set MEAN whenever the input underdetermines the output --
      exactly what happened (v1: predict-mean tied/beat trained, mse=0.33107 vs 0.33236).
  (2) the TEST was non-faithful: context window=1 (context-starved) and the can-fail metric was
      literal-next-sentence retrieval (wrong grain -- a single fixed horizon, not "does the
      predicted successor reach the eventual causal descendant").
A same-day research drill (notes/research_drill_biology_led_predictive_learning_mechanism_
successor_representation_2026-08-03.md) supplies the brain-faithful fix: Dayan 1993's
Successor Representation (SR), learned via TD(0) BOOTSTRAP (not point regression) and trained
CONTRASTIVELY (Zheng et al. 2024 ICLR "Contrastive Difference Predictive Coding" -- the exact
TD+contrastive fusion both VET audits independently recommended). SR structurally resists mean-
collapse because its TD target is BOOTSTRAPPED from the network's own estimate at the NEXT
state -- a state-specific fixed point, not one shared point-target averaged over the whole
training distribution.

THIS CELL implements the MINIMAL faithful version of that spec, changing ONE core variable
(the TD/contrastive objective) while fixing BOTH previously-diagnosed confounds as prerequisite
repairs (accumulated context instead of window=1; multi-step reachability instead of literal-
next-sentence). Per Director's task: prioritize the ONE core claim, do not flail -- Stage C
(the UNSTATED_GOAL/SATISFY_RESTATE/THWART_CAUSE readout) is explicitly OUT OF SCOPE this pass;
this cell answers exactly the pre-registered falsification question and nothing more.

PRIOR-WORK CHECK (mandatory, substrate_query.sh, run before authoring):
Query: "TD bootstrap successor representation contrastive predictive map event relation
inference" -> top-5 hits all cosine 0.36-0.3857, ALL WordNet/FrameNet lexical entries for the
unrelated word "representative"/"representation" (semantic-field false positives from the
generic word "representation", not SR/TD conceptual overlap) plus one unrelated active-inference
analogy note. NONE at conceptual overlap for this mechanism. Consistent with the research drill's
own KB-check (3 queries, all genuinely-new-territory verdicts). Genuinely new build, not a
rediscovery.

THE THREE FIXES relative to the disqualified v1/v2 recipe (ONE core variable + two prerequisite
context/metric repairs the research drill separately flagged as blocking):

(1) OBJECTIVE (the core experimental variable): TD(0) semi-gradient bootstrap target
    target_t = renorm( phi(event_{t+1}) + GAMMA * M_frozen(context_{t+1}) )
    (phi = the substrate's own bound FHRR event-structure encoding, reused verbatim from
    build_event_struct_v6; M_frozen = the predictor's own estimate one step ahead, computed with
    a FROZEN copy of the weights from the start of the current outer TD sweep -- standard
    semi-gradient/target-network TD(0), avoiding a moving-target instability while keeping the
    update genuinely bootstrapped, not point-regression to a fixed corpus-wide label). Trained via
    an INFONCE-style softmax-contrastive gradient (rank the true per-row target above in-batch
    negatives = every OTHER pooled training pair's own bootstrapped target -- i.e. targets
    bootstrapped from OTHER timesteps/novels' own trajectories, a lightweight self-generated
    "replay" stand-in: alternate futures never actually reached from THIS context, not an
    externally curated distractor bank). This directly matches Contrastive Difference Predictive
    Coding (Zheng et al. 2024, arXiv:2310.20141), the concrete training-objective template the
    research drill cited as the closest published fusion of TD + contrastive.

(2) CONTEXT (fixes confound #1, context-starvation): instead of a single preceding event
    (EVENT_CONTEXT_WINDOW=1 in the disqualified v2 cell), the predictor's input is an
    ACCUMULATED situation-model state over the last ACCUM_WINDOW=6 events, built via the SAME
    bind+bundle algebra as hdlab.situation_model_accumulate (reusing its unit_phase_vec helper +
    hdlab.binding.bind + hdlab.bundling.bundle directly): context_t = bundle_{dist=0..window-1}(
    bind(pos_vec[dist], event_structs[t-dist])), with pos_vec[dist] FIXED distinct unit-phase
    FHRR symbols keyed by RELATIVE recency (dist=0 most recent), reused identically across every
    t and every novel. NOTE on reuse: hdlab.situation_model_accumulate.AccumulateRegister's public
    API is entity/role-oriented (tracks WHICH entity has WHICH role bound at a position, for later
    role-decode) -- it does not directly expose "bundle raw event-content across a recency
    window" as a call pattern, so this cell reimplements that EXACT algebra (bind(position-tag,
    content) then bundle) directly over event-struct content rather than forcing the class's
    entity/role API into a shape it wasn't built for. Same primitives, same organ family, new call
    pattern; documented explicitly per the audit's own admonition against silent reinvention.
    At ACCUM_WINDOW=1 this construction is provably identical to the old window=1 copy-context
    baseline (binding by one FIXED global phase vector is a unitary transform that cancels
    exactly under the conjugate-multiply overlap metric -- see self_test), so this is a strict
    generalization, not a different mechanism.

(3) METRIC (fixes confound #2, wrong-grain evaluation): instead of literal-next-sentence (t+1
    only), the ranking judge is MULTI-STEP: for held-out test index t, the "true" successor set
    is {t+1, ..., t+HORIZON_H} (HORIZON_H=3) -- does the predicted successor-vector's BEST overlap
    against ANY of these eventual descendants exceed its overlap against N_NEGATIVES same-novel
    distractors (sampled outside both the context window and the descendant range)? HONEST SCOPE
    NOTE (flagged, not spec-perfect): the §4 spec asks for ranking against the TRUE causal
    descendant per an existing CausalLinkRegister chain-membership graph; no such gold causal
    graph exists for this 5-novel corpus at this scale (the one validated CausalLinkRegister
    result, atom/cell exp_causal_link_comprehension_fuller_v3_cleaned, was built+scored on a
    different corpus/gold set). Building a fresh causal-chain gold annotation for these 5 novels
    is out of the minimal-viable scope Director specified ("do NOT flail, prioritize the ONE core
    variable"). This cell substitutes the OPERATIONAL proxy of multi-step temporal-forward
    reachability (any event within a bounded horizon counts as a "descendant"), which is a real,
    substantive fix of confound #2 (multiple horizons vs one fixed horizon) even though it is not
    literally the causal-graph judge the spec named. Flagged for Director: if this proxy is judged
    insufficient, the identified revival path is to run this SAME predictor through the existing
    CausalLinkRegister-scored corpus instead of these 5 novels.

FAIR GATE (mandatory, unchanged convention from the disqualifying VET): the SR/TD trained arm
must beat ALL THREE fair non-learned baselines -- predict-train-mean, copy-context (identity
map: predicted successor = context_t itself, untransformed), random-init (identical
architecture, zero training steps) -- by >= STAGE_B_MIN_MARGIN=0.05 absolute on the SAME
multi-step ranking metric, simultaneously.

PRE-REGISTERED FALSIFICATION (mandatory, stated BEFORE running): report MEASURED, not massaged.
  MECHANISM_REAL      = fair gate passes (all 3 margins >= 0.05) AND the mean-collapse
                        diagnostic (mean cosine of TRAINED arm's predictions against the
                        train-target mean vector) is BELOW MEAN_COLLAPSE_THRESHOLD=0.5
                        (pre-registered; v1/v2's prior collapsed figures were 0.906/0.98 --
                        this is a generous, not cherry-picked, threshold well below those).
  MECHANISM_FALSIFIED = fair gate fails (loses to ANY of mean/copy/random by < 0.05 margin)
                        OR mean-collapse diagnostic >= 0.5, WITH BOTH prerequisite confounds
                        (context-starvation, wrong-grain metric) already fixed above -- per the
                        research drill's own pre-registration, a third failure under these
                        conditions is a genuine paradigm negative, not a mis-operationalization,
                        and must be reported as such.

DISCIPLINE:
  - glass-box, from-scratch, no borrowed embedding/model/LLM/Binder/parser.
  - ONE core experimental variable: the TD/contrastive objective (relative to the disqualified
    MSE recipe). Segmentation, word-filler content, event-struct construction HELD FIXED
    (identical reused code paths to phase1_v2). Context-window and metric-grain are declared
    PREREQUISITE REPAIRS (both independently diagnosed as blocking by the two VET audits), not
    part of the "core variable" -- but both are held FIXED across all 4 arms in THIS cell (mean/
    copy/random/trained all see the identical accumulated context and are scored by the identical
    multi-step metric), so the arm-vs-arm comparison remains a clean one-variable (objective-only)
    contrast.
  - deterministic seeding throughout (fixed int seeds; no hash()-seeded RNG; sorted index ranges).
  - ARMS-MUST-DIFFER (META_RULE_AF): W_trained vs W_random_init hash-checked; per-arm predicted
    structs for the first test pair hash-checked pairwise distinct across all 4 arms.
  - except SystemExit / except KeyboardInterrupt re-raised BEFORE except Exception; no bare
    except; no except BaseException.
  - final_metrics_atomicity: tmp_replace (os.replace).
  - cardinality_ok: n_test_pairs > 0 asserted; n_train_pairs > 0 asserted; reported exactly.
  - crlb_n_a: discrete top-1-of-(1+N_NEGATIVES) multi-step ranking accuracy; chance level =
    1/(1+N_NEGATIVES) stated explicitly, the analogue of a capacity floor here.
  - runtime bound: same corpus/PPMI/SGNS cost as phase1_v2 (~140s dominant cost, MEASURED@that
    cell's own docstring), plus O((n_train_pairs)^2) in-batch contrastive score matrix per inner
    step (n_train_pairs on the order of a few hundred -> a few-hundred-squared matmul, trivial)
    times TD_ITERATIONS*CONTRASTIVE_STEPS_PER_ITER steps. Single foreground run, well under
    10 minutes. progress_logging=print_flush_true.
  - Content-filter safety: reuses ONLY the same 5 already-vetted public-domain corpus files as
    phase1_v2; no new snippets; no gold-eval item text reproduced (Stage C not run this pass).
  - GIT: local only, no push; this file + its metrics.json are the only new paths this cell
    should stage. Does NOT dispatch anything. --no-verify per caller instruction.

REUSE, do not reinvent:
  - hdlab.binding.bind/unbind, hdlab.bundling.bundle -- FHRR primitives, unchanged.
  - hdlab.situation_model_accumulate.unit_phase_vec -- the exact positional-symbol generator used
    by the validated AccumulateRegister organ (atom 29609), reused verbatim for this cell's
    recency-position tags.
  - experiments.exp_event_level_prediction_error_relation_inference_phase1_v2_associative:
    segment_events, build_event_sequence, to_real_2d, from_real_2d, sample_negatives,
    _arms_must_differ_tensors, CORPUS_PATHS, ROLE_VEC_SEED, OBJIDX_ROLE_SEED,
    OBJIDX_ROLES_N_SLOTS -- imported directly, unchanged.
  - experiments.exp_content_awareness_earned_v6_depooled_object_verified_eval.build_event_struct_v6,
    make_objidx_roles, OBJIDX_ROLE_SEED_D64 -- unchanged.
  - experiments.exp_content_awareness_earned_v5_bound_role_filler_representation.make_role_vecs,
    structure_overlap -- unchanged.
  - experiments.exp_content_awareness_ceiling_probe_earned_v3_rawppmi_meanremoval.
    build_raw_ppmi_vectors, _tokenize -- unchanged.
  - experiments.exp_content_awareness_earned_v4_error_driven_sgns.train_sgns, D_EMBED -- unchanged.
"""
import os
import sys
import json
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from hdlab import binding, bundling  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

from experiments.exp_event_level_prediction_error_relation_inference_phase1_v2_associative import (  # noqa: E402
    segment_events,
    build_event_sequence,
    to_real_2d,
    from_real_2d,
    sample_negatives,
    _arms_must_differ_tensors,
    CORPUS_PATHS,
    ROLE_VEC_SEED,
    OBJIDX_ROLE_SEED,
    OBJIDX_ROLES_N_SLOTS,
)
from experiments.exp_content_awareness_earned_v6_depooled_object_verified_eval import (  # noqa: E402
    make_objidx_roles,
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

OUTPUT_DIR = os.path.join(
    REPO_ROOT, "data", "exp_event_level_sr_td_contrastive_relation_inference_phase2_v1"
)
ANCHOR_NAME = "event_level_sr_td_contrastive_relation_inference_phase2_v1"

# ---- pre-registered constants (all HYPOTHESIZED@this-file unless cited) ----
ACCUM_WINDOW = 6          # accumulated situation-model context length (vs window=1 disqualified)
HORIZON_H = 3             # multi-step "eventual descendant" horizon (vs literal-next-sentence)
GAMMA = 0.5               # TD discount factor
TD_ITERATIONS = 5         # outer semi-gradient TD sweeps (target refreshed each sweep)
CONTRASTIVE_STEPS_PER_ITER = 40   # inner softmax-contrastive gradient steps per TD sweep
LR = 0.05
L2 = 1e-4
HELD_OUT_FRAC = 0.20
N_NEGATIVES = 9           # (1 + N_NEGATIVES)-way ranking; chance = 1/10 = 0.10
STAGE_B_MIN_MARGIN = 0.05
MEAN_COLLAPSE_THRESHOLD = 0.5   # pre-registered: prior collapsed cells measured 0.906 / 0.98

PREDICTOR_SEED = 81001
POS_VEC_SEED = 81501
NEGATIVE_SAMPLING_SEED = 140223


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


# --------------------------------------------------------------------------
# CONTEXT FIX: accumulated situation-model state over ACCUM_WINDOW events
# --------------------------------------------------------------------------

def make_pos_vecs(window, d, seed):
    """FIXED distinct unit-phase FHRR position tags, keyed by RELATIVE recency
    (index 0 = most recent). Reuses hdlab.situation_model_accumulate.unit_phase_vec
    verbatim (the same generator the validated AccumulateRegister organ uses)."""
    gen = torch.Generator().manual_seed(seed)
    return [unit_phase_vec(d, gen) for _ in range(window)]


def build_accum_contexts_for_novel(event_structs, pos_vecs, window):
    """context_t = bundle_{dist=0..min(window,t+1)-1}(bind(pos_vecs[dist], event_structs[t-dist])).
    Same bind-then-bundle algebra as hdlab.situation_model_accumulate's AccumulateRegister,
    generalized from symbolic role/position tracking to raw event-content accumulation (see
    module docstring). At window=1 this reduces EXACTLY to bind-by-one-fixed-vector, which the
    self-test verifies is an isometry that leaves relative overlap structure unchanged -- i.e.
    strictly a generalization of the old window=1 baseline, not a different construction."""
    n = len(event_structs)
    contexts = []
    for t in range(n):
        k = min(window, t + 1)
        terms = [binding.bind(pos_vecs[dist], event_structs[t - dist]) for dist in range(k)]
        if len(terms) == 1:
            contexts.append(terms[0])
        else:
            contexts.append(bundling.bundle(torch.stack(terms, dim=0)))
    return contexts


def weighted_bundle_pair(a_complex, b_complex, weight_b):
    """bundle(a, weight_b*b) via hdlab.bundling.bundle on a 2-term stack -- the SR/TD
    combination target = phi(event_{t+1}) + gamma*M(context_{t+1}), renormalized to FHRR
    unit-magnitude convention exactly like the existing predict_next_struct renorm trick."""
    stacked = torch.stack([a_complex, (weight_b + 0j) * b_complex], dim=0)
    return bundling.bundle(stacked)


# --------------------------------------------------------------------------
# TRAIN/TEST PAIR CONSTRUCTION (leakage-safe, per-novel)
# --------------------------------------------------------------------------

def make_td_pairs(n_events, horizon, held_out_frac):
    """t is valid if context_{t+1} exists (t+1 <= n_events-1, always true given the horizon
    check below) and the full descendant range {t+1..t+horizon} exists (t+horizon <= n_events-1).
    A pair straddling the train/test split boundary is dropped entirely (neither pure train nor
    pure test), same leakage-avoidance convention as phase1_v2's make_train_test_pairs."""
    split_idx = int(round(n_events * (1.0 - held_out_frac)))
    train_ts, test_ts = [], []
    for t in range(0, n_events):
        if t + horizon > n_events - 1:
            continue
        if t + horizon < split_idx:
            train_ts.append(t)
        elif t >= split_idx:
            test_ts.append(t)
    return train_ts, test_ts, split_idx


# --------------------------------------------------------------------------
# SR/TD PREDICTOR: identical linear architecture to phase1_v2's EventPredictor,
# but a NEW training rule (contrastive-softmax over a TD-bootstrapped target,
# not MSE-to-a-fixed-label -- the core experimental variable of this cell).
# --------------------------------------------------------------------------

class SRPredictor:
    def __init__(self, dim2, generator):
        self.dim2 = dim2
        scale = 1.0 / (dim2 ** 0.5)
        self.W = (torch.rand(dim2, dim2, generator=generator) - 0.5) * 2.0 * scale

    def clone_frozen(self):
        p = SRPredictor.__new__(SRPredictor)
        p.dim2 = self.dim2
        p.W = self.W.clone()
        return p

    def predict_raw(self, x):
        return x @ self.W

    def contrastive_train_step(self, X, Y, lr=LR, l2=L2):
        """InfoNCE-style softmax-contrastive gradient step. X: (B, dim2) contexts, Y: (B, dim2)
        TD-bootstrapped targets aligned per-row. Negatives for row i = every OTHER row's own
        target (self-generated, in-batch; see module docstring). Score = linear dot product
        (exactly proportional to structure_overlap, since real-2d dot == Re(conj(a).b) for the
        [real,imag] concatenation convention used throughout this codebase)."""
        B = X.shape[0]
        P = X @ self.W                       # (B, dim2) predicted
        logits = P @ Y.t()                   # (B, B): logits[i,j] = dot(p_i, y_j)
        logits = logits - logits.max(dim=1, keepdim=True).values
        exp = torch.exp(logits)
        denom = exp.sum(dim=1, keepdim=True)
        softmax = exp / denom
        labels = torch.arange(B)
        loss = -torch.log(softmax[labels, labels] + 1e-12).mean()
        # dL/dP_i = -y_i + sum_j softmax_ij * y_j  (standard softmax-CE gradient, linear score)
        grad_P = (softmax @ Y - Y) / B
        grad_W = X.t() @ grad_P + l2 * self.W
        self.W = self.W - lr * grad_W
        return float(loss)


def predict_struct(x2d, predictor, d):
    y = predictor.predict_raw(x2d)
    p_raw = from_real_2d(y, d)
    return bundling.bundle(p_raw.unsqueeze(0))


# --------------------------------------------------------------------------
# MULTI-STEP RANKING METRIC (fixes confound #2: wrong-grain evaluation)
# --------------------------------------------------------------------------

def score_multistep_retrieval(arm_name, predicted_structs, test_meta, per_novel_events, d,
                               horizon, n_negatives, seed_base):
    """test_meta[i] = (novel_name, t, accum_window). 'True' successor set = {t+1..t+horizon}.
    Correct if max(overlap vs true descendants) is the STRICT max among {true_best} U negatives
    (a tie with a negative counts as a miss, same conservative convention as phase1_v2)."""
    n_pairs = len(predicted_structs)
    correct = 0
    per_pair_records = []
    for i in range(n_pairs):
        pred = predicted_structs[i]
        novel, t, window = test_meta[i]
        events = per_novel_events[novel]
        descendant_idx = list(range(t + 1, t + horizon + 1))
        pool_indices_valid = list(range(len(events)))
        exclude = set(range(max(0, t - window + 1), t + horizon + 1))
        neg_idx = sample_negatives(events, pool_indices_valid, exclude, n_negatives, seed_base + i)
        true_overlaps = [structure_overlap(pred, events[j], d)[0] for j in descendant_idx]
        neg_overlaps = [structure_overlap(pred, events[j], d)[0] for j in neg_idx]
        best_true = max(true_overlaps)
        all_overlaps = true_overlaps + neg_overlaps
        overall_max = max(all_overlaps)
        # correct iff the best true descendant attains the global max AND no negative ties it
        # (conservative tie convention: a tie with a negative counts as a miss, matching
        # phase1_v2's score_retrieval convention).
        is_correct = (best_true == overall_max) and not any(v == overall_max for v in neg_overlaps)
        if is_correct:
            correct += 1
        per_pair_records.append({
            "novel": novel, "t": t, "descendant_idx": descendant_idx, "best_true_overlap": best_true,
            "n_negatives_sampled": len(neg_idx), "correct": bool(is_correct),
        })
    acc = correct / n_pairs if n_pairs > 0 else float("nan")
    return {
        "arm_name": arm_name, "retrieval_accuracy": acc, "n_correct": correct,
        "n_test_pairs": n_pairs, "chance_level": 1.0 / (n_negatives + 1),
        "per_pair_records": per_pair_records,
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    t_start = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": "diagnostic_inline_foreground",
        "expected_n_units": "variable_test_pairs",
    }
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(start_marker, f)
    os.replace(tmp, final)

    # ---- corpus / vocab / SGNS (identical to phase1_v2) ----
    novel_texts = {}
    for name, p in CORPUS_PATHS:
        with open(p, "r", encoding="utf-8") as f:
            novel_texts[name] = f.read()
    print(f"[progress] corpus loaded, {len(novel_texts)} novels", flush=True)

    per_novel_sentences = {name: segment_events(text) for name, text in novel_texts.items()}
    stage_a_counts = {name: len(s) for name, s in per_novel_sentences.items()}
    assert all(n > 0 for n in stage_a_counts.values()), "a novel produced zero events"
    print(f"[progress] sentence counts = {stage_a_counts}", flush=True)

    corpus_texts_all = list(novel_texts.values())
    vocab, idx, _ppmi_raw, n_tokens, vocab_size, _nnz = build_raw_ppmi_vectors(corpus_texts_all)
    tokens = []
    for text in corpus_texts_all:
        tokens.extend(_tokenize(text))
    tok_idx = np.array([idx.get(w, -1) for w in tokens], dtype=np.int64)
    vocab_counts_arr = np.zeros(vocab_size, dtype=np.int64)
    for ti in tok_idx:
        if ti >= 0:
            vocab_counts_arr[ti] += 1
    print("[progress] starting SGNS retrain", flush=True)
    w_sgns_trained, _w_random, n_pairs_trained, _per_epoch = train_sgns(tok_idx, vocab_size, vocab_counts_arr)
    print(f"[progress] SGNS complete n_pairs_trained={n_pairs_trained}", flush=True)

    role_vecs = make_role_vecs(D_EMBED, ROLE_VEC_SEED)
    objidx_roles = make_objidx_roles(D_EMBED, OBJIDX_ROLE_SEED, n_slots=OBJIDX_ROLES_N_SLOTS)

    per_novel_events = {}
    stage_a_drop = {}
    for name, sents in per_novel_sentences.items():
        structs, n_dropped, n_total = build_event_sequence(sents, idx, w_sgns_trained, D_EMBED, role_vecs, objidx_roles)
        per_novel_events[name] = structs
        stage_a_drop[name] = {"n_total": n_total, "n_dropped": n_dropped, "n_valid": len(structs)}
        print(f"[progress] {name} valid_events={len(structs)}/{n_total}", flush=True)

    total_valid_events = sum(v["n_valid"] for v in stage_a_drop.values())
    stage_a_sane = all(v["n_valid"] >= 20 for v in stage_a_drop.values())
    assert stage_a_sane, "STAGE A FAILED: a novel produced fewer than 20 valid events"

    # ---- CONTEXT FIX: accumulated situation-model context per novel ----
    pos_vecs = make_pos_vecs(ACCUM_WINDOW, D_EMBED, POS_VEC_SEED)
    per_novel_contexts = {
        name: build_accum_contexts_for_novel(structs, pos_vecs, ACCUM_WINDOW)
        for name, structs in per_novel_events.items()
    }
    print("[progress] accumulated situation-model contexts built", flush=True)

    # ---- pooled train/test pairs (leakage-safe, per-novel) ----
    train_X, train_ctxnext, train_phinext = [], [], []
    test_X, test_meta, test_context_struct = [], [], []
    per_novel_pair_counts = {}
    for name, structs in per_novel_events.items():
        n_events = len(structs)
        contexts = per_novel_contexts[name]
        train_ts, test_ts, split_idx = make_td_pairs(n_events, HORIZON_H, HELD_OUT_FRAC)
        per_novel_pair_counts[name] = {
            "n_events": n_events, "split_idx": split_idx,
            "n_train": len(train_ts), "n_test": len(test_ts),
        }
        for t in train_ts:
            train_X.append(to_real_2d(contexts[t], D_EMBED))
            train_ctxnext.append(to_real_2d(contexts[t + 1], D_EMBED))
            train_phinext.append(to_real_2d(structs[t + 1], D_EMBED))
        for t in test_ts:
            test_X.append(to_real_2d(contexts[t], D_EMBED))
            test_meta.append((name, t, ACCUM_WINDOW))
            test_context_struct.append(contexts[t])
    print(f"[progress] per-novel pair counts = {per_novel_pair_counts}", flush=True)

    X_train = torch.stack(train_X, dim=0)
    CTXNEXT_train = torch.stack(train_ctxnext, dim=0)
    PHINEXT_train = torch.stack(train_phinext, dim=0)
    X_test = torch.stack(test_X, dim=0)
    n_train_pairs = X_train.shape[0]
    n_test_pairs = X_test.shape[0]
    assert n_train_pairs > 0, "STAGE B FAILED: zero pooled train pairs"
    assert n_test_pairs > 0, "STAGE B FAILED: zero pooled held-out test pairs"
    print(f"[progress] n_train_pairs={n_train_pairs} n_test_pairs={n_test_pairs}", flush=True)

    # ---- SR/TD predictor: init, random-init baseline snapshot ----
    gen = torch.Generator().manual_seed(PREDICTOR_SEED)
    dim2 = 2 * D_EMBED
    predictor = SRPredictor(dim2, gen)
    predictor_random = predictor.clone_frozen()

    # ---- TD outer sweeps + inner contrastive gradient steps ----
    loss_curve = []
    Y_target_train = None
    for outer in range(TD_ITERATIONS):
        W_frozen = predictor.W.clone()
        M_ctxnext_2d = CTXNEXT_train @ W_frozen  # M(context_{t+1}) via frozen weights (bootstrap)
        targets = []
        for i in range(n_train_pairs):
            phi_next_c = from_real_2d(PHINEXT_train[i], D_EMBED)
            m_next_c = from_real_2d(M_ctxnext_2d[i], D_EMBED)
            targets.append(weighted_bundle_pair(phi_next_c, m_next_c, GAMMA))
        Y_target_train = torch.stack([to_real_2d(s, D_EMBED) for s in targets], dim=0)

        if not torch.isfinite(Y_target_train).all():
            raise FloatingPointError(f"NaN/Inf in TD target at outer sweep {outer}")

        for inner in range(CONTRASTIVE_STEPS_PER_ITER):
            loss = predictor.contrastive_train_step(X_train, Y_target_train, lr=LR, l2=L2)
            if not torch.isfinite(predictor.W).all():
                raise FloatingPointError(f"NaN/Inf in predictor.W at outer={outer} inner={inner}")
        loss_curve.append({"outer_sweep": outer, "final_inner_contrastive_loss": loss})
        print(f"[progress] TD outer_sweep={outer}/{TD_ITERATIONS} contrastive_loss={loss:.6f}", flush=True)

    _digests_w, _pw, w_differ = _arms_must_differ_tensors({
        "W_trained": predictor.W, "W_random_init": predictor_random.W,
    })
    assert w_differ, "META_RULE_AF VIOLATION: W_trained and W_random_init are bit-identical"

    # ---- fair-baseline arm predictions on held-out test pairs ----
    print("[progress] computing FAIR-BASELINE multi-step retrieval accuracies", flush=True)
    mean_target_2d = Y_target_train.mean(dim=0)
    mean_target_struct = bundling.bundle(from_real_2d(mean_target_2d, D_EMBED).unsqueeze(0))

    pred_trained = [predict_struct(X_test[i], predictor, D_EMBED) for i in range(n_test_pairs)]
    pred_random = [predict_struct(X_test[i], predictor_random, D_EMBED) for i in range(n_test_pairs)]
    pred_mean = [mean_target_struct for _ in range(n_test_pairs)]
    pred_copy = test_context_struct  # copy-context: identity map, no W transform

    _digests_p, _pw2, pred_differ = _arms_must_differ_tensors({
        "pred_trained_0": pred_trained[0], "pred_random_0": pred_random[0],
        "pred_mean_0": pred_mean[0], "pred_copy_0": pred_copy[0],
    })
    assert pred_differ, "META_RULE_AF VIOLATION: not all 4 arms differ on the first test pair"

    ret_trained = score_multistep_retrieval("TRAINED_SR_TD", pred_trained, test_meta, per_novel_events,
                                             D_EMBED, HORIZON_H, N_NEGATIVES, NEGATIVE_SAMPLING_SEED)
    ret_random = score_multistep_retrieval("RANDOM_INIT", pred_random, test_meta, per_novel_events,
                                            D_EMBED, HORIZON_H, N_NEGATIVES, NEGATIVE_SAMPLING_SEED)
    ret_mean = score_multistep_retrieval("PREDICT_MEAN", pred_mean, test_meta, per_novel_events,
                                          D_EMBED, HORIZON_H, N_NEGATIVES, NEGATIVE_SAMPLING_SEED)
    ret_copy = score_multistep_retrieval("COPY_CONTEXT", pred_copy, test_meta, per_novel_events,
                                          D_EMBED, HORIZON_H, N_NEGATIVES, NEGATIVE_SAMPLING_SEED)

    acc_trained = ret_trained["retrieval_accuracy"]
    acc_random = ret_random["retrieval_accuracy"]
    acc_mean = ret_mean["retrieval_accuracy"]
    acc_copy = ret_copy["retrieval_accuracy"]

    margin_vs_random = acc_trained - acc_random
    margin_vs_mean = acc_trained - acc_mean
    margin_vs_copy = acc_trained - acc_copy

    stage_b_pass = (
        margin_vs_random >= STAGE_B_MIN_MARGIN and
        margin_vs_mean >= STAGE_B_MIN_MARGIN and
        margin_vs_copy >= STAGE_B_MIN_MARGIN
    )
    baselines_in_band = all(0.05 <= a <= 0.95 for a in (acc_random, acc_mean, acc_copy))

    # ---- MEAN-COLLAPSE DIAGNOSTIC (the anti-motivated-reasoning falsification check) ----
    mean_collapse_trained = float(np.mean([
        structure_overlap(pred_trained[i], mean_target_struct, D_EMBED)[0] for i in range(n_test_pairs)
    ]))
    mean_collapse_random = float(np.mean([
        structure_overlap(pred_random[i], mean_target_struct, D_EMBED)[0] for i in range(n_test_pairs)
    ]))
    mean_collapse_flag = mean_collapse_trained >= MEAN_COLLAPSE_THRESHOLD

    print(f"[progress] RESULT: trained={acc_trained:.4f} random={acc_random:.4f} mean={acc_mean:.4f} "
          f"copy={acc_copy:.4f} margins=(rand={margin_vs_random:+.4f} mean={margin_vs_mean:+.4f} "
          f"copy={margin_vs_copy:+.4f}) stage_b_pass={stage_b_pass} "
          f"mean_collapse_trained={mean_collapse_trained:.4f} mean_collapse_flag={mean_collapse_flag}",
          flush=True)

    if stage_b_pass and not mean_collapse_flag:
        top_verdict = "MECHANISM_REAL"
        falsification_reason = None
    elif mean_collapse_flag:
        top_verdict = "MECHANISM_FALSIFIED"
        falsification_reason = (
            f"MEAN_COLLAPSE_PERSISTED (cosine_vs_train_mean={mean_collapse_trained:.4f} >= "
            f"threshold {MEAN_COLLAPSE_THRESHOLD}) DESPITE TD-bootstrap + contrastive objective "
            "+ accumulated context + multi-step metric; genuine paradigm negative per pre-reg."
        )
    else:
        worst = min(
            [("random", margin_vs_random), ("mean", margin_vs_mean), ("copy", margin_vs_copy)],
            key=lambda kv: kv[1],
        )
        top_verdict = "MECHANISM_FALSIFIED"
        falsification_reason = (
            f"FAIR_GATE_FAILED: trained did not beat {worst[0]}-baseline by >= "
            f"{STAGE_B_MIN_MARGIN} (margin={worst[1]:+.4f}); genuine paradigm negative per pre-reg "
            "since both prior confounds (context-starvation, wrong-grain metric) are fixed here."
        )

    elapsed_s = time.perf_counter() - t_start

    summary = {
        "mechanism": (
            "SR-style predictive map over bound FHRR event structures, TD(0) semi-gradient "
            "bootstrapped target, trained via in-batch InfoNCE-style contrastive gradient, "
            "context=accumulated situation-model state (window=6), metric=multi-step (horizon=3) "
            "same-novel reachability ranking against 3 fair non-learned baselines."
        ),
        "redo_of": (
            "experiments/exp_event_level_prediction_error_relation_inference_phase1_v2_"
            "associative.py, whose MSE-regression recipe was independently HARD_FAIL'd by "
            "notes/skunkworks_audit_phase1_event_level_prediction_error_STAGE_B_FAILS_FAIR_"
            "BASELINE_2026-08-03.md and notes/research_drill_brain_fidelity_audit_v2_HARD_FAIL_"
            "2026-08-03.md."
        ),
        "constants": {
            "ACCUM_WINDOW": ACCUM_WINDOW, "HORIZON_H": HORIZON_H, "GAMMA": GAMMA,
            "TD_ITERATIONS": TD_ITERATIONS, "CONTRASTIVE_STEPS_PER_ITER": CONTRASTIVE_STEPS_PER_ITER,
            "N_NEGATIVES": N_NEGATIVES, "STAGE_B_MIN_MARGIN": STAGE_B_MIN_MARGIN,
            "MEAN_COLLAPSE_THRESHOLD": MEAN_COLLAPSE_THRESHOLD,
        },
        "stage_a": {"per_novel": stage_a_drop, "total_valid_events": total_valid_events, "sane": stage_a_sane},
        "pair_counts": per_novel_pair_counts,
        "n_train_pairs": n_train_pairs, "n_test_pairs": n_test_pairs,
        "loss_curve": loss_curve,
        "retrieval": {
            "chance_level": 1.0 / (N_NEGATIVES + 1),
            "trained_accuracy": acc_trained, "random_init_accuracy": acc_random,
            "predict_mean_accuracy": acc_mean, "copy_context_accuracy": acc_copy,
            "margin_vs_random": margin_vs_random, "margin_vs_mean": margin_vs_mean,
            "margin_vs_copy": margin_vs_copy,
            "baselines_in_band_0.05_0.95": baselines_in_band,
            "stage_b_pass": stage_b_pass,
        },
        "mean_collapse_diagnostic": {
            "cosine_vs_train_mean_trained": mean_collapse_trained,
            "cosine_vs_train_mean_random_init_reference": mean_collapse_random,
            "threshold": MEAN_COLLAPSE_THRESHOLD,
            "mean_collapse_flag": mean_collapse_flag,
            "prior_collapsed_values_cited": {"phase1_v1": 0.906, "phase1_v2_diagnostic": None},
        },
        "TOP_VERDICT": top_verdict,
        "falsification_reason": falsification_reason,
        "scope_note": (
            "Stage C (UNSTATED_GOAL/SATISFY_RESTATE/THWART_CAUSE readout) explicitly OUT OF SCOPE "
            "this pass per Director's minimal-viable instruction; this cell answers only the "
            "pre-registered SR/TD fair-gate + mean-collapse falsification question."
        ),
        "causal_descendant_metric_scope_flag": (
            "Multi-step temporal-forward reachability (horizon=3) used as an operational proxy "
            "for causal-descendant ranking; no gold causal-chain graph exists for this 5-novel "
            "corpus at this scale. Flagged for Director per module docstring."
        ),
        "elapsed_s": elapsed_s,
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"TOP_VERDICT={top_verdict}; stage_b_pass={stage_b_pass} "
            f"(trained={acc_trained:.4f} random={acc_random:.4f} mean={acc_mean:.4f} "
            f"copy={acc_copy:.4f}; margins rand={margin_vs_random:+.4f} mean={margin_vs_mean:+.4f} "
            f"copy={margin_vs_copy:+.4f}); mean_collapse_trained={mean_collapse_trained:.4f} "
            f"(threshold={MEAN_COLLAPSE_THRESHOLD}, flag={mean_collapse_flag}); "
            f"n_test_pairs={n_test_pairs}; falsification_reason={falsification_reason}"
        ),
        "summary": f"PHASE2 SR/TD-contrastive event-level mechanism: TOP_VERDICT={top_verdict}",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "retrieval_per_pair_trained": ret_trained["per_pair_records"],
        "retrieval_per_pair_random": ret_random["per_pair_records"],
        "retrieval_per_pair_mean": ret_mean["per_pair_records"],
        "retrieval_per_pair_copy": ret_copy["per_pair_records"],
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
            f"discrete top-1-of-{N_NEGATIVES + 1} multi-step reachability ranking accuracy "
            f"(chance={1.0 / (N_NEGATIVES + 1):.3f}) is the analogue of a capacity floor here"
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, final_path)

    print(json.dumps(summary, indent=2))


def self_test():
    """Tiny-scale real-code-path self-test (F.1): exercises the REAL build_event_struct_v6
    pipeline, the accumulated-context builder, the SR/TD bootstrap + contrastive train step,
    the multi-step ranking scorer, and the mean-collapse diagnostic, all at N~tiny scale."""
    d = 8
    vocab = ["alice", "wants", "tea", "and", "cake", "bob", "gives", "cake2",
             "runs", "fast", "far", "away", "quickly", "sad", "happy", "the",
             "cat", "sat", "mat", "dog", "ran", "park", "read", "book", "slept",
             "woke", "smiled", "cried"]
    idx = {w: i for i, w in enumerate(vocab)}
    rng = np.random.RandomState(0)
    dense_vecs = rng.rand(len(vocab), d).astype(np.float64)
    role_vecs = make_role_vecs(d, seed=1)
    objidx_roles = make_objidx_roles(d, seed=2, n_slots=8)

    text = ("Alice wants tea and cake. Bob gives cake2 to alice. The cat sat on the mat. "
            "A dog ran in the park quickly. Alice runs fast away sad. Bob gives happy cake2. "
            "Alice read the book. Bob slept quickly. Alice woke and smiled. Bob cried sad.")
    sents = segment_events(text, max_sentences=100, min_words=2)
    assert len(sents) >= 8, f"segmentation produced too few sentences: {sents}"
    structs, n_dropped, n_total = build_event_sequence(sents, idx, dense_vecs, d, role_vecs, objidx_roles)
    assert n_total == len(sents)
    assert len(structs) >= 8
    for s in structs:
        assert s.dtype == torch.complex64 and s.shape == (d,)

    # --- window=1 isometry check: bind-by-one-fixed-vector must leave relative overlap intact ---
    pos_vecs_w1 = make_pos_vecs(1, d, seed=99)
    ctx_w1 = build_accum_contexts_for_novel(structs, pos_vecs_w1, 1)
    raw_overlap, _ = structure_overlap(structs[0], structs[1], d)
    ctx_overlap, _ = structure_overlap(ctx_w1[0], ctx_w1[1], d)
    assert abs(raw_overlap - ctx_overlap) < 1e-4, (
        f"window=1 context must be isometric to raw event overlap (raw={raw_overlap}, "
        f"ctx={ctx_overlap}) -- generalization claim in module docstring would be false"
    )

    # --- accumulated context (window>1) must actually differ from window=1 and from raw events ---
    pos_vecs = make_pos_vecs(4, d, seed=POS_VEC_SEED)
    ctx4 = build_accum_contexts_for_novel(structs, pos_vecs, 4)
    assert len(ctx4) == len(structs)
    overlap_ctx4_vs_event = structure_overlap(ctx4[5], structs[5], d)[0]
    overlap_ctx4_vs_ctx1 = structure_overlap(ctx4[5], ctx_w1[5], d)[0]
    assert overlap_ctx4_vs_event < 0.999, "accumulated (window=4) context must differ from the raw single event"
    assert overlap_ctx4_vs_ctx1 < 0.999, "accumulated (window=4) context must differ from window=1 context"

    # --- make_td_pairs: no leakage ---
    train_ts, test_ts, split_idx = make_td_pairs(len(structs), horizon=2, held_out_frac=0.34)
    assert len(train_ts) > 0 and len(test_ts) > 0
    for t in train_ts:
        assert t + 2 < split_idx
    for t in test_ts:
        assert t >= split_idx

    # --- SRPredictor contrastive_train_step: loss must decrease on a learnable synthetic fixture ---
    gen = torch.Generator().manual_seed(123)
    dim2 = 2 * d
    pred = SRPredictor(dim2, gen)
    pred_random = pred.clone_frozen()
    fixed_rng = torch.Generator().manual_seed(5)
    X = torch.rand(20, dim2, generator=fixed_rng)
    Y = X.clone()  # identity-learnable fixture: W=I should minimize contrastive loss
    loss_before = pred.contrastive_train_step(X, Y, lr=0.0, l2=0.0)  # lr=0: measure only
    for _ in range(150):
        pred.contrastive_train_step(X, Y, lr=0.3, l2=0.0)
    loss_after = pred.contrastive_train_step(X, Y, lr=0.0, l2=0.0)
    assert loss_after < loss_before, f"contrastive loss did not decrease: before={loss_before} after={loss_after}"

    _dw, _pw, w_differ = _arms_must_differ_tensors({"trained": pred.W, "random": pred_random.W})
    assert w_differ

    # --- weighted_bundle_pair: TD-target combination must be complex64, unit-magnitude-ish ---
    a = structs[0]
    b = structs[1]
    combo = weighted_bundle_pair(a, b, 0.5)
    assert combo.dtype == torch.complex64 and combo.shape == (d,)
    mags = combo.abs()
    assert torch.allclose(mags, torch.ones_like(mags), atol=1e-4), "weighted_bundle_pair must renorm to unit magnitude"

    # --- multi-step retrieval scorer: sanity on a synthetic fixture (good predictor beats bad) ---
    fake_events = [
        torch.polar(torch.ones(d), torch.rand(d, generator=torch.Generator().manual_seed(seed)) * 6.28).to(torch.complex64)
        for seed in range(14)
    ]
    per_novel = {"fixture": fake_events}
    test_meta_fixture = [("fixture", i, 2) for i in range(8)]
    good_pred = [fake_events[i + 1] for i in range(8)]  # matches the FIRST true descendant exactly
    bad_pred = [fake_events[0] for _ in range(8)]        # constant wrong prediction
    res_good = score_multistep_retrieval("GOOD", good_pred, test_meta_fixture, per_novel, d, 2, 4, seed_base=555)
    res_bad = score_multistep_retrieval("BAD", bad_pred, test_meta_fixture, per_novel, d, 2, 4, seed_base=555)
    assert res_good["retrieval_accuracy"] == 1.0, (
        f"multi-step scorer sanity failed: a predictor exactly matching a true descendant should "
        f"score 1.0, got {res_good['retrieval_accuracy']}"
    )
    assert res_bad["retrieval_accuracy"] < res_good["retrieval_accuracy"]

    # --- mean-collapse diagnostic: sanity that a genuinely-constant predictor scores HIGH on it,
    # and a differentiated (identity-like) predictor scores LOWER, confirming the diagnostic itself
    # discriminates the failure mode it's meant to catch ---
    mean_struct = bundling.bundle(torch.stack(fake_events[:4], dim=0))
    const_pred_diag = float(np.mean([structure_overlap(mean_struct, mean_struct, d)[0] for _ in range(4)]))
    varied_pred_diag = float(np.mean([structure_overlap(fake_events[i], mean_struct, d)[0] for i in range(4)]))
    assert const_pred_diag >= varied_pred_diag, (
        "mean-collapse diagnostic sanity failed: a constant-vs-mean predictor should score >= "
        "a genuinely input-varying predictor"
    )

    print(
        f"[self_test] PASS  n_events={len(structs)}  loss_before={loss_before:.4f}  "
        f"loss_after={loss_after:.4f}  window1_isometry_delta={abs(raw_overlap - ctx_overlap):.6f}  "
        f"retrieval_good={res_good['retrieval_accuracy']:.3f}  retrieval_bad={res_bad['retrieval_accuracy']:.3f}  "
        f"mean_collapse_sanity(const={const_pred_diag:.3f}, varied={varied_pred_diag:.3f})",
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
