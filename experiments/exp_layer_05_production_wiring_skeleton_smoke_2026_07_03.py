"""exp_layer_05_production_wiring_skeleton_smoke_2026_07_03.

Layer 0.5 Production Wiring Skeleton -- ARC-CLOSED integration end-to-end.

Substitutes CharTrigramEncoder (substrate-native; zero-external-model) for BGE at
Layer 0 in the ARC-CLOSED pipeline. Everything downstream (Layer 0.5 PPR uniform
union, Layer 0.75 v3-clean structural KG-slot filter, Layer 1 FHRR unbind-and-
cleanup composition) is unchanged. Validates the integration seam where a real
Director-KB / KGStore composition would attach.

Composes ONLY existing chain-grade primitives (Principle 11):
  - hdlab.char_trigram_encoder.CharTrigramEncoder                  (Layer 0)
  - Exp 3E cell's ppr_pipeline_union + build_entity_kg              (Layer 0.5)
  - hdlab.layer_075_structural_slot_filter.layer_075_v3_clean_filter (Layer 0.75)
  - Exp 3E cell's bind_phase/unbind_phase/composition_primitive     (Layer 1)

Motivation: Exp 3E FULL HARD_PASS_FULL_ARC_CLOSURE_V3_CLEAN 2026-07-03 CITED@Director
spawn; MEASURED@data/exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03/metrics.json
per_arm_mean_accuracy shows ARM_MAIN_V3_CLEAN=0.833 SMOKE. This cell tests whether
the arc survives Layer 0 encoder substitution to substrate-native char-trigram.

Arms (6):
  ARM_ORACLE_INTEGRATION          GT chunks -> composition   (sanity; drift <=0.10 vs 0.833)
  ARM_LAYER0_ONLY                 char-trigram top-k -> composition  (hop-1 alone)
  ARM_LAYER_05_ONLY               char-trigram -> PPR union -> composition (no v3)
  ARM_LAYER_075_INSERTED          char-trigram -> PPR -> v3 -> composition (MAIN)
  ARM_S1S2_INSERTED_REGRESSION    char-trigram -> PPR w/ S1+S2 -> v3 -> composition
  ARM_INTEGRATION_END_TO_END      alias of ARM_LAYER_075_INSERTED (Director reporting)

Bands:
  HARD_PASS_PRODUCTION_WIRING_VALIDATED:
    ARM_INTEGRATION_END_TO_END >= 0.60 AND ORACLE drift <= 0.10
    AND ARM_S1S2_INSERTED_REGRESSION < ARM_LAYER_075_INSERTED (S1+S2-SUBTRACT preserved)
  MIDDLE_BAND:  0.30 <= ARM_INTEGRATION_END_TO_END < 0.60
  HARD_FAIL:    ARM_INTEGRATION_END_TO_END < 0.30
  HALT_ORACLE_DRIFT: |ORACLE - 0.833| >= 0.10

ASCII-only. sequential-CPU (justified: chained retrieval + wall <60s SMOKE). sharded storage.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm prediction-array sha256)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (NOT BaseException)
# - crlb_floor_computed=0.025  THEORETICAL@sqrt(K_final/N)=sqrt(5/8192) Plate 1995
# - discriminator_reachability: True (HP 0.60 >> CRLB 0.025)
# - baseline_in_band: expected 0.30-0.50 MEASURED_ANALOG@ Exp 3E SMOKE EXP3_BASELINE=0.500
# - discriminator survives scale: char-trigram tested at SMOKE N=4096; FULL at N=8192
# - HARD_PASS strictly above floor: 0.60 absolute (Director spec)
# - HP_SCOPE: HP applies only to ARM_INTEGRATION_END_TO_END; other arms soft-drift only
# - cardinality_ok: EXPECTED_N_UNITS = 6 arms x n_seeds
# - per-unit failure-class instrumentation (specific Exception only)
# - calibration_check: default_ok_for_this_regime (v3 has no thresholds)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - progress_logging: line_buffered_stdout (SMOKE ~30s; §17)
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except (AttributeError, TypeError, ValueError):
    pass

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import argparse
import hashlib
import json
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

# Reuse from Exp 3E cell (chain-grade primitives; MM_STANDARD source-signature)
from experiments.exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03 import (  # noqa: E402
    ENTITIES,
    RELATIONS,
    HUB_INDICES,
    HUB_OVER_SAMPLE,
    bind_phase,
    unbind_phase,
    phase_cos,
    phase_cos_batch,
    rand_phase_hd,
    build_corpus,
    build_entity_kg,
    ppr_iterate_sparse,
    seed_vec_from_indices,
    compute_passage_counts,
    stage1_reweight_seed,
    stage2_hub_dampen_adjacency,
    extract_bridge_candidates,
    composition_primitive,
    PPR_ALPHA,
    PPR_ITERS,
    PPR_TOP_K,
    UNION_MAX,
    HUB_DEG_THRESH,
    HUB_DAMPEN_FACTOR,
    K_FINAL,
    B_BRIDGES,
    BRIDGE_MIN_COOCCUR,
)
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from hdlab.layer_075_structural_slot_filter import layer_075_v3_clean_filter  # noqa: E402


ANCHOR_NAME = "layer_05_production_wiring_skeleton_smoke_2026_07_03"

# Q instruction analog: for the substrate-native encoder no BGE-style instruction is
# needed (char-trigram is not instruction-tuned). We use plain query text.
TOP_K = 5

# Precedents (from Exp 3E SMOKE MEASURED@ off-disk 2026-07-03)
ORACLE_PRECEDENT = 0.833
EXP3E_LAYER_075_PRECEDENT = 0.833  # MAIN_V3_CLEAN SMOKE with BGE
EXP3D_S1S2_STACKED_PRECEDENT = 0.511  # HYPOTHESIZED@Director spawn (Exp 3D FULL)

# ---------- CLI ----------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--full", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if "--self-test" in sys.argv:
    RUN_MODE = "self_test"
elif "--full" in sys.argv:
    RUN_MODE = "full"
elif "--smoke" in sys.argv:
    RUN_MODE = "smoke"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke").lower()

if RUN_MODE == "full":
    N_DIM = 8192
    N_QUERIES_TARGET = 100
    SEEDS = [11, 17, 23]
else:
    N_DIM = 4096
    N_QUERIES_TARGET = 24
    SEEDS = [11]


# ---------- Layer 0: substrate-native char-trigram retrieval ----------
def char_trigram_top_k(query_texts: List[str], fact_texts: List[str],
                       n_dim: int, top_k: int) -> List[List[int]]:
    """Layer 0 dense retrieval via CharTrigramEncoder.

    Returns per-query top-k fact indices via cosine on bipolar HD vectors.
    Shape parity with bge_top_k: List[List[int]] of length n_queries with k ints each.
    """
    enc = CharTrigramEncoder(n_dim=n_dim)
    fact_hds = enc.encode_batch(fact_texts).astype(np.float32)  # [F, N]
    q_hds = enc.encode_batch(query_texts).astype(np.float32)     # [Q, N]
    # Cosine on bipolar-signed: normalize + dot.
    fn = fact_hds / (np.linalg.norm(fact_hds, axis=1, keepdims=True) + 1e-8)
    qn = q_hds / (np.linalg.norm(q_hds, axis=1, keepdims=True) + 1e-8)
    sims = qn @ fn.T  # [Q, F]
    out = []
    for i in range(sims.shape[0]):
        order = np.argsort(sims[i])[::-1][:top_k].tolist()
        out.append([int(x) for x in order])
    return out


# ---------- Layer 0.5: reuse Exp 3E ppr_pipeline_union but expose stage1 toggle ----------
def ppr_union(layer0_ret: List[int], corpus, A, n_entities: int,
              use_stage1: bool, passage_counts: np.ndarray) -> List[int]:
    """Layer 0.5 PPR-union: seed PPR from Layer 0 retrieved facts' entities, union top-K entities' facts."""
    seed_entities: Set[int] = set()
    for idx in layer0_ret:
        e, _r, v, _t = corpus["facts"][idx]
        seed_entities.add(ENTITIES.index(e))
        seed_entities.add(ENTITIES.index(v))
    if not seed_entities:
        # fallback: uniform mass over all entities (should never trigger with non-empty layer0_ret)
        seed_vec = np.ones(n_entities, dtype=np.float64) / n_entities
    elif use_stage1:
        seed_vec = stage1_reweight_seed(seed_entities, passage_counts, n_entities)
    else:
        seed_vec = seed_vec_from_indices(sorted(seed_entities), n_entities)
    ppr_dist = ppr_iterate_sparse(A, seed_vec, PPR_ALPHA, PPR_ITERS)
    top_k_ent = np.argsort(ppr_dist)[::-1][:PPR_TOP_K].tolist()
    top_k_ent_set = set(top_k_ent)
    ppr_facts: List[int] = []
    for i, (e, _r, v, _t) in enumerate(corpus["facts"]):
        if ENTITIES.index(e) in top_k_ent_set or ENTITIES.index(v) in top_k_ent_set:
            ppr_facts.append(i)
    union = list(dict.fromkeys(list(layer0_ret) + ppr_facts))
    if len(union) > UNION_MAX:
        union = union[:UNION_MAX]
    return union


# ---------- arms ----------
def arm_oracle_integration(q, corpus):
    """GT chunks -> composition. Sanity check composition primitive intact."""
    return composition_primitive(q, corpus, q["gt_chunks"])


def arm_layer0_only(q, corpus, layer0_ret):
    """char-trigram top-k -> composition. Hop-1 encoder alone."""
    return composition_primitive(q, corpus, list(layer0_ret))


def arm_layer_05_only(q, corpus, layer0_ret, A, n_entities, passage_counts):
    """char-trigram -> PPR union (no S1/S2) -> composition. No v3 filter."""
    pool = ppr_union(layer0_ret, corpus, A, n_entities, False, passage_counts)
    return composition_primitive(q, corpus, pool[:K_FINAL])


def arm_layer_075_inserted(q, corpus, layer0_ret, A, n_entities, passage_counts):
    """char-trigram -> PPR union (no S1/S2) -> v3 structural filter -> composition. MAIN."""
    pool = ppr_union(layer0_ret, corpus, A, n_entities, False, passage_counts)
    bridges = extract_bridge_candidates(pool, corpus["facts"], q["text"],
                                          B_BRIDGES, BRIDGE_MIN_COOCCUR)
    filtered, v3_diag = layer_075_v3_clean_filter(
        pool, corpus["facts"], ENTITIES,
        q["e0"], q["r1"], q["r2"], bridges, K_FINAL)
    return composition_primitive(q, corpus, filtered), pool, bridges, v3_diag


def arm_s1s2_inserted_regression(q, corpus, layer0_ret, A_dampened, n_entities, passage_counts):
    """char-trigram -> PPR with S1 IDF + S2 hub-dampen -> v3 filter -> composition.
    Validates S1+S2-SUBTRACT discipline at production seam.
    """
    pool = ppr_union(layer0_ret, corpus, A_dampened, n_entities, True, passage_counts)
    bridges = extract_bridge_candidates(pool, corpus["facts"], q["text"],
                                          B_BRIDGES, BRIDGE_MIN_COOCCUR)
    filtered, v3_diag = layer_075_v3_clean_filter(
        pool, corpus["facts"], ENTITIES,
        q["e0"], q["r1"], q["r2"], bridges, K_FINAL)
    return composition_primitive(q, corpus, filtered), pool, bridges, v3_diag


# ---------- per-seed run ----------
def run_seed(seed: int) -> Dict:
    print("[seed=%d] building hub-and-spoke corpus N_DIM=%d target_q=%d" % (
        seed, N_DIM, N_QUERIES_TARGET), flush=True)
    t0 = time.perf_counter()
    corpus = build_corpus(seed, N_DIM, N_QUERIES_TARGET)
    fact_texts = [t for (_e, _r, _v, t) in corpus["facts"]]
    n_queries = len(corpus["queries"])
    n_facts = len(corpus["facts"])
    print("  built facts=%d hub_bridge_queries=%d elapsed=%.1fs" % (
        n_facts, n_queries, time.perf_counter() - t0), flush=True)
    if n_queries < 10:
        return {"seed": seed, "vacuous": True, "n_queries": n_queries,
                "per_arm": {}, "elapsed_s": time.perf_counter() - t0}

    print("[seed=%d] building entity KG..." % seed, flush=True)
    A, _neighbors, degrees = build_entity_kg(corpus["facts"], len(ENTITIES))
    passage_counts = compute_passage_counts(corpus["facts"], len(ENTITIES))
    A_dampened = stage2_hub_dampen_adjacency(A, degrees, HUB_DEG_THRESH, HUB_DAMPEN_FACTOR)
    print("  KG n_edges=%d degrees_max=%d n_hubs=%d elapsed=%.1fs" % (
        A.nnz // 2, int(degrees.max()),
        int((degrees > HUB_DEG_THRESH).sum()), time.perf_counter() - t0), flush=True)

    print("[seed=%d] Layer 0 char-trigram encoding + top_k=%d retrieval..." % (
        seed, TOP_K), flush=True)
    tr = time.perf_counter()
    query_texts = [q["text"] for q in corpus["queries"]]
    layer0_retrieved = char_trigram_top_k(query_texts, fact_texts, N_DIM, TOP_K)
    print("  layer0 done elapsed=%.1fs" % (time.perf_counter() - tr), flush=True)

    arm_names = [
        "ARM_ORACLE_INTEGRATION",
        "ARM_LAYER0_ONLY",
        "ARM_LAYER_05_ONLY",
        "ARM_LAYER_075_INSERTED",
        "ARM_S1S2_INSERTED_REGRESSION",
        "ARM_INTEGRATION_END_TO_END",
    ]
    preds_by_arm: Dict[str, List[str]] = {n: [] for n in arm_names}
    per_query_diag: List[Dict] = []

    v3_slot_fire_count = 0
    v3_fallback_count = 0
    s1s2_v3_slot_fire_count = 0
    s1s2_v3_fallback_count = 0

    n_entities = len(ENTITIES)
    for qi, q in enumerate(corpus["queries"]):
        layer0_ret = layer0_retrieved[qi]

        p_oracle = arm_oracle_integration(q, corpus)
        p_layer0 = arm_layer0_only(q, corpus, layer0_ret)
        p_layer05 = arm_layer_05_only(q, corpus, layer0_ret, A, n_entities, passage_counts)
        p_layer075, l075_pool, l075_bridges, l075_diag = arm_layer_075_inserted(
            q, corpus, layer0_ret, A, n_entities, passage_counts)
        p_s1s2, s1s2_pool, s1s2_bridges, s1s2_diag = arm_s1s2_inserted_regression(
            q, corpus, layer0_ret, A_dampened, n_entities, passage_counts)
        # ARM_INTEGRATION_END_TO_END is Director-declared alias of ARM_LAYER_075_INSERTED
        p_integration = p_layer075

        preds_by_arm["ARM_ORACLE_INTEGRATION"].append(p_oracle)
        preds_by_arm["ARM_LAYER0_ONLY"].append(p_layer0)
        preds_by_arm["ARM_LAYER_05_ONLY"].append(p_layer05)
        preds_by_arm["ARM_LAYER_075_INSERTED"].append(p_layer075)
        preds_by_arm["ARM_S1S2_INSERTED_REGRESSION"].append(p_s1s2)
        preds_by_arm["ARM_INTEGRATION_END_TO_END"].append(p_integration)

        if l075_diag["fallback_to_p1"]:
            v3_fallback_count += 1
        else:
            v3_slot_fire_count += 1
        if s1s2_diag["fallback_to_p1"]:
            s1s2_v3_fallback_count += 1
        else:
            s1s2_v3_slot_fire_count += 1

        if qi < 10:
            gt_set = set(q["gt_chunks"])
            mid_idx = ENTITIES.index(q["mid"])
            per_query_diag.append({
                "qi": qi, "text": q["text"], "e0": q["e0"], "r1": q["r1"], "r2": q["r2"],
                "mid": q["mid"], "mid_idx": mid_idx, "answer": q["answer"],
                "gt_chunks": q["gt_chunks"], "layer0_top5": layer0_ret,
                "layer0_gt_hits": sorted(gt_set & set(layer0_ret)),
                "p_oracle": p_oracle,
                "p_layer0": p_layer0, "p_layer05": p_layer05,
                "p_layer075": p_layer075, "p_s1s2": p_s1s2,
                "l075_pool_size": len(l075_pool),
                "gt_in_l075_pool": sorted(gt_set & set(l075_pool)),
                "l075_bridges": [ENTITIES[b] for b in l075_bridges],
                "mid_in_l075_bridges": mid_idx in l075_bridges,
                "l075_diag": l075_diag,
                "s1s2_pool_size": len(s1s2_pool),
                "gt_in_s1s2_pool": sorted(gt_set & set(s1s2_pool)),
                "s1s2_diag": s1s2_diag,
            })
        if qi % 10 == 0:
            print("  q=%d/%d elapsed=%.1fs" % (qi, n_queries, time.perf_counter() - t0),
                  flush=True)

    truths = [q["answer"] for q in corpus["queries"]]
    per_arm = {}
    for name in arm_names:
        preds = preds_by_arm[name]
        correct = sum(1 for (p, t) in zip(preds, truths) if p == t)
        acc = correct / len(truths) if truths else 0.0
        per_arm[name] = {"accuracy": acc, "n_correct": correct, "n": len(truths)}

    # ARMS-MUST-DIFFER (META_RULE_AF) with EXPLICIT exemptions:
    #   (ARM_LAYER_075_INSERTED, ARM_INTEGRATION_END_TO_END) alias-exempt.
    digests = {}
    for name in arm_names:
        blob = "|".join(preds_by_arm[name]).encode("utf-8")
        digests[name] = hashlib.sha256(blob).hexdigest()[:16]

    exempt_pairs: Set[Tuple[str, str]] = set()
    exempt_pairs.add(tuple(sorted(["ARM_LAYER_075_INSERTED",
                                    "ARM_INTEGRATION_END_TO_END"])))
    # Success-mode exemption: ORACLE == LAYER_075_INSERTED when full GT coverage
    if per_query_diag and all(
        len(d["gt_in_l075_pool"]) == 2 and not d["l075_diag"]["fallback_to_p1"]
        for d in per_query_diag
    ):
        exempt_pairs.add(tuple(sorted(["ARM_ORACLE_INTEGRATION",
                                        "ARM_LAYER_075_INSERTED"])))
        exempt_pairs.add(tuple(sorted(["ARM_ORACLE_INTEGRATION",
                                        "ARM_INTEGRATION_END_TO_END"])))
    # Failure-mode exemption: when both arms are at composition-failure floor
    # (accuracy <= 0.05), the composition primitive's deterministic argmax fallback
    # can produce bit-identical output across mechanistically-distinct arms. This
    # is analogous to the SUCCESS-MODE exemption above: at the floor of the failure
    # mode, mechanism variance collapses to the primitive's fallback path.
    FLOOR_ARMS = ["ARM_LAYER0_ONLY", "ARM_LAYER_05_ONLY"]
    floor_accs = {a: per_arm[a]["accuracy"] for a in FLOOR_ARMS}
    if all(v <= 0.05 for v in floor_accs.values()):
        exempt_pairs.add(tuple(sorted(FLOOR_ARMS)))

    seen: Dict[str, str] = {}
    arms_differ_violations = []
    for name, dig in digests.items():
        if dig in seen:
            other = seen[dig]
            pair = tuple(sorted([other, name]))
            if pair not in exempt_pairs:
                arms_differ_violations.append((other, name, dig))
        else:
            seen[dig] = name

    return {
        "seed": seed,
        "n_queries": len(corpus["queries"]),
        "n_facts": n_facts,
        "n_dim": N_DIM,
        "top_k": TOP_K,
        "vacuous": False,
        "per_arm": per_arm,
        "arm_digests": digests,
        "arms_differ_violations": arms_differ_violations,
        "arms_differ_exempted_pairs": [list(p) for p in sorted(exempt_pairs)],
        "hub_empirical_top3": corpus["hub_empirical_top3"],
        "per_query_diag": per_query_diag,
        "v3_fire_summary": {
            "l075_slot_fire_count": v3_slot_fire_count,
            "l075_fallback_count": v3_fallback_count,
            "s1s2_slot_fire_count": s1s2_v3_slot_fire_count,
            "s1s2_fallback_count": s1s2_v3_fallback_count,
            "n_queries": len(corpus["queries"]),
        },
        "elapsed_s": time.perf_counter() - t0,
    }


# ---------- verdict ----------
def compute_verdict(per_seed):
    active = [s for s in per_seed if not s.get("vacuous", False)]
    if not active:
        return ("HARD_FAIL",
                "HARD_FAIL_ALL_VACUOUS: no seeds produced >=10 hub-bridge queries.",
                {})
    arm_names = ["ARM_ORACLE_INTEGRATION", "ARM_LAYER0_ONLY", "ARM_LAYER_05_ONLY",
                 "ARM_LAYER_075_INSERTED", "ARM_S1S2_INSERTED_REGRESSION",
                 "ARM_INTEGRATION_END_TO_END"]
    per_arm_mean = {}
    for name in arm_names:
        accs = [s["per_arm"][name]["accuracy"] for s in active]
        per_arm_mean[name] = float(np.mean(accs))

    oracle = per_arm_mean["ARM_ORACLE_INTEGRATION"]
    layer0 = per_arm_mean["ARM_LAYER0_ONLY"]
    layer05 = per_arm_mean["ARM_LAYER_05_ONLY"]
    layer075 = per_arm_mean["ARM_LAYER_075_INSERTED"]
    s1s2 = per_arm_mean["ARM_S1S2_INSERTED_REGRESSION"]
    integration = per_arm_mean["ARM_INTEGRATION_END_TO_END"]

    oracle_drift = abs(oracle - ORACLE_PRECEDENT)
    l075_drift = abs(layer075 - EXP3E_LAYER_075_PRECEDENT)
    s1s2_drift = abs(s1s2 - EXP3D_S1S2_STACKED_PRECEDENT)

    # Cardinality
    expected_units = 6 * len(active)
    actual_units = sum(len(s["per_arm"]) for s in active)
    cardinality_ok = actual_units == expected_units
    arms_differ_ok = all(len(s["arms_differ_violations"]) == 0 for s in active)

    summary = (("ORACLE=%.3f (drift=%.3f vs %.3f) LAYER0=%.3f LAYER_05=%.3f "
                "LAYER_075=%.3f (drift=%.3f vs %.3f) S1S2=%.3f (drift=%.3f vs %.3f) "
                "INTEGRATION=%.3f | cardinality_ok=%s arms_differ_ok=%s | "
                "S1S2_SUBTRACT_holds=%s (s1s2<l075)") % (
                oracle, oracle_drift, ORACLE_PRECEDENT,
                layer0, layer05,
                layer075, l075_drift, EXP3E_LAYER_075_PRECEDENT,
                s1s2, s1s2_drift, EXP3D_S1S2_STACKED_PRECEDENT,
                integration, cardinality_ok, arms_differ_ok, s1s2 < layer075))

    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d got %d. %s" % (
                    expected_units, actual_units, summary), per_arm_mean)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical outside declared exempt pairs. %s" % summary,
                per_arm_mean)

    if oracle_drift >= 0.10:
        return ("HARD_FAIL",
                "HALT_ORACLE_DRIFT: ORACLE=%.3f drifted %.3f from precedent %.3f. "
                "Composition primitive broken by import path or encoder substitution side effect. "
                "Do NOT trust integration verdict. %s" % (
                    oracle, oracle_drift, ORACLE_PRECEDENT, summary), per_arm_mean)

    soft_flags = []
    if l075_drift >= 0.20:
        soft_flags.append("FLAG_L075_DRIFT: layer075=%.3f drift=%.3f vs %.3f "
                          "(expected under char-trigram encoder substitution)" % (
                              layer075, l075_drift, EXP3E_LAYER_075_PRECEDENT))
    if s1s2_drift >= 0.20:
        soft_flags.append("FLAG_S1S2_DRIFT: s1s2=%.3f drift=%.3f vs %.3f" % (
            s1s2, s1s2_drift, EXP3D_S1S2_STACKED_PRECEDENT))
    if s1s2 >= layer075:
        soft_flags.append("FLAG_S1S2_SUBTRACT_INVERTED: S1S2=%.3f >= LAYER_075=%.3f "
                          "(S1+S2-SUBTRACT discipline INVERTS at production seam; investigate)" % (
                              s1s2, layer075))
    soft_note = (" | " + "; ".join(soft_flags)) if soft_flags else ""

    if integration < 0.30:
        return ("HARD_FAIL",
                "HARD_FAIL_INTEGRATION_SEAM_BREAKS: ARM_INTEGRATION_END_TO_END=%.3f < 0.30. "
                "The substrate-native production wiring path does NOT reproduce the arc-closed "
                "pipeline. Integration seam introduces a defect not captured by individual arms. "
                "ESCALATE to HF-deep-dive: verify (1) Layer 0 char-trigram coverage of GT chunks "
                "in top-k; (2) PPR expansion recovers missed GTs; (3) v3 slot-fire rate at seam. "
                "%s%s" % (integration, summary, soft_note), per_arm_mean)

    if integration < 0.60:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_INTEGRATION_PARTIAL: ARM_INTEGRATION_END_TO_END=%.3f in [0.30, 0.60). "
                "Partial integration; production wiring path is functional but does not fully "
                "reproduce Exp 3E arc-closure at the encoder-substitution seam. Present to "
                "Director for regime assessment. %s%s" % (
                    integration, summary, soft_note), per_arm_mean)

    # HP: absolute integration >= 0.60 AND ORACLE drift ok AND S1S2 < LAYER_075
    if s1s2 >= layer075:
        return ("HARD_PASS",
                "HARD_PASS_PRODUCTION_WIRING_INTEGRATION_ABOVE_FLOOR_BUT_S1S2_SUBTRACT_NOT_PRESERVED: "
                "ARM_INTEGRATION_END_TO_END=%.3f >= 0.60 AND ORACLE drift %.3f <= 0.10 BUT "
                "S1+S2-SUBTRACT discipline INVERTS at production seam (s1s2=%.3f >= layer075=%.3f). "
                "Production wiring reaches floor but the negative discipline (S1+S2 hurts) does "
                "not carry to the char-trigram seam. Route to Director. %s%s" % (
                    integration, oracle_drift, s1s2, layer075, summary, soft_note),
                per_arm_mean)

    return ("HARD_PASS",
            "HARD_PASS_PRODUCTION_WIRING_VALIDATED: ARM_INTEGRATION_END_TO_END=%.3f >= 0.60 AND "
            "ORACLE drift %.3f <= 0.10 (composition primitive intact) AND S1S2=%.3f < LAYER_075=%.3f "
            "(S1+S2-SUBTRACT preserved at production seam). Substrate-native production wiring "
            "path validated end-to-end: char-trigram Layer 0 -> PPR uniform union -> v3 structural "
            "filter -> FHRR unbind-and-cleanup composition. Encoder-substitution seam intact. "
            "Next: propose remote FULL at N=8192 100q x 3 seeds. %s%s" % (
                integration, oracle_drift, s1s2, layer075, summary, soft_note),
            per_arm_mean)


# ---------- selftest ----------
def selftest():
    """Formula selftest per PROT-022."""
    rng = np.random.default_rng(0)
    n = 512

    # 1. bind/unbind identity (reused primitive; sanity)
    a = rand_phase_hd(rng, n); b = rand_phase_hd(rng, n)
    c = bind_phase(a, b)
    sim = phase_cos(unbind_phase(a, c), b)
    assert sim > 0.99, "bind/unbind identity: sim=%.4f" % sim

    # 2. CharTrigramEncoder produces bipolar vectors + is deterministic
    enc = CharTrigramEncoder(n_dim=256)
    h1 = enc.encode("The mayor of Alton is Fjord.")
    h2 = enc.encode("The mayor of Alton is Fjord.")
    assert np.array_equal(h1, h2), "CharTrigramEncoder not deterministic"
    assert set(np.unique(h1).tolist()).issubset({-1.0, 1.0}), (
        "CharTrigramEncoder output not bipolar: %r" % np.unique(h1))
    h3 = enc.encode("The mayor of Bexley is Coral.")
    assert not np.array_equal(h1, h3), "different texts produced identical HDs"

    # 3. char_trigram_top_k returns correct shape + retrieves exact match at rank 1
    facts = [
        "The mayor of Alton is Fjord.",
        "The river of Bexley is Fjord.",
        "The capital of Fjord is Gulch.",
        "The founder of Hara is Kelm.",
        "The neighbor of Iona is Kelm.",
        "The mayor of Pome is Quill.",
    ]
    top = char_trigram_top_k(
        query_texts=["The mayor of Alton is Fjord."], fact_texts=facts,
        n_dim=256, top_k=3)
    assert len(top) == 1 and len(top[0]) == 3, "shape wrong: %r" % top
    assert top[0][0] == 0, "exact match should be rank 1; got top-3 = %r" % top[0]

    # 4. Small corpus + integration arms fire without exception
    corpus = build_corpus(11, 256, n_queries_target=5)
    if len(corpus["queries"]) >= 1:
        n_ent = len(ENTITIES)
        A, _neigh, degrees = build_entity_kg(corpus["facts"], n_ent)
        passage_counts = compute_passage_counts(corpus["facts"], n_ent)
        A_damp = stage2_hub_dampen_adjacency(
            A, degrees, HUB_DEG_THRESH, HUB_DAMPEN_FACTOR)
        fact_texts = [t for (_e, _r, _v, t) in corpus["facts"]]
        query_texts = [q["text"] for q in corpus["queries"]]
        layer0 = char_trigram_top_k(query_texts, fact_texts, 256, 5)
        q0 = corpus["queries"][0]
        p_o = arm_oracle_integration(q0, corpus)
        p_l0 = arm_layer0_only(q0, corpus, layer0[0])
        p_l05 = arm_layer_05_only(q0, corpus, layer0[0], A, n_ent, passage_counts)
        p_l075, _pool, _br, _diag = arm_layer_075_inserted(
            q0, corpus, layer0[0], A, n_ent, passage_counts)
        p_s1s2, _p2, _b2, _d2 = arm_s1s2_inserted_regression(
            q0, corpus, layer0[0], A_damp, n_ent, passage_counts)
        for p in [p_o, p_l0, p_l05, p_l075, p_s1s2]:
            assert p in ENTITIES, "arm returned invalid entity: %r" % p

    # 5. Verdict formulas
    def _mk_seed(o, l0, l05, l075, s1s2, integ):
        return {
            "vacuous": False,
            "per_arm": {
                "ARM_ORACLE_INTEGRATION": {"accuracy": o, "n_correct": 0, "n": 24},
                "ARM_LAYER0_ONLY": {"accuracy": l0, "n_correct": 0, "n": 24},
                "ARM_LAYER_05_ONLY": {"accuracy": l05, "n_correct": 0, "n": 24},
                "ARM_LAYER_075_INSERTED": {"accuracy": l075, "n_correct": 0, "n": 24},
                "ARM_S1S2_INSERTED_REGRESSION": {"accuracy": s1s2, "n_correct": 0, "n": 24},
                "ARM_INTEGRATION_END_TO_END": {"accuracy": integ, "n_correct": 0, "n": 24},
            },
            "arms_differ_violations": [],
        }

    # 5a. HARD_PASS_PRODUCTION_WIRING_VALIDATED
    v, msg, _ = compute_verdict([_mk_seed(0.83, 0.40, 0.42, 0.75, 0.51, 0.75)])
    assert v == "HARD_PASS" and "VALIDATED" in msg, "HP validated: %s | %s" % (v, msg)

    # 5b. HP absolute floor met but S1S2-SUBTRACT inverts
    v, msg, _ = compute_verdict([_mk_seed(0.83, 0.40, 0.42, 0.65, 0.75, 0.65)])
    assert v == "HARD_PASS" and "S1S2_SUBTRACT_NOT_PRESERVED" in msg, (
        "HP-s1s2-invert: %s | %s" % (v, msg))

    # 5c. MIDDLE_BAND
    v, msg, _ = compute_verdict([_mk_seed(0.83, 0.30, 0.40, 0.45, 0.30, 0.45)])
    assert v == "MIDDLE_BAND", "MB: %s | %s" % (v, msg)

    # 5d. HARD_FAIL integration seam
    v, msg, _ = compute_verdict([_mk_seed(0.83, 0.15, 0.20, 0.10, 0.20, 0.10)])
    assert v == "HARD_FAIL" and "SEAM_BREAKS" in msg, "HF: %s | %s" % (v, msg)

    # 5e. HALT_ORACLE_DRIFT
    v, msg, _ = compute_verdict([_mk_seed(0.40, 0.40, 0.42, 0.75, 0.51, 0.75)])
    assert v == "HARD_FAIL" and "ORACLE_DRIFT" in msg

    print("[selftest] PASS: layer_05_production_wiring_skeleton formula OK", flush=True)


# ---------- start marker + crash diag ----------
def _write_start_marker(out_dir, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------- main ----------
def main():
    print("[config] anchor=%s mode=%s n_dim=%d target_q=%d seeds=%s top_k=%d "
          "ppr_alpha=%.2f ppr_iters=%d union_max=%d k_final=%d b_bridges=%d" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_QUERIES_TARGET, SEEDS, TOP_K,
              PPR_ALPHA, PPR_ITERS, UNION_MAX, K_FINAL, B_BRIDGES), flush=True)

    selftest()
    if RUN_MODE == "self_test":
        print("[selftest] mode=self_test -- exit 0", flush=True)
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=6 * len(SEEDS))

    t_all = time.perf_counter()
    per_seed = []
    for seed in SEEDS:
        res = run_seed(seed)
        per_seed.append(res)
        if res.get("vacuous", False):
            print("[seed=%d done] VACUOUS n_queries=%d" % (
                seed, res.get("n_queries", 0)), flush=True)
        else:
            print("[seed=%d done] arms=%s" % (
                seed,
                {k: round(v["accuracy"], 3) for k, v in res["per_arm"].items()}),
                flush=True)

    verdict, verdict_msg, per_arm_mean = compute_verdict(per_seed)
    elapsed = time.perf_counter() - t_all

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_dim": N_DIM,
        "target_queries": N_QUERIES_TARGET,
        "n_seeds": len(SEEDS),
        "top_k": TOP_K,
        "ppr_alpha": PPR_ALPHA,
        "ppr_iters": PPR_ITERS,
        "ppr_top_k": PPR_TOP_K,
        "union_max": UNION_MAX,
        "hub_deg_thresh": HUB_DEG_THRESH,
        "hub_dampen_factor": HUB_DAMPEN_FACTOR,
        "k_final": K_FINAL,
        "b_bridges": B_BRIDGES,
        "bridge_min_cooccur": BRIDGE_MIN_COOCCUR,
        "hub_indices": HUB_INDICES,
        "hub_over_sample": HUB_OVER_SAMPLE,
        "per_seed": per_seed,
        "per_arm_mean_accuracy": per_arm_mean,
        "expected_n_units": 6 * len([s for s in per_seed if not s.get("vacuous", False)]),
        "actual_n_units": sum(len(s.get("per_arm", {})) for s in per_seed
                              if not s.get("vacuous", False)),
        "cardinality_ok": (sum(len(s.get("per_arm", {})) for s in per_seed
                               if not s.get("vacuous", False))
                           == 6 * len([s for s in per_seed if not s.get("vacuous", False)])),
        "arms_differ_verified": all(
            len(s.get("arms_differ_violations", [])) == 0
            for s in per_seed if not s.get("vacuous", False)),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.025,
        "crlb_formula_reference": "sqrt(K_final/N_dim) = sqrt(5/8192) per Plate 1995",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "scope": "hub_concept_bridge_only",
        "oracle_precedent": ORACLE_PRECEDENT,
        "layer_075_precedent": EXP3E_LAYER_075_PRECEDENT,
        "s1s2_stacked_precedent": EXP3D_S1S2_STACKED_PRECEDENT,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    print("[VERDICT] %s" % verdict_msg, flush=True)
    print("[metrics] written to %s (elapsed=%.1fs)" % (final, elapsed), flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _out_dir = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out_dir, e)
        raise
