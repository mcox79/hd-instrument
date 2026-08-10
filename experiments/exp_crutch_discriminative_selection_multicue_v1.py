# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (A/B/C prediction-vector digests pairwise differ)
# - final_metrics_atomicity declared (tmp_replace)
# - except SystemExit: raise BEFORE except KeyboardInterrupt: raise BEFORE except Exception (no
#   BaseException, no bare except:)
# - crlb_n/a declared (discrete 3-way classification accuracy; no capacity/noise-floor discriminator
#   threshold applies)
# - HP_SCOPE: per-arm HARD-PASS/MIDDLE_BAND/HARD-FAIL bands (see prereg); never aggregated
# - cardinality_ok: EXPECTED_N_DEV_UNITS = n_dev * 2 (real + scramble side)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (GATE_THRESH = median bow_margin over dev,
#   computed fresh at run start; RELEVANT_RELATIONS map is HYPOTHESIZED@author-design, never fit)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL compute_item_features / resolve_item_arm / fit_arm_c / exp_checkpoint
#   round-trip at trivial scale (real_code_path_exercised); no synthetic-only shortcut branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_crutch_discriminative_selection_multicue_v1.md for the full pre-reg
# (prior-work check, owned-organ pointers, bands, dispatch plan).
"""exp_crutch_discriminative_selection_multicue_v1 -- DISCRIMINATIVE selection over the crutch
spreading-activation candidate set for the crutch-fade Social IQa arc (2026-08-10).

The coverage diagnosis (508ee9b0d) settled that the CSKG crutch overwhelmingly HAS the needed fact
(94% of 1-hop misses reachable within <=3 hops) but that raw reachability is NON-DISCRIMINATIVE on a
dense small-world graph: a SCRAMBLED context reaches the gold answer too. A coordinator refinement
sharpened this further: reachability was measured ORACLE-TARGETED (path TO the known gold); at k3
even scramble reaches gold 53% of the time, so ALL the useful signal must be in HOW a candidate is
reached, not WHETHER -- and the discriminator must run NO-ORACLE (choose among SIQa's 3 candidates
without the gold label at scoring time; gold is used only to measure accuracy and to fit Arm C's
combination weights on TRAIN, held out from DEV).

Mechanism: retrieval/evidence-gathering is UNCHANGED across all 3 arms (the coverage diag's own
hub-capped `spreading_activation_scores` + `crutch_candidate_scores`, reused unmodified, called
PER-CUE instead of on one bundled context). ONE VARIABLE = how that per-cue evidence is COMBINED:
  A: pure multi-cue CONVERGENCE (how many distinct cues' activation reach the candidate, weighted by
     the activation-decay's own built-in path-directness/specificity).
  B: A + QUESTION-TYPE relation-gating (drop a cue's hop-1 contribution when its relation family is
     not relevant to the question type -- e.g. a "how would X feel" question gates in xReact/xAttr,
     not generic AtLocation).
  C: A LEARNED linear combination of 4 graph-structural features (multi-cue count, activation-sum
     directness, relation-gating delta, and a backward abductive/coherence score -- does the
     candidate best EXPLAIN the context, not just get reached by it) fit by softmax-GD on SIQa TRAIN
     labels, evaluated on held-out DEV. Guard: features are GRAPH-STRUCTURE-only (no lexical
     surface features); the REAL-trained weights are applied AS-IS to SCRAMBLE-graph features at
     eval time -- if Arm C still discriminates there, it memorized a structural artifact, not real
     content (the WIQA over-fit lesson).

Every arm is AUGMENT-NOT-REPLACE: BoW is always-on underneath; an arm only overrides BoW on an item
that is (a) BoW-ambiguous (gap-flagged, same adaptive-margin gate the base 9-arm cell uses), (b) has
>=2 candidates reached by SOME cue (real 3-way competition), and (c) has a STRICT (non-tied) winner
under that arm's own score -- otherwise ABSTAIN -> BoW, which makes no-regression structural.

SCRAMBLE-COLLAPSE is the decisive control on every arm independently: the raw argmax prototype from
the coverage diagnosis failed exactly here (scramble's own newly-covered accuracy exceeded real's).
A scramble-CLEAN win of ANY size on any arm is the meaningful result of this cell.

Modes:
  --self-test  Tiny synthetic CSKG (~20 nodes) with a planted multi-cue-convergence case, a planted
               RELATION-GATING-FLIP case (proves B changes the decision, not just a number), and a
               tiny synthetic Arm-C training set (proves the GD fit converges + generalizes). Real
               calls into compute_item_features / resolve_item_arm / fit_arm_c / exp_checkpoint.
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

ANCHOR_NAME = "crutch_discriminative_selection_multicue_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- author-designed constants (HYPOTHESIZED@author-design unless cited) ----
CUES_PER_ITEM = 5                  # compute-bounding cap; least-hubby cues kept first
HOPS_DISCRIMINATOR = 2             # sharpened per coordinator framing: k3 lets even scrambled cues
                                    # small-world-bridge to gold (coverage diag's own k2-vs-k3 find)
DECAY = 0.4                        # CITED@exp_crutch_retrieval_coverage_diag_v1 (reused verbatim,
                                    # not re-tuned on this data -- avoids p-hacking)
SCORE_MODE = "hub_penalized"       # CITED@exp_crutch_fade_social_iqa_v1 (matches shipped FULL config)
SMOKE_DEV_CAP = 250
SMOKE_TRAIN_FIT_CAP = 300
TRAIN_FIT_CAP = 4000
SEEDS_ARM_C = [7, 13, 19]
L2_REG = 0.02
LR = 0.5
N_EPOCHS = 400
FEATURE_NAMES = ["F_conv", "F_path", "gate_delta", "F_coh"]

# ---- pre-registered bands (see prereg "HARD-PASS / MIDDLE_BAND / HARD-FAIL bands") ----
HP_REAL_MARGIN = 0.05
MB_REAL_MARGIN = 0.02
SCRAMBLE_COLLAPSE_MAX = 0.03
NONDISCRIM_GAP = 0.02
NOREGRESSION_SLACK = 0.005
MIN_FIRE_FRACTION = 0.05

# ---- question-type classifier (question text ONLY -- no oracle leak; keyword match, not fit) ----
RELEVANT_RELATIONS: Dict[str, frozenset] = {
    "FEELING": frozenset({"xreact", "oreact", "xattr", "hasproperty", "mayhaveproperty"}),
    "DESCRIPTION": frozenset({"xattr", "hasproperty", "mayhaveproperty", "capableof"}),
    "MOTIVATION": frozenset({"xintent", "xwant", "motivatedbygoal"}),
    "PREREQUISITE": frozenset({"xneed", "hasprerequisite"}),
    "NEXT_ACTION": frozenset({"xwant", "xeffect", "hassubevent", "capableof"}),
    "EFFECT": frozenset({"xeffect", "oeffect", "causes", "hassubevent"}),
    "OTHER": frozenset(),
}


def classify_question_type(question: str) -> str:
    """Pure keyword match on the QUESTION TEXT ONLY (never context/answers/gold) -- no-oracle."""
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
    F_conv = [0] * n_cand
    F_path = [0.0] * n_cand
    F_conv_gated = [0] * n_cand
    F_path_gated = [0.0] * n_cand
    F_coh = [0.0] * n_cand

    for cue in cues:
        _hop1_scores, hop1_driving = crutch_candidate_scores([cue], ans_concepts_list, idx,
                                                              SCORE_MODE, node_degree)
        mh_scores, _activation, _diag = spreading_activation_scores(
            [cue], ans_concepts_list, adjacency, idx, node_degree, hub_thresh=HUB_DEGREE_THRESH,
            max_hops=HOPS_DISCRIMINATOR, decay=DECAY, max_visited=MAX_VISITED_SAFETY_CAP)
        for j in range(n_cand):
            s = mh_scores[j]
            if s <= 0.0:
                continue
            F_conv[j] += 1
            F_path[j] += s
            pk = hop1_driving[j]
            is_irrelevant = False
            if pk is not None and relevant:
                rf = relation_family(idx, pk)
                if rf not in relevant:
                    is_irrelevant = True
            if not is_irrelevant:
                F_conv_gated[j] += 1
                F_path_gated[j] += s

    for j in range(n_cand):
        if F_conv[j] > 0 and ans_concepts_list[j]:
            coh_scores, _a2, _d2 = spreading_activation_scores(
                ans_concepts_list[j], [ctx_concepts_used], adjacency, idx, node_degree,
                hub_thresh=HUB_DEGREE_THRESH, max_hops=HOPS_DISCRIMINATOR, decay=DECAY,
                max_visited=MAX_VISITED_SAFETY_CAP)
            F_coh[j] = coh_scores[0]

    covered = [F_conv[j] > 0 for j in range(n_cand)]
    gate_delta = [F_conv_gated[j] - F_conv[j] for j in range(n_cand)]

    return {
        "b_scores": b_scores, "qtype": qtype, "covered": covered, "n_covered": sum(covered),
        "F_conv": F_conv, "F_path": F_path, "F_conv_gated": F_conv_gated,
        "F_path_gated": F_path_gated, "gate_delta": gate_delta, "F_coh": F_coh,
        "n_cues_used": len(cues),
    }


def feature_matrix(features: dict) -> np.ndarray:
    n = len(features["F_conv"])
    M = np.zeros((n, 4), dtype=np.float64)
    for j in range(n):
        M[j, 0] = features["F_conv"][j]
        M[j, 1] = features["F_path"][j]
        M[j, 2] = features["gate_delta"][j]
        M[j, 3] = features["F_coh"][j]
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
    own score has a strict winner. Otherwise abstains (caller falls back to bow_pred)."""
    margin = bow_margin(features["b_scores"])
    gap = (margin == 0.0) or (margin < gate_thresh)
    if not gap:
        return {"fired": False, "pred_idx": None, "reason": "not_gap_flagged"}
    if features["n_covered"] < 2:
        return {"fired": False, "pred_idx": None, "reason": "insufficient_coverage"}
    n = len(features["F_conv"])
    if arm == "A":
        scores = [(features["F_conv"][j], features["F_path"][j]) for j in range(n)]
    elif arm == "B":
        scores = [(features["F_conv_gated"][j], features["F_path_gated"][j]) for j in range(n)]
    elif arm == "C":
        if w is None or mean is None or std is None:
            raise ValueError("arm C requires w, mean, std")
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
# Arm C: pointwise softmax-GD fit over the 4 graph-structural features (shared weight vector
# across candidates -- candidate identity A/B/C is not semantically meaningful, only its features).
def fit_arm_c(train_feats: List[np.ndarray], train_gold: List[int], seed: int, mean: np.ndarray,
              std: np.ndarray, ablate_feature: Optional[int] = None, lr: float = LR,
              n_epochs: int = N_EPOCHS, l2: float = L2_REG) -> np.ndarray:
    rng = np.random.default_rng(seed)  # PROT-023/F.5: fixed int seed, no hash()
    F = 4
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


