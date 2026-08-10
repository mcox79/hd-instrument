# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (D1/D2 prediction-vector digests pairwise differ)
# - final_metrics_atomicity declared (tmp_replace)
# - except SystemExit: raise BEFORE except KeyboardInterrupt: raise BEFORE except Exception (no
#   BaseException, no bare except:)
# - crlb_n/a declared (discrete 3-way classification accuracy; no capacity/noise-floor discriminator
#   threshold applies)
# - HP_SCOPE: per-arm HARD-PASS/MIDDLE_BAND/HARD-FAIL bands (see prereg; identical bands to iter-1)
# - cardinality_ok: EXPECTED_N_DEV_UNITS = n_dev * 2
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (GATE_THRESH = median-of-strictly-positive
#   bow_margin over dev, reused verbatim from iter-1's fix; RELEVANT_RELATIONS map is
#   HYPOTHESIZED@author-design, never fit; MIN_COH_CONVERGENCE=2 is HYPOTHESIZED@author-design)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL compute_item_features / resolve_item_arm / fit_arm_d2 /
#   exp_checkpoint round-trip at trivial scale (real_code_path_exercised); no synthetic-only shortcut
# - progress_logging: print_flush_true
# See preregs/2026-08-10_crutch_discriminative_selection_coherence_tom_v2.md for the full pre-reg.
"""exp_crutch_discriminative_selection_coherence_tom_v2 -- iter-2 of the DISCRIMINATIVE selection
cell for the crutch-fade Social IQa arc (2026-08-10), per
notes/design_crutch_discriminator_iter2_coherence_tom_2026-08-10.md.

ITER-1 (79c354a6d, exp_crutch_discriminative_selection_multicue_v1.py) landed HARD_FAIL on all 3
arms but SCRAMBLE-CLEAN: real margins A=-0.0037 B=-0.0101 C=-0.0046 MEASURED@
data/exp_crutch_discriminative_selection_multicue_v1/metrics.json (all ~0, matching BoW), scramble
margins -0.10 to -0.15 (deeply collapsed, the decisive control held). The mechanism IS real (a
scrambled graph gives the discriminator nothing to lock onto) but too WEAK to beat BoW. Per-feature
ablation on that cell's Arm C (MEASURED@ same file, "arm_C_ablation.F_conv") found dropping the raw
multi-cue CONVERGENCE-COUNT feature nudges real margin to +0.013 (still short of the +0.02
MIDDLE_BAND floor) while scramble stays deeply collapsed (-0.167) -- convergence-COUNT correlates on
TRAIN (the learned Arm C gave it the largest weight, 0.123) but does not generalize on a dense
small-world graph; the generalizable signal lives in the TOP-DOWN features (path-directness,
relation-gating, backward coherence), not the bottom-up count.

This cell is the ONE mechanism-indicated iteration that follows from that finding (director design
note, see path above): (1) DROP raw convergence-count as a scoring feature entirely (keep it only as
the existing structural "covered" definition -- unchanged no-regression/abstain architecture); (2)
STRENGTHEN the coherence feature into a proper RETRIEVE-VALIDATE check: a per-cue BACKWARD spreading-
activation pass from each covered candidate (mirrors the forward per-cue convergence loop, reusing
the SAME owned `spreading_activation_scores` primitive with seeds/target swapped), VALIDATED by
requiring convergence on >=2 DISTINCT context cues before the coherence signal counts at all (a
single-path "coherent" hit could be a hub artifact; multi-anchor convergence is the actual
validation, mirroring the same coincidence-detection principle iter-1 used forward, now applied as a
gate rather than a raw magnitude); (3) make relation-gating ToM-AWARE with a TIGHTENED map restricted
to ATOMIC's own mental-state relations (xIntent/xWant for why/want-motivation questions,
xReact/oReact for feeling questions, xEffect/oEffect for next-action/consequence questions -- iter-
1's map mixed in ConceptNet relations like hasproperty/mayhaveproperty/motivatedbygoal/
hasprerequisite/causes, diluting the ToM-specific signal); this gating is now applied to BOTH the
forward evidence (gate_delta) AND the backward coherence pass (same hop-1 driving-relation lookup,
reused across both directions since a pair_key's relation type is direction-independent even though
the BFS activation itself is NOT symmetric -- backward seeds from the candidate's own concepts, which
were not pre-filtered for low degree the way cues were, so it is a genuinely new signal, not a
recomputation of the forward pass); (4) KEEP path-directness (F_path, the ablation's most load-
bearing feature for scramble-collapse -- dropping it in iter-1's ablation caused scramble margin to
INVERT to +0.176, non-collapsed).

Two arms, per Director's iter-2 spec (retrieval/evidence-gathering UNCHANGED, still the ONE
variable = how per-cue evidence combines):
  D1: FIXED principled weights, no label-fitting. Algebraically D1_score = F_path + gate_delta +
      F_coh = F_path_gated + F_coh (gate_delta = F_path_gated - F_path by construction, so summing
      all three collapses to "ToM-relation-gated path-directness plus validated backward
      coherence" -- a single interpretable quantity, exposed as 3 addends only so D2's learner and
      the ablation can weigh/drop each independently).
  D2: SAME 3 features, LEARNED linear combination (softmax-GD, 3 seeds {7,13,19}, TRAIN-fit,
      held-out DEV eval) -- does learning help now that the overfit-prone convergence-count feature
      is gone and coherence is stronger? Same WIQA-lesson guard as iter-1: REAL-trained weights
      applied AS-IS to SCRAMBLE features at eval (never retrained on scramble).

Prior-work check (`bash tools/substrate_query.sh "coherence retrieve-validate ToM relation-gating
discriminator SIQa mentalizing crutch"`, cosine ranked, 2026-08-10): top hit cosine=0.3291
(CN_discriminating, a generic concept-graph node matching only on the surface word "discriminating"),
followed by cosine<=0.3096 hits that are either the same generic concept-node family or an unrelated
entity-grid/coherence-metric research note (chain_grade_decision_slate_reading_frontier, permutation-
based discourse coherence for a DIFFERENT reading-order task, not retrieval discrimination). None is
a prior cell on this question; this is noise from char-trigram overlap on "discriminat-", not a
substantive match. VERDICT: genuinely novel iteration on this program's own iter-1 cell (79c354a6d),
not a rediscovery. (iter-1's own pre-reg additionally grepped hdlab/notes/preregs/experiments for a
"Stage-2A retrieve-VALIDATE loop" the director's design notes (both iter-1's and this iter-2's)
pointed to and found ZERO hits both times; this cell again implements the retrieve-validate coherence
check NATIVELY via the owned spreading_activation_scores primitive rather than importing a phantom
organ -- disclosed in the pre-reg.)

Modes:
  --self-test  Tiny synthetic CSKG (~20 nodes) with planted cases: multi-cue-convergence structure
               (reused from iter-1) now checked against the retrieve-VALIDATE coherence gate (2-cue
               candidate passes MIN_COH_CONVERGENCE, 1-cue candidate does not); a ToM relation-gating
               FLIP case restricted to pure ATOMIC relations; D1's algebraic identity
               (F_path+gate_delta+F_coh == F_path_gated+F_coh); D2 GD fit+generalize; abstain;
               arms-differ; tightened RELEVANT_RELATIONS map assertions.
  --smoke      Full real CSKG index (the graph IS the discriminator) + capped dev + capped
               train-fit population -- discriminator-preview per DISCRIMINATOR-MUST-SURVIVE-SCALE.
  --full       All 1954 SIQa dev items x 2 sides (real, scramble); train-fit population capped
               (compute-bounding, disclosed, not a benchmark population).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import numpy as np  # noqa: E402

# ---- reuse, do NOT rebuild (design note + prereg "Owned organs reused") ----
from experiments.exp_crutch_fade_social_iqa_v1 import (  # noqa: E402
    canon, content_words, pair_key, _edge_weight, _hub_penalty,
    load_cskg_index, cskg_node_set_from_index, compute_node_degree, relation_family,
    extract_concepts, load_siqa, bow_scores, bow_margin, argmax_tiebreak, label_idx,
    crutch_candidate_scores, _scramble_partner, scramble_crutch_candidate_scores,
    HUB_DEGREE_THRESH, CSKG_DIR, SIQA_DIR,
)
from experiments.exp_crutch_retrieval_coverage_diag_v1 import (  # noqa: E402
    build_adjacency, spreading_activation_scores, MAX_VISITED_SAFETY_CAP,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "crutch_discriminative_selection_coherence_tom_v2"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- author-designed constants (HYPOTHESIZED@author-design unless cited) ----
CUES_PER_ITEM = 5                  # CITED@exp_crutch_discriminative_selection_multicue_v1 (unchanged)
HOPS_DISCRIMINATOR = 2             # CITED@exp_crutch_discriminative_selection_multicue_v1 (unchanged;
                                    # k3 lets even scrambled cues small-world-bridge to gold)
DECAY = 0.4                        # CITED@exp_crutch_retrieval_coverage_diag_v1 (reused verbatim)
SCORE_MODE = "hub_penalized"       # CITED@exp_crutch_fade_social_iqa_v1 (matches shipped FULL config)
MIN_COH_CONVERGENCE = 2            # HYPOTHESIZED@author-design: the retrieve-VALIDATE gate -- a
                                    # candidate's backward spread must converge on >=2 DISTINCT
                                    # context cues before the coherence signal counts (mirrors the
                                    # existing n_covered>=2 firing-gate's "coincidence, not fluke"
                                    # convention already used elsewhere in this cell family)
SMOKE_DEV_CAP = 250                # CITED@exp_crutch_discriminative_selection_multicue_v1
SMOKE_TRAIN_FIT_CAP = 300          # CITED@exp_crutch_discriminative_selection_multicue_v1
TRAIN_FIT_CAP = 4000
SEEDS_D2 = [7, 13, 19]
L2_REG = 0.02
LR = 0.5
N_EPOCHS = 400
FEATURE_NAMES = ["F_path", "gate_delta", "F_coh"]  # F_conv (raw convergence-count) DROPPED per
                                                    # iter-1's ablation finding (net drag, overfit)

# ---- pre-registered bands (identical numeric bands to iter-1; see prereg "HARD-PASS / MIDDLE_BAND /
# HARD-FAIL bands") ----
HP_REAL_MARGIN = 0.05
MB_REAL_MARGIN = 0.02
SCRAMBLE_COLLAPSE_MAX = 0.03
NONDISCRIM_GAP = 0.02
NOREGRESSION_SLACK = 0.005
MIN_FIRE_FRACTION = 0.05

# ---- question-type classifier (question text ONLY -- no oracle leak; keyword match, not fit) ----
# TIGHTENED 2026-08-10 (iter-2, design note item 3): RELEVANT_RELATIONS restricted to ATOMIC's OWN
# mental-state relation vocabulary (xIntent/xWant/xReact/oReact/xEffect/oEffect/xAttr/xNeed) per the
# 3 explicit ToM pairs the design note specifies (why/want->xIntent/xWant; feel->xReact/oReact;
# next->xEffect/oEffect), PLUS two disclosed author-design extensions applying the same ATOMIC-only
# discipline to DESCRIPTION->xAttr and PREREQUISITE->xNeed (iter-1 left these as ConceptNet-mixed
# buckets: hasproperty/mayhaveproperty/capableof/hasprerequisite -- inconsistent with "ATOMIC mental-
# state relations" applied everywhere else). MEASURED@shard sample (exp_crutch_fade_social_iqa_v1.py
# comment, 300k-edge sample) confirms all 8 relation names below are present in the loaded CSKG.
RELEVANT_RELATIONS: Dict[str, frozenset] = {
    "FEELING": frozenset({"xreact", "oreact"}),
    "DESCRIPTION": frozenset({"xattr"}),
    "MOTIVATION": frozenset({"xintent", "xwant"}),
    "PREREQUISITE": frozenset({"xneed"}),
    "NEXT_ACTION": frozenset({"xeffect", "oeffect"}),
    "EFFECT": frozenset({"xeffect", "oeffect"}),
    "OTHER": frozenset(),
}


def classify_question_type(question: str) -> str:
    """Pure keyword match on the QUESTION TEXT ONLY (never context/answers/gold) -- no-oracle.
    CITED@exp_crutch_discriminative_selection_multicue_v1 (unchanged classifier; only the relation
    map above was tightened)."""
    q = question.lower()
    if any(k in q for k in ("describe", "seen as", "consider", "known as")):
        return "DESCRIPTION"
    if "feel" in q:
        return "FEELING"
    if any(k in q for k in ("why", "wanted to", "want to", "motive")):
        return "MOTIVATION"
    if any(k in q for k in ("need to do before", "before this", "prior to", "need before")):
        return "PREREQUISITE"
    if any(k in q for k in ("next", "going to do", "will do", "do next")):
        return "NEXT_ACTION"
    if any(k in q for k in ("happen", "result of", "effect")):
        return "EFFECT"
    return "OTHER"


# =====================================================================================
# start-marker / crash diagnostics / atomic metrics (per exp_dev canonical checklist)
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _hb(output_dir, stage, t0, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - t0, 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} t={row['elapsed_s']}s {extra or ''}", flush=True)


# =====================================================================================
# cue selection: dedupe already done by extract_concepts; sort ascending by node-degree (most
# specific/least-hub first) so a CUES_PER_ITEM cap keeps the most informative cues.
def select_cues(ctx_concepts: List[str], node_degree: Dict[str, int], cap: int) -> List[str]:
    ranked = sorted(ctx_concepts, key=lambda c: node_degree.get(c, 0))
    return ranked[:cap]


# =====================================================================================
# per-item feature computation (real OR scramble side). NO-ORACLE: never reads gold_idx.
def compute_item_features(item: dict, node_set: frozenset, idx: Dict[str, List[Tuple[str, float]]],
                          adjacency: Dict[str, List[str]], node_degree: Dict[str, int],
                          node_list: List[str], item_id: str, scramble: bool) -> dict:
    b_scores = bow_scores(item)
    qtype = classify_question_type(item["question"])
    relevant = RELEVANT_RELATIONS.get(qtype, frozenset())

    ctx_concepts_true = extract_concepts(item["context"] + " " + item["question"], node_set)
    ans_concepts_list = [extract_concepts(item[k], node_set) for k in ("answerA", "answerB", "answerC")]

    if scramble:
        ctx_concepts_used = [_scramble_partner(f"{item_id}|{c}|ctx", node_list, c) for c in ctx_concepts_true]
    else:
        ctx_concepts_used = ctx_concepts_true

    cues = select_cues(ctx_concepts_used, node_degree, CUES_PER_ITEM)
    n_cand = len(ans_concepts_list)

    # ---- structural covered-definition ONLY (F_conv is NOT a scoring feature in iter-2) ----
    F_conv = [0] * n_cand
    # ---- top-down feature 1: path-directness/specificity (KEPT, per design note item 4) ----
    F_path = [0.0] * n_cand
    F_path_gated = [0.0] * n_cand
    # per-(cue,candidate) hop-1 ToM-irrelevance flag, reused for BOTH forward gating and backward
    # coherence gating below (a pair_key's relation type is direction-independent even though the
    # BFS activation itself is not -- see module docstring)
    hop1_irrel_by_cue: List[List[bool]] = []

    for cue in cues:
        _hop1_scores, hop1_driving = crutch_candidate_scores([cue], ans_concepts_list, idx,
                                                              SCORE_MODE, node_degree)
        mh_scores, _activation, _diag = spreading_activation_scores(
            [cue], ans_concepts_list, adjacency, idx, node_degree, hub_thresh=HUB_DEGREE_THRESH,
            max_hops=HOPS_DISCRIMINATOR, decay=DECAY, max_visited=MAX_VISITED_SAFETY_CAP)
        irrel_this_cue = []
        for j in range(n_cand):
            pk = hop1_driving[j]
            is_irrelevant = False
            if pk is not None and relevant:
                rf = relation_family(idx, pk)
                if rf not in relevant:
                    is_irrelevant = True
            irrel_this_cue.append(is_irrelevant)
            s = mh_scores[j]
            if s <= 0.0:
                continue
            F_conv[j] += 1
            F_path[j] += s
            if not is_irrelevant:
                F_path_gated[j] += s
        hop1_irrel_by_cue.append(irrel_this_cue)

    # top-down feature 2: ToM-relation-gating delta (redefined iter-2: path-SUM scale, not count
    # scale, so units match F_path/F_coh -- iter-1's count-scale gate_delta mildly HELPED in
    # ablation; scale-matching removes the F_conv-class scale-mismatch failure mode)
    gate_delta = [F_path_gated[j] - F_path[j] for j in range(n_cand)]  # always <= 0

    covered = [F_conv[j] > 0 for j in range(n_cand)]

    # ---- top-down feature 3 (STRENGTHENED): retrieve-VALIDATE backward coherence ----
    # RETRIEVE: per covered candidate, backward spreading-activation from the candidate's OWN
    # concepts, targeted at EACH selected cue individually (mirrors the forward per-cue loop with
    # seeds/target swapped -- NOT a recomputation of the forward pass: the candidate's concepts were
    # not pre-filtered for low degree the way cues were, so the hub-cap on the SEED itself makes this
    # a genuinely new signal). VALIDATE: only counts if the candidate's backward evidence converges
    # on >=2 DISTINCT context cues (MIN_COH_CONVERGENCE) -- a single-path "coherent" hit could be a
    # hub-adjacency artifact; multi-anchor convergence is the actual validation. ToM-gated using the
    # SAME hop1_irrel_by_cue flags computed above (ONE gating principle applied to both directions).
    F_coh_conv = [0] * n_cand
    F_coh_path = [0.0] * n_cand
    for j in range(n_cand):
        if not covered[j] or not ans_concepts_list[j]:
            continue  # compute-bounding: backward pass only for forward-covered candidates
        for ci, cue in enumerate(cues):
            if hop1_irrel_by_cue[ci][j]:
                continue  # ToM-irrelevant hop-1 relation: excluded from coherence too
            bwd_scores, _a2, _d2 = spreading_activation_scores(
                ans_concepts_list[j], [[cue]], adjacency, idx, node_degree,
                hub_thresh=HUB_DEGREE_THRESH, max_hops=HOPS_DISCRIMINATOR, decay=DECAY,
                max_visited=MAX_VISITED_SAFETY_CAP)
            bscore = bwd_scores[0]
            if bscore <= 0.0:
                continue
            F_coh_conv[j] += 1
            F_coh_path[j] += bscore
    F_coh = [F_coh_path[j] if F_coh_conv[j] >= MIN_COH_CONVERGENCE else 0.0 for j in range(n_cand)]

    return {
        "b_scores": b_scores, "qtype": qtype, "covered": covered, "n_covered": sum(covered),
        "F_conv": F_conv, "F_path": F_path, "F_path_gated": F_path_gated, "gate_delta": gate_delta,
        "F_coh_conv": F_coh_conv, "F_coh_path": F_coh_path, "F_coh": F_coh,
        "n_cues_used": len(cues),
    }


def feature_matrix(features: dict) -> np.ndarray:
    n = len(features["F_path"])
    M = np.zeros((n, 3), dtype=np.float64)
    for j in range(n):
        M[j, 0] = features["F_path"][j]
        M[j, 1] = features["gate_delta"][j]
        M[j, 2] = features["F_coh"][j]
    return M


def fit_norm_stats(feat_mats: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    stacked = np.concatenate(feat_mats, axis=0)
    mean = stacked.mean(axis=0)
    std = stacked.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    return mean, std


def normalize(M: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (M - mean) / std


def strict_argmax(scores: List[Tuple]) -> Optional[int]:
    """Index of the strict (non-tied) top scorer, or None if top1==top2 (ties abstain)."""
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    if len(order) < 2:
        return order[0] if order else None
    top1, top2 = order[0], order[1]
    if scores[top1] > scores[top2]:
        return top1
    return None


def resolve_item_arm(features: dict, arm: str, gate_thresh: float, w: Optional[np.ndarray] = None,
                     mean: Optional[np.ndarray] = None, std: Optional[np.ndarray] = None,
                     ablate_feature: Optional[int] = None) -> dict:
    """AUGMENT-NOT-REPLACE: fires only if (a) BoW is gap-flagged, (b) n_covered>=2, (c) this arm's
    own score has a strict winner. Otherwise abstains (caller falls back to bow_pred).
    CITED@exp_crutch_discriminative_selection_multicue_v1 (unchanged abstain-gate architecture)."""
    margin = bow_margin(features["b_scores"])
    gap = (margin == 0.0) or (margin < gate_thresh)
    if not gap:
        return {"fired": False, "pred_idx": None, "reason": "not_gap_flagged"}
    if features["n_covered"] < 2:
        return {"fired": False, "pred_idx": None, "reason": "insufficient_coverage"}
    n = len(features["F_path"])
    if arm == "D1":
        # D1_score = F_path + gate_delta + F_coh, algebraically F_path_gated + F_coh (fixed,
        # unweighted, no label-fit -- see module docstring)
        terms_all = [[features["F_path"][j], features["gate_delta"][j], features["F_coh"][j]]
                    for j in range(n)]
        if ablate_feature is not None:
            for j in range(n):
                terms_all[j][ablate_feature] = 0.0
        scores = [(sum(t),) for t in terms_all]
    elif arm == "D2":
        if w is None or mean is None or std is None:
            raise ValueError("arm D2 requires w, mean, std")
        M = feature_matrix(features)
        Mn = normalize(M, mean, std)
        if ablate_feature is not None:
            Mn = Mn.copy()
            Mn[:, ablate_feature] = 0.0
        lin = Mn @ w[:-1] + w[-1]
        scores = [(float(lin[j]),) for j in range(n)]
    else:
        raise ValueError(f"unknown arm {arm!r}")
    winner = strict_argmax(scores)
    if winner is None:
        return {"fired": False, "pred_idx": None, "reason": "tied"}
    return {"fired": True, "pred_idx": winner, "reason": "fired"}


# =====================================================================================
# D2: pointwise softmax-GD fit over the 3 graph-structural top-down features (shared weight vector
# across candidates). CITED@exp_crutch_discriminative_selection_multicue_v1's fit_arm_c (unchanged
# mechanics, F=3 instead of F=4).
def fit_arm_d2(train_feats: List[np.ndarray], train_gold: List[int], seed: int, mean: np.ndarray,
               std: np.ndarray, ablate_feature: Optional[int] = None, lr: float = LR,
               n_epochs: int = N_EPOCHS, l2: float = L2_REG) -> np.ndarray:
    rng = np.random.default_rng(seed)  # PROT-023/F.5: fixed int seed, no hash()
    F = 3
    w = (rng.standard_normal(F + 1).astype(np.float64)) * 0.01
    X = np.stack([normalize(m, mean, std) for m in train_feats], axis=0)  # [N,3,F]
    if ablate_feature is not None:
        X = X.copy()
        X[:, :, ablate_feature] = 0.0
    y = np.array(train_gold, dtype=np.int64)
    N = X.shape[0]
    if N == 0:
        return w
    for _epoch in range(n_epochs):
        lin = X @ w[:-1] + w[-1]                       # [N,3]
        lin_shift = lin - lin.max(axis=1, keepdims=True)
        exp = np.exp(lin_shift)
        probs = exp / exp.sum(axis=1, keepdims=True)   # [N,3]
        grad_scores = probs.copy()
        grad_scores[np.arange(N), y] -= 1.0
        grad_scores /= N
        grad_w = np.einsum("nc,ncf->f", grad_scores, X) + l2 * w[:-1]
        grad_b = grad_scores.sum(axis=(0, 1))
        w[:-1] -= lr * grad_w
        w[-1] -= lr * grad_b
    return w


def arm_d2_train_accuracy(train_feats: List[np.ndarray], train_gold: List[int], w: np.ndarray,
                          mean: np.ndarray, std: np.ndarray, ablate_feature: Optional[int] = None) -> float:
    if not train_feats:
        return 0.0
    n_correct = 0
    for M, gold in zip(train_feats, train_gold):
        Mn = normalize(M, mean, std)
        if ablate_feature is not None:
            Mn = Mn.copy()
            Mn[:, ablate_feature] = 0.0
        lin = Mn @ w[:-1] + w[-1]
        pred = int(np.argmax(lin))
        if pred == gold:
            n_correct += 1
    return n_correct / len(train_feats)


# =====================================================================================
def eval_arm(dev_recs: Dict[int, dict], arm: str, gate_thresh: float, w=None, mean=None, std=None,
            ablate_feature: Optional[int] = None) -> dict:
    n_fired = n_correct_fired = n_bow_correct_on_fired = n_overall_correct = 0
    n = len(dev_recs)
    for i in range(n):
        rec = dev_recs[i]
        feats, gold, bow_pred = rec["features"], rec["gold"], rec["bow_pred"]
        res = resolve_item_arm(feats, arm, gate_thresh, w, mean, std, ablate_feature)
        if res["fired"]:
            n_fired += 1
            if res["pred_idx"] == gold:
                n_correct_fired += 1
            if bow_pred == gold:
                n_bow_correct_on_fired += 1
            final_pred = res["pred_idx"]
        else:
            final_pred = bow_pred
        if final_pred == gold:
            n_overall_correct += 1
    covered_acc = (n_correct_fired / n_fired) if n_fired else None
    bow_on_covered = (n_bow_correct_on_fired / n_fired) if n_fired else None
    margin = (covered_acc - bow_on_covered) if n_fired else None
    return {
        "n_fired": n_fired, "fire_fraction": (n_fired / n) if n else None,
        "covered_subset_accuracy": covered_acc, "bow_accuracy_on_covered_subset": bow_on_covered,
        "margin": margin, "overall_accuracy_with_abstain": (n_overall_correct / n) if n else None,
    }


def classify_verdict(real_eval: dict, scr_eval: dict, bow_only_overall: float, n_dev: int) -> Tuple[str, str]:
    """CITED@exp_crutch_discriminative_selection_multicue_v1 (identical bands, reused verbatim)."""
    if real_eval["margin"] is None or real_eval["n_fired"] < MIN_FIRE_FRACTION * n_dev:
        return "HARD_FAIL", f"vacuous fire n_fired={real_eval['n_fired']} (< {MIN_FIRE_FRACTION}*n_dev)"
    margin_real = real_eval["margin"]
    margin_scr = scr_eval["margin"] if scr_eval["margin"] is not None else 0.0
    overall = real_eval["overall_accuracy_with_abstain"]
    if overall < bow_only_overall - NOREGRESSION_SLACK:
        return "HARD_FAIL", f"regression: overall={overall:.4f} < bow_only={bow_only_overall:.4f}-{NOREGRESSION_SLACK}"
    if margin_real < 0:
        return "HARD_FAIL", f"negative real margin {margin_real:.4f}"
    if margin_scr > (margin_real - NONDISCRIM_GAP):
        return "HARD_FAIL", (f"scramble margin {margin_scr:.4f} not below real margin "
                             f"{margin_real:.4f}-{NONDISCRIM_GAP} (non-discriminative)")
    collapse_ok = margin_scr <= SCRAMBLE_COLLAPSE_MAX
    if margin_real >= HP_REAL_MARGIN and collapse_ok:
        return "HARD_PASS", f"real_margin={margin_real:.4f}>=0.05, scramble_margin={margin_scr:.4f}<=0.03"
    if margin_real >= MB_REAL_MARGIN and collapse_ok:
        return "MIDDLE_BAND", f"real_margin={margin_real:.4f} in [0.02,0.05), scramble collapsed {margin_scr:.4f}"
    return "HARD_FAIL", f"real_margin={margin_real:.4f} below MB floor or scramble not collapsed ({margin_scr:.4f})"


# =====================================================================================
def run(output_dir: str, run_mode: str, dev_cap: Optional[int], train_fit_cap: int) -> dict:
    t0 = time.perf_counter()
    os.makedirs(output_dir, exist_ok=True)
    print(f"[run] ANCHOR={ANCHOR_NAME} mode={run_mode} dev_cap={dev_cap} train_fit_cap={train_fit_cap}",
          flush=True)

    idx = load_cskg_index(CSKG_DIR)
    node_set = cskg_node_set_from_index(idx)
    node_degree = compute_node_degree(idx)
    adjacency = build_adjacency(idx)
    node_list = sorted(node_set)  # PROT-023: sorted(set()), never list(set())
    _hb(output_dir, "cskg_loaded", t0, {"n_edges_pairs": len(idx), "n_nodes": len(node_set)})

    train_all, dev_all = load_siqa()
    dev = dev_all[:dev_cap] if dev_cap else dev_all
    n_dev = len(dev)
    _write_start_marker(output_dir, run_mode, n_dev * 2)

    # GATE_THRESH = median of STRICTLY-POSITIVE bow-margins only. CITED@
    # exp_crutch_discriminative_selection_multicue_v1 (the base cell's fix, reused verbatim -- a
    # plain median-of-ALL-margins degenerates to 0.0 since SIQa answers tie >=50% of the time).
    dev_margins_all = [bow_margin(bow_scores(it)) for it in dev]
    dev_margins_pos = sorted(m for m in dev_margins_all if m > 0.0)
    gate_thresh = dev_margins_pos[len(dev_margins_pos) // 2] if dev_margins_pos else 0.5
    n_tied = sum(1 for m in dev_margins_all if m == 0.0)
    _hb(output_dir, "gate_thresh_computed", t0,
        {"gate_thresh": gate_thresh, "n_tied": n_tied, "n_dev_margins": len(dev_margins_all)})

    # ---- Gate D positive control: reproduce the base cell's own 1-hop coverage_rate ----
    n_gap = n_1hop_cov = 0
    for it in dev:
        b = bow_scores(it)
        m = bow_margin(b)
        if not ((m == 0.0) or (m < gate_thresh)):
            continue
        n_gap += 1
        gold = label_idx(it)
        ctx_c = extract_concepts(it["context"] + " " + it["question"], node_set)
        ans_c = [extract_concepts(it[k], node_set) for k in ("answerA", "answerB", "answerC")]
        c_scores, _drv = crutch_candidate_scores(ctx_c, ans_c, idx, SCORE_MODE, node_degree)
        if c_scores[gold] > 0.0:
            n_1hop_cov += 1
    positive_control_1hop_coverage = (n_1hop_cov / n_gap) if n_gap else None
    _hb(output_dir, "positive_control_done", t0,
        {"coverage": positive_control_1hop_coverage, "n_gap": n_gap})

    # ---- DEV: real + scramble per-item features, checkpointed per (side, item_idx) ----
    done = completed_units(output_dir)
    loaded = load_units(output_dir)
    dev_recs: Dict[str, Dict[int, dict]] = {"real": {}, "scramble": {}}
    for i, it in enumerate(dev):
        gold = label_idx(it)
        for side in ("real", "scramble"):
            key = unit_key("dev", side, i)
            if key in done:
                rec = loaded[key]
            else:
                feats = compute_item_features(it, node_set, idx, adjacency, node_degree, node_list,
                                              item_id=f"dev{i}", scramble=(side == "scramble"))
                rec = {"features": feats, "gold": gold, "bow_pred": argmax_tiebreak(feats["b_scores"])}
                record_unit(output_dir, key, rec)
            dev_recs[side][i] = rec
        if i % 100 == 0 or i == n_dev - 1:
            _hb(output_dir, "dev_features", t0, {"i": i, "n_dev": n_dev})
    _hb(output_dir, "dev_features_done", t0, {"n_dev": n_dev})

    bow_only_correct = sum(1 for i in range(n_dev) if dev_recs["real"][i]["bow_pred"] == dev_recs["real"][i]["gold"])
    bow_only_overall_accuracy = (bow_only_correct / n_dev) if n_dev else None

    # ---- TRAIN fit population (real side only): gap-flagged + covered, capped, deterministic order ----
    train_feats: List[np.ndarray] = []
    train_gold: List[int] = []
    j_scanned = 0
    for j, it in enumerate(train_all):
        if len(train_feats) >= train_fit_cap:
            break
        j_scanned += 1
        b = bow_scores(it)
        m = bow_margin(b)
        if not ((m == 0.0) or (m < gate_thresh)):
            continue
        key = unit_key("trainfeat", j)
        if key in done:
            feats = loaded[key]["features"]
        else:
            feats = compute_item_features(it, node_set, idx, adjacency, node_degree, node_list,
                                          item_id=f"train{j}", scramble=False)
            record_unit(output_dir, key, {"features": feats})
        if feats["n_covered"] < 2:
            continue
        train_feats.append(feature_matrix(feats))
        train_gold.append(label_idx(it))
        if len(train_feats) % 200 == 0:
            _hb(output_dir, "train_fit_scan", t0, {"n_collected": len(train_feats), "j_scanned": j_scanned})
    _hb(output_dir, "train_fit_scan_done", t0,
        {"n_collected": len(train_feats), "j_scanned": j_scanned, "train_fit_cap": train_fit_cap})

    if train_feats:
        mean, std = fit_norm_stats(train_feats)
    else:
        mean, std = np.zeros(3), np.ones(3)

    arm_d2_weights = {seed: fit_arm_d2(train_feats, train_gold, seed, mean, std) for seed in SEEDS_D2}
    arm_d2_train_acc = {seed: arm_d2_train_accuracy(train_feats, train_gold, w, mean, std)
                        for seed, w in arm_d2_weights.items()}
    _hb(output_dir, "arm_d2_fit_done", t0, {"train_acc": arm_d2_train_acc})

    # ---- per-feature ablation for BOTH D1 (fixed, near-zero extra compute) and D2 (refit) ----
    d1_ablation_eval = {}
    d2_ablation_weights = {}
    d2_ablation_train_acc = {}
    d2_ablation_eval = {}
    seed0 = SEEDS_D2[0]
    for fi, fname in enumerate(FEATURE_NAMES):
        w_abl = fit_arm_d2(train_feats, train_gold, seed0, mean, std, ablate_feature=fi)
        d2_ablation_weights[fname] = w_abl
        d2_ablation_train_acc[fname] = arm_d2_train_accuracy(train_feats, train_gold, w_abl, mean, std,
                                                              ablate_feature=fi)

    # ---- Evaluate D1 / D2(each seed) on DEV real + scramble ----
    results = {"D1": {}}
    for side in ("real", "scramble"):
        results["D1"][side] = eval_arm(dev_recs[side], "D1", gate_thresh)
    results["D2"] = {}
    for seed, w in arm_d2_weights.items():
        results["D2"][seed] = {side: eval_arm(dev_recs[side], "D2", gate_thresh, w, mean, std)
                               for side in ("real", "scramble")}
    d2_headline = results["D2"][SEEDS_D2[0]]

    for fi, fname in enumerate(FEATURE_NAMES):
        d1_ablation_eval[fname] = {side: eval_arm(dev_recs[side], "D1", gate_thresh, ablate_feature=fi)
                                   for side in ("real", "scramble")}
        w_abl = d2_ablation_weights[fname]
        d2_ablation_eval[fname] = {side: eval_arm(dev_recs[side], "D2", gate_thresh, w_abl, mean, std,
                                                   ablate_feature=fi) for side in ("real", "scramble")}

    tier_D1, msg_D1 = classify_verdict(results["D1"]["real"], results["D1"]["scramble"], bow_only_overall_accuracy, n_dev)
    tier_D2, msg_D2 = classify_verdict(d2_headline["real"], d2_headline["scramble"], bow_only_overall_accuracy, n_dev)

    tiers = {"D1": tier_D1, "D2": tier_D2}
    order = {"HARD_PASS": 2, "MIDDLE_BAND": 1, "HARD_FAIL": 0}
    best_arm = max(tiers, key=lambda a: order[tiers[a]])
    top_verdict = tiers[best_arm]
    verdict_msg = (f"D1={tier_D1}({msg_D1}) | D2={tier_D2}({msg_D2}) | "
                  f"best_arm={best_arm} | bow_only_overall={bow_only_overall_accuracy}")

    # ---- arms-differ (META_RULE_AF) ----
    pred_vec = {}
    for arm_key, w_ in (("D1", None), ("D2", arm_d2_weights[SEEDS_D2[0]])):
        preds = []
        for i in range(n_dev):
            feats = dev_recs["real"][i]["features"]
            res = resolve_item_arm(feats, arm_key, gate_thresh, w_, mean, std)
            preds.append(res["pred_idx"] if res["fired"] else -1)
        pred_vec[arm_key] = preds
    digests = {a: hashlib.sha256(json.dumps(p).encode()).hexdigest() for a, p in pred_vec.items()}
    arms_differ = digests["D1"] != digests["D2"]

    elapsed_s = time.perf_counter() - t0
    metrics = {
        "verdict": top_verdict, "verdict_msg": verdict_msg,
        "summary": f"{ANCHOR_NAME} {run_mode}: best_arm={best_arm} tier={top_verdict}",
        "elapsed_s": elapsed_s, "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "config": {"CUES_PER_ITEM": CUES_PER_ITEM, "HOPS_DISCRIMINATOR": HOPS_DISCRIMINATOR,
                  "DECAY": DECAY, "SCORE_MODE": SCORE_MODE, "MIN_COH_CONVERGENCE": MIN_COH_CONVERGENCE,
                  "gate_thresh": gate_thresh, "n_dev": n_dev, "train_fit_cap": train_fit_cap,
                  "n_train_fit_collected": len(train_feats), "j_scanned_for_train_fit": j_scanned},
        "bow_only_overall_accuracy": bow_only_overall_accuracy,
        "positive_control_1hop_coverage": positive_control_1hop_coverage,
        "positive_control_reference": 0.2465, "positive_control_tolerance": 0.02,
        "positive_control_ok": (positive_control_1hop_coverage is not None and
                                abs(positive_control_1hop_coverage - 0.2465) <= 0.02),
        "arm_D1": {"real": results["D1"]["real"], "scramble": results["D1"]["scramble"],
                  "tier": tier_D1, "tier_msg": msg_D1, "ablation": d1_ablation_eval},
        "arm_D2": {"headline_seed": SEEDS_D2[0], "real": d2_headline["real"],
                  "scramble": d2_headline["scramble"], "tier": tier_D2, "tier_msg": msg_D2,
                  "per_seed": {str(s): results["D2"][s] for s in SEEDS_D2},
                  "per_seed_train_acc": {str(s): arm_d2_train_acc[s] for s in SEEDS_D2},
                  "weight_vectors": {str(s): arm_d2_weights[s].tolist() for s in SEEDS_D2},
                  "ablation": {fname: {"eval": d2_ablation_eval[fname],
                                       "train_acc": d2_ablation_train_acc[fname],
                                       "weight_vector": d2_ablation_weights[fname].tolist()}
                              for fname in FEATURE_NAMES}},
        "feature_names": FEATURE_NAMES,
        "best_arm": best_arm, "routing_recommendation": (
            "SHIP_DISCRIMINATOR" if top_verdict == "HARD_PASS" else
            "PARTIAL_PROGRESS_ITERATE" if top_verdict == "MIDDLE_BAND" else
            "DISCRIMINATOR_STILL_NON_DECISIVE"),
        "arms_differ_verified": arms_differ, "arm_digests": digests,
        "arms_differ_exempted": [],
        "cardinality_ok": (len(completed_units(output_dir)) >= n_dev * 2),
        "expected_n_dev_units": n_dev * 2,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "discrete 3-way classification accuracy on a real benchmark; no capacity/noise-floor discriminator applies",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "calibration_check": "adaptive_with_discriminator_gate",
        "storage_strategy": "no_storage",
        "iter": 2, "iter1_reference": "79c354a6d / data/exp_crutch_discriminative_selection_multicue_v1/metrics.json",
    }
    _atomic_write_metrics(output_dir, metrics)
    _hb(output_dir, "done", t0, {"verdict": top_verdict})
    return metrics


# =====================================================================================
def self_test() -> dict:
    t0 = time.perf_counter()
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="crutch_disc_v2_selftest_")

    # ---- planted synthetic CSKG: case 1 (convergence -> retrieve-VALIDATE coherence gate) + case 2
    # (ToM relation-gating flip, ATOMIC-only) ----
    idx: Dict[str, List[Tuple[str, float]]] = {}

    def add_edge(a, b, rel, trust=1.0):
        idx.setdefault(pair_key(a, b), []).append((rel, trust))

    # case 1: candidate candalpha reached by TWO cues (cueone,cuetwo) via a RELEVANT relation for
    # the (OTHER-typed, ungated) question -- backward spread from candalpha reaches BOTH cues
    # (same edges, undirected) -> F_coh_conv=2 -> PASSES MIN_COH_CONVERGENCE -> F_coh nonzero.
    # candbeta reached by ONE cue (cuethree) -> backward spread reaches only 1 cue -> F_coh_conv=1
    # -> FAILS the gate -> F_coh=0 even though its raw single-path activation is nonzero.
    add_edge("cueone", "candalpha", "genericrel")
    add_edge("cuetwo", "candalpha", "genericrel2")
    add_edge("cuethree", "candbeta", "genericrel3")
    # case 2: candidate candpsi reached by TWO cues via IRRELEVANT-to-FEELING ConceptNet relations
    # (atlocation, usedfor -- NOT in the tightened ATOMIC-only RELEVANT_RELATIONS['FEELING']);
    # candquin reached by ONE cue via a RELEVANT ATOMIC relation (xreact).
    add_edge("gcueone", "candpsi", "atlocation")
    add_edge("gcuetwo", "candpsi", "usedfor")
    add_edge("gcuethree", "candquin", "xreact")

    node_set = cskg_node_set_from_index(idx)
    node_degree = compute_node_degree(idx)
    adjacency = build_adjacency(idx)
    node_list = sorted(node_set)

    # ---- tightened RELEVANT_RELATIONS map assertions (design note item 3) ----
    assert RELEVANT_RELATIONS["MOTIVATION"] == frozenset({"xintent", "xwant"}), RELEVANT_RELATIONS["MOTIVATION"]
    assert RELEVANT_RELATIONS["FEELING"] == frozenset({"xreact", "oreact"}), RELEVANT_RELATIONS["FEELING"]
    assert RELEVANT_RELATIONS["NEXT_ACTION"] == frozenset({"xeffect", "oeffect"}), RELEVANT_RELATIONS["NEXT_ACTION"]
    assert "hasproperty" not in RELEVANT_RELATIONS["FEELING"], "ConceptNet relation leaked into ATOMIC-only map"
    assert "motivatedbygoal" not in RELEVANT_RELATIONS["MOTIVATION"], "ConceptNet relation leaked into ATOMIC-only map"
    assert "capableof" not in RELEVANT_RELATIONS["NEXT_ACTION"], "ConceptNet relation leaked into ATOMIC-only map"

    item1 = {"context": "cueone cuetwo cuethree filler words with no overlap", "question": "which fact applies here",
            "answerA": "candalpha zzq", "answerB": "candbeta zzq", "answerC": "candchi zzq", "label": "1"}
    item2 = {"context": "gcueone gcuetwo gcuethree filler words with no overlap",
            "question": "how would somebody feel afterwards",
            "answerA": "candpsi zzq", "answerB": "candquin zzq", "answerC": "candrho zzq", "label": "2"}

    feats1 = compute_item_features(item1, node_set, idx, adjacency, node_degree, node_list,
                                   item_id="t1", scramble=False)
    assert feats1["F_conv"] == [2, 1, 0], f"case1 F_conv (structural covered-def) unexpected: {feats1['F_conv']}"
    assert feats1["n_covered"] == 2, f"case1 n_covered unexpected: {feats1['n_covered']}"
    # retrieve-VALIDATE gate: candalpha's backward spread converges on 2 cues -> passes; candbeta's
    # on 1 cue -> fails (F_coh forced to 0.0 even though raw F_coh_path may be nonzero)
    assert feats1["F_coh_conv"][0] == 2, f"case1 candalpha F_coh_conv expected 2: {feats1['F_coh_conv']}"
    assert feats1["F_coh_conv"][1] == 1, f"case1 candbeta F_coh_conv expected 1: {feats1['F_coh_conv']}"
    assert feats1["F_coh"][0] > 0.0, f"case1 candalpha F_coh should PASS the validate gate: {feats1['F_coh']}"
    assert feats1["F_coh"][1] == 0.0, f"case1 candbeta F_coh should FAIL the validate gate (n_conv<2): {feats1['F_coh']}"
    # D1 algebraic identity: F_path + gate_delta == F_path_gated (exactly, no relevant-set active on
    # OTHER-typed question -> gate_delta should be 0 here since nothing is gated)
    for j in range(3):
        lhs = feats1["F_path"][j] + feats1["gate_delta"][j]
        rhs = feats1["F_path_gated"][j]
        assert abs(lhs - rhs) < 1e-9, f"case1 D1 algebraic identity violated at j={j}: {lhs} vs {rhs}"
    res1_d1 = resolve_item_arm(feats1, "D1", gate_thresh=0.9)  # margin==0.0 -> gap regardless of thresh
    assert res1_d1["fired"] and res1_d1["pred_idx"] == 0, (
        f"case1 D1 should pick candalpha (validated coherence): {res1_d1}")

    feats2 = compute_item_features(item2, node_set, idx, adjacency, node_degree, node_list,
                                   item_id="t2", scramble=False)
    assert feats2["qtype"] == "FEELING", f"case2 qtype misclassified: {feats2['qtype']}"
    assert feats2["F_conv"] == [2, 1, 0], f"case2 F_conv unexpected: {feats2['F_conv']}"
    # ToM-relation gating: candpsi's 2 cues are BOTH ConceptNet-irrelevant to FEELING -> F_path_gated
    # drops to 0; candquin's 1 cue is ATOMIC-relevant (xreact) -> survives gating.
    assert feats2["F_path_gated"][0] == 0.0, f"case2 candpsi F_path_gated should be gated to 0: {feats2['F_path_gated']}"
    assert feats2["F_path_gated"][1] > 0.0, f"case2 candquin F_path_gated should survive gating: {feats2['F_path_gated']}"
    res2_d1 = resolve_item_arm(feats2, "D1", gate_thresh=0.9)
    assert res2_d1["fired"] and res2_d1["pred_idx"] == 1, (
        f"case2 D1 expected CORRECT pick 1 (ToM-relation-gating flip): {res2_d1}")

    # ---- abstain: only 1 candidate covered ----
    item3 = {"context": "cueone filler words with no overlap", "question": "what happened",
            "answerA": "candalpha zzq", "answerB": "zzzq nope", "answerC": "zzzzq nopealt", "label": "1"}
    feats3 = compute_item_features(item3, node_set, idx, adjacency, node_degree, node_list,
                                   item_id="t3", scramble=False)
    assert feats3["n_covered"] == 1, f"case3 expected n_covered=1: {feats3['n_covered']}"
    res3_d1 = resolve_item_arm(feats3, "D1", gate_thresh=0.9)
    assert not res3_d1["fired"], f"case3 should abstain (n_covered<2): {res3_d1}"

    # ---- D2: tiny synthetic training set, deterministic pattern (label = argmax F_path col) ----
    rng = np.random.default_rng(2026)
    syn_feats, syn_gold = [], []
    for _ in range(60):
        M = rng.integers(0, 4, size=(3, 3)).astype(np.float64)
        gold = int(np.argmax(M[:, 0]))  # driven by col0 (F_path)
        syn_feats.append(M)
        syn_gold.append(gold)
    mean, std = fit_norm_stats(syn_feats)
    w_syn = fit_arm_d2(syn_feats, syn_gold, seed=7, mean=mean, std=std, n_epochs=500)
    train_acc = arm_d2_train_accuracy(syn_feats, syn_gold, w_syn, mean, std)
    assert train_acc >= 0.70, f"arm D2 GD failed to fit separable synthetic pattern: train_acc={train_acc}"
    held_feats, held_gold = [], []
    for _ in range(15):
        M = rng.integers(0, 4, size=(3, 3)).astype(np.float64)
        held_feats.append(M)
        held_gold.append(int(np.argmax(M[:, 0])))
    held_acc = arm_d2_train_accuracy(held_feats, held_gold, w_syn, mean, std)
    assert held_acc >= 0.60, f"arm D2 failed to generalize to held-out synthetic rows: held_acc={held_acc}"

    # ---- exp_checkpoint real round-trip (real_code_path_exercised) ----
    ck_dir = os.path.join(tmpdir, "ckpt")
    k = unit_key("dev", "real", 0)
    assert k not in completed_units(ck_dir)
    record_unit(ck_dir, k, {"x": 1})
    assert k in completed_units(ck_dir)
    assert load_units(ck_dir)[k] == {"x": 1}

    # ---- determinism: re-run case1/case2 feature computation, must be bit-identical ----
    feats1b = compute_item_features(item1, node_set, idx, adjacency, node_degree, node_list,
                                    item_id="t1", scramble=False)
    assert json.dumps(feats1, sort_keys=True) == json.dumps(feats1b, sort_keys=True), \
        "compute_item_features not deterministic across repeated calls"

    # ---- arms-differ: D1 (fixed sum) vs D2 (untrained random-init weights) on the 2 planted items ----
    w0 = fit_arm_d2([feature_matrix(feats1), feature_matrix(feats2)], [0, 1], seed=7,
                    mean=np.array([0.1, -0.1, 0.1]), std=np.array([1.0, 1.0, 1.0]), n_epochs=50)
    preds_d1, preds_d2 = [], []
    for feats in (feats1, feats2, feats3):
        r1 = resolve_item_arm(feats, "D1", gate_thresh=0.9)
        r2 = resolve_item_arm(feats, "D2", gate_thresh=0.9, w=w0,
                              mean=np.array([0.1, -0.1, 0.1]), std=np.array([1.0, 1.0, 1.0]))
        preds_d1.append(r1["pred_idx"] if r1["fired"] else -1)
        preds_d2.append(r2["pred_idx"] if r2["fired"] else -1)
    # not asserting they differ (small planted set may coincide) -- just that both are computable and
    # well-formed; the FULL-scale arms_differ_verified gate is the load-bearing check (per META_RULE_AF)
    assert len(preds_d1) == 3 and len(preds_d2) == 3

    # ---- classify_question_type sanity ----
    assert classify_question_type("How would you describe X?") == "DESCRIPTION"
    assert classify_question_type("How would X feel afterwards?") == "FEELING"
    assert classify_question_type("Why did X do this?") == "MOTIVATION"
    assert classify_question_type("What will X do next?") == "NEXT_ACTION"
    assert classify_question_type("What will happen to X?") == "EFFECT"
    assert classify_question_type("Completely unrelated text") == "OTHER"

    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    elapsed = time.perf_counter() - t0
    print(f"[self_test] PASS in {elapsed:.2f}s: retrieve-validate coherence gate, ToM relation-gating "
         "flip (ATOMIC-only), D1 algebraic identity, abstain, D2 GD fit+generalize, exp_checkpoint "
         "round-trip, determinism, question-type classifier", flush=True)
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "all planted cases + D2 GD checks passed",
           "summary": "SELFTEST_PASS", "elapsed_s": elapsed, "run_mode": "self_test",
           "anchor_name": ANCHOR_NAME, "ts_iso": datetime.now(timezone.utc).isoformat(),
           "pid": os.getpid()}


# =====================================================================================
def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--out-tag", type=str, default=None)
    args = parser.parse_args(argv)

    if args.self_test:
        output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_selftest")
        try:
            metrics = self_test()
            _atomic_write_metrics(output_dir, metrics)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001 (not BaseException; preserves SystemExit/KeyboardInterrupt)
            _write_crash_metrics(output_dir, e)
            raise
        return

    if args.smoke:
        suffix = f"_smoke_{args.out_tag}" if args.out_tag else "_smoke"
        output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")
        try:
            run(output_dir, "smoke", dev_cap=SMOKE_DEV_CAP, train_fit_cap=SMOKE_TRAIN_FIT_CAP)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001
            _write_crash_metrics(output_dir, e)
            raise
        return

    if args.full:
        suffix = f"_{args.out_tag}" if args.out_tag else ""
        output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")
        try:
            run(output_dir, "full", dev_cap=None, train_fit_cap=TRAIN_FIT_CAP)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001
            _write_crash_metrics(output_dir, e)
            raise
        return

    parser.error("one of --self-test / --smoke / --full is required")


if __name__ == "__main__":
    main()
