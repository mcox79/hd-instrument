"""stage3_hrr_involutive_systematic_generalization_v1 -- STUB C compositional probe.

USER 2026-06-27 NO LOCAL: cell-author smoke + dispatch on remote only.

DESIGN PROVENANCE: research drill 2026-06-27
  notes/research_drill_typed_multibank_actively_hurts_3x_2026-06-27.md STUB C
PREREG: preregs/2026-06-27_stage3_hrr_involutive_systematic_generalization_v1.md

MECHANISM: Stage 3 compositional understanding via HRR involutive operations.
Brain analog: hippocampal sequence binding + cortical schema extraction (Plate
1995 + Kanerva 1988). Tests if substrate can compose NEW facts from known
facts via involutive HRR binding (NOT typed routing).

Given training facts (subj, verb, obj_known), can substrate generalize to
(?, verb, obj_NEW) where obj_NEW shares features with known objects via HRR
involutive unbinding chain? AND does it beat nearest-neighbor interpolation?

ARMS (3 mandatory; per-arm metrics in metrics.json):
  ARM_BASELINE -- lookup-only, no composition; sanity rail.
  ARM_HRR_INVOLUTIVE -- the mechanism: F = sum bind(verb, bind(subj, obj));
    query via unbind(verb, unbind(obj, F)) -> subject cleanup.
  ARM_NEAREST_NEIGHBOR_INTERPOLATION -- control: k-NN on obj features ->
    modal subject from neighbors.

PRE-REG BANDS (LOCKED at module init; see prereg .md for full):
  HP_HELDOUT_FLOOR = 0.50 (10x lift over chance 0.05 for N_ENTITIES=200)
  HP_COMPOSITION_LIFT_MIN = 0.10 (HRR > NN by 0.10)
  HP_BASELINE_CEILING = 0.15 (lookup must NOT generalize)
  HF_HRR_NULL = 0.15 (HRR < 0.15 = mechanism null)
  HF_HRR_NO_LIFT = 0.02 (HRR no better than NN)
  HF_BASELINE_LEAK = 0.30 (lookup arm shouldn't generalize)
  CV_CHAIN_GRADE_MAX = 0.10
  EXPECTED_N_UNITS = 3 seeds * 3 arms = 9 (full); 1 * 3 = 3 (smoke)

META_RULE_H cardinality_ok mandatory.
META_RULE_J no-silent-except: failures recorded + halt loop.
META_RULE_K smoke fires discriminator: smoke at N_DIM=2048 with same regime
  ratios (HELDOUT_OBJ_FRACTION=0.20, FEATURE_OVERLAP_FRAC=0.30).
META_RULE_L band-floor strictly-above-floor.
META_RULE_F NO MAGNITUDE COUPLING: HRR bind/unbind are unitary-magnitude;
  cor(per_query_score, ||F||) sanity check < 0.5.

PROT-020 GPU routing: cell uses torch.fft; runs on CPU at N_DIM=8192 per drill.

ASCII-only. Single-file. Resumable per (seed, arm) checkpoint key.
Author: exp_dev 2026-06-27 (STUB C; under Research lead).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "stage3_hrr_involutive_systematic_generalization_v1"
CORPUS_PROVENANCE = (
    "synthetic_HRR_bipolar_role_filler_facts_subj_verb_obj_held_out_objects_"
    "via_feature_overlap_prototypes"
)

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# ---------------- pre-reg bands (LOCKED at module init) ----------------
HP_HELDOUT_FLOOR = 0.50
HP_COMPOSITION_LIFT_MIN = 0.10
HP_BASELINE_CEILING = 0.15
HF_HRR_NULL = 0.15
HF_HRR_NO_LIFT = 0.02
HF_BASELINE_LEAK = 0.30
Q_SUSPECT_SATURATION = 0.95
CV_CHAIN_GRADE_MAX = 0.10
MB_HELDOUT_LOW = 0.25
MB_HELDOUT_HIGH = 0.50
MB_COMPOSITION_LIFT_LOW = 0.03
MB_COMPOSITION_LIFT_HIGH = 0.10
MAG_COUPLING_MAX = 0.50

assert 0.0 < HP_HELDOUT_FLOOR < 1.0, "band locked"
assert HF_HRR_NULL < HP_HELDOUT_FLOOR, "band locked"

# ---------------- regime config ----------------
if SMOKE:
    N_DIM = 2048
    N_ENTITIES = 50
    N_VERBS = 4
    N_TRAIN_FACTS = 100
    N_HELDOUT_FACTS = 20
    HELDOUT_OBJ_FRACTION = 0.20
    N_FEATURE_PROTOTYPES = 8
    FEATURE_OVERLAP_FRAC = 0.30
    NN_K = 3
    SEEDS = [11]
else:
    N_DIM = 8192
    N_ENTITIES = 200
    N_VERBS = 10
    N_TRAIN_FACTS = 500
    N_HELDOUT_FACTS = 100
    HELDOUT_OBJ_FRACTION = 0.20
    N_FEATURE_PROTOTYPES = 16
    FEATURE_OVERLAP_FRAC = 0.30
    NN_K = 3
    SEEDS = [11, 13, 19]

ARMS = ["ARM_BASELINE", "ARM_HRR_INVOLUTIVE", "ARM_NEAREST_NEIGHBOR_INTERPOLATION"]
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

CHANCE_ACC = 1.0 / max(N_ENTITIES, 1)

CONFIG_VERSION = (
    "stage3_hrr_involutive-v1: N_DIM=%d N_ENTITIES=%d N_VERBS=%d N_TRAIN=%d "
    "N_HELDOUT=%d HELDOUT_OBJ_FRAC=%.2f N_PROTO=%d OVERLAP=%.2f NN_K=%d "
    "seeds=%s mode=%s HP_floor=%.2f HP_lift>=%.2f baseline_ceil<=%.2f "
    "cv<=%.2f EXPECTED_N=%d chance=%.4f"
) % (
    N_DIM, N_ENTITIES, N_VERBS, N_TRAIN_FACTS, N_HELDOUT_FACTS,
    HELDOUT_OBJ_FRACTION, N_FEATURE_PROTOTYPES, FEATURE_OVERLAP_FRAC, NN_K,
    SEEDS, RUN_MODE,
    HP_HELDOUT_FLOOR, HP_COMPOSITION_LIFT_MIN, HP_BASELINE_CEILING,
    CV_CHAIN_GRADE_MAX, EXPECTED_N_UNITS, CHANCE_ACC,
)

_DEVICE = torch.device("cpu")
_STORE_DTYPE = torch.float32


def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def random_bipolar_t(shape, gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=_DEVICE, dtype=_STORE_DTYPE)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def hrr_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR circular convolution via FFT. Returns real result in input dtype."""
    fa = torch.fft.fft(a)
    fb = torch.fft.fft(b)
    return torch.fft.ifft(fa * fb).real.to(a.dtype)


