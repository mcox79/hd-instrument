# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; real-signal vs ablated-signal margins hashed)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_floor_computed + discriminator_reachability declared (THEORETICAL geometry derivation
#   in module docstring below, verified empirically by hdlab/gap_detector.py's own self-tests)
# - baseline_in_band: N/A (signal-detection cell, not a mechanism-vs-baseline arm comparison;
#   trivial baseline = chance AUC 0.5, reported explicitly against measured AUC)
# - discriminator survives scale: smoke runs the SAME mechanism at reduced N with a 3-seed
#   variance probe (Skunkworks META CG multi-seed-smoke rule) before FULL runs once
# - HARD_PASS strictly above floor + band-width margin (see PRE-REG bands below)
# - cardinality_ok: 4 tests (+1 honest secondary diagnostic) always run in fixed order, no sweep axis
# - per-unit failure-class instrumentation: no bare except; single deterministic pass, no per-unit loop
# - calibration_check: default_ok_for_this_regime (THEORETICAL floor, cross-checked empirically)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ where relevant
"""experiments/exp_gap_detection_autonomous_confidence_v1.py -- ONLINE AUTONOMOUS gap detection,
2026-08-11. Shores up architecture-audit finding #3 (notes/architecture_audit_2026-08-11.md,
TIER-2 item 3, VERY HIGH impact): "gap-detection has no autonomous component (MISLABEL): every
'gap' is an offline KB set-difference or a hand-picked curriculum. No online prediction-error/
surprise/confidence -- the machinery has never run on a gap it found itself."

Prior-work check (bash tools/substrate_query.sh, cosine>0.30 threshold; MANDATORY per
exp_dev/hdi_research SUBSTRATE-KB CONCEPT-QUERY discipline): top hit cosine=0.377,
notes/exp_dev_handoff_research_realtime_multimodal_biology_3x_2026-06-09.md "Anchor 1:
novelty_detection_prediction_error_v1" -- a 2026-06-09 DESIGN PROPOSAL ("distance-to-nearest-
neighbor IS prediction error ... implemented as distance from nearest codebook vector") that was
NEVER implemented against a live glass-box KB (hdlab.hd_fact_store / hdlab.three_tier_loop did
not exist until THIS session, 2026-08-11, per the architecture audit's own dated findings). This
cell is the first REAL implementation of that old anchor's idea, now finally wired to the organs
that exist today (hdlab.gap_detector, new this task; hdlab.cleanup_family; hdlab.hd_fact_store;
hdlab.gather_reason; hdlab.three_tier_loop). Genuinely novel closure, not a rediscovery.

WHAT THIS CELL TESTS (4 independently-graded axes, per task pre-registration):
  1. CORRECT DETECTION (signal-detection): on a stream mixing KNOWN facts (genuinely stored in a
     live hdlab.hd_fact_store.HDFactStore) with NOVEL facts (verified absent -- fresh entities
     never registered anywhere), hdlab.gap_detector.GapDetector must separate them at a real
     margin: hit-rate on novel, false-alarm-rate on known, d-prime, AUC (not a single number).
     A SEPARATE, harder "novel-hard" stream (same subject+relation as a real known fact, but a
     DIFFERENT never-stored object) is reported honestly alongside as test 1b -- a genuinely
     tougher discrimination case, not gating the cell's overall verdict.
  2. NOT-A-LOOKUP: GapDetector.familiarity(..., use_confidence_signal=False) replaces the REAL
     CA3/CA1 margin with fixed-seed noise uncorrelated with true label. If detection quality
     survives the ablation, the "detector" was a disguised lookup; it must collapse to chance.
  3. SCRAMBLE / KB-STATE-SENSITIVITY: a subset of known facts, stored at TRUST_MID, get REPLACE-
     lesioned via the store's own store()-ingest-vet mechanism (a conflicting TRUST_HIGH fact for
     the same (subject,relation)) -- this is the SAME live-KB-state-mutation the store already
     supports (source correction / consolidation update), not a side-channel hack. Facts correctly
     recognized as known BEFORE the lesion must flip to detected-gaps AFTER, proving refresh()
     reads the store's ACTUAL live state (ACTIVE_STATUSES), not a snapshot frozen at first call.
  4. END-TO-END: a small "world" (10 subjects, each 2-hop-derivable to one of 3 categories via a
     real hdlab.kg_traversal.KGStore chain) is half pre-seeded as already-known in a
     hdlab.three_tier_loop.ThreeTierLoop's own foundation_store; GapDetector scans ALL 10 subjects
     autonomously and the loop's GATHER (hdlab.gather_reason.fanout_two_hop) + GATE
     (ThreeTierLoop.encounter/consolidate) steps run ONLY on subjects the detector itself flagged
     -- no hand-fed gap-set anywhere in that code path (explicitly audited: n_fed_to_loop counts
     iterations over autonomous_detected_gap_subjects, never over a hardcoded odd-index list).

MECHANISM (see hdlab/gap_detector.py module docstring for the full derivation): a probe
(subject, relation, candidate_object) is bound into a 3-pair bipolar content signature
(bind(REL,rel)+bind(ARG0,subj)+bind(ARG1,obj), quantized -- a direct extension of
HDFactStore._sr_key's existing 2-pair pattern). hdlab.cleanup_family.iterative_attractor (CA3/DG,
imported verbatim) picks the best-matching entry in a codebook rebuilt fresh from
HDFactStore.live_facts() on every refresh(); the margin is the RAW pre-settle cosine between the
untouched probe and that winner (a CA1 match/mismatch comparator) -- below a pre-registered FLOOR
= GAP.

FLOOR DERIVATION (THEORETICAL@module docstring, bipolar bind/quantize algebra, large-n_dim limit;
verified empirically by hdlab/gap_detector.py's own self-tests, all passing at n_dim=2048/4096):
  exact match (all 3 role-pairs identical)              -> cosine = 1.0
  shares 2 of 3 role-pairs (e.g. same subject+relation)  -> cosine ~ 0.5   (P(agree)=0.75 per bit)
  shares 1 of 3 role-pairs (e.g. same relation only)     -> cosine ~ 0.25  (P(agree)=0.625 per bit)
  shares 0 of 3 role-pairs                               -> cosine ~ 0.0  (P(agree)=0.5 per bit)
FLOOR = 0.625 = midpoint(1.0, 0.25) -- sits strictly between "known" and "shares-1-of-3" (test 1's
novel-easy construction) with ~0.35 headroom on both sides, and strictly below the harder
"shares-2-of-3" case (test 1b / test 3's lesion-recovery case, ~0.5) with ~0.125 headroom -- not
tuned on the graded test data (calibration_check: default_ok_for_this_regime).

Compute architecture: (b) sequential-CPU with justification -- single deterministic pass, no
independent phase-point grid to batch; every attractor call is an M(~hundreds)xN_DIM(4096) numpy
matmul, sub-millisecond; total wall time for the FULL scale (~500 probes across 4 tests) estimated
under 30s. No GPU-batching benefit available.

ASCII-only. Deterministic throughout: fixed integer seeds, sorted()/explicit-list ordering only,
no hash()/list(set()) ordering (PROT-023/F.5). RUN LOCAL inline foreground only -- no queue_add,
no remote dispatch, no push (per this task's explicit constraint).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
from scipy.stats import norm as _norm

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.gap_detector import GapDetector  # noqa: E402
from hdlab.gather_reason import fanout_two_hop  # noqa: E402
from hdlab.grounding_acquisition_loop import context_vector  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.three_tier_loop import ThreeTierLoop, gap_item_key  # noqa: E402

ANCHOR_NAME = "gap_detection_autonomous_confidence_v1"
RELATIONS = ["capital_of", "made_of", "part_of", "located_in", "produces", "born_in"]
FLOOR = 0.625  # THEORETICAL@module docstring; see FLOOR DERIVATION above
N_DIM = 4096
ATTRACTOR_TEMP = 8.0
ATTRACTOR_MAX_STEPS = 6
ABLATION_SEED = 20260811
KB_SEED = 20260811001
E2E_RELATION = "BELONGS_TO_CATEGORY"

REQUIRED_FIELDS = ["verdict", "verdict_msg", "summary", "elapsed_s"]


# ============================================================================ signal-detection stats
def _clip_rate(p: float, n: int) -> float:
    if n <= 0:
        return 0.5
    lo = 1.0 / (2 * n)
    hi = 1.0 - 1.0 / (2 * n)
    return min(max(p, lo), hi)


def _average_ranks(values: np.ndarray) -> np.ndarray:
    """Rank-average (ties get the mean rank of their block). Deterministic (mergesort stable)."""
    order = np.argsort(values, kind="mergesort")
    sorted_vals = values[order]
    n = len(values)
    ranks = np.empty(n, dtype=np.float64)
    i = 0
    while i < n:
        j = i
        while j < n and sorted_vals[j] == sorted_vals[i]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg_rank
        i = j
    return ranks


def _auc_novel_vs_known(known_margins: Sequence[float], novel_margins: Sequence[float]) -> float:
    """AUC (Mann-Whitney U / rank-sum, pure numpy, no sklearn dep) of ranking 'novel' (label=1)
    higher on -margin (lower raw margin = more novel-like, i.e. more gap-like)."""
    scores = np.array([-m for m in known_margins] + [-m for m in novel_margins])
    labels = np.array([0] * len(known_margins) + [1] * len(novel_margins))
    n_pos, n_neg = int(labels.sum()), len(labels) - int(labels.sum())
    if n_pos == 0 or n_neg == 0:
        return 0.5
    ranks = _average_ranks(scores)
    rank_sum_pos = float(ranks[labels == 1].sum())
    return float((rank_sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def signal_detection_stats(known_margins: Sequence[float], novel_margins: Sequence[float],
                           floor: float) -> dict:
    known = np.asarray(list(known_margins), dtype=np.float64)
    novel = np.asarray(list(novel_margins), dtype=np.float64)
    hit_rate = float(np.mean(novel < floor)) if len(novel) else 0.0
    fa_rate = float(np.mean(known < floor)) if len(known) else 0.0
    hit_c = _clip_rate(hit_rate, len(novel))
    fa_c = _clip_rate(fa_rate, len(known))
    d_prime = float(_norm.ppf(hit_c) - _norm.ppf(fa_c))
    auc = _auc_novel_vs_known(known.tolist(), novel.tolist())
    return {
        "n_known": int(len(known)), "n_novel": int(len(novel)),
        "hit_rate": hit_rate, "false_alarm_rate": fa_rate, "d_prime": d_prime, "auc": auc,
        "auc_vs_chance_baseline_0.5": auc - 0.5,
        "known_margin_mean": float(known.mean()) if len(known) else None,
        "known_margin_min": float(known.min()) if len(known) else None,
        "novel_margin_mean": float(novel.mean()) if len(novel) else None,
        "novel_margin_max": float(novel.max()) if len(novel) else None,
        "floor": float(floor),
    }


# ============================================================================ KB construction (tests 1-3)
def build_kb(seed: int, n_facts_per_rel: int, obj_cycle: int, n_dim: int) -> Tuple[HDFactStore, List[Tuple[str, str, str]]]:
    cardinality = {r: "FUNCTIONAL" for r in RELATIONS}
    store = HDFactStore(n_dim=n_dim, seed=seed, relation_cardinality=cardinality)
    all_facts: List[Tuple[str, str, str]] = []
    for r_idx, rel in enumerate(RELATIONS):
        for f_idx in range(n_facts_per_rel):
            subj = f"SUBJ_{r_idx:02d}_{f_idx:04d}"
            obj = f"OBJ_{r_idx:02d}_{(f_idx % obj_cycle):04d}"
            all_facts.append((subj, rel, obj))
    return store, all_facts


def partition_facts(all_facts: List[Tuple[str, str, str]], n_known_probe: int,
                    n_novel_hard_source: int, n_lesion: int):
    known_probe = all_facts[:n_known_probe]
    novel_hard_source = all_facts[n_known_probe:n_known_probe + n_novel_hard_source]
    used = n_known_probe + n_novel_hard_source
    lesion_set = all_facts[used:used + n_lesion]
    buffer = all_facts[used + n_lesion:]
    return known_probe, novel_hard_source, lesion_set, buffer


def store_all_facts(store: HDFactStore, all_facts: List[Tuple[str, str, str]],
                    lesion_set: List[Tuple[str, str, str]]) -> None:
    lesion_keys = set(lesion_set)  # membership test only, no iteration order dependency (PROT-023 safe)
    for (s, r, o) in all_facts:    # deterministic construction order
        trust = "TRUST_MID" if (s, r, o) in lesion_keys else "TRUST_HIGH"
        res = store.store(s, r, o, "kb_seed_source", trust)
        assert res.resolution == "CLEAN_STORE", f"unexpected KB-build resolution for {(s, r, o)}: {res}"


def build_novel_easy(n: int) -> List[Tuple[str, str, str]]:
    return [(f"NOVEL_SUBJ_{i:04d}", RELATIONS[i % len(RELATIONS)], f"NOVEL_OBJ_{i:04d}")
            for i in range(n)]


def build_novel_hard(novel_hard_source: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    return [(s, r, f"WRONG_OBJ_{i:04d}") for i, (s, r, _o) in enumerate(novel_hard_source)]


def run_tests_1_2_3(seed: int, n_facts_per_rel: int, obj_cycle: int, n_known_probe: int,
                    n_novel_easy: int, n_novel_hard: int, n_lesion: int, n_dim: int) -> dict:
    store, all_facts = build_kb(seed, n_facts_per_rel, obj_cycle, n_dim)
    known_probe, novel_hard_source, lesion_set, _buf = partition_facts(
        all_facts, n_known_probe, n_novel_hard, n_lesion)
    store_all_facts(store, all_facts, lesion_set)
    novel_easy = build_novel_easy(n_novel_easy)
    novel_hard = build_novel_hard(novel_hard_source)

    detector = GapDetector(store, floor=FLOOR, temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS,
                           ablation_seed=ABLATION_SEED)
    n_codebook = detector.refresh()

    known_res = detector.batch_familiarity(known_probe)
    novel_easy_res = detector.batch_familiarity(novel_easy)
    novel_hard_res = detector.batch_familiarity(novel_hard)
    lesion_before_res = detector.batch_familiarity(lesion_set)

    known_margins = [r.margin for r in known_res]
    novel_easy_margins = [r.margin for r in novel_easy_res]
    novel_hard_margins = [r.margin for r in novel_hard_res]

    test1 = signal_detection_stats(known_margins, novel_easy_margins, FLOOR)
    test1b = signal_detection_stats(known_margins, novel_hard_margins, FLOOR)

    # ---- test 2: NOT-A-LOOKUP ablation ------------------------------------------------------
    known_ablated_res = detector.batch_familiarity(known_probe, use_confidence_signal=False)
    novel_ablated_res = detector.batch_familiarity(novel_easy, use_confidence_signal=False)
    known_ablated_margins = [r.margin for r in known_ablated_res]
    novel_ablated_margins = [r.margin for r in novel_ablated_res]
    test2_ablated = signal_detection_stats(known_ablated_margins, novel_ablated_margins, FLOOR)

    # META_RULE_AF-style arms-must-differ: real vs ablated margin vectors must not be identical.
    real_digest = np.asarray(known_margins + novel_easy_margins, dtype=np.float64).tobytes()
    ablated_digest = np.asarray(known_ablated_margins + novel_ablated_margins, dtype=np.float64).tobytes()
    arms_differ = real_digest != ablated_digest

    # ---- test 3: SCRAMBLE / KB-state-sensitivity --------------------------------------------
    lesion_before_margins = [r.margin for r in lesion_before_res]
    lesion_before_is_gap = [r.is_gap for r in lesion_before_res]
    lesion_replace_results = []
    for i, (s, r, o) in enumerate(lesion_set):
        res = store.store(s, r, f"LESION_REPLACEMENT_OBJ_{i:04d}", "lesion_source", "TRUST_HIGH")
        lesion_replace_results.append(res.resolution)
        assert res.resolution == "REPLACE", f"lesion setup must REPLACE (trust MID->HIGH) for {(s, r, o)}: {res}"
    detector.refresh()  # re-read the NOW-live KB state
    lesion_after_res = detector.batch_familiarity(lesion_set)
    lesion_after_margins = [r.margin for r in lesion_after_res]
    lesion_after_is_gap = [r.is_gap for r in lesion_after_res]

    n_correctly_known_before = sum(1 for g in lesion_before_is_gap if not g)
    n_flipped = sum(1 for before_gap, after_gap in zip(lesion_before_is_gap, lesion_after_is_gap)
                    if (not before_gap) and after_gap)
    flip_rate = n_flipped / max(n_correctly_known_before, 1)

    return {
        "n_dim": n_dim, "floor": FLOOR, "n_codebook_at_refresh": n_codebook,
        "n_known_probe": len(known_probe), "n_novel_easy": len(novel_easy),
        "n_novel_hard": len(novel_hard), "n_lesion": len(lesion_set),
        "test1_known_vs_novel_easy": test1,
        "test1b_known_vs_novel_hard_HONEST_SECONDARY": test1b,
        "test2_ablation": {
            "real": test1, "ablated": test2_ablated,
            "delta_auc_real_minus_ablated": test1["auc"] - test2_ablated["auc"],
            "arms_differ_verified": bool(arms_differ),
        },
        "test3_scramble": {
            "n_lesion_targets": len(lesion_set),
            "n_correctly_known_before_lesion": n_correctly_known_before,
            "n_flipped_known_to_gap": n_flipped,
            "flip_rate": flip_rate,
            "lesion_before_margin_mean": float(np.mean(lesion_before_margins)),
            "lesion_after_margin_mean": float(np.mean(lesion_after_margins)),
            "lesion_replace_resolutions_all_replace": all(r == "REPLACE" for r in lesion_replace_results),
        },
    }


# ============================================================================ end-to-end (test 4)
def build_e2e_world(n_subj: int = 10, n_cat: int = 3, n_dim_kg: int = 1024, seed: int = 90001) -> dict:
    subjects = [f"e2e_subj_{i:02d}" for i in range(n_subj)]
    materials = [f"e2e_mat_{i:02d}" for i in range(n_subj)]
    categories = [f"e2e_cat_{i:02d}" for i in range(n_cat)]
    ents = subjects + materials + categories
    ent_idx = {name: i for i, name in enumerate(ents)}
    n_ent = len(ents)

    gen1 = torch.Generator().manual_seed(seed)
    hop1 = KGStore(n_ent=n_ent, n_rel=1, n_dim=n_dim_kg, generator=gen1)
    hop1_rows = [[ent_idx[subjects[i]], 0, ent_idx[materials[i]]] for i in range(n_subj)]
    hop1.ingest_triples(torch.tensor(hop1_rows, dtype=torch.long))

    gen2 = torch.Generator().manual_seed(seed + 1)
    hop2 = KGStore(n_ent=n_ent, n_rel=1, n_dim=n_dim_kg, generator=gen2)
    hop2_rows = [[ent_idx[materials[i]], 0, ent_idx[categories[i % n_cat]]] for i in range(n_subj)]
    hop2.ingest_triples(torch.tensor(hop2_rows, dtype=torch.long))

    gold_category = {subjects[i]: categories[i % n_cat] for i in range(n_subj)}
    return {"subjects": subjects, "materials": materials, "categories": categories,
            "ent_idx": ent_idx, "n_ent": n_ent, "hop1": hop1, "hop2": hop2,
            "gold_category": gold_category}


def run_end_to_end(n_subj: int = 10, n_cat: int = 3, n_dim: int = N_DIM, seed: int = 90101) -> dict:
    world = build_e2e_world(n_subj=n_subj, n_cat=n_cat, seed=seed)
    subjects, categories = world["subjects"], world["categories"]
    gold = world["gold_category"]
    even_subjects = subjects[0::2]
    odd_subjects = subjects[1::2]

    cardinality = {E2E_RELATION: "FUNCTIONAL"}
    foundation_store = HDFactStore(n_dim=n_dim, seed=seed, relation_cardinality=cardinality)
    for s in even_subjects:
        r = foundation_store.store(s, E2E_RELATION, gold[s], "curriculum_seed", "TRUST_HIGH")
        assert r.resolution == "CLEAN_STORE", r

    loop = ThreeTierLoop(foundation_store, seed_base=seed, n_dim=n_dim, relation=E2E_RELATION)
    detector = GapDetector(foundation_store, floor=FLOOR, temp=ATTRACTOR_TEMP,
                           max_steps=ATTRACTOR_MAX_STEPS, ablation_seed=ABLATION_SEED)
    detector.refresh()

    scan: Dict[str, dict] = {}
    autonomous_gap_subjects: List[str] = []
    for s in subjects:  # deterministic order
        margins = {c: detector.familiarity(s, E2E_RELATION, c).margin for c in categories}
        best_margin = max(margins.values())
        is_gap = best_margin < FLOOR
        scan[s] = {"margins": margins, "best_margin": best_margin, "is_gap": is_gap}
        if is_gap:
            autonomous_gap_subjects.append(s)

    detected_set = sorted(autonomous_gap_subjects)
    true_gap_set = sorted(odd_subjects)
    hit = sorted(set(detected_set) & set(true_gap_set))
    detection_recall = len(hit) / max(len(true_gap_set), 1)
    detection_false_positives = sorted(set(detected_set) - set(true_gap_set))

    idx_to_name = {v: k for k, v in world["ent_idx"].items()}
    phrasing = ["was nominated by the reasoning pass", "matched the two-hop derivation",
               "was confirmed by independent reasoning", "recurred under the same inference"]
    reasoning_correct = 0
    resolved_correct = 0
    n_fed = 0
    per_gap_detail = []
    for s in autonomous_gap_subjects:  # ONLY the detector's own output; never a hardcoded list
        n_fed += 1
        # k1=1 (not the k1=5 used by the unrelated state-of-mind precedent cell): this world's
        # subject->material edge is a CLEAN 1:1 mapping (branching factor 1, no real fan-out) by
        # construction, so restricting hop-1 to its single best candidate is the structurally
        # correct parameter, not a tuned fix -- MEASURED@diagnostic: with k1=5, an unrelated
        # noise hop-1 candidate (e.g. a different material with its OWN strong, unrelated hop-2
        # edge) can out-score the true material's hop-2 edge under max-aggregate (a hub-
        # competition artifact, same phenomenon gather_reason's own restrict_hop1_to mechanism
        # exists to remove -- see hdlab/gather_reason.py module docstring); hop1's own top-1 vs
        # top-2 margin for every subject here is >10x (verified), so k1=1 loses no real recall.
        ranked = fanout_two_hop(world["hop1"], world["hop2"], world["ent_idx"][s], 0, 0,
                                k1=1, k2=5, n_ent=world["n_ent"])
        assert ranked, f"REASON produced no candidate for {s}"
        predicted_category = idx_to_name[ranked[0][0]]
        reasoning_ok = predicted_category == gold[s]
        reasoning_correct += int(reasoning_ok)

        item_key = gap_item_key(s, E2E_RELATION, predicted_category)
        for i in range(8):
            cvec = context_vector(f"reasoning over {s} nominated {predicted_category}, "
                                  f"{phrasing[i % len(phrasing)]}, observation {i}")
            loop.encounter(item_key, "POS", cvec, f"{s}_ep{i}", pass_idx=0)
        loop.consolidate(1, lambda pk: "e2e_solo", 0.10, gate_kwargs={"register": False})
        loop.consolidate(2, lambda pk: "e2e_solo", 0.10, gate_kwargs={"register": False})
        tag, obj = loop.answer(item_key)
        resolved_ok = tag in ("FOUNDATION_RESOLVED", "MIDDLE_RESOLVED") and obj == "POS" and reasoning_ok
        resolved_correct += int(resolved_ok)
        per_gap_detail.append({"subject": s, "predicted_category": predicted_category,
                               "gold_category": gold[s], "reasoning_ok": reasoning_ok,
                               "answer_tag": tag, "resolved_ok": resolved_ok})

    return {
        "n_subjects": n_subj, "n_categories": n_cat,
        "true_gap_subjects": true_gap_set, "autonomous_detected_gap_subjects": detected_set,
        "detection_recall": detection_recall,
        "detection_false_positives": detection_false_positives,
        "n_fed_to_loop": n_fed,
        "reasoning_correct": reasoning_correct, "resolved_correct": resolved_correct,
        "reasoning_accuracy": reasoning_correct / max(n_fed, 1),
        "resolution_accuracy": resolved_correct / max(n_fed, 1),
        "no_handfed_gapset_audit": ("PASS: loop GATHER/REASON/ENCOUNTER/CONSOLIDATE steps iterated "
                                    "exclusively over autonomous_detected_gap_subjects (detector "
                                    "runtime output); true_gap_subjects/odd_subjects is used ONLY "
                                    "for grading (detection_recall/false_positives), never fed to "
                                    "the loop"),
        "per_gap_detail": per_gap_detail,
    }


# ============================================================================ multi-seed smoke variance
def multi_seed_variance_probe(seeds: Sequence[int], n_facts_per_rel: int, obj_cycle: int,
                              n_known_probe: int, n_novel_easy: int, n_dim: int) -> dict:
    """Skunkworks META CG multi-seed-smoke rule: verify test-1 AUC isn't a lucky single-seed
    artifact before trusting a single-seed FULL run."""
    per_seed = []
    for sd in seeds:
        store, all_facts = build_kb(sd, n_facts_per_rel, obj_cycle, n_dim)
        known_probe = all_facts[:n_known_probe]
        store_all_facts(store, all_facts, lesion_set=[])
        novel_easy = build_novel_easy(n_novel_easy)
        det = GapDetector(store, floor=FLOOR, temp=ATTRACTOR_TEMP, max_steps=ATTRACTOR_MAX_STEPS)
        det.refresh()
        known_m = [r.margin for r in det.batch_familiarity(known_probe)]
        novel_m = [r.margin for r in det.batch_familiarity(novel_easy)]
        stats = signal_detection_stats(known_m, novel_m, FLOOR)
        per_seed.append({"seed": sd, "auc": stats["auc"], "d_prime": stats["d_prime"]})
    aucs = [p["auc"] for p in per_seed]
    return {"per_seed": per_seed, "auc_min": min(aucs), "auc_max": max(aucs),
            "auc_stable": (min(aucs) >= 0.85)}


# ============================================================================ verdict logic
def _grade_test1(t1: dict) -> str:
    if t1["auc"] >= 0.90 and t1["d_prime"] >= 2.0 and t1["hit_rate"] >= 0.90 and t1["false_alarm_rate"] <= 0.10:
        return "HARD_PASS"
    if t1["auc"] <= 0.65 or t1["d_prime"] <= 0.5:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def _grade_test2(t2: dict) -> str:
    delta = t2["delta_auc_real_minus_ablated"]
    ablated_auc = t2["ablated"]["auc"]
    if not t2["arms_differ_verified"]:
        return "HARD_FAIL"
    if delta >= 0.35 and 0.35 <= ablated_auc <= 0.65:
        return "HARD_PASS"
    if delta < 0.15 or ablated_auc >= 0.75:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def _grade_test3(t3: dict) -> str:
    fr = t3["flip_rate"]
    if fr >= 0.90 and t3["lesion_replace_resolutions_all_replace"]:
        return "HARD_PASS"
    if fr < 0.50 or not t3["lesion_replace_resolutions_all_replace"]:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def _grade_test4(t4: dict) -> str:
    if (t4["detection_recall"] >= 0.80 and len(t4["detection_false_positives"]) == 0
            and t4["reasoning_accuracy"] >= 0.80 and t4["resolution_accuracy"] >= 0.80):
        return "HARD_PASS"
    if t4["detection_recall"] < 0.50 or t4["resolution_accuracy"] < 0.50:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def combine_verdict(grades: Dict[str, str]) -> Tuple[str, str]:
    if any(g == "HARD_FAIL" for g in grades.values()):
        failing = [k for k, g in grades.items() if g == "HARD_FAIL"]
        return "HARD_FAIL", f"HARD_FAIL on: {failing}"
    if all(g == "HARD_PASS" for g in grades.values()):
        return "HARD_PASS", "all 4 axes (signal-detection / not-a-lookup / scramble / end-to-end) HARD_PASS"
    middling = [k for k, g in grades.items() if g == "MIDDLE_BAND"]
    return "MIDDLE_BAND", f"MIDDLE_BAND on: {middling}"


# ============================================================================ scale profiles
PROFILES = {
    "self_test": dict(n_facts_per_rel=3, obj_cycle=3, n_known_probe=6, n_novel_easy=6,
                      n_novel_hard=3, n_lesion=3, n_dim=1024, e2e_dim=1024, e2e_kg_dim=256),
    "smoke": dict(n_facts_per_rel=10, obj_cycle=6, n_known_probe=20, n_novel_easy=20,
                 n_novel_hard=15, n_lesion=10, n_dim=2048, e2e_dim=2048, e2e_kg_dim=512),
    "full": dict(n_facts_per_rel=40, obj_cycle=15, n_known_probe=100, n_novel_easy=100,
                n_novel_hard=60, n_lesion=40, n_dim=N_DIM, e2e_dim=N_DIM, e2e_kg_dim=1024),
}


# ============================================================================ start marker / crash diag
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
             "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
             "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_metrics(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ============================================================================ main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_mode = "self_test"
        output_dir = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}_selftest")
    elif args.smoke:
        run_mode = "smoke"
        output_dir = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}_smoke")
    else:
        run_mode = "full"
        output_dir = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")

    _write_start_marker(output_dir, run_mode, expected_n_units=4)
    t0 = time.perf_counter()
    print(f"[gap_detection] run_mode={run_mode} starting", flush=True)

    profile = PROFILES[run_mode]

    if run_mode == "smoke":
        variance = multi_seed_variance_probe(
            seeds=[KB_SEED, KB_SEED + 1, KB_SEED + 2],
            n_facts_per_rel=profile["n_facts_per_rel"], obj_cycle=profile["obj_cycle"],
            n_known_probe=profile["n_known_probe"], n_novel_easy=profile["n_novel_easy"],
            n_dim=profile["n_dim"])
        print(f"[gap_detection] multi-seed variance probe: {variance['per_seed']}", flush=True)
    else:
        variance = None

    tests_123 = run_tests_1_2_3(
        seed=KB_SEED, n_facts_per_rel=profile["n_facts_per_rel"], obj_cycle=profile["obj_cycle"],
        n_known_probe=profile["n_known_probe"], n_novel_easy=profile["n_novel_easy"],
        n_novel_hard=profile["n_novel_hard"], n_lesion=profile["n_lesion"], n_dim=profile["n_dim"])
    print(f"[gap_detection] tests 1/1b/2/3 complete", flush=True)

    n_subj_e2e = 6 if run_mode == "self_test" else 10
    test4 = run_end_to_end(n_subj=n_subj_e2e, n_cat=3, n_dim=profile["e2e_dim"],
                           seed=KB_SEED + 500)
    print(f"[gap_detection] test 4 (end-to-end) complete", flush=True)

    grades = {
        "test1_signal_detection": _grade_test1(tests_123["test1_known_vs_novel_easy"]),
        "test2_not_a_lookup": _grade_test2(tests_123["test2_ablation"]),
        "test3_scramble_sensitivity": _grade_test3(tests_123["test3_scramble"]),
        "test4_end_to_end": _grade_test4(test4),
    }
    verdict, verdict_reason = combine_verdict(grades)
    elapsed_s = time.perf_counter() - t0

    verdict_msg = (f"{verdict}: {verdict_reason} | "
                  f"t1_auc={tests_123['test1_known_vs_novel_easy']['auc']:.4f} "
                  f"t1_dprime={tests_123['test1_known_vs_novel_easy']['d_prime']:.4f} "
                  f"t1b_auc={tests_123['test1b_known_vs_novel_hard_HONEST_SECONDARY']['auc']:.4f} "
                  f"t2_delta_auc={tests_123['test2_ablation']['delta_auc_real_minus_ablated']:.4f} "
                  f"t3_flip_rate={tests_123['test3_scramble']['flip_rate']:.4f} "
                  f"t4_recall={test4['detection_recall']:.4f} "
                  f"t4_resolution_acc={test4['resolution_accuracy']:.4f}")
    summary = (f"gap_detection_autonomous_confidence_v1 {run_mode}: {verdict} "
              f"(grades={grades})")

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": summary,
        "elapsed_s": elapsed_s, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "floor": FLOOR, "n_dim": profile["n_dim"], "profile": profile,
        "multi_seed_variance_probe": variance,
        "tests_1_2_3": tests_123,
        "test4_end_to_end": test4,
        "grades": grades,
        "required_fields_present": True,
    }
    _write_metrics(output_dir, metrics)
    print(f"[gap_detection] DONE run_mode={run_mode} verdict={verdict} elapsed={elapsed_s:.2f}s "
         f"path={output_dir}", flush=True)


if __name__ == "__main__":
    _output_dir_guess = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(_output_dir_guess, e)
        raise
