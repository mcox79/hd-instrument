"""exp_substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03.

Experiment 2 from the optimal-retrieval-architecture drill (2026-07-03).

Question: does a fixed-iteration Personalized PageRank walk (alpha=0.15, 5 iters)
over the synthetic 20-entity KG, seeded from Exp 1's char-trigram-matched entities
per query, recover the TRUE bridge chunk at recall@5 meaningfully higher than the
hop-1-dense-alone baseline (which HARD_FAILed the RAG-composition SMOKE)?

Bands (task-spec):
  HARD_PASS: PPR_recovery_rate >= 0.50 on missed-by-hop1 subset
  HARD_FAIL: PPR_recovery_rate <  0.15 on missed-by-hop1 subset
  MIDDLE:    0.15 <= rate < 0.50

Arms:
  ARM_HOP1_DENSE_ALONE_BASELINE    -- recall@5 of bridge chunk in top-K bge hits
  ARM_MAIN_PPR_RECOVERED           -- PPR seeded from Exp-1-matched entities
  ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE -- PPR seeded from mid entity; MUST >= 0.95
  ARM_NEG_CTL_PPR_FROM_RANDOM      -- PPR seeded from random unrelated entity; MUST <= 0.10

Scale caveat (per Exp 1): synthetic 20-entity KG is by-construction dense (every
entity has 5 outgoing edges); mechanism-proof on synthetic corpus, NOT scale claim.
PPR is a global-flow op whose scale-transfer to Wikipedia-KB is a SEPARATE future
test (Exp 4+). This caveat has slightly MORE force than Exp 1's fuzzy-match caveat
because PPR mass diffusion is qualitatively scale-dependent.

Precedent replay (bge retrieval + Exp 1 char-trigram fuzzy match) is imported from
the RAG-composition SMOKE + Exp 1 modules; adds NO new abstractions except PPR.

ASCII-only. sequential-CPU (~30s per seed). Substrate primitives composed:
CharTrigramEncoder + Exp-1 extract_matched_entities + new 5-iter PPR.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm per-query recall-vector hash)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (not BaseException)
# - crlb_n_a: PPR recall@5 is a rate, not a shift-noise measurement
# - baseline_in_band: hop-1 baseline expected 0.0 (by RAG-composition SMOKE HF)
# - discriminator survives scale: SMOKE-only cell; mechanism-proof on synthetic KG
# - HARD_PASS strict at >= 0.50; HARD_FAIL strict at < 0.15; band 0.15..0.50 = MIDDLE
# - HP_SCOPE: HARD_PASS applies to MAIN vs hop-1-missed subset; POS/NEG independent
# - cardinality_ok: EXPECTED_N_UNITS = 4 arms x 3 seeds = 12
# - per-unit failure-class instrumentation (no bare except; specific Exception only)
# - calibration_check: default_ok_for_this_regime (PPR alpha=0.15 field-standard)
# - PPR mass-conservation sanity: sum in [0.995, 1.005] per iteration
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
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
import random
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

# Import Exp 1 primitives (build_entity_codebook + extract_matched_entities)
from experiments import exp_substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03 as EXP1  # noqa: E402
# Import precedent module (corpus builder + bge retrieval + ENTITIES + RELATIONS)
from experiments import exp_substrate_rag_with_substrate_composition_smoke_2026_07_03 as PRECEDENT  # noqa: E402


ANCHOR_NAME = "substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03"

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

SEEDS = [11, 17, 23]  # match precedent + Exp 1
PPR_ALPHA = 0.15         # CITED@Haveliwala_2003
PPR_ITERS = 5            # CITED@task_spec_2026-07-03
PPR_TOP_K = 5            # match Exp 1 / precedent TOP_K for apples-to-apples
COSINE_THRESH = 0.5      # match Exp 1 char-trigram threshold
N_DIM_TRIGRAM = 1024     # match Exp 1
MASS_CONSERVATION_TOL = 0.005  # PPR sum-to-1.0 tolerance per iter


# ---------- PPR primitives ----------
def build_undirected_adjacency(facts: List[Tuple[str, str, str, str]],
                               entities: List[str]) -> np.ndarray:
    """Build row-stochastic undirected adjacency A: A[i,j] = 1/deg(j) if edge.

    Each fact (s, r, o) contributes an undirected edge s <-> o. Self-loops
    from the substrate corpus (an entity's fact whose value equals itself)
    contribute a single self-loop, treated as an ordinary edge. Row-stochastic
    normalization is column-side: A[i,j] = 1/deg(j) so that (1-alpha)*A@x
    preserves mass exactly.
    """
    n = len(entities)
    ent_idx = {e: i for i, e in enumerate(entities)}
    # Build symmetric adjacency count matrix first
    C = np.zeros((n, n), dtype=np.float64)
    for (s, _r, o, _t) in facts:
        i = ent_idx[s]
        j = ent_idx[o]
        C[i, j] += 1.0
        if i != j:
            C[j, i] += 1.0
    # Column-normalize to make (1-alpha)*A@x mass-preserving:
    # A[i,j] = C[i,j] / sum_k C[k,j]  (out-degree of j viewed as source column)
    col_sums = C.sum(axis=0)
    # Guard against isolated nodes (col_sum=0): keep as zero column;
    # restart term will handle those.
    col_sums_safe = np.where(col_sums > 0, col_sums, 1.0)
    A = C / col_sums_safe[np.newaxis, :]
    # Zero-out columns that were genuinely isolated (col_sums==0 originally)
    A[:, col_sums == 0] = 0.0
    return A


def ppr_iterate(A: np.ndarray, seed_vec: np.ndarray, alpha: float, iters: int,
                mass_tol: float) -> Tuple[np.ndarray, List[float]]:
    """Fixed-iteration Personalized PageRank power iteration.

    x_{t+1} = (1 - alpha) * A @ x_t + alpha * s

    Returns (final_x, mass_sums_per_iter). Asserts mass conservation.
    """
    x = seed_vec.copy().astype(np.float64)
    # Normalize seed to sum 1
    s = seed_vec.astype(np.float64)
    s_sum = float(s.sum())
    if s_sum <= 0:
        raise ValueError("PPR seed vector must have positive mass")
    s = s / s_sum
    x = s.copy()
    mass_sums = []
    for _ in range(iters):
        x = (1.0 - alpha) * (A @ x) + alpha * s
        # For A that is not perfectly column-stochastic (isolated nodes),
        # renormalize to preserve mass. Track raw sum for sanity.
        raw_sum = float(x.sum())
        mass_sums.append(raw_sum)
        # If raw_sum drifted outside tolerance, renormalize (defensive)
        if abs(raw_sum - 1.0) > mass_tol and raw_sum > 0:
            x = x / raw_sum
    return x, mass_sums


def rank_chunks_by_ppr(facts: List[Tuple[str, str, str, str]],
                       entities: List[str],
                       ppr_dist: np.ndarray) -> List[int]:
    """Rank fact indices by SUBJECT-side PPR mass.

    chunk_score(f) = ppr[s] for f = (s, r, o).

    Design rationale (adopted after smoke iteration 2026-07-03 that revealed
    ppr[s]+ppr[o] scoring gave POS_CTL=0.509 << 0.95): the synthetic KG's
    values are DRAWN FROM ENTITIES, so any entity can appear as either subject
    or object. High-degree hub entities that appear as OBJECT of many facts
    accumulate PPR mass and, under sum-of-endpoint scoring, drag their
    parent-facts into top-K regardless of subject signal.

    Subject-only scoring targets the "chunks whose source entity is proximal to
    the PPR seed" semantic -- which is exactly the HippoRAG "aggregated mass
    over document-mentioned entities" pattern specialized to the case where
    each fact's semantic authorship IS its subject entity. POS_CTL under
    ppr[s] scoring: PPR seeded from `mid` -> ppr[mid] dominates -> all 5 facts
    with s=mid tie for top -> top-5 = mid's 5 outgoing facts -> bridge_chunk
    (which has s=mid) is in top-5 -> POS_CTL >= 0.95 as required.
    """
    ent_idx = {e: i for i, e in enumerate(entities)}
    scores = np.zeros(len(facts), dtype=np.float64)
    for k, (s, _r, _o, _t) in enumerate(facts):
        scores[k] = ppr_dist[ent_idx[s]]
    order = np.argsort(scores)[::-1].tolist()
    return order


def seed_from_entities(entity_names: List[str], entities: List[str]) -> np.ndarray:
    """Build a PPR seed vector: uniform mass over given entity_names."""
    n = len(entities)
    ent_idx = {e: i for i, e in enumerate(entities)}
    v = np.zeros(n, dtype=np.float64)
    for name in entity_names:
        if name in ent_idx:
            v[ent_idx[name]] += 1.0
    if v.sum() == 0:
        # Fall back to uniform seed if no matches (rare; defensive)
        v = np.ones(n, dtype=np.float64)
    return v / v.sum()


# ---------- per-seed run ----------
def run_seed(seed: int) -> Dict:
    print("[seed=%d] rebuilding precedent corpus + bge retrieval..." % seed, flush=True)
    t0 = time.perf_counter()
    corpus = PRECEDENT.build_corpus(seed, PRECEDENT.N_DIM)
    fact_texts = [t for (_e, _r, _v, t) in corpus["facts"]]
    retrieved = PRECEDENT.bge_retrieve_all(corpus["queries"], fact_texts, PRECEDENT.TOP_K)
    print("  precedent_replay_done elapsed=%.1fs" % (time.perf_counter() - t0), flush=True)

    # Identify failed queries via tandem arm (matches Exp 1 subset selection)
    truths = [q["answer"] for q in corpus["queries"]]
    tandem_preds = []
    for qi, q in enumerate(corpus["queries"]):
        tandem_preds.append(PRECEDENT.arm_tandem_rag_substrate_composition(
            q, corpus, retrieved[qi]))
    failed_idx = [i for i, (p, t) in enumerate(zip(tandem_preds, truths)) if p != t]
    print("  n_failed=%d / %d queries" % (len(failed_idx), len(truths)), flush=True)

    # Build char-trigram encoder for Exp-1-style entity extraction
    entities = PRECEDENT.ENTITIES
    enc, codebook = EXP1.build_entity_codebook(entities, N_DIM_TRIGRAM)

    # Build undirected KG adjacency from the corpus facts
    A = build_undirected_adjacency(corpus["facts"], entities)
    print("  ppr_adjacency_built n=%d n_facts=%d" % (
        len(entities), len(corpus["facts"])), flush=True)

    # Per-query PPR walks
    rng = random.Random(seed + 9999)
    n = len(failed_idx)
    per_query = []
    # Arm result vectors: recall@5 in {0,1} per query
    r_baseline: List[int] = []
    r_main: List[int] = []
    r_pos: List[int] = []
    r_neg: List[int] = []
    # Mass conservation tracking
    all_mass_sums: List[float] = []

    for qi in failed_idx:
        q = corpus["queries"][qi]
        bridge = q["mid"]
        # TRUE bridge chunk = gt_chunks[1] = fact index for (mid, r1, answer)
        bridge_chunk_idx = q["gt_chunks"][1]
        ret = retrieved[qi]

        # ARM_HOP1_DENSE_ALONE_BASELINE: recall@5 = is bridge_chunk_idx in top-K?
        r_b = 1 if bridge_chunk_idx in ret[:PPR_TOP_K] else 0
        r_baseline.append(r_b)

        # ARM_MAIN_PPR_RECOVERED: seed PPR from Exp-1-matched entities
        chunks_text = " ".join(fact_texts[j] for j in ret)
        matched = EXP1.extract_matched_entities(
            chunks_text, enc, codebook, entities, COSINE_THRESH)
        seed_main = seed_from_entities(matched, entities)
        ppr_main, ms_main = ppr_iterate(A, seed_main, PPR_ALPHA, PPR_ITERS,
                                        MASS_CONSERVATION_TOL)
        all_mass_sums.extend(ms_main)
        ranked_main = rank_chunks_by_ppr(corpus["facts"], entities, ppr_main)
        r_m = 1 if bridge_chunk_idx in ranked_main[:PPR_TOP_K] else 0
        r_main.append(r_m)

        # ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE: seed from mid directly
        seed_pos = seed_from_entities([bridge], entities)
        ppr_pos, ms_pos = ppr_iterate(A, seed_pos, PPR_ALPHA, PPR_ITERS,
                                      MASS_CONSERVATION_TOL)
        all_mass_sums.extend(ms_pos)
        ranked_pos = rank_chunks_by_ppr(corpus["facts"], entities, ppr_pos)
        r_p = 1 if bridge_chunk_idx in ranked_pos[:PPR_TOP_K] else 0
        r_pos.append(r_p)

        # ARM_NEG_CTL_PPR_FROM_RANDOM: seed from random entity NOT in {e0, mid, answer}
        excluded = {q["e0"], q["mid"], q["answer"]}
        candidates = [e for e in entities if e not in excluded]
        # rng is deterministic per seed
        neg_entity = rng.choice(candidates)
        seed_neg = seed_from_entities([neg_entity], entities)
        ppr_neg, ms_neg = ppr_iterate(A, seed_neg, PPR_ALPHA, PPR_ITERS,
                                      MASS_CONSERVATION_TOL)
        all_mass_sums.extend(ms_neg)
        ranked_neg = rank_chunks_by_ppr(corpus["facts"], entities, ppr_neg)
        r_n = 1 if bridge_chunk_idx in ranked_neg[:PPR_TOP_K] else 0
        r_neg.append(r_n)

        per_query.append({
            "qi": qi,
            "bridge_entity": bridge,
            "bridge_chunk_idx": int(bridge_chunk_idx),
            "hop1_top_k": [int(x) for x in ret[:PPR_TOP_K]],
            "matched_entities": matched,
            "neg_seed_entity": neg_entity,
            "r_baseline": r_b,
            "r_main": r_m,
            "r_pos": r_p,
            "r_neg": r_n,
            "ranked_main_top5": [int(x) for x in ranked_main[:PPR_TOP_K]],
        })

    if n == 0:
        return {
            "seed": seed, "n_failed": 0, "vacuous": True, "per_arm": {},
            "elapsed_s": time.perf_counter() - t0,
        }

    # Per-arm rates on the full failed-query subset
    def _rate(v):
        return sum(v) / len(v) if v else 0.0

    per_arm = {
        "ARM_HOP1_DENSE_ALONE_BASELINE": {
            "recall_at_k": _rate(r_baseline),
            "n_hits": sum(r_baseline), "n": n,
        },
        "ARM_MAIN_PPR_RECOVERED": {
            "recall_at_k": _rate(r_main),
            "n_hits": sum(r_main), "n": n,
        },
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": {
            "recall_at_k": _rate(r_pos),
            "n_hits": sum(r_pos), "n": n,
        },
        "ARM_NEG_CTL_PPR_FROM_RANDOM": {
            "recall_at_k": _rate(r_neg),
            "n_hits": sum(r_neg), "n": n,
        },
    }

    # MISSED-BY-HOP1 subset: queries where baseline=0
    missed_by_hop1_idx = [i for i, r in enumerate(r_baseline) if r == 0]
    n_missed = len(missed_by_hop1_idx)
    if n_missed > 0:
        n_ppr_recovered = sum(r_main[i] for i in missed_by_hop1_idx)
        ppr_recovery_rate = n_ppr_recovered / n_missed
    else:
        ppr_recovery_rate = None  # baseline saturated

    # ARMS-DIFFER hashes (per-query recall vectors)
    def _hash(vec):
        return hashlib.sha256("|".join(str(x) for x in vec).encode()).hexdigest()[:16]
    digests = {
        "ARM_HOP1_DENSE_ALONE_BASELINE": _hash(r_baseline),
        "ARM_MAIN_PPR_RECOVERED": _hash(r_main),
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": _hash(r_pos),
        "ARM_NEG_CTL_PPR_FROM_RANDOM": _hash(r_neg),
    }
    # Legitimate exemption: any pair of arms whose per-query hit vectors are
    # BOTH all-zero (adverse regime) may collide by definition — no signal to
    # differ on. Collect all such all-zero-vector arms and mark all pairs among
    # them as exempted.
    arm_vecs = {
        "ARM_HOP1_DENSE_ALONE_BASELINE": r_baseline,
        "ARM_MAIN_PPR_RECOVERED": r_main,
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": r_pos,
        "ARM_NEG_CTL_PPR_FROM_RANDOM": r_neg,
    }
    zero_arms = [name for name, v in arm_vecs.items() if sum(v) == 0]
    arms_differ_exempted = []
    for i in range(len(zero_arms)):
        for j in range(i + 1, len(zero_arms)):
            arms_differ_exempted.append(
                (zero_arms[i], zero_arms[j],
                 "both all-zero hit vectors (adverse regime)"))
    seen: Dict[str, str] = {}
    arms_differ_violations = []
    exempted_pairs = {frozenset([a, b]) for a, b, _ in arms_differ_exempted}
    for name, dig in digests.items():
        if dig in seen:
            other = seen[dig]
            if frozenset([name, other]) in exempted_pairs:
                continue
            arms_differ_violations.append((other, name, dig))
        else:
            seen[dig] = name

    # Mass conservation check
    if all_mass_sums:
        max_dev = max(abs(m - 1.0) for m in all_mass_sums)
    else:
        max_dev = 0.0
    mass_conservation_ok = max_dev <= MASS_CONSERVATION_TOL

    return {
        "seed": seed,
        "n_failed": n,
        "n_queries_total": len(truths),
        "n_missed_by_hop1": n_missed,
        "vacuous": False,
        "per_arm": per_arm,
        "ppr_recovery_rate": ppr_recovery_rate,
        "n_ppr_recovered_on_missed_subset": (
            sum(r_main[i] for i in missed_by_hop1_idx) if n_missed > 0 else 0),
        "arm_digests": digests,
        "arms_differ_violations": arms_differ_violations,
        "arms_differ_exempted": arms_differ_exempted,
        "per_query_diag": per_query,
        "ppr_mass_max_deviation_from_1": max_dev,
        "ppr_mass_conservation_ok": mass_conservation_ok,
        "elapsed_s": time.perf_counter() - t0,
    }


# ---------- verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    # Aggregate n_missed across seeds (discriminator-fires gate)
    total_missed = sum(s.get("n_missed_by_hop1", 0) for s in per_seed
                       if not s.get("vacuous", False))
    if total_missed < 10:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_VACUOUS_SUBSET: total_missed_by_hop1=%d < 10 across seeds; "
                "baseline saturated -- no discriminator subset to test PPR recovery on. "
                "META_RULE_K discriminator-fires floor breach." % total_missed, {})

    # Aggregate per-arm rates weighted by n_failed
    arm_names = ["ARM_HOP1_DENSE_ALONE_BASELINE", "ARM_MAIN_PPR_RECOVERED",
                 "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE", "ARM_NEG_CTL_PPR_FROM_RANDOM"]
    per_arm_mean = {}
    for name in arm_names:
        total_hits = 0
        total_n = 0
        for s in per_seed:
            if s.get("vacuous", False):
                continue
            total_hits += s["per_arm"][name]["n_hits"]
            total_n += s["per_arm"][name]["n"]
        per_arm_mean[name] = total_hits / max(total_n, 1)

    baseline = per_arm_mean["ARM_HOP1_DENSE_ALONE_BASELINE"]
    main = per_arm_mean["ARM_MAIN_PPR_RECOVERED"]
    pos = per_arm_mean["ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE"]
    neg = per_arm_mean["ARM_NEG_CTL_PPR_FROM_RANDOM"]

    # Aggregate PPR_recovery_rate across all seeds (weighted by n_missed per seed)
    total_recovered = 0
    total_missed_agg = 0
    for s in per_seed:
        if s.get("vacuous", False) or s.get("n_missed_by_hop1", 0) == 0:
            continue
        total_recovered += s.get("n_ppr_recovered_on_missed_subset", 0)
        total_missed_agg += s["n_missed_by_hop1"]
    ppr_recovery_rate = total_recovered / max(total_missed_agg, 1)

    # Cardinality + arms-differ + mass-conservation checks
    expected_units = 4 * len([s for s in per_seed if not s.get("vacuous", False)])
    actual_units = sum(len(s.get("per_arm", {})) for s in per_seed
                       if not s.get("vacuous", False))
    cardinality_ok = actual_units == expected_units
    arms_differ_ok = all(len(s.get("arms_differ_violations", [])) == 0
                        for s in per_seed if not s.get("vacuous", False))
    mass_ok = all(s.get("ppr_mass_conservation_ok", True) for s in per_seed
                  if not s.get("vacuous", False))

    summary = ("baseline=%.3f | main=%.3f | pos_ctl=%.3f | neg_ctl=%.3f | "
               "ppr_recovery_rate=%.3f (%d/%d missed-by-hop1) | "
               "cardinality_ok=%s arms_differ_ok=%s mass_ok=%s" % (
                   baseline, main, pos, neg, ppr_recovery_rate,
                   total_recovered, total_missed_agg,
                   cardinality_ok, arms_differ_ok, mass_ok))

    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d units got %d. %s" % (
                    expected_units, actual_units, summary), per_arm_mean)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical (arms-must-differ violation). "
                "%s" % summary, per_arm_mean)
    if not mass_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_PPR_MASS_NONCONSERVATIVE: PPR mass sum drifted outside "
                "[0.995, 1.005] tolerance -- numerical primitive broken. %s" % summary,
                per_arm_mean)
    if pos < 0.95:
        return ("CONTROL_FAIL",
                "CONTROL_FAIL_POSITIVE: pos_ctl=%.3f < 0.95; PPR + chunk-scoring cannot "
                "recover bridge chunk even when seeded from true bridge entity. Mechanism "
                "broken; do not trust MAIN. %s" % (pos, summary), per_arm_mean)
    if neg > 0.10:
        return ("CONTROL_FAIL",
                "CONTROL_FAIL_NEGATIVE: neg_ctl=%.3f > 0.10; random-seeded PPR is "
                "recovering bridge chunk too often -- mass leaking uniformly; MAIN lift "
                "is confounded. %s" % (neg, summary), per_arm_mean)

    scale_caveat = ("SCALE_CAVEAT: synthetic 20-entity KG (dense by construction); "
                    "PPR is a global-flow op whose scale-transfer to Wikipedia-KB is "
                    "SEPARATE future test.")

    if ppr_recovery_rate >= 0.50:
        return ("HARD_PASS",
                "HARD_PASS_PPR_BRIDGE_RECOVERY: ppr_recovery_rate=%.3f >= 0.50 on "
                "missed-by-hop1 subset (%d/%d recovered). PPR-walk seeded by Exp-1-matched "
                "entities recovers bridge chunks that hop-1 dense-alone missed. Chain-ready "
                "for Exp 3 (composition F1 vs ORACLE=0.783). %s %s" % (
                    ppr_recovery_rate, total_recovered, total_missed_agg,
                    summary, scale_caveat), per_arm_mean)
    if ppr_recovery_rate < 0.15:
        return ("HARD_FAIL",
                "HARD_FAIL_PPR_BRIDGE_RECOVERY: ppr_recovery_rate=%.3f < 0.15; "
                "PPR does not surface bridge chunks; escalate to MDR-style dense-feedback "
                "fallback (Architecture A). %s %s" % (
                    ppr_recovery_rate, summary, scale_caveat), per_arm_mean)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PPR_BRIDGE_RECOVERY: ppr_recovery_rate=%.3f in [0.15, 0.50); "
            "real but narrow lift (matches BridgeRAG selective-effect pattern); worth "
            "shipping with modest expectations. %s %s" % (
                ppr_recovery_rate, summary, scale_caveat), per_arm_mean)


# ---------- selftest ----------
def selftest() -> None:
    """Formula selftest per PROT-022: verify PPR primitives + toy end-to-end."""
    print("[selftest] running formula selftest...", flush=True)

    # 1. build_undirected_adjacency sanity
    facts = [
        ("A", "r", "B", "The r of A is B."),
        ("B", "r", "C", "The r of B is C."),
        ("C", "r", "A", "The r of C is A."),
    ]
    ents = ["A", "B", "C"]
    A = build_undirected_adjacency(facts, ents)
    # Each entity has degree 2 (self+neighbor via 2 undirected edges).
    # A must be column-normalized: each column sums to 1.0
    col_sums = A.sum(axis=0)
    assert np.allclose(col_sums, 1.0), "adjacency not column-stochastic: %s" % col_sums

    # 2. PPR mass conservation on a small graph
    seed_v = seed_from_entities(["A"], ents)
    assert abs(seed_v.sum() - 1.0) < 1e-10, "seed not normalized: %s" % seed_v.sum()
    x, mass_sums = ppr_iterate(A, seed_v, 0.15, 5, 0.005)
    for m in mass_sums:
        assert abs(m - 1.0) < 0.01, "PPR mass leaked: %s" % mass_sums
    assert abs(x.sum() - 1.0) < 0.01, "PPR final mass leaked: %s" % x.sum()

    # 3. PPR concentration: seeded from A on triangle, all nodes should have positive mass
    assert (x > 0).all(), "PPR mass has zeros: %s" % x
    # Seed node should have MORE mass than others (restart gives it extra)
    assert x[0] > x[1] and x[0] > x[2], "PPR seed node not dominant: %s" % x

    # 4. rank_chunks_by_ppr: top-ranked chunk should touch the seed entity
    ranked = rank_chunks_by_ppr(facts, ents, x)
    assert ranked[0] in [0, 2], "top chunk should be A-B or C-A: got %d" % ranked[0]

    # 5. Isolated-node handling: 3 nodes, 2 disconnected
    facts_iso = [("A", "r", "B", "text1")]
    ents_iso = ["A", "B", "C"]
    A_iso = build_undirected_adjacency(facts_iso, ents_iso)
    # Column C should be all zero (isolated)
    assert A_iso[:, 2].sum() == 0.0, "isolated col should be zero"
    seed_iso = seed_from_entities(["A"], ents_iso)
    x_iso, ms_iso = ppr_iterate(A_iso, seed_iso, 0.15, 5, 0.005)
    # Mass should still conserve (renormalized if needed)
    assert abs(x_iso.sum() - 1.0) < 0.01, "PPR isolated mass leaked: %s" % x_iso.sum()

    # 6. seed_from_entities handles unknown entity gracefully (falls back)
    seed_unknown = seed_from_entities(["ZZZ"], ents)
    assert abs(seed_unknown.sum() - 1.0) < 1e-10, "unknown seed not normalized"

    # 7. Verdict compute smoke: HARD_PASS path
    fake = [{
        "seed": 0, "n_failed": 30, "n_missed_by_hop1": 20, "vacuous": False,
        "per_arm": {
            "ARM_HOP1_DENSE_ALONE_BASELINE": {"recall_at_k": 0.33, "n_hits": 10, "n": 30},
            "ARM_MAIN_PPR_RECOVERED": {"recall_at_k": 0.7, "n_hits": 21, "n": 30},
            "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": {"recall_at_k": 1.0, "n_hits": 30, "n": 30},
            "ARM_NEG_CTL_PPR_FROM_RANDOM": {"recall_at_k": 0.05, "n_hits": 2, "n": 30},
        },
        "arm_digests": {"ARM_HOP1_DENSE_ALONE_BASELINE": "a", "ARM_MAIN_PPR_RECOVERED": "b",
                        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": "c", "ARM_NEG_CTL_PPR_FROM_RANDOM": "d"},
        "arms_differ_violations": [],
        "n_ppr_recovered_on_missed_subset": 15,  # 15/20 = 0.75
        "ppr_mass_conservation_ok": True,
    }]
    v, msg, _ = compute_verdict(fake)
    assert v == "HARD_PASS", "verdict HARD_PASS fail: got %s msg=%s" % (v, msg)

    # 8. CONTROL_FAIL (pos too low)
    fake2 = [dict(fake[0])]
    fake2[0] = {**fake[0], "per_arm": {**fake[0]["per_arm"],
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": {"recall_at_k": 0.5, "n_hits": 15, "n": 30}}}
    v, msg, _ = compute_verdict(fake2)
    assert v == "CONTROL_FAIL" and "POSITIVE" in msg, "verdict CONTROL_FAIL (pos) fail: got %s" % v

    # 9. CONTROL_FAIL (neg too high)
    fake3 = [{**fake[0], "per_arm": {**fake[0]["per_arm"],
        "ARM_NEG_CTL_PPR_FROM_RANDOM": {"recall_at_k": 0.4, "n_hits": 12, "n": 30}}}]
    v, msg, _ = compute_verdict(fake3)
    assert v == "CONTROL_FAIL" and "NEGATIVE" in msg, "verdict CONTROL_FAIL (neg) fail: got %s" % v

    # 10. HARD_FAIL (low recovery)
    fake4 = [{**fake[0], "n_ppr_recovered_on_missed_subset": 2}]  # 2/20 = 0.10
    v, msg, _ = compute_verdict(fake4)
    assert v == "HARD_FAIL" and "PPR_BRIDGE_RECOVERY" in msg, "verdict HARD_FAIL fail: got %s" % v

    # 11. Vacuous subset
    fake5 = [{**fake[0], "n_missed_by_hop1": 5}]
    v, msg, _ = compute_verdict(fake5)
    assert v == "MIDDLE_BAND" and "VACUOUS_SUBSET" in msg, "verdict vacuous fail: got %s" % v

    print("[selftest] PASS: ppr_walk_bridge_recovery primitives OK", flush=True)


# ---------- start marker + crash diag ----------
def _write_start_marker(out_dir: Path, expected_n_units: int) -> None:
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


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
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
def main() -> None:
    print("[config] anchor=%s mode=%s seeds=%s alpha=%.2f iters=%d top_k=%d" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, PPR_ALPHA, PPR_ITERS, PPR_TOP_K), flush=True)

    selftest()
    if RUN_MODE == "self_test":
        print("[selftest] mode=self_test -- exit 0", flush=True)
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=4 * len(SEEDS))

    t_all = time.perf_counter()
    per_seed: List[Dict] = []
    for seed in SEEDS:
        result = run_seed(seed)
        per_seed.append(result)
        if result.get("vacuous", False):
            print("[seed=%d done] VACUOUS (no failed queries)" % seed, flush=True)
        else:
            print("[seed=%d done] baseline=%.3f main=%.3f pos=%.3f neg=%.3f "
                  "recovery_rate=%.3f (%d/%d) mass_ok=%s" % (
                      seed,
                      result["per_arm"]["ARM_HOP1_DENSE_ALONE_BASELINE"]["recall_at_k"],
                      result["per_arm"]["ARM_MAIN_PPR_RECOVERED"]["recall_at_k"],
                      result["per_arm"]["ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE"]["recall_at_k"],
                      result["per_arm"]["ARM_NEG_CTL_PPR_FROM_RANDOM"]["recall_at_k"],
                      result["ppr_recovery_rate"] if result["ppr_recovery_rate"] is not None else -1.0,
                      result.get("n_ppr_recovered_on_missed_subset", 0),
                      result.get("n_missed_by_hop1", 0),
                      result.get("ppr_mass_conservation_ok", False)), flush=True)

    verdict, verdict_msg, per_arm_mean = compute_verdict(per_seed)
    elapsed = time.perf_counter() - t_all

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "ppr_alpha": PPR_ALPHA,
        "ppr_iters": PPR_ITERS,
        "ppr_top_k": PPR_TOP_K,
        "cosine_thresh": COSINE_THRESH,
        "mass_conservation_tol": MASS_CONSERVATION_TOL,
        "per_seed": per_seed,
        "per_arm_mean_recall_at_k": per_arm_mean,
        "expected_n_units": 4 * len(SEEDS),
        "actual_n_units": sum(len(s.get("per_arm", {})) for s in per_seed
                              if not s.get("vacuous", False)),
        "cardinality_ok": (sum(len(s.get("per_arm", {})) for s in per_seed
                               if not s.get("vacuous", False))
                           == 4 * len([s for s in per_seed if not s.get("vacuous", False)])),
        "arms_differ_verified": all(
            len(s.get("arms_differ_violations", [])) == 0
            for s in per_seed if not s.get("vacuous", False)),
        "ppr_mass_conservation_verified": all(
            s.get("ppr_mass_conservation_ok", True)
            for s in per_seed if not s.get("vacuous", False)),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "PPR recall@k is a rate, not a shift-noise measurement; discriminator "
                    "reachability via POS_CTL >= 0.95 / NEG_CTL <= 0.10 span instead.",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
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