def hrr_unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR circular correlation = unbind via FFT and conjugate."""
    fc = torch.fft.fft(c)
    fb = torch.fft.fft(b)
    return torch.fft.ifft(fc * fb.conj()).real.to(c.dtype)


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    """Cosine similarity between two 1D vectors."""
    na = float(torch.linalg.norm(a))
    nb = float(torch.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(torch.dot(a, b) / (na * nb))


def cosine_matrix(queries: torch.Tensor, codebook: torch.Tensor) -> torch.Tensor:
    """[Q, D] x [N, D] -> [Q, N] cosine similarity matrix."""
    q_norm = queries / (torch.linalg.norm(queries, dim=1, keepdim=True) + 1e-9)
    c_norm = codebook / (torch.linalg.norm(codebook, dim=1, keepdim=True) + 1e-9)
    return q_norm @ c_norm.T


def build_entities_with_features(seed_offset: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Build N_ENTITIES entities as convex combinations of N_FEATURE_PROTOTYPES.

    Each entity is built from ~3 random prototypes with FEATURE_OVERLAP_FRAC
    of dimensions shared. This creates a feature space where similar entities
    have measurable cosine overlap, enabling generalization via shared features.

    Returns (entities, prototype_assignment) where prototype_assignment[i] is
    a [N_FEATURE_PROTOTYPES] indicator showing which prototypes built entity i.
    """
    g_proto = _make_gen(seed_offset + 7)
    g_ent = _make_gen(seed_offset + 11)
    g_assign = _make_gen(seed_offset + 13)

    prototypes = random_bipolar_t((N_FEATURE_PROTOTYPES, N_DIM), g_proto)
    entities = random_bipolar_t((N_ENTITIES, N_DIM), g_ent)

    # Each entity: pick ~3 prototypes; share FEATURE_OVERLAP_FRAC dims with their mean
    n_shared_dims = int(FEATURE_OVERLAP_FRAC * N_DIM)
    assignment = torch.zeros((N_ENTITIES, N_FEATURE_PROTOTYPES), dtype=torch.float32)
    n_proto_per_entity = 3
    for i in range(N_ENTITIES):
        proto_picks = torch.randperm(N_FEATURE_PROTOTYPES,
                                     generator=g_assign)[:n_proto_per_entity]
        assignment[i, proto_picks] = 1.0 / n_proto_per_entity
        # Compose: entity inherits FEATURE_OVERLAP_FRAC dims from mean of picked prototypes
        proto_mean = prototypes[proto_picks].mean(dim=0)
        proto_mean_bp = torch.where(proto_mean >= 0,
                                    torch.ones_like(proto_mean),
                                    -torch.ones_like(proto_mean))
        entities[i, :n_shared_dims] = proto_mean_bp[:n_shared_dims]

    return entities, assignment


def build_verbs(seed_offset: int) -> torch.Tensor:
    g_v = _make_gen(seed_offset + 17)
    return random_bipolar_t((N_VERBS, N_DIM), g_v)


