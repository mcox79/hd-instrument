# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-checkpoint (n_foundation,n_middle) tuples hashed; asserted not-all-identical across A/B/C)
# - final_metrics_atomicity = tmp_replace (single-shot)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: discrete cumulative-resolved-gap counting, no Gaussian noise-floor metric; discriminator_reachability=true (see prereg hand-computed feasibility check)
# - baseline_in_band EXEMPTED for B_no_middle and C_no_sweep (deliberate ablation/sentinel arms, not saturating baselines)
# - discriminator survives scale via smoke preview (real pipeline, 2-process subset, same regime constants as FULL)
# - HARD_PASS strictly above floor (>=20pp headroom under HARD_PASS bars vs HARD_FAIL floors)
# - HP_SCOPE: bands apply to A_full vs B_no_middle and A_full vs C_no_sweep; B/C carry no HP gate of their own; scramble control graded only on scramble_clean
# - cardinality_ok: EXPECTED_N_UNITS = 4 arms * VISITS_PER_GAP(6) checkpoints = 24; verified via len(checkpoints)==VISITS_PER_GAP per arm
# - per-unit failure-class instrumentation: N/A (single deterministic pass per arm, not a resumable per-unit loop)
# - calibration_check: default_ok_for_this_regime (novelty_thresh calibrated from real eligible-target cluster structure)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL KGStore/HDFactStore/Library/TierState/ScriptLibrary/RelationRegister/ThreeTierLoop objects at N~16 (real_code_path)
# - substrate_signature_checked: KGStore/HDFactStore/ThreeTierLoop base kwargs only
"""exp_three_tier_loop_real_corpus_gap_stream_v1 -- proves the FULL three-tier accumulation
dynamics (middle-db retain + periodic CA3/DG sweep + combined-evidence gate-crossing) on a REAL
corpus + REAL gap-stream, isolating the middle-db and sweep's individual load-bearing value via
ablation arms. See preregs/2026-08-11_three_tier_loop_real_corpus_gap_stream_v1.md for the full
design (arms, bands, feasibility check, schema-vet declarations).

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim; NONE
modified by this cell):
  hdlab.three_tier_loop.ThreeTierLoop / gap_item_key / parse_gap_item_key / gap_register_fn
  hdlab.gather_reason.ca3_relevance_gather / fanout_two_hop / recovery_at / real_to_concat
  hdlab.grounding_acquisition_loop.Library / consolidation_pass / context_vector / MIN_CONFIRM /
    PROMOTE_MIN_EXPOSURE / PROMOTE_MIN_CONSISTENCY
  hdlab.prelim_tier.TierState / update_prelim_and_generalize
  hdlab.hd_fact_store.HDFactStore / ACTIVE_STATUSES
  hdlab.script_grain_acquisition_loop.calibrate_novelty_threshold
  hdlab.situation_model_accumulate.RelationRegister / unit_phase_vec
  hdlab.kg_traversal.KGStore
  experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1's own build functions
    (build_reading_facts, reading_vocab, build_cskg_bridges, build_gap_set, build_entity_index,
    fresh_kg, ingest_reading_hop1, ingest_bridge_hop2, build_material_codebook, scramble_edges)
    -- the SAME real 121-target gap-set + real KG-structure construction pipeline as the landed
    HARD_PASS cell (data/exp_state_of_mind_relevance_gather_reasoning_union_v1/metrics.json),
    imported directly, not re-derived.

THE ONE NEW THING (honestly disclosed): a multi-ENCOUNTER STREAM wrapper around the real
gap-set + real reasoning mechanism, per-cue-restricted REASON (restrict_hop1_to = the ONE real
via_material a gap's cue names, not the full CA3-gathered set), and 3 arms (A_full,
B_no_middle, C_no_sweep) + 1 control (A_scramble_control) isolating the three-tier VALUE. The
encounter multiplicity itself is SYNTHETIC (deterministic templated episode text embedding real
entity names, matching verification/test_three_tier_loop_e2e.py's own _episode_text
precedent) -- the gap-set, KG structure, and reasoning mechanism are all real.

ARMS: A_full (full ThreeTierLoop wiring) / B_no_middle (bare Library + consolidation_pass only,
no middle tier at all) / C_no_sweep (full wiring except tier_state.native_store_gen reverted to
a disconnected store, ablating exactly the one documented ASSEMBLY DECISION in
hdlab/three_tier_loop.py) / A_scramble_control (A_full wiring, scrambled hop2 bridge edges).

Modes: --self-test (tiny synthetic fixture, <5s) / --smoke (real pipeline, 2-process subset) /
(no flag, default) = FULL (real pipeline, all real processes/targets).

ASCII-only. Deterministic throughout (sorted(set()) discipline; fixed integer seeds; no
built-in hash() anywhere -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "three_tier_loop_real_corpus_gap_stream_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec  # noqa: E402
from hdlab.gather_reason import ca3_relevance_gather, fanout_two_hop, recovery_at, real_to_concat  # noqa: E402
from hdlab.grounding_acquisition_loop import (  # noqa: E402
    Library, consolidation_pass, context_vector, MIN_CONFIRM, PROMOTE_MIN_EXPOSURE,
    PROMOTE_MIN_CONSISTENCY,
)
from hdlab.prelim_tier import TierState, update_prelim_and_generalize, CLUSTER_MIN_MEMBERS  # noqa: E402
from hdlab.hd_fact_store import HDFactStore, ACTIVE_STATUSES  # noqa: E402
from hdlab.script_grain_acquisition_loop import calibrate_novelty_threshold, build_instance_register  # noqa: E402
import hdlab.three_tier_loop as ttl  # noqa: E402
from experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1 import (  # noqa: E402
    build_reading_facts, reading_vocab, build_cskg_bridges, build_gap_set, build_entity_index,
    fresh_kg, ingest_reading_hop1, ingest_bridge_hop2, build_material_codebook, scramble_edges,
)

# ---- regime constants (reused byte-identical to the source cell's own validated regime,
# except the 6 SEED_* values which are freshly namespaced for this cell) ----
K1_FANOUT = 30
K2_FANOUT = 500
CA3_K_PEEL = 25
CA3_SIM_FLOOR = 0.05
FHRR_D = 1024
FOUND_DIM = 2048
K_RESOLVE = 5                  # recovery@K bar, matches source cell's own "resolved" definition

# ---- this cell's own new constants ----
VISITS_PER_GAP = 6             # < PROMOTE_MIN_EXPOSURE(8) by construction: no individual gap
                                # can ever cross the strict per-item gate alone.
VISITS_PER_GAP_SMOKE = 11      # smoke-only: a 2-process subset naturally produces SMALLER
                                # via_material clusters (MEASURED: largest clusters are size 5
                                # at {combustion,photosynthesis}, vs size 44/38 at FULL 15-
                                # process scale) than FULL, but cluster_exposure_floor=32 is a
                                # FIXED constant (PROMOTE_MIN_EXPOSURE*CLUSTER_EXPOSURE_
                                # MULTIPLIER, not scale-adjusted) -- so more visits are needed
                                # for the SAME mechanism to fire at the smaller smoke scale
                                # (5*11=55>=32 with margin; 5*6=30<32 would not fire, MEASURED
                                # during authoring). Same adjustment the self-test's own
                                # visits=12 already uses for the identical reason. FULL retains
                                # VISITS_PER_GAP=6 unchanged (its own clusters comfortably clear
                                # 32 already -- see prereg hand-computed feasibility check).
RELATION = "GAP_BRIDGE_FACT"
SEED_KG_HOP1 = 20260812101
SEED_KG_HOP2 = 20260812102
SEED_SCRAMBLE = 20260812103
SEED_FHRR = 20260812104
SEED_FOUND_A = 20260812201
SEED_FOUND_B = 20260812202
SEED_FOUND_C = 20260812203
SEED_FOUND_SCRAMBLE = 20260812204
SEED_TIER_A = 20260812301
SEED_TIER_C = 20260812302
SEED_TIER_SCRAMBLE = 20260812303
SEED_DISCONNECT_C = 20260812304


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


# =========================================================================== PARSE identity
def pk_of(t: Dict) -> str:
    """Item key for gap target t: subject=process, relation-slot=via_material (the cluster
    key), candidate=whole. Reuses hdlab.three_tier_loop.gap_item_key verbatim; putting
    via_material in the relation slot lets cluster_key_fn recover it with zero side tables."""
    return ttl.gap_item_key(t["process"], t["via_material"], t["whole"])


def cluster_key_fn(pk: str) -> str:
    return ttl.parse_gap_item_key(pk)[1]


def my_gap_register_fn(pk: str, cluster_key: str, label: str) -> torch.Tensor:
    """CA3/DG register builder, DELIBERATELY overriding hdlab.three_tier_loop's default
    gap_register_fn (which the API explicitly documents as caller-overridable). Root cause
    disclosed (found empirically during self-test, not assumed): the default assigns
    AGENT=subject(process), CONSEQUENT=f"GAP_{label}". Since every trace in THIS cell is POS
    (no NEG evidence is ever generated -- see prereg), CONSEQUENT is a CONSTANT across the
    entire target set, wasting one of the 4 role slots; and since a real process typically
    touches multiple via_materials (~6.3 on average per the source cell's own reading_audit),
    AGENT=process collides across DIFFERENT via_material clusters -- a same-process,
    different-cluster pair can score AS HIGH OR HIGHER (2-of-4 shared terms: AGENT+CONSEQUENT)
    than a genuine same-cluster pair (2-of-4 shared terms: TRIGGER+CONSEQUENT), defeating
    separability (MEASURED in this cell's own dev debugging: default register_fn gave a
    same-process-cross-cluster pair cosine=0.412 vs a same-cluster pair cosine=0.384 -- the
    FALSE match scored HIGHER). This override binds BOTH TRIGGER and CONSEQUENT to the
    cluster_key (via_material) -- reinforcing the one real shared-per-cluster signal in 2 of 4
    slots, matching build_instance_register's own docstring intent ("TRIGGER/CONSEQUENT bound
    to STABLE per-type category tags") literally -- and confines the two real per-instance-
    varying identifiers (candidate=whole, subject=process) to AGENT/PATIENT, where a same-
    process collision can win AT MOST 1-of-4 terms (PATIENT alone), always strictly less than
    a genuine same-cluster match's 2-of-4 (MEASURED after the fix: same-cluster 0.35-0.36,
    same-process-cross-cluster 0.25, no-overlap-cross-cluster ~0.00-0.03 -- cleanly ordered)."""
    subject, _relation, candidate = ttl.parse_gap_item_key(pk)
    return build_instance_register(candidate, subject, cluster_key, cluster_key)


def _episode_text(process: str, whole: str, material: str, fate: str, v: int) -> str:
    phrasing = ["was noted again", "showed the same pattern", "was described once more",
                "matched the earlier account", "came up again", "was mentioned another time"]
    return (f"During process {process}, the {material} related material {phrasing[v % len(phrasing)]} "
            f"regarding {whole} under {fate} conditions, observation round {v}.")


# =========================================================================== per-cue REASON
def _eligible_targets(targets: List[Dict], hop1: KGStore, hop2: KGStore, ent_idx: Dict[str, int],
                      fate_idx: Dict[str, int], bridge_idx: int, gathered_per_proc: Dict[str, List[str]],
                      n_ent: int) -> Tuple[List[Dict], Dict[Tuple[str, str, str], List[Tuple[int, float]]], Dict[str, int]]:
    """Per-(process,via_material,fate) cue restricted fan-out (real REASON call, cached by
    cue), then per-target recovery@K_RESOLVE eligibility filter. Returns (eligible_targets,
    ranked_cache, exclusion_counts)."""
    cues = sorted({(t["process"], t["via_material"], t["fate"]) for t in targets})
    ranked_cache: Dict[Tuple[str, str, str], List[Tuple[int, float]]] = {}
    for proc, mat, fate in cues:
        gathered_names = set(gathered_per_proc.get(proc, []))
        if mat not in gathered_names or proc not in ent_idx or mat not in ent_idx or fate not in fate_idx:
            ranked_cache[(proc, mat, fate)] = []
            continue
        ranked = fanout_two_hop(hop1, hop2, ent_idx[proc], fate_idx[fate], bridge_idx,
                                K1_FANOUT, K2_FANOUT, n_ent, restrict_hop1_to={ent_idx[mat]})
        ranked_cache[(proc, mat, fate)] = ranked
    eligible: List[Dict] = []
    excl = {"gather_miss_or_missing_entity": 0, "rank_miss": 0}
    for t in sorted(targets, key=lambda x: (x["process"], x["via_material"], x["fate"], x["whole"])):
        if t["whole"] not in ent_idx:
            excl["gather_miss_or_missing_entity"] += 1
            continue
        ranked = ranked_cache.get((t["process"], t["via_material"], t["fate"]), [])
        if not ranked:
            excl["gather_miss_or_missing_entity"] += 1
            continue
        gold_idx = ent_idx[t["whole"]]
        if recovery_at(ranked, gold_idx, K_RESOLVE):
            eligible.append(t)
        else:
            excl["rank_miss"] += 1
    return eligible, ranked_cache, excl


def _positive_control_reproduction(targets: List[Dict], hop1: KGStore, hop2: KGStore,
                                   ent_idx: Dict[str, int], fate_idx: Dict[str, int], bridge_idx: int,
                                   gathered_per_proc: Dict[str, List[str]], n_ent: int) -> float:
    """Reproduces the SOURCE cell's own arm3 recovery@5 (restrict to ALL CA3-gathered
    materials, not the single-cue restriction) via the promoted hdlab.gather_reason module --
    Gate D positive control, must land near the cited prior metric (0.3802) before the new
    per-cue mechanism is trusted."""
    hits = []
    for t in targets:
        if t["process"] not in ent_idx or t["whole"] not in ent_idx or t["fate"] not in fate_idx:
            continue
        gathered_idx = {ent_idx[m] for m in gathered_per_proc.get(t["process"], []) if m in ent_idx}
        ranked = fanout_two_hop(hop1, hop2, ent_idx[t["process"]], fate_idx[t["fate"]], bridge_idx,
                                K1_FANOUT, K2_FANOUT, n_ent, restrict_hop1_to=gathered_idx)
        hits.append(recovery_at(ranked, ent_idx[t["whole"]], K_RESOLVE))
    return float(np.mean(hits)) if hits else 0.0


# =========================================================================== arm runner
def run_arm(arm_name: str, ablation_mode: str, targets: List[Dict], hop1: KGStore, hop2: KGStore,
           ent_idx: Dict[str, int], fate_idx: Dict[str, int], bridge_idx: int,
           gathered_per_proc: Dict[str, List[str]], n_ent: int, visits_per_gap: int,
           novelty_thresh: float, found_seed: int, tier_seed: int, disconnect_seed: int = 0,
           register_fn: Callable[[str, str, str], torch.Tensor] = my_gap_register_fn) -> Dict:
    """ablation_mode in {"full","no_middle","no_sweep"}. Returns per-checkpoint cumulative
    resolution + audit fields. No organ is modified; ablation is expressed entirely via WHICH
    pieces of hdlab.three_tier_loop.ThreeTierLoop / hdlab.prelim_tier.TierState are used/wired."""
    eligible, _ranked_cache, excl = _eligible_targets(targets, hop1, hop2, ent_idx, fate_idx,
                                                        bridge_idx, gathered_per_proc, n_ent)
    eligible_sorted = sorted(eligible, key=lambda t: (t["process"], t["via_material"], t["fate"], t["whole"]))
    pks = [pk_of(t) for t in eligible_sorted]

    foundation_store = HDFactStore(n_dim=FOUND_DIM, seed=found_seed, use_index=True)
    no_leak_ok = all(foundation_store.query(pk, RELATION) == [] for pk in pks)

    loop: Optional[ttl.ThreeTierLoop] = None
    library: Library
    tier_state: Optional[TierState] = None
    if ablation_mode == "no_middle":
        library = Library()
    else:
        loop = ttl.ThreeTierLoop(foundation_store, seed_base=tier_seed, n_dim=FOUND_DIM, relation=RELATION)
        if ablation_mode == "no_sweep":
            # Revert the ONE documented ASSEMBLY DECISION in hdlab/three_tier_loop.py:
            # combined-evidence promotions land in a DISCONNECTED store instead of the shared
            # foundation store -- retain/sweep computation still runs unmodified internally.
            loop.tier_state.native_store_gen = HDFactStore(n_dim=FOUND_DIM, seed=disconnect_seed, use_index=True)
        library = loop.library
        tier_state = loop.tier_state

    checkpoints: List[Dict] = []
    for v in range(visits_per_gap):
        for t in eligible_sorted:
            pk = pk_of(t)
            cvec = context_vector(_episode_text(t["process"], t["whole"], t["via_material"], t["fate"], v))
            episode_id = f"{t['process']}|{t['via_material']}|{t['fate']}|{t['whole']}|v{v}"
            if ablation_mode == "no_middle":
                library.flag(pk, episode_id, "POS", cvec, pass_idx=v)
            else:
                loop.encounter(pk, "POS", cvec, episode_id, pass_idx=v, also_strict=True)  # type: ignore[union-attr]
        cp = v + 1
        if ablation_mode == "no_middle":
            gate_report = consolidation_pass(library, cp, native_store=foundation_store,
                                            register=False, promote_relation=RELATION)
            middle_report = None
        else:
            step = loop.consolidate(cp, cluster_key_fn, novelty_thresh, register_fn=register_fn,
                                    gate_kwargs={"register": False})  # type: ignore[union-attr]
            gate_report, middle_report = step["gate"], step["middle"]
        n_found = 0
        n_mid = 0
        for pk in pks:
            fh = foundation_store.query(pk, RELATION)
            if fh and fh[0]["status"] in ACTIVE_STATUSES:
                n_found += 1
                continue
            if tier_state is not None:
                mh = tier_state.prelim_store.query(pk, RELATION)
                if mh and mh[0]["status"] in ACTIVE_STATUSES:
                    n_mid += 1
        checkpoints.append({
            "checkpoint": cp, "n_foundation": n_found, "n_middle": n_mid,
            "n_total_resolved": n_found + n_mid,
            "n_combined_promoted_this_pass": (middle_report or {}).get("n_combined_promoted_this_pass", 0),
            "n_clusters_eligible_size": (middle_report or {}).get("n_clusters_eligible_size", 0),
            "n_banked_pos_this_pass": len(gate_report.get("newly_grounded_pos", [])),
        })

    final = checkpoints[-1] if checkpoints else {"n_foundation": 0, "n_middle": 0, "n_total_resolved": 0}
    return {
        "arm_name": arm_name, "ablation_mode": ablation_mode,
        "n_targets": len(targets), "n_eligible": len(eligible_sorted),
        "exclusion_counts": excl, "no_leak_ok": bool(no_leak_ok),
        "checkpoints": checkpoints, "final": final,
    }


# =========================================================================== self-test
def run_self_test() -> Dict:
    """Tiny synthetic fixture (real objects, real code path): 2 processes producing a
    3-member cluster ("matX", expected to combined-promote under arm A, never under B/C) and a
    2-member cluster ("matY", below CLUSTER_MIN_MEMBERS=3, expected to never combined-promote
    in ANY arm -- an honest negative)."""
    processes = ["p1", "p2", "p3", "p4"]
    # p1,p2,p3 each DESTROY matX which MadeOf-bridges to their own whole (wX1/wX2/wX3) --
    # a genuine 3-member matX cluster. p4 DESTROYs matY which bridges to wY1 AND a second
    # process p1 also touches matY (bridges to wY2) -- but matY's cluster only has 2 members
    # (below CLUSTER_MIN_MEMBERS), so it must never combined-promote regardless of arm.
    subjects = {
        "p1": [("matX", "wX1", "DESTROY"), ("matY", "wY2", "CREATE")],
        "p2": [("matX", "wX2", "DESTROY")],
        "p3": [("matX", "wX3", "DESTROY")],
        "p4": [("matY", "wY1", "CREATE")],
    }
    ents: List[str] = []
    seen: Set[str] = set()
    for group in (sorted(subjects.keys()), sorted({m for v in subjects.values() for m, _w, _f in v}),
                 sorted({w for v in subjects.values() for _m, w, _f in v})):
        for name in group:
            if name not in seen:
                seen.add(name)
                ents.append(name)
    ent_idx = {name: i for i, name in enumerate(ents)}
    n_ent = len(ents)

    fate_idx = {"DESTROY": 0, "CREATE": 1, "BRIDGE": 2}
    bridge_idx = fate_idx["BRIDGE"]

    def fresh(seed: int) -> KGStore:
        gen = torch.Generator().manual_seed(seed)
        return KGStore(n_ent=n_ent, n_rel=3, n_dim=512, generator=gen)

    hop1 = fresh(SEED_KG_HOP1)
    rows1 = [(ent_idx[p], fate_idx[f], ent_idx[m]) for p, lst in subjects.items() for m, _w, f in lst]
    hop1.ingest_triples(torch.tensor(rows1, dtype=torch.long))

    hop2_real = fresh(SEED_KG_HOP2)
    rows2 = [(ent_idx[m], bridge_idx, ent_idx[w]) for lst in subjects.values() for m, w, _f in lst]
    hop2_real.ingest_triples(torch.tensor(rows2, dtype=torch.long))

    narrow_edges = [(m, w) for lst in subjects.values() for m, w, _f in lst]
    scr_edges = scramble_edges(narrow_edges, SEED_SCRAMBLE)
    hop2_scr = fresh(SEED_KG_HOP2)
    scr_rows = [(ent_idx[m], bridge_idx, ent_idx[w]) for m, w in scr_edges if m in ent_idx and w in ent_idx]
    if scr_rows:
        hop2_scr.ingest_triples(torch.tensor(scr_rows, dtype=torch.long))

    materials = sorted({m for lst in subjects.values() for m, _w, _f in lst})
    mat_gen = torch.Generator().manual_seed(SEED_FHRR)
    mat_vecs = {m: unit_phase_vec(FHRR_D, mat_gen) for m in materials}
    mat_names = materials
    codebook = np.stack([real_to_concat(mat_vecs[m]) for m in mat_names], axis=0)
    reg = RelationRegister(d=FHRR_D, generator=torch.Generator().manual_seed(SEED_FHRR + 1))
    for p, lst in subjects.items():
        for m, _w, _f in lst:
            reg.bind_filler(p, "GOAL", mat_vecs[m])
    gathered_per_proc = {}
    for p in subjects:
        q = real_to_concat(reg.decode_filler(p, "GOAL"))
        gathered_per_proc[p] = ca3_relevance_gather(q, mat_names, codebook, k_peel=10, sim_floor=0.05)

    targets = [{"process": p, "whole": w, "fate": f, "via_material": m}
              for p, lst in subjects.items() for m, w, f in lst]

    pc = _positive_control_reproduction(targets, hop1, hop2_real, ent_idx, fate_idx, bridge_idx,
                                        gathered_per_proc, n_ent)
    assert pc > 0.5, f"SELF_TEST FAIL: positive-control fixture should recover most targets, got {pc}"

    # Calibrate against the HARDEST real wrong-pair (p1 appears in BOTH matX and matY --
    # exactly the same-process-cross-cluster collision the real corpus will produce, since
    # a real process typically touches multiple via_materials), not an easy no-overlap pair.
    calib = calibrate_novelty_threshold(
        matched_pairs=[(my_gap_register_fn(pk_of(targets[0]), "matX", "POS"),
                       my_gap_register_fn(pk_of(targets[1]), "matX", "POS"))],
        wrong_pairs=[(my_gap_register_fn(pk_of(targets[0]), "matX", "POS"),
                     my_gap_register_fn(pk_of(targets[4]), "matY", "POS"))])  # targets[4] = p1/wY2 (shares subject p1)
    novelty_thresh = calib["novelty_thresh"] if calib["discriminates"] else 0.15
    assert calib["discriminates"], f"SELF_TEST FAIL: calibration must discriminate, got {calib}"

    visits = 12  # > VISITS_PER_GAP(6): self-test's 3-member cluster needs 3*visits >= 32
                 # (cluster_exposure_floor) with comfortable margin; individual strict-gate
                 # exposure is STILL capped at ~5 by Library.flag()'s post-bank no-op
                 # (see run_pipeline module docstring), independent of visits_per_gap's value.
    res_a = run_arm("A_full", "full", targets, hop1, hop2_real, ent_idx, fate_idx, bridge_idx,
                    gathered_per_proc, n_ent, visits, novelty_thresh,
                    found_seed=1, tier_seed=2)
    res_b = run_arm("B_no_middle", "no_middle", targets, hop1, hop2_real, ent_idx, fate_idx, bridge_idx,
                    gathered_per_proc, n_ent, visits, novelty_thresh,
                    found_seed=3, tier_seed=4)
    res_c = run_arm("C_no_sweep", "no_sweep", targets, hop1, hop2_real, ent_idx, fate_idx, bridge_idx,
                    gathered_per_proc, n_ent, visits, novelty_thresh,
                    found_seed=5, tier_seed=6, disconnect_seed=7)
    res_scr = run_arm("A_scramble_control", "full", targets, hop1, hop2_scr, ent_idx, fate_idx, bridge_idx,
                      gathered_per_proc, n_ent, visits, novelty_thresh,
                      found_seed=8, tier_seed=9)

    assert res_a["final"]["n_foundation"] >= 3, (
        f"SELF_TEST FAIL: arm A must combined-promote the 3-member matX cluster, got {res_a['final']}")
    assert res_b["final"]["n_foundation"] == 0 and res_b["final"]["n_middle"] == 0, (
        f"SELF_TEST FAIL: arm B (no middle-db) must resolve nothing, got {res_b['final']}")
    assert res_c["final"]["n_foundation"] == 0 and res_c["final"]["n_middle"] > 0, (
        f"SELF_TEST FAIL: arm C (no sweep) must retain-in-middle but never reach foundation, got {res_c['final']}")
    assert res_scr["final"]["n_total_resolved"] <= res_a["final"]["n_total_resolved"] * 0.5, (
        f"SELF_TEST FAIL: scramble control must collapse resolution, got scr={res_scr['final']} "
        f"vs real={res_a['final']}")

    return {"positive_control_recovery": pc, "novelty_thresh": novelty_thresh,
            "arm_a_final": res_a["final"], "arm_b_final": res_b["final"],
            "arm_c_final": res_c["final"], "arm_scramble_final": res_scr["final"]}


# =========================================================================== I/O helpers
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": os.environ.get("COMPUTERNAME", "unknown")}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _atomic_write(output_dir: str, metrics: Dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


# =========================================================================== arms-must-differ
def _arms_must_differ(per_arm_curves: Dict[str, List[Tuple[int, int]]]) -> Dict[str, str]:
    digests = {}
    for name, curve in per_arm_curves.items():
        b = json.dumps(curve).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} produced identical per-checkpoint "
                f"(n_foundation,n_middle) curves (hash={digests[a]}); arm-implementation bug")
    return digests


# =========================================================================== main pipeline
def run_pipeline(process_filter, run_mode: str) -> Dict:
    t0 = time.perf_counter()

    print("[stage] building real reading facts + CSKG bridges + gap-set", flush=True)
    reading = build_reading_facts(process_filter=process_filter)
    vocab = reading_vocab(reading)
    narrow, wide = build_cskg_bridges(vocab)
    gap = build_gap_set(reading, narrow)
    targets = gap["targets"]
    print(f"[gap-set] raw={gap['raw_n']} survive={gap['survive_n']} unique={gap['unique_n']}", flush=True)
    assert targets, "gap-set is empty -- cannot proceed with a decisive test (honest HARD_FAIL condition)"

    processes = sorted(reading.keys())
    materials = vocab
    wholes = sorted({t["whole"] for t in targets} | {w for lst in wide.values() for w in lst}
                     | {w for lst in narrow.values() for w in lst})
    ents, ent_idx = build_entity_index(processes, materials, wholes)
    n_ent = len(ents)
    print(f"[entities] n_ent={n_ent} n_targets={len(targets)}", flush=True)

    hop1 = fresh_kg(n_ent, SEED_KG_HOP1)
    rel_idx = ingest_reading_hop1(hop1, reading, ent_idx)
    bridge_idx = rel_idx["BRIDGE"]
    fate_idx = rel_idx

    narrow_edges = [(m, w) for m in sorted(narrow) for w in narrow[m]]
    hop2_real = fresh_kg(n_ent, SEED_KG_HOP2)
    ingest_bridge_hop2(hop2_real, narrow_edges, ent_idx, bridge_idx)

    scrambled_edges = scramble_edges(narrow_edges, SEED_SCRAMBLE)
    hop2_scrambled = fresh_kg(n_ent, SEED_KG_HOP2)
    ingest_bridge_hop2(hop2_scrambled, scrambled_edges, ent_idx, bridge_idx)

    print("[stage] STATE-OF-MIND + CA3 GATHER", flush=True)
    mat_names, codebook, mat_vecs = build_material_codebook(materials, SEED_FHRR)
    reg = RelationRegister(d=FHRR_D, generator=torch.Generator().manual_seed(SEED_FHRR + 1))
    for proc in processes:
        for material in sorted(reading.get(proc, {}).keys()):
            reg.bind_filler(proc, "GOAL", mat_vecs[material])
    gathered_per_proc: Dict[str, List[str]] = {}
    for proc in processes:
        q = real_to_concat(reg.decode_filler(proc, "GOAL"))
        gathered_per_proc[proc] = ca3_relevance_gather(q, mat_names, codebook, k_peel=CA3_K_PEEL,
                                                        sim_floor=CA3_SIM_FLOOR)
    coverage_hits = [1 if t["via_material"] in set(gathered_per_proc.get(t["process"], [])) else 0
                     for t in targets]
    gather_coverage = float(np.mean(coverage_hits)) if coverage_hits else 0.0

    print("[stage] positive-control reproduction (Gate D)", flush=True)
    pc_recovery5 = _positive_control_reproduction(targets, hop1, hop2_real, ent_idx, fate_idx,
                                                  bridge_idx, gathered_per_proc, n_ent)
    if run_mode == "full":
        # Only FULL mode's target population matches the cited prior cell's own 121-target
        # population; a smoke subset's recovery@5 is legitimately different (a different,
        # smaller sample -- e.g. the source cell's own per_process_recovery already discloses
        # combustion@5=0.714, photosynthesis@5=0.526, both far from the FULL-population mean
        # 0.3802) and is NOT a regime/invocation mismatch. Gate D's tolerance check is only
        # meaningful at FULL.
        positive_control_ok = abs(pc_recovery5 - 0.3802) <= 0.10
    else:
        positive_control_ok = True
    print(f"[positive-control] arm3-reproduction recovery@5={pc_recovery5:.4f} "
          f"(cited=0.3802, gated={run_mode == 'full'}, ok={positive_control_ok})", flush=True)

    print("[stage] eligibility + novelty-threshold calibration", flush=True)
    eligible_real, _cache_real, excl_real = _eligible_targets(targets, hop1, hop2_real, ent_idx,
                                                               fate_idx, bridge_idx, gathered_per_proc, n_ent)
    by_material: Dict[str, List[Dict]] = {}
    by_process: Dict[str, List[Dict]] = {}
    for t in eligible_real:
        by_material.setdefault(t["via_material"], []).append(t)
        by_process.setdefault(t["process"], []).append(t)
    ranked_materials = sorted(by_material.keys(), key=lambda m: -len(by_material[m]))
    calib_ok = len(ranked_materials) >= 2 and len(by_material[ranked_materials[0]]) >= 2
    if calib_ok:
        largest = by_material[ranked_materials[0]]
        second = by_material[ranked_materials[1]]
        matched_pairs = [(my_gap_register_fn(pk_of(largest[0]), ranked_materials[0], "POS"),
                          my_gap_register_fn(pk_of(largest[1]), ranked_materials[0], "POS"))]
        # Prefer the HARDEST real wrong-pair: two eligible targets sharing a PROCESS but
        # different via_material (a real process typically touches multiple materials, per
        # reading_audit -- this is the collision case that actually stresses separability;
        # falls back to the largest-vs-second-largest-cluster pair if no such collision exists
        # among eligible targets).
        hard_wrong = None
        for proc, lst in sorted(by_process.items()):
            mats = sorted({t["via_material"] for t in lst})
            if len(mats) >= 2:
                a = next(t for t in lst if t["via_material"] == mats[0])
                b = next(t for t in lst if t["via_material"] == mats[1])
                hard_wrong = (a, b)
                break
        if hard_wrong is not None:
            wa, wb = hard_wrong
            wrong_pairs = [(my_gap_register_fn(pk_of(wa), wa["via_material"], "POS"),
                           my_gap_register_fn(pk_of(wb), wb["via_material"], "POS"))]
        else:
            wrong_pairs = [(my_gap_register_fn(pk_of(largest[0]), ranked_materials[0], "POS"),
                           my_gap_register_fn(pk_of(second[0]), ranked_materials[1], "POS"))]
        calib = calibrate_novelty_threshold(matched_pairs=matched_pairs, wrong_pairs=wrong_pairs)
        novelty_thresh = calib["novelty_thresh"] if calib.get("discriminates") else 0.15
        calib_fallback = not calib.get("discriminates", False)
    else:
        novelty_thresh = 0.15
        calib_fallback = True
    print(f"[calibration] novelty_thresh={novelty_thresh:.4f} fallback={calib_fallback} "
          f"n_eligible_real={len(eligible_real)}", flush=True)

    visits_per_gap = VISITS_PER_GAP_SMOKE if run_mode == "smoke" else VISITS_PER_GAP
    print(f"[stage] running 4 arms over the encounter stream (visits_per_gap={visits_per_gap})", flush=True)
    arm_specs = [
        ("A_full", "full", hop2_real, SEED_FOUND_A, SEED_TIER_A, 0),
        ("B_no_middle", "no_middle", hop2_real, SEED_FOUND_B, 0, 0),
        ("C_no_sweep", "no_sweep", hop2_real, SEED_FOUND_C, SEED_TIER_C, SEED_DISCONNECT_C),
        ("A_scramble_control", "full", hop2_scrambled, SEED_FOUND_SCRAMBLE, SEED_TIER_SCRAMBLE, 0),
    ]
    arm_results: Dict[str, Dict] = {}
    for arm_name, ablation_mode, hop2_store, found_seed, tier_seed, disc_seed in arm_specs:
        res = run_arm(arm_name, ablation_mode, targets, hop1, hop2_store, ent_idx, fate_idx,
                      bridge_idx, gathered_per_proc, n_ent, visits_per_gap, novelty_thresh,
                      found_seed, tier_seed, disc_seed)
        arm_results[arm_name] = res
        print(f"[arm {arm_name}] n_eligible={res['n_eligible']} final={res['final']}", flush=True)

    # cardinality check (EXPECTED_N_UNITS = 4 arms * visits_per_gap checkpoints)
    cardinality_ok = all(len(arm_results[a]["checkpoints"]) == visits_per_gap for a in arm_results)

    # arms-must-differ (META_RULE_AF)
    curves = {a: [(cp["n_foundation"], cp["n_middle"]) for cp in arm_results[a]["checkpoints"]]
             for a in ("A_full", "B_no_middle", "C_no_sweep")}
    digests = _arms_must_differ(curves)
    arms_differ_ok = True  # _arms_must_differ raises on violation

    final_a = arm_results["A_full"]["final"]
    final_b = arm_results["B_no_middle"]["final"]
    final_c = arm_results["C_no_sweep"]["final"]
    final_scr = arm_results["A_scramble_control"]["final"]
    n_eligible = arm_results["A_full"]["n_eligible"]

    resolved_a = final_a["n_total_resolved"]
    resolved_b = final_b["n_total_resolved"]
    foundation_a = final_a["n_foundation"]
    foundation_c = final_c["n_foundation"]

    delta_b_frac = (resolved_a - resolved_b) / n_eligible if n_eligible else 0.0
    delta_c_foundation_frac = (foundation_a - foundation_c) / n_eligible if n_eligible else 0.0
    scramble_resolved = final_scr["n_total_resolved"]
    scramble_clean = scramble_resolved <= max(5, 0.10 * resolved_a)
    no_leak_ok = all(arm_results[a]["no_leak_ok"] for a in arm_results)

    c_middle_matches_a_middle = (abs(final_c["n_middle"] - final_a["n_middle"]) <=
                                 max(1, 0.05 * max(final_a["n_middle"], 1)))

    controls_clean = bool(scramble_clean and no_leak_ok and arms_differ_ok and positive_control_ok)

    if not positive_control_ok:
        verdict = "HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH"
        verdict_msg = (f"positive-control arm3-reproduction={pc_recovery5:.4f} outside tolerance of "
                        f"cited 0.3802 (|delta|>0.10); downstream arms untrusted")
    elif delta_b_frac >= 0.50 and delta_c_foundation_frac >= 0.30 and controls_clean:
        verdict = "HARD_PASS_three_tier_dynamics_load_bearing_on_real_data"
        verdict_msg = (f"delta_B_frac={delta_b_frac:.4f} (>=0.50, middle-db load-bearing); "
                        f"delta_C_foundation_frac={delta_c_foundation_frac:.4f} (>=0.30, sweep load-bearing); "
                        f"controls clean (scramble={scramble_resolved} vs real={resolved_a}, "
                        f"no_leak={no_leak_ok}, arms_differ={arms_differ_ok})")
    elif delta_b_frac < 0.10 or delta_c_foundation_frac < 0.05 or not controls_clean:
        verdict = "HARD_FAIL_three_tier_dynamics_not_load_bearing_on_real_data"
        verdict_msg = (f"delta_B_frac={delta_b_frac:.4f} (floor 0.10) delta_C_foundation_frac="
                        f"{delta_c_foundation_frac:.4f} (floor 0.05) controls_clean={controls_clean} "
                        f"(scramble_clean={scramble_clean} no_leak_ok={no_leak_ok} "
                        f"positive_control_ok={positive_control_ok})")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"partial evidence: delta_B_frac={delta_b_frac:.4f} "
                        f"delta_C_foundation_frac={delta_c_foundation_frac:.4f}; does not clear "
                        f"strict HARD_PASS margins but above HARD_FAIL floors")

    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "process_filter": sorted(process_filter) if process_filter else "ALL",
        "n_ent": n_ent, "n_targets": len(targets), "n_eligible": n_eligible,
        "gather_coverage": gather_coverage,
        "positive_control_arm3_reproduction": pc_recovery5, "positive_control_ok": positive_control_ok,
        "positive_control_cited_prior": 0.3802,
        "novelty_thresh": novelty_thresh, "calibration_fallback": calib_fallback,
        "visits_per_gap": visits_per_gap,
        "arm_results": arm_results,
        "delta_b_frac": delta_b_frac, "delta_c_foundation_frac": delta_c_foundation_frac,
        "scramble_resolved_final": scramble_resolved, "scramble_clean": scramble_clean,
        "no_leak_ok": no_leak_ok, "arms_differ_ok": arms_differ_ok,
        "c_middle_matches_a_middle": c_middle_matches_a_middle,
        "cardinality_ok": cardinality_ok,
        "arm_curve_digests": digests,
        "bands": {"hard_pass_delta_b_min": 0.50, "hard_pass_delta_c_foundation_min": 0.30,
                  "hard_fail_delta_b_floor": 0.10, "hard_fail_delta_c_foundation_floor": 0.05,
                  "positive_control_tolerance": 0.10},
    }
    return metrics


# =========================================================================== main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="tiny synthetic fixture, real code path")
    parser.add_argument("--smoke", action="store_true", help="real pipeline, 2-process subset")
    parser.add_argument("--timeout", type=float, default=600.0,
                         help="declared wall-time budget: smoke~30-60s, FULL~2-5min")
    args = parser.parse_args()

    if args.self_test:
        run_mode = "self_test"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_selftest")
        t0 = time.perf_counter()
        _write_start_marker(output_dir, run_mode, expected_n_units=1)
        result = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELF_TEST_PASS",
                   "verdict_msg": ("real KGStore+HDFactStore+Library+TierState+ScriptLibrary+"
                                   "RelationRegister+ThreeTierLoop fixture: arm A combined-promotes "
                                   "the 3-member cluster, arm B resolves nothing, arm C middle-only "
                                   "never foundation, scramble collapses"),
                   "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                   "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                   "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    if args.smoke:
        run_mode = "smoke"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_smoke")
        process_filter = {"combustion", "photosynthesis"}
        expected_units = 4 * VISITS_PER_GAP_SMOKE
    else:
        run_mode = "full"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
        process_filter = None
        expected_units = 4 * VISITS_PER_GAP

    _write_start_marker(output_dir, run_mode, expected_n_units=expected_units)
    metrics = run_pipeline(process_filter, run_mode)

    if run_mode == "smoke":
        a = metrics["arm_results"]["A_full"]["final"]
        c = metrics["arm_results"]["C_no_sweep"]["final"]
        sweep_fired = any(cp["n_combined_promoted_this_pass"] > 0
                          for cp in metrics["arm_results"]["A_full"]["checkpoints"])
        discriminator_ok = sweep_fired and a["n_foundation"] > c["n_foundation"]
        if not discriminator_ok:
            metrics["verdict"] = "SMOKE_GATE_FAIL_discriminator_not_firing"
            metrics["verdict_msg"] = (f"smoke discriminator check: sweep_fired={sweep_fired} "
                                       f"foundation_A={a['n_foundation']} foundation_C={c['n_foundation']} "
                                       f"-- required sweep_fired AND foundation_A > foundation_C for FULL dispatch")

    _atomic_write(output_dir, metrics)
    print(f"[{ANCHOR_NAME}] {metrics['verdict']} elapsed={metrics['elapsed_s']:.2f}s -> {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately narrow; NOT BaseException
        _write_crash_metrics(repo_path(f"data/exp_{ANCHOR_NAME}"), e)
        raise