def arm_c_train_accuracy(train_feats: List[np.ndarray], train_gold: List[int], w: np.ndarray,
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

    # GATE_THRESH = median of STRICTLY-POSITIVE bow-margins only (NOT all margins). CITED@
    # exp_crutch_fade_social_iqa_v1.py:900-914 (Stage-0 comment): SIQa answers are short non-
    # extractive phrases, so raw BoW overlap ties (margin==0.0 exactly) for >=50% of dev -- a
    # plain median-of-ALL-margins threshold degenerates to 0.0, which silently disables margin-
    # based gap-flagging (only the explicit all-zero tie case still fires; the "margin < thresh"
    # clause becomes structurally vacuous since margin can never be negative). The base cell
    # diagnosed and fixed this exact bug; reused verbatim here (this cell's positive-control gate
    # independently caught the SAME failure mode before this fix -- coverage measured 0.204 vs the
    # 0.2465 reference before the fix, confirming the gap-flagged population was mis-sized).
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
        mean, std = np.zeros(4), np.ones(4)

    arm_c_weights = {seed: fit_arm_c(train_feats, train_gold, seed, mean, std) for seed in SEEDS_ARM_C}
    arm_c_train_acc = {seed: arm_c_train_accuracy(train_feats, train_gold, w, mean, std)
                       for seed, w in arm_c_weights.items()}
    _hb(output_dir, "arm_c_fit_done", t0, {"train_acc": arm_c_train_acc})

    ablation_weights = {}
    ablation_train_acc = {}
    seed0 = SEEDS_ARM_C[0]
    for fi, fname in enumerate(FEATURE_NAMES):
        w_abl = fit_arm_c(train_feats, train_gold, seed0, mean, std, ablate_feature=fi)
        ablation_weights[fname] = w_abl
        ablation_train_acc[fname] = arm_c_train_accuracy(train_feats, train_gold, w_abl, mean, std,
                                                          ablate_feature=fi)

    # ---- Evaluate A / B / C(each seed) on DEV real + scramble ----
    results = {"A": {}, "B": {}}
    for side in ("real", "scramble"):
        results["A"][side] = eval_arm(dev_recs[side], "A", gate_thresh)
        results["B"][side] = eval_arm(dev_recs[side], "B", gate_thresh)
    results["C"] = {}
    for seed, w in arm_c_weights.items():
        results["C"][seed] = {side: eval_arm(dev_recs[side], "C", gate_thresh, w, mean, std)
                              for side in ("real", "scramble")}
    # Arm C headline = seed 7 (first of SEEDS_ARM_C), others report stability
    c_headline = results["C"][SEEDS_ARM_C[0]]

    ablation_eval = {}
    for fi, fname in enumerate(FEATURE_NAMES):
        w_abl = ablation_weights[fname]
        ablation_eval[fname] = {side: eval_arm(dev_recs[side], "C", gate_thresh, w_abl, mean, std,
                                               ablate_feature=fi) for side in ("real", "scramble")}

    tier_A, msg_A = classify_verdict(results["A"]["real"], results["A"]["scramble"], bow_only_overall_accuracy, n_dev)
    tier_B, msg_B = classify_verdict(results["B"]["real"], results["B"]["scramble"], bow_only_overall_accuracy, n_dev)
    tier_C, msg_C = classify_verdict(c_headline["real"], c_headline["scramble"], bow_only_overall_accuracy, n_dev)

    tiers = {"A": tier_A, "B": tier_B, "C": tier_C}
    order = {"HARD_PASS": 2, "MIDDLE_BAND": 1, "HARD_FAIL": 0}
    best_arm = max(tiers, key=lambda a: order[tiers[a]])
    top_verdict = tiers[best_arm]
    verdict_msg = (f"A={tier_A}({msg_A}) | B={tier_B}({msg_B}) | C={tier_C}({msg_C}) | "
                  f"best_arm={best_arm} | bow_only_overall={bow_only_overall_accuracy}")

    # ---- arms-differ (META_RULE_AF) ----
    pred_vec = {}
    for arm_key, w_, side_lbl in (("A", None, "real"), ("B", None, "real"), ("C", arm_c_weights[SEEDS_ARM_C[0]], "real")):
        preds = []
        for i in range(n_dev):
            feats = dev_recs[side_lbl][i]["features"]
            res = resolve_item_arm(feats, arm_key, gate_thresh, w_, mean, std)
            preds.append(res["pred_idx"] if res["fired"] else -1)
        pred_vec[arm_key] = preds
    digests = {a: hashlib.sha256(json.dumps(p).encode()).hexdigest() for a, p in pred_vec.items()}
    arms_differ = len({digests["A"], digests["B"], digests["C"]}) >= 2  # at least one pair differs;
                                                                        # A==B is expected on OTHER-
                                                                        # only dev subsets (disclosed)

    elapsed_s = time.perf_counter() - t0
    metrics = {
        "verdict": top_verdict, "verdict_msg": verdict_msg,
        "summary": f"{ANCHOR_NAME} {run_mode}: best_arm={best_arm} tier={top_verdict}",
        "elapsed_s": elapsed_s, "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "config": {"CUES_PER_ITEM": CUES_PER_ITEM, "HOPS_DISCRIMINATOR": HOPS_DISCRIMINATOR,
                  "DECAY": DECAY, "SCORE_MODE": SCORE_MODE, "gate_thresh": gate_thresh,
                  "n_dev": n_dev, "train_fit_cap": train_fit_cap, "n_train_fit_collected": len(train_feats),
                  "j_scanned_for_train_fit": j_scanned},
        "bow_only_overall_accuracy": bow_only_overall_accuracy,
        "positive_control_1hop_coverage": positive_control_1hop_coverage,
        "positive_control_reference": 0.2465, "positive_control_tolerance": 0.02,
        "positive_control_ok": (positive_control_1hop_coverage is not None and
                                abs(positive_control_1hop_coverage - 0.2465) <= 0.02),
        "arm_A": {"real": results["A"]["real"], "scramble": results["A"]["scramble"],
                 "tier": tier_A, "tier_msg": msg_A},
        "arm_B": {"real": results["B"]["real"], "scramble": results["B"]["scramble"],
                 "tier": tier_B, "tier_msg": msg_B},
        "arm_C": {"headline_seed": SEEDS_ARM_C[0], "real": c_headline["real"],
                 "scramble": c_headline["scramble"], "tier": tier_C, "tier_msg": msg_C,
                 "per_seed": {str(s): results["C"][s] for s in SEEDS_ARM_C},
                 "per_seed_train_acc": {str(s): arm_c_train_acc[s] for s in SEEDS_ARM_C},
                 "weight_vectors": {str(s): arm_c_weights[s].tolist() for s in SEEDS_ARM_C}},
        "arm_C_ablation": {fname: {"eval": ablation_eval[fname], "train_acc": ablation_train_acc[fname],
                                   "weight_vector": ablation_weights[fname].tolist()}
                          for fname in FEATURE_NAMES},
        "feature_names": FEATURE_NAMES,
        "best_arm": best_arm, "routing_recommendation": (
            "SHIP_DISCRIMINATOR" if top_verdict == "HARD_PASS" else
            "PARTIAL_PROGRESS_ITERATE" if top_verdict == "MIDDLE_BAND" else
            "DISCRIMINATOR_STILL_NON_DECISIVE"),
        "arms_differ_verified": arms_differ, "arm_digests": digests,
        "arms_differ_exempted": [["A", "B"]] if digests["A"] == digests["B"] else [],
        "cardinality_ok": (len(completed_units(output_dir)) >= n_dev * 2),
        "expected_n_dev_units": n_dev * 2,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "discrete 3-way classification accuracy on a real benchmark; no capacity/noise-floor discriminator applies",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "calibration_check": "adaptive_with_discriminator_gate",
        "storage_strategy": "no_storage",
    }
    _atomic_write_metrics(output_dir, metrics)
    _hb(output_dir, "done", t0, {"verdict": top_verdict})
    return metrics