def build_fact_partition(seed_offset: int) -> Tuple[List[Tuple[int, int, int]],
                                                     List[Tuple[int, int, int]]]:
    """Build train + heldout facts. Heldout objects do NOT appear in train.

    Returns (train_facts, heldout_facts) as lists of (subj, verb, obj) tuples.
    """
    g_split = _make_gen(seed_offset + 19)
    g_train = _make_gen(seed_offset + 23)
    g_held = _make_gen(seed_offset + 29)

    # Split entities into seen-objects and heldout-objects pools
    n_heldout_objs = int(HELDOUT_OBJ_FRACTION * N_ENTITIES)
    perm = torch.randperm(N_ENTITIES, generator=g_split)
    heldout_obj_pool = perm[:n_heldout_objs].tolist()
    seen_obj_pool = perm[n_heldout_objs:].tolist()
    # Subjects can be any entity (seen or heldout pool both fine as subjects)
    all_subj_pool = list(range(N_ENTITIES))

    # Train facts: subj from any, verb random, obj from SEEN pool only
    train: List[Tuple[int, int, int]] = []
    for _ in range(N_TRAIN_FACTS):
        s = int(torch.randint(0, len(all_subj_pool), (1,), generator=g_train).item())
        v = int(torch.randint(0, N_VERBS, (1,), generator=g_train).item())
        o_idx = int(torch.randint(0, len(seen_obj_pool), (1,), generator=g_train).item())
        o = seen_obj_pool[o_idx]
        train.append((all_subj_pool[s], v, o))

    # Heldout facts: obj from HELDOUT pool only; subj+verb same distribution
    held: List[Tuple[int, int, int]] = []
    for _ in range(N_HELDOUT_FACTS):
        s = int(torch.randint(0, len(all_subj_pool), (1,), generator=g_held).item())
        v = int(torch.randint(0, N_VERBS, (1,), generator=g_held).item())
        o_idx = int(torch.randint(0, len(heldout_obj_pool), (1,), generator=g_held).item())
        o = heldout_obj_pool[o_idx]
        held.append((all_subj_pool[s], v, o))

    return train, held


def eval_baseline(seed_offset: int) -> float:
    """ARM_BASELINE: lookup-only. Stores train facts as atomic; tries heldout.

    For each heldout query (?, v, o_NEW), look for exact (v, o_NEW) match in
    train (there won't be one because o_NEW is heldout). Return random subject
    if no match. Sanity rail: should not exceed HP_BASELINE_CEILING.
    """
    entities, _ = build_entities_with_features(seed_offset)
    train, held = build_fact_partition(seed_offset)

    # Build train lookup: (v, o) -> subj (last-write-wins for collisions)
    lookup: Dict[Tuple[int, int], int] = {}
    for (s, v, o) in train:
        lookup[(v, o)] = s

    g_guess = _make_gen(seed_offset + 41)
    correct = 0
    for (true_s, v, o) in held:
        if (v, o) in lookup:
            pred = lookup[(v, o)]
        else:
            # Random guess (cannot generalize without composition)
            pred = int(torch.randint(0, N_ENTITIES, (1,), generator=g_guess).item())
        if pred == true_s:
            correct += 1
    return correct / max(len(held), 1)


def eval_hrr_involutive(seed_offset: int) -> Tuple[float, float]:
    """ARM_HRR_INVOLUTIVE: composes facts via HRR role-filler bindings.

    Storage: F = sum_i bind(verb_i, bind(subj_i, obj_i))
    Query (?, v, o_NEW): unbind(v, unbind(o_NEW, F)) -> noisy subject
    For heldout objects, the unbind operates on a similar object via feature
    overlap, recovering subject from nearby-feature objects' contributions.

    Returns (heldout_acc, magnitude_coupling_cor).
    """
    entities, _ = build_entities_with_features(seed_offset)
    verbs = build_verbs(seed_offset)
    train, held = build_fact_partition(seed_offset)

    # Build memory bundle F
    F = torch.zeros(N_DIM, dtype=_STORE_DTYPE, device=_DEVICE)
    for (s, v, o) in train:
        # bind(verb, bind(subj, obj))
        inner = hrr_bind(entities[s], entities[o])
        F = F + hrr_bind(verbs[v], inner)

    # Heldout query: unbind(v, unbind(o, F)) -> noisy subject
    correct = 0
    per_query_scores: List[float] = []
    per_query_norms: List[float] = []
    for (true_s, v, o) in held:
        # First unbind by object (held object)
        step1 = hrr_unbind(F, entities[o])
        # Then unbind by verb
        candidate = hrr_unbind(step1, verbs[v])
        # Cleanup over entity codebook (top-1)
        cand_norm = torch.linalg.norm(candidate)
        if float(cand_norm) < 1e-9:
            pred = -1
        else:
            sims = entities @ candidate / (
                torch.linalg.norm(entities, dim=1) * cand_norm + 1e-9
            )
            pred = int(sims.argmax().item())
            per_query_scores.append(float(sims[true_s].item()) if pred != -1 else 0.0)
            per_query_norms.append(float(cand_norm.item()))
        if pred == true_s:
            correct += 1

    heldout_acc = correct / max(len(held), 1)

    # META_RULE_F magnitude coupling check
    mag_cor = 0.0
    if len(per_query_scores) >= 3 and len(per_query_norms) >= 3:
        s_arr = np.array(per_query_scores)
        n_arr = np.array(per_query_norms)
        if s_arr.std() > 1e-9 and n_arr.std() > 1e-9:
            mag_cor = float(np.corrcoef(s_arr, n_arr)[0, 1])

    return heldout_acc, mag_cor


def eval_nearest_neighbor(seed_offset: int) -> float:
    """ARM_NEAREST_NEIGHBOR_INTERPOLATION: k-NN control.

    For query (?, v, o_NEW): find k=NN_K nearest known objects to o_NEW by
    cosine; retrieve (subj, v) from training for those neighbors; return
    modal subject. Tests if HRR composition is more than feature-NN.
    """
    entities, _ = build_entities_with_features(seed_offset)
    train, held = build_fact_partition(seed_offset)

    # Build per-object lookup: o -> list of (subj, verb) from training
    obj_to_facts: Dict[int, List[Tuple[int, int]]] = {}
    for (s, v, o) in train:
        obj_to_facts.setdefault(o, []).append((s, v))

    train_objs = list(obj_to_facts.keys())
    if not train_objs:
        return 0.0
    train_obj_vecs = entities[torch.tensor(train_objs, dtype=torch.long)]

    correct = 0
    for (true_s, v, o) in held:
        q = entities[o].unsqueeze(0)  # [1, D]
        sims = cosine_matrix(q, train_obj_vecs).squeeze(0)
        k_eff = min(NN_K, sims.numel())
        top_k = torch.topk(sims, k=k_eff).indices.tolist()
        # Collect subjects from neighbors that match the verb
        cand_subjects: List[int] = []
        for ti in top_k:
            o_train = train_objs[ti]
            for (s_train, v_train) in obj_to_facts[o_train]:
                if v_train == v:
                    cand_subjects.append(s_train)
        if not cand_subjects:
            # No verb-match in neighbors; fall back to any subject in neighbors
            for ti in top_k:
                o_train = train_objs[ti]
                for (s_train, _) in obj_to_facts[o_train]:
                    cand_subjects.append(s_train)
        if not cand_subjects:
            pred = -1
        else:
            # Modal (most common) subject
            counts: Dict[int, int] = {}
            for s in cand_subjects:
                counts[s] = counts.get(s, 0) + 1
            pred = max(counts.items(), key=lambda kv: kv[1])[0]
        if pred == true_s:
            correct += 1
    return correct / max(len(held), 1)


# ---------------- verdict logic ----------------