# =====================================================================================
def self_test() -> dict:
    t0 = time.perf_counter()
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="crutch_disc_selftest_")

    # ---- planted synthetic CSKG: case 1 (convergence) + case 2 (relation-gating flip) ----
    # NB: content_words()'s tokenizer regex is [a-z']+ (no digits) -- all planted node ids MUST be
    # pure alphabetic (canon() is a no-op on already-clean lowercase-alpha strings), or the text
    # tokenizer silently drops the digit suffix and grounding fails (caught by this self-test).
    idx: Dict[str, List[Tuple[str, float]]] = {}

    def add_edge(a, b, rel, trust=1.0):
        idx.setdefault(pair_key(a, b), []).append((rel, trust))

    # case 1: candidate candalpha reached by TWO cues (cueone,cuetwo); candbeta by one (cuethree);
    # candchi unreached.
    add_edge("cueone", "candalpha", "genericrel")
    add_edge("cuetwo", "candalpha", "genericrel2")
    add_edge("cuethree", "candbeta", "genericrel3")
    # case 2: candidate candpsi reached by TWO cues via IRRELEVANT-to-FEELING relations; candquin by
    # ONE cue via a RELEVANT (xreact) relation. candrho unreached.
    add_edge("gcueone", "candpsi", "atlocation")
    add_edge("gcuetwo", "candpsi", "usedfor")
    add_edge("gcuethree", "candquin", "xreact")

    node_set = cskg_node_set_from_index(idx)
    node_degree = compute_node_degree(idx)
    adjacency = build_adjacency(idx)
    node_list = sorted(node_set)

    item1 = {"context": "cueone cuetwo cuethree filler words with no overlap", "question": "what happened",
            "answerA": "candalpha zzq", "answerB": "candbeta zzq", "answerC": "candchi zzq", "label": "1"}
    item2 = {"context": "gcueone gcuetwo gcuethree filler words with no overlap",
            "question": "how would somebody feel afterwards",
            "answerA": "candpsi zzq", "answerB": "candquin zzq", "answerC": "candrho zzq", "label": "2"}

    feats1 = compute_item_features(item1, node_set, idx, adjacency, node_degree, node_list,
                                   item_id="t1", scramble=False)
    assert feats1["F_conv"] == [2, 1, 0], f"case1 F_conv unexpected: {feats1['F_conv']}"
    assert feats1["n_covered"] == 2, f"case1 n_covered unexpected: {feats1['n_covered']}"
    res1_a = resolve_item_arm(feats1, "A", gate_thresh=0.9)  # margin==0.0 -> gap regardless of thresh
    assert res1_a["fired"] and res1_a["pred_idx"] == 0, f"case1 arm A should pick candidate 0: {res1_a}"

    feats2 = compute_item_features(item2, node_set, idx, adjacency, node_degree, node_list,
                                   item_id="t2", scramble=False)
    assert feats2["qtype"] == "FEELING", f"case2 qtype misclassified: {feats2['qtype']}"
    assert feats2["F_conv"] == [2, 1, 0], f"case2 F_conv unexpected: {feats2['F_conv']}"
    assert feats2["F_conv_gated"] == [0, 1, 0], f"case2 F_conv_gated unexpected: {feats2['F_conv_gated']}"
    res2_a = resolve_item_arm(feats2, "A", gate_thresh=0.9)
    res2_b = resolve_item_arm(feats2, "B", gate_thresh=0.9)
    assert res2_a["fired"] and res2_a["pred_idx"] == 0, f"case2 arm A expected WRONG pick 0: {res2_a}"
    assert res2_b["fired"] and res2_b["pred_idx"] == 1, f"case2 arm B expected CORRECT pick 1 (gating flip): {res2_b}"

    # ---- abstain: only 1 candidate covered ----
    item3 = {"context": "cueone filler words with no overlap", "question": "what happened",
            "answerA": "candalpha zzq", "answerB": "zzzq nope", "answerC": "zzzzq nopealt", "label": "1"}
    feats3 = compute_item_features(item3, node_set, idx, adjacency, node_degree, node_list,
                                   item_id="t3", scramble=False)
    assert feats3["n_covered"] == 1, f"case3 expected n_covered=1: {feats3['n_covered']}"
    res3_a = resolve_item_arm(feats3, "A", gate_thresh=0.9)
    assert not res3_a["fired"], f"case3 should abstain (n_covered<2): {res3_a}"

    # ---- Arm C: tiny synthetic training set, deterministic pattern (label = argmax F_conv col) ----
    rng = np.random.default_rng(2026)
    syn_feats, syn_gold = [], []
    for _ in range(60):
        M = rng.integers(0, 4, size=(3, 4)).astype(np.float64)
        # inject noise on cols 2,3 uncorrelated with label; label driven by col0 (F_conv)
        gold = int(np.argmax(M[:, 0]))
        syn_feats.append(M)
        syn_gold.append(gold)
    mean, std = fit_norm_stats(syn_feats)
    w_syn = fit_arm_c(syn_feats, syn_gold, seed=7, mean=mean, std=std, n_epochs=500)
    train_acc = arm_c_train_accuracy(syn_feats, syn_gold, w_syn, mean, std)
    assert train_acc >= 0.70, f"arm C GD failed to fit separable synthetic pattern: train_acc={train_acc}"
    # held-out generalization check
    held_feats, held_gold = [], []
    for _ in range(15):
        M = rng.integers(0, 4, size=(3, 4)).astype(np.float64)
        held_feats.append(M)
        held_gold.append(int(np.argmax(M[:, 0])))
    held_acc = arm_c_train_accuracy(held_feats, held_gold, w_syn, mean, std)
    assert held_acc >= 0.60, f"arm C failed to generalize to held-out synthetic rows: held_acc={held_acc}"

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
    print(f"[self_test] PASS in {elapsed:.2f}s: convergence, gating-flip, abstain, arm-C GD fit+"
         "generalize, exp_checkpoint round-trip, determinism, question-type classifier", flush=True)
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "all planted cases + arm-C GD checks passed",
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