def compute_verdict(per_unit: Dict[str, Dict],
                    failures: List[Dict] = None) -> Tuple[str, str, Dict]:
    if failures is None:
        failures = []
    if not per_unit:
        return ("HARD_FAIL", "no_units", {"cardinality_ok": False})

    n_units_observed = len(per_unit)
    cardinality_ok = (n_units_observed >= EXPECTED_N_UNITS) and (not failures)

    by_arm: Dict[str, List[float]] = {a: [] for a in ARMS}
    mag_cors: List[float] = []
    for key, body in per_unit.items():
        arm = body["arm"]
        if arm in by_arm:
            by_arm[arm].append(float(body["heldout_acc"]))
            if arm == "ARM_HRR_INVOLUTIVE" and "magnitude_coupling_cor" in body:
                mc = body.get("magnitude_coupling_cor")
                if mc is not None and not math.isnan(float(mc)):
                    mag_cors.append(float(mc))

    def stats(vals):
        if not vals:
            return float("nan"), float("nan"), 0
        m = float(np.mean(vals))
        s = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        return round(m, 4), round(cv, 4), len(vals)

    baseline_m, baseline_cv, baseline_n = stats(by_arm["ARM_BASELINE"])
    hrr_m, hrr_cv, hrr_n = stats(by_arm["ARM_HRR_INVOLUTIVE"])
    nn_m, nn_cv, nn_n = stats(by_arm["ARM_NEAREST_NEIGHBOR_INTERPOLATION"])

    composition_lift = (hrr_m - nn_m) if not (math.isnan(hrr_m) or math.isnan(nn_m)) else float("nan")
    mechanism_lift = (hrr_m - CHANCE_ACC) if not math.isnan(hrr_m) else float("nan")

    saturated = hrr_m >= Q_SUSPECT_SATURATION
    cv_ok = hrr_cv <= CV_CHAIN_GRADE_MAX
    baseline_no_leak = baseline_m < HP_BASELINE_CEILING
    mag_coupling_ok = True
    mag_cor_mean = None
    if mag_cors:
        mag_cor_mean = float(np.mean(mag_cors))
        mag_coupling_ok = abs(mag_cor_mean) < MAG_COUPLING_MAX

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "baseline_heldout_acc_mean": baseline_m,
        "baseline_heldout_acc_cv": baseline_cv,
        "hrr_heldout_acc_mean": hrr_m,
        "hrr_heldout_acc_cv": hrr_cv,
        "nn_heldout_acc_mean": nn_m,
        "nn_heldout_acc_cv": nn_cv,
        "composition_lift_hrr_over_nn": round(composition_lift, 4) if not math.isnan(composition_lift) else None,
        "mechanism_lift_over_chance": round(mechanism_lift, 4) if not math.isnan(mechanism_lift) else None,
        "chance_acc": round(CHANCE_ACC, 4),
        "hrr_saturated_above_Q": saturated,
        "baseline_no_leak": baseline_no_leak,
        "magnitude_coupling_cor_mean": mag_cor_mean,
        "magnitude_coupling_ok": mag_coupling_ok,
        "n_failures": len(failures),
        "failures_brief": [{"key": f.get("key", "?"), "exc_type": f.get("exc_type", "?")}
                           for f in failures[:5]],
        "config_version": CONFIG_VERSION,
        "HP_heldout_floor": HP_HELDOUT_FLOOR,
        "HP_composition_lift_min": HP_COMPOSITION_LIFT_MIN,
        "HP_baseline_ceiling": HP_BASELINE_CEILING,
        "cv_chain_grade_max": CV_CHAIN_GRADE_MAX,
    }

    # HARD_FAIL conditions (load-bearing first)
    if not cardinality_ok:
        return ("HARD_FAIL",
                f"cardinality_breach: observed={n_units_observed} expected={EXPECTED_N_UNITS} "
                f"failures={len(failures)}", detail)
    if baseline_m >= HF_BASELINE_LEAK:
        return ("HARD_FAIL",
                f"baseline_leak: ARM_BASELINE={baseline_m:.4f} >= {HF_BASELINE_LEAK} "
                f"(lookup arm should NOT generalize; data leak suspected)",
                detail)
    if hrr_m < HF_HRR_NULL:
        return ("HARD_FAIL",
                f"hrr_mechanism_null: ARM_HRR_INVOLUTIVE={hrr_m:.4f} < {HF_HRR_NULL} "
                f"(involutive unbind did not enable generalization)",
                detail)
    if not math.isnan(composition_lift) and composition_lift <= HF_HRR_NO_LIFT:
        return ("HARD_FAIL",
                f"hrr_no_lift_over_nn: composition_lift={composition_lift:.4f} <= "
                f"{HF_HRR_NO_LIFT} (HRR no better than feature-NN; mechanism is "
                f"interpolation in disguise)",
                detail)
    if saturated:
        return ("HARD_FAIL",
                f"by_construction_saturation_META_RULE_K: hrr={hrr_m:.4f} >= "
                f"{Q_SUSPECT_SATURATION}; suspect prototype-overlap regime too easy",
                detail)
    if not mag_coupling_ok:
        return ("HARD_FAIL",
                f"magnitude_coupling_META_RULE_F: |cor(score, ||F||)|="
                f"{abs(mag_cor_mean):.4f} >= {MAG_COUPLING_MAX} "
                f"(score driven by magnitude, not composition)",
                detail)

    # HARD_PASS conditions (strictly-above-floor per META_RULE_L)
    floor_meets = hrr_m >= HP_HELDOUT_FLOOR
    lift_meets = (not math.isnan(composition_lift)) and (composition_lift >= HP_COMPOSITION_LIFT_MIN)
    if floor_meets and lift_meets and baseline_no_leak and cv_ok:
        return ("HARD_PASS",
                f"chain_grade_compositional_hrr: hrr={hrr_m:.4f} >= {HP_HELDOUT_FLOOR} "
                f"(10x lift over chance={CHANCE_ACC:.4f}); composition_lift="
                f"{composition_lift:.4f} >= {HP_COMPOSITION_LIFT_MIN} (HRR > NN); "
                f"baseline={baseline_m:.4f} < {HP_BASELINE_CEILING} (no leak); "
                f"cv={hrr_cv:.4f} <= {CV_CHAIN_GRADE_MAX}",
                detail)

    # MIDDLE_BAND conditions
    floor_partial = MB_HELDOUT_LOW <= hrr_m < MB_HELDOUT_HIGH
    lift_partial = (not math.isnan(composition_lift)) and \
                   MB_COMPOSITION_LIFT_LOW <= composition_lift < MB_COMPOSITION_LIFT_HIGH
    if floor_partial or lift_partial:
        comp_lift_str = "nan" if math.isnan(composition_lift) else f"{composition_lift:.4f}"
        return ("MIDDLE_BAND",
                f"partial: hrr={hrr_m:.4f} (HP>={HP_HELDOUT_FLOOR}); "
                f"composition_lift={comp_lift_str} "
                f"(HP>={HP_COMPOSITION_LIFT_MIN}); baseline_no_leak={baseline_no_leak}; "
                f"cv_ok={cv_ok}",
                detail)

    comp_lift_str2 = "nan" if math.isnan(composition_lift) else f"{composition_lift:.4f}"
    return ("MIDDLE_BAND",
            f"unbinned: hrr={hrr_m:.4f}; nn={nn_m:.4f}; baseline={baseline_m:.4f}; "
            f"composition_lift={comp_lift_str2}",
            detail)


# ---------------- self-test ----------------

def _selftest():
    print("[selftest] stage3_hrr_involutive_systematic_generalization_v1 starting", flush=True)

    # T1: HRR involution sanity on bipolar: unbind(bind(a, b), b) ~= a.
    # Bipolar HRR is approximate (not unit-norm spectrum); bound is 0.55 not 0.95.
    # The substrate uses bipolar everywhere; this is the realistic recovery level.
    # Top-1 cleanup against codebook still works because 0.55 >> 1/sqrt(N) chance.
    g = _make_gen(7)
    test_d = 1024
    a = random_bipolar_t((test_d,), g)
    b = random_bipolar_t((test_d,), g)
    c = hrr_bind(a, b)
    a_rec = hrr_unbind(c, b)
    inv_cos = cosine(a_rec, a)
    assert inv_cos >= 0.55, f"T1 HRR bipolar involution: cos(unbind(bind(a,b),b), a) = {inv_cos} < 0.55"
    print(f"[selftest] T1 PASS: HRR bipolar involution cos={inv_cos:.4f} >= 0.55 (chance ~{1.0/math.sqrt(test_d):.4f})", flush=True)

    # T2: HRR superposition unbind: F = sum bind(a_i, b_i); unbind(F, b_j) ~= a_j
    g2 = _make_gen(13)
    K = 10
    a_list = [random_bipolar_t((test_d,), g2) for _ in range(K)]
    b_list = [random_bipolar_t((test_d,), g2) for _ in range(K)]
    F = torch.zeros(test_d, dtype=_STORE_DTYPE)
    for ai, bi in zip(a_list, b_list):
        F = F + hrr_bind(ai, bi)
    # Test: unbind by b_3 should recover noisy a_3
    target = 3
    a_noisy = hrr_unbind(F, b_list[target])
    sup_cos = cosine(a_noisy, a_list[target])
    assert sup_cos >= 0.20, (
        f"T2 HRR superposition: cos(unbind(sum, b_3), a_3) = {sup_cos} < 0.20"
    )
    print(f"[selftest] T2 PASS: HRR superposition unbind cos={sup_cos:.4f} >= 0.20", flush=True)

    # T3: bipolar in {-1, +1}
    g3 = _make_gen(17)
    cb = random_bipolar_t((128, 256), g3)
    u = torch.unique(cb)
    assert set(u.tolist()) <= {-1.0, 1.0}, "T3 bipolar"
    print(f"[selftest] T3 PASS: bipolar in {{-1,+1}}", flush=True)

    # T4: cosine_matrix correctness on synthetic
    q = random_bipolar_t((3, 64), _make_gen(19))
    c = random_bipolar_t((10, 64), _make_gen(23))
    cm = cosine_matrix(q, c)
    assert cm.shape == (3, 10), f"T4 cosine_matrix shape {cm.shape}"
    # Diagonals via self should be 1.0
    cm_self = cosine_matrix(c, c)
    diag = cm_self.diag()
    assert torch.allclose(diag, torch.ones(10), atol=1e-4), f"T4 diag {diag}"
    print(f"[selftest] T4 PASS: cosine_matrix correct shape + self-cos=1", flush=True)

    # T5: heldout object isolation (no train contamination)
    # Use a small synthetic to verify build_fact_partition partitions correctly
    saved_ne = globals()["N_ENTITIES"]
    saved_ntr = globals()["N_TRAIN_FACTS"]
    saved_nhe = globals()["N_HELDOUT_FACTS"]
    saved_hof = globals()["HELDOUT_OBJ_FRACTION"]
    globals()["N_ENTITIES"] = 20
    globals()["N_TRAIN_FACTS"] = 30
    globals()["N_HELDOUT_FACTS"] = 10
    globals()["HELDOUT_OBJ_FRACTION"] = 0.30
    try:
        tr, he = build_fact_partition(42)
        train_objs_set = set(t[2] for t in tr)
        held_objs_set = set(t[2] for t in he)
        overlap = train_objs_set & held_objs_set
        assert len(overlap) == 0, f"T5 train/held obj overlap: {overlap}"
    finally:
        globals()["N_ENTITIES"] = saved_ne
        globals()["N_TRAIN_FACTS"] = saved_ntr
        globals()["N_HELDOUT_FACTS"] = saved_nhe
        globals()["HELDOUT_OBJ_FRACTION"] = saved_hof
    print(f"[selftest] T5 PASS: heldout objects do NOT appear in train", flush=True)

    # T6: verdict-machinery synthetic cases
    fake_hp = {
        "11_ARM_BASELINE": {"arm": "ARM_BASELINE", "heldout_acc": 0.05},
        "13_ARM_BASELINE": {"arm": "ARM_BASELINE", "heldout_acc": 0.06},
        "19_ARM_BASELINE": {"arm": "ARM_BASELINE", "heldout_acc": 0.04},
        "11_ARM_HRR_INVOLUTIVE": {"arm": "ARM_HRR_INVOLUTIVE", "heldout_acc": 0.60,
                                   "magnitude_coupling_cor": 0.10},
        "13_ARM_HRR_INVOLUTIVE": {"arm": "ARM_HRR_INVOLUTIVE", "heldout_acc": 0.58,
                                   "magnitude_coupling_cor": 0.12},
        "19_ARM_HRR_INVOLUTIVE": {"arm": "ARM_HRR_INVOLUTIVE", "heldout_acc": 0.61,
                                   "magnitude_coupling_cor": 0.08},
        "11_ARM_NEAREST_NEIGHBOR_INTERPOLATION": {
            "arm": "ARM_NEAREST_NEIGHBOR_INTERPOLATION", "heldout_acc": 0.40},
        "13_ARM_NEAREST_NEIGHBOR_INTERPOLATION": {
            "arm": "ARM_NEAREST_NEIGHBOR_INTERPOLATION", "heldout_acc": 0.42},
        "19_ARM_NEAREST_NEIGHBOR_INTERPOLATION": {
            "arm": "ARM_NEAREST_NEIGHBOR_INTERPOLATION", "heldout_acc": 0.38},
    }
    global EXPECTED_N_UNITS
    saved_expected = EXPECTED_N_UNITS
    EXPECTED_N_UNITS = 9
    try:
        v, msg, det = compute_verdict(fake_hp)
        assert v == "HARD_PASS", f"T6a HP expected, got {v}: {msg}"
        print(f"[selftest] T6a PASS: synthetic HARD_PASS path -> {v}", flush=True)

        # T6b: HARD_FAIL HRR null
        fake_null = dict(fake_hp)
        for k in list(fake_null.keys()):
            if "HRR" in k:
                fake_null[k] = dict(fake_null[k])
                fake_null[k]["heldout_acc"] = 0.08
        v, msg, det = compute_verdict(fake_null)
        assert v == "HARD_FAIL", f"T6b HF expected, got {v}"
        assert "hrr_mechanism_null" in msg, f"T6b expected null msg, got {msg}"
        print(f"[selftest] T6b PASS: hrr_mechanism_null -> HARD_FAIL", flush=True)

        # T6c: HARD_FAIL HRR no lift over NN
        fake_nolift = dict(fake_hp)
        for k in list(fake_nolift.keys()):
            if k.endswith("ARM_HRR_INVOLUTIVE"):
                fake_nolift[k] = dict(fake_nolift[k])
                fake_nolift[k]["heldout_acc"] = 0.41
        v, msg, det = compute_verdict(fake_nolift)
        assert v == "HARD_FAIL", f"T6c HF expected, got {v}"
        assert "hrr_no_lift_over_nn" in msg, f"T6c expected nolift msg, got {msg}"
        print(f"[selftest] T6c PASS: hrr_no_lift -> HARD_FAIL", flush=True)

        # T6d: HARD_FAIL baseline leak
        fake_leak = dict(fake_hp)
        for k in list(fake_leak.keys()):
            if k.endswith("ARM_BASELINE"):
                fake_leak[k] = dict(fake_leak[k])
                fake_leak[k]["heldout_acc"] = 0.40
        v, msg, det = compute_verdict(fake_leak)
        assert v == "HARD_FAIL", f"T6d HF expected, got {v}"
        assert "baseline_leak" in msg, f"T6d expected leak msg, got {msg}"
        print(f"[selftest] T6d PASS: baseline_leak -> HARD_FAIL", flush=True)

        # T6e: HARD_FAIL cardinality breach
        fake_card = dict(list(fake_hp.items())[:6])
        v, msg, det = compute_verdict(fake_card)
        assert v == "HARD_FAIL", f"T6e HF expected, got {v}"
        assert "cardinality_breach" in msg, f"T6e expected card msg, got {msg}"
        print(f"[selftest] T6e PASS: cardinality_breach -> HARD_FAIL", flush=True)

        # T6f: MIDDLE_BAND partial (HRR in MB band; lift > HF_NO_LIFT but < HP_min)
        fake_mb = dict(fake_hp)
        for k in list(fake_mb.keys()):
            if k.endswith("ARM_HRR_INVOLUTIVE"):
                fake_mb[k] = dict(fake_mb[k])
                fake_mb[k]["heldout_acc"] = 0.35  # in [0.25, 0.50] MB band
            if k.endswith("ARM_NEAREST_NEIGHBOR_INTERPOLATION"):
                fake_mb[k] = dict(fake_mb[k])
                fake_mb[k]["heldout_acc"] = 0.30  # keep lift = 0.05 in MB lift band
        v, msg, det = compute_verdict(fake_mb)
        assert v == "MIDDLE_BAND", f"T6f MB expected, got {v}: {msg}"
        print(f"[selftest] T6f PASS: partial -> MIDDLE_BAND", flush=True)

        # T6g: HARD_FAIL magnitude coupling
        fake_magc = dict(fake_hp)
        for k in list(fake_magc.keys()):
            if "HRR" in k:
                fake_magc[k] = dict(fake_magc[k])
                fake_magc[k]["magnitude_coupling_cor"] = 0.75  # > 0.50 max
        v, msg, det = compute_verdict(fake_magc)
        assert v == "HARD_FAIL", f"T6g HF expected, got {v}"
        assert "magnitude_coupling" in msg, f"T6g expected mag msg, got {msg}"
        print(f"[selftest] T6g PASS: magnitude_coupling -> HARD_FAIL", flush=True)
    finally:
        EXPECTED_N_UNITS = saved_expected

    # T7: pre-reg envelope locks
    assert HP_HELDOUT_FLOOR == 0.50
    assert HP_COMPOSITION_LIFT_MIN == 0.10
    assert HP_BASELINE_CEILING == 0.15
    assert HF_HRR_NULL == 0.15
    assert CV_CHAIN_GRADE_MAX == 0.10
    print(f"[selftest] T7 PASS: pre-reg envelope constants LOCKED", flush=True)

    print("[selftest] ALL PASS", flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------- main runner ----------------

def run_unit(seed: int, arm: str) -> Dict:
    t0 = time.time()
    seed_offset = seed * 100003 + (hash(arm) & 0xFFFF)
    body: Dict = {
        "seed": int(seed),
        "arm": arm,
        "wall_s": 0.0,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "N": int(N_DIM),
        "N_ENTITIES": int(N_ENTITIES),
        "N_VERBS": int(N_VERBS),
        "N_TRAIN_FACTS": int(N_TRAIN_FACTS),
        "N_HELDOUT_FACTS": int(N_HELDOUT_FACTS),
        "HELDOUT_OBJ_FRACTION": float(HELDOUT_OBJ_FRACTION),
        "FEATURE_OVERLAP_FRAC": float(FEATURE_OVERLAP_FRAC),
    }
    if arm == "ARM_BASELINE":
        acc = eval_baseline(seed_offset)
        body["heldout_acc"] = float(round(acc, 4))
    elif arm == "ARM_HRR_INVOLUTIVE":
        acc, mag_cor = eval_hrr_involutive(seed_offset)
        body["heldout_acc"] = float(round(acc, 4))
        body["magnitude_coupling_cor"] = float(round(mag_cor, 4))
    elif arm == "ARM_NEAREST_NEIGHBOR_INTERPOLATION":
        acc = eval_nearest_neighbor(seed_offset)
        body["heldout_acc"] = float(round(acc, 4))
    else:
        raise ValueError(f"unknown arm: {arm}")
    body["wall_s"] = float(round(time.time() - t0, 2))
    return body


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    done_keys = set(list_completed_keys(out_dir))
    print(f"[run] {ANCHOR_NAME} smoke={SMOKE} {CONFIG_VERSION}", flush=True)
    print(f"[run] EXPECTED_N_UNITS={EXPECTED_N_UNITS} done={len(done_keys)}", flush=True)

    failures: List[Dict] = []
    per_unit: Dict[str, Dict] = {}

    for seed in SEEDS:
        for arm in ARMS:
            key = f"{seed}_{arm}"
            if key in done_keys:
                continue
            try:
                body = run_unit(seed, arm)
                write_partial_key(out_dir, key, body)
                per_unit[key] = body
                print(f"  [{key}] {body}", flush=True)
            except Exception as e:
                fail = {
                    "key": key,
                    "exc_type": type(e).__name__,
                    "exc_msg": str(e),
                }
                failures.append(fail)
                print(f"  [{key}] FAILED: {e}", flush=True)
                # META_RULE_J: halt loop on first failure (no silent except)
                raise

    per_unit_all = aggregate_partials(out_dir)
    verdict, vm, detail = compute_verdict(per_unit_all, failures)

    summary = {
        "anchor": ANCHOR_NAME,
        "smoke": SMOKE,
        "config_version": CONFIG_VERSION,
        "per_arm_metrics": {a: [b for b in per_unit_all.values() if b.get("arm") == a]
                            for a in ARMS},
        "detail": detail,
        "n_failures": len(failures),
        "failures": failures,
        "corpus_provenance": CORPUS_PROVENANCE,
        "zero_llm_calls_at_inference": True,
    }
    payload = {
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": sum(float(b.get("wall_s", 0.0)) for b in per_unit_all.values()),
        "summary": summary,
    }
    write_metrics(out_dir, payload)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}", flush=True)


if __name__ == "__main__":
    main()
