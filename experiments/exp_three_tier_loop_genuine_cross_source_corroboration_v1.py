# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: G_full vs R_reference asserted; G_full vs {G_no_middle,G_no_sweep,
#   G_scramble} EXEMPTED (pre-registered rationale: all 4 G_* arms share the SAME genuine
#   encounter stream, whose per-item trace count never reaches MIN_CONFIRM=4 regardless of tier
#   wiring or chain-scrambling -- see preregs/2026-08-11_three_tier_loop_genuine_cross_source_
#   corroboration_v1.md "Controls" section)
# - final_metrics_atomicity = tmp_replace (single-shot)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: discrete per-item trace-count retain floor (n>=MIN_CONFIRM=4), not a Gaussian
#   noise-floor metric; discriminator_reachability=FALSE for G_full by measured Step-1 ceiling
#   (max 3 real distinct sources per gap) vs MIN_CONFIRM=4 -- verified empirically below, not
#   just hand-computed (self-test proves the SAME code path DOES promote at n=4/size=10)
# - baseline_in_band EXEMPTED for G_no_middle/G_no_sweep/G_scramble (deliberate ablation/sentinel
#   arms; ALL G_* arms including G_full are expected near-zero by the pre-registered arithmetic)
# - discriminator survives scale: smoke gate checks R_reference (the reused-mechanism sanity arm)
#   fires normally, NOT G_full (G_full is analytically expected to stay at 0 at any scale)
# - HP_SCOPE: HARD_PASS/HARD_FAIL gates apply to G_full only; R_reference carries its own single
#   reproduces_prior gate
# - cardinality_ok: EXPECTED checkpoints = n_waves (2 smoke / 3 full) for each G_* arm,
#   VISITS_PER_GAP(6, or VISITS_PER_GAP_SMOKE at smoke) for R_reference
# - per-unit failure-class instrumentation: N/A (single deterministic pass per arm, 5 arms total)
# - calibration_check: default_ok_for_this_regime (novelty_thresh calibrated identically to the
#   landed cell, imported verbatim, over this run's own real eligible-target cluster structure)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL KGStore/HDFactStore/Library/TierState/ScriptLibrary/RelationRegister/
#   ThreeTierLoop objects (via the reused source cell's own self-test) PLUS a new tiny fixture
#   isolating the MIN_CONFIRM=4 boundary (real_code_path)
# - substrate_signature_checked: KGStore/HDFactStore/ThreeTierLoop/TierState base kwargs only
"""exp_three_tier_loop_genuine_cross_source_corroboration_v1 -- removes the one honest caveat in
the landed exp_three_tier_loop_real_corpus_gap_stream_v1 (commit 73c54d094): that cell's 6
encounters/gap were TEMPLATED-SYNTHETIC repeats of the SAME fact. This cell replaces them with
GENUINE DISTINCT-SOURCE encounters -- each real source (CSKG, CauseNet-precision, a ProPara-
derived process-physics KB, go.obo) that independently carries weak/partial evidence for a gap
counts as ONE real encounter, never repeated -- and measures whether accumulating this GENUINE
cross-source corroboration in the middle-db + consolidation sweep crosses the same strict
combined-evidence gate on real data. See preregs/2026-08-11_three_tier_loop_genuine_cross_source_
corroboration_v1.md for the full design (Step-1 measurement table, Step-2 mechanism arithmetic,
arms, bands, self-test, schema-vet declarations).

STEP 1 (the headline measurement, computed inline every run): for each of the 121 real MadeOf-
bridge gaps, how many of 4 named sources carry weak/partial evidence? CSKG's /r/MadeOf edge
defines the gap (trivially present for all 121); CauseNet-precision and a ProPara-derived
process-physics KB (data/benchmark_trap_check/propara_process_physics_kb_v1.json, loaded via the
SAME dependency chain as data/exp_bootstrap_dense_process_article_reading_fade_v6/'s own _load_kb
-- that cell's OWN reading-extraction leg was measured NON-independent of the gap-set's S_READ,
same corpus + same extractor, so it is excluded and this KB substituted, disclosed in the
pre-reg) each independently corroborate a real subset; go.obo (Gene Ontology) is measured to
contribute ZERO genuine material/whole-level evidence (its only literal hit is the process name
"photosynthesis" itself, a name-existence coincidence with no relational content).
MEASURED@preregs/2026-08-11_three_tier_loop_genuine_cross_source_corroboration_v1.md: 54/121 all
gaps (44.6%) and 36/62 eligible gaps (58.1%) have >=2 real distinct sources; max observed = 3
(CSKG+CauseNet+KB); MIN_CONFIRM=4 (hdlab.grounding_acquisition_loop) is the retain-into-middle-
tier floor a gap's own trace count must clear BEFORE it can even be registered into a CA3/DG
cluster -- 3 < 4 predicts G_full's combined-evidence promotion stays at 0 regardless of cluster
size, a mechanism-level (not merely observational) finding this cell VERIFIES by actually running
the real pipeline.

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim; NONE
modified by this cell):
  hdlab.three_tier_loop.ThreeTierLoop / gap_item_key / parse_gap_item_key
  hdlab.grounding_acquisition_loop.Library / consolidation_pass / context_vector / MIN_CONFIRM /
    PROMOTE_MIN_EXPOSURE / PROMOTE_MIN_CONSISTENCY
  hdlab.prelim_tier.TierState / update_prelim_and_generalize / CLUSTER_MIN_MEMBERS /
    CLUSTER_EXPOSURE_MULTIPLIER
  hdlab.hd_fact_store.HDFactStore / ACTIVE_STATUSES
  hdlab.script_grain_acquisition_loop.calibrate_novelty_threshold / build_instance_register
  hdlab.gather_reason.ca3_relevance_gather / fanout_two_hop / recovery_at / real_to_concat
  hdlab.situation_model_accumulate.RelationRegister / unit_phase_vec
  hdlab.kg_traversal.KGStore
  experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1's own build functions
    (build_reading_facts, reading_vocab, build_cskg_bridges, build_gap_set, build_entity_index,
    fresh_kg, ingest_reading_hop1, ingest_bridge_hop2, build_material_codebook, scramble_edges)
  experiments.exp_three_tier_loop_real_corpus_gap_stream_v1's own functions (pk_of,
    cluster_key_fn, my_gap_register_fn, _eligible_targets, _positive_control_reproduction,
    run_arm, run_self_test, VISITS_PER_GAP, VISITS_PER_GAP_SMOKE, K1_FANOUT, K2_FANOUT,
    CA3_K_PEEL, CA3_SIM_FLOOR, FHRR_D, FOUND_DIM, RELATION, SEED_KG_HOP1, SEED_KG_HOP2,
    SEED_SCRAMBLE, SEED_FHRR)

THE ONE NEW THING (honestly disclosed): (a) a Step-1 cross-source-coverage measurement (CSKG-
extra-relation scan, CauseNet 3-pair-type scan, ProPara-KB role-schema lookup, go.obo literal
scan); (b) a genuine distinct-source encounter-wave constructor (up to 3 waves per gap: CSKG
always, CauseNet if a literal pair was measured, KB-role-schema if a literal role hit was
measured -- NEVER repeated, NEVER templated-synthetic multiplicity); (c) run_genuine_arm, a
thin generalization of the landed cell's own run_arm loop structure (rounds -> waves; a target
participates in a wave ONLY if it has real source-evidence for that wave, instead of every
eligible target every round).

ARMS: G_full (full ThreeTierLoop wiring, genuine waves) / G_no_middle (bare Library, genuine
waves) / G_no_sweep (disconnected native_store_gen, genuine waves) / G_scramble (G_full wiring,
scrambled hop2, genuine waves, eligibility recomputed) / R_reference (POSITIVE CONTROL: the
landed cell's own A_full arm via VISITS_PER_GAP=6 templated repeats, reproduced verbatim via
imported run_arm -- proves this cell's plumbing is correct so a G_full zero is legible as a
genuine finding, and gives the literal "before" side of the caveat-removal contrast).

Modes: --self-test (source cell's own fixture + a new MIN_CONFIRM-boundary fixture, <10s) /
--smoke (real pipeline, 2-process subset, CauseNet scan skipped -> 2-wave ceiling) / (no flag,
default) = FULL (real pipeline, all real processes/targets, 3-wave ceiling, CauseNet scan
included).

ASCII-only. Deterministic throughout (sorted(set()) discipline; fixed integer seeds; no built-in
hash() anywhere -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import bz2
import glob
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "three_tier_loop_genuine_cross_source_corroboration_v1"
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
from hdlab.prelim_tier import (  # noqa: E402
    TierState, update_prelim_and_generalize, CLUSTER_MIN_MEMBERS, CLUSTER_EXPOSURE_MULTIPLIER,
)
from hdlab.hd_fact_store import HDFactStore, ACTIVE_STATUSES  # noqa: E402
from hdlab.script_grain_acquisition_loop import calibrate_novelty_threshold, build_instance_register  # noqa: E402
import hdlab.three_tier_loop as ttl  # noqa: E402
from experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1 import (  # noqa: E402
    build_reading_facts, reading_vocab, build_cskg_bridges, build_gap_set, build_entity_index,
    fresh_kg, ingest_reading_hop1, ingest_bridge_hop2, build_material_codebook, scramble_edges,
)
from experiments.exp_three_tier_loop_real_corpus_gap_stream_v1 import (  # noqa: E402
    pk_of, cluster_key_fn, my_gap_register_fn, _eligible_targets, _positive_control_reproduction,
    run_arm, run_self_test as reference_run_self_test,
    VISITS_PER_GAP, VISITS_PER_GAP_SMOKE, K1_FANOUT, K2_FANOUT, CA3_K_PEEL, CA3_SIM_FLOOR,
    FHRR_D, FOUND_DIM, RELATION, SEED_KG_HOP1, SEED_KG_HOP2, SEED_SCRAMBLE, SEED_FHRR,
)

# ---- this cell's own fresh seeds (distinct namespace from the source cell's) ----
SEED_FOUND_G_FULL = 20260813101
SEED_TIER_G_FULL = 20260813102
SEED_FOUND_G_NOMID = 20260813103
SEED_FOUND_G_NOSWEEP = 20260813104
SEED_TIER_G_NOSWEEP = 20260813105
SEED_DISCONNECT_G = 20260813106
SEED_FOUND_G_SCR = 20260813107
SEED_TIER_G_SCR = 20260813108
SEED_FOUND_R = 20260813109
SEED_TIER_R = 20260813110


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


# =========================================================================== STEP 1: MEASURE
def compute_cskg_extra(materials: List[str], wholes: List[str], processes: List[str]):
    """Single streaming pass over all CSKG shards. Returns (mat_whole_rel, proc_whole_rel,
    proc_mat_rel, n_rows): relation-type sets keyed by the (subject,object) pair, in the
    material/whole/process direction that actually matched (either direction in the raw data)."""
    mat_set, whole_set, proc_set = set(materials), set(wholes), set(processes)
    cskg_glob = repo_path(os.path.join("data", "cskg_foundation_v1", "edges_shard_*.jsonl"))
    mat_whole_rel: Dict[Tuple[str, str], Set[str]] = {}
    proc_whole_rel: Dict[Tuple[str, str], Set[str]] = {}
    proc_mat_rel: Dict[Tuple[str, str], Set[str]] = {}
    n_rows = 0
    for fn in sorted(glob.glob(cskg_glob)):
        with open(fn, encoding="utf-8") as f:
            for line in f:
                n_rows += 1
                row = json.loads(line)
                s, o, rel = row["subject"], row["obj"], row["relation"]
                if s in mat_set and o in whole_set:
                    mat_whole_rel.setdefault((s, o), set()).add(rel)
                if o in mat_set and s in whole_set:
                    mat_whole_rel.setdefault((o, s), set()).add(rel)
                if s in proc_set and o in whole_set:
                    proc_whole_rel.setdefault((s, o), set()).add(rel)
                if o in proc_set and s in whole_set:
                    proc_whole_rel.setdefault((o, s), set()).add(rel)
                if s in proc_set and o in mat_set:
                    proc_mat_rel.setdefault((s, o), set()).add(rel)
                if o in proc_set and s in mat_set:
                    proc_mat_rel.setdefault((o, s), set()).add(rel)
    return mat_whole_rel, proc_whole_rel, proc_mat_rel, n_rows


def compute_causenet_pairs(materials: List[str], wholes: List[str], processes: List[str]):
    """Single streaming decompression pass over causenet-precision.jsonl.bz2 (~197806 rows,
    ~50-80s). Extends the landed cell's own causenet_leak_check (which only checked
    (process,whole)) with (material,whole) and (process,material) literal-pair checks."""
    mat_set, whole_set, proc_set = set(materials), set(wholes), set(processes)
    path = repo_path(os.path.join("data", "bio_kb_cache", "causenet", "causenet-precision.jsonl.bz2"))
    cn_mat_whole: Set[Tuple[str, str]] = set()
    cn_proc_mat: Set[Tuple[str, str]] = set()
    cn_proc_whole: Set[Tuple[str, str]] = set()
    n_rows = 0
    with bz2.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            n_rows += 1
            row = json.loads(line)
            cr = row["causal_relation"]
            c, e = cr["cause"]["concept"], cr["effect"]["concept"]
            if c in mat_set and e in whole_set:
                cn_mat_whole.add((c, e))
            elif e in mat_set and c in whole_set:
                cn_mat_whole.add((e, c))
            if c in proc_set and e in mat_set:
                cn_proc_mat.add((c, e))
            elif e in proc_set and c in mat_set:
                cn_proc_mat.add((e, c))
            if c in proc_set and e in whole_set:
                cn_proc_whole.add((c, e))
            elif e in proc_set and c in whole_set:
                cn_proc_whole.add((e, c))
    return cn_mat_whole, cn_proc_mat, cn_proc_whole, n_rows


def _singularize(t: str) -> str:
    if t.endswith("es") and len(t) > 4:
        return t[:-2]
    if t.endswith("s") and len(t) > 3:
        return t[:-1]
    return t


def _norm_variants(s: str) -> Set[str]:
    base = s.lower()
    return {base, _singularize(base), base + "s"}


def compute_kb_role_hits(processes: List[str], materials: List[str]):
    """ProPara-derived process-physics role schema (data/benchmark_trap_check/
    propara_process_physics_kb_v1.json, the SAME dependency the fade_v6 cell's own _load_kb()
    loads -- see pre-reg Step 1 item 3). Returns ({(process,material): [roles]}, kb_path)."""
    kb_path = repo_path(os.path.join("data", "benchmark_trap_check", "propara_process_physics_kb_v1.json"))
    kb = json.load(open(kb_path, encoding="utf-8"))
    kb_procs = kb["processes"]
    hits: Dict[Tuple[str, str], List[str]] = {}
    for p in processes:
        if p not in kb_procs:
            continue
        d = kb_procs[p]
        for role in ("consumes", "produces", "moves"):
            role_terms = {t.lower() for t in d.get(role, [])}
            for m in materials:
                if _norm_variants(m) & role_terms:
                    hits.setdefault((p, m), []).append(role)
    return hits, kb_path


def compute_go_literal_hits(materials: List[str], wholes: List[str], processes: List[str]):
    """go.obo literal term-name scan (audit record only; measured to contribute ZERO genuine
    material/whole-level evidence -- excluded from wave construction, see pre-reg)."""
    go_path = repo_path(os.path.join("data", "bio_kb_cache", "go", "go.obo"))
    all_names = set(materials) | set(wholes) | set(processes)
    go_terms: Set[str] = set()
    n_terms = 0
    cur_id = None
    with open(go_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "[Term]":
                cur_id = None
            elif line.startswith("id: "):
                cur_id = line[4:].strip()
            elif line.startswith("name: ") and cur_id is not None:
                go_terms.add(line[6:].strip().lower())
                n_terms += 1
    hits = {}
    for name in sorted(all_names):
        probe = name.replace("_", " ").lower()
        if probe in go_terms:
            hits[name] = probe
    return hits, n_terms


# =========================================================================== genuine encounter waves
def pk_of_genuine(t: Dict) -> str:
    """Fate-disambiguated item key for the G_* (genuine-encounter) arms ONLY. The reused pk_of
    (ttl.gap_item_key(process, via_material, whole) -- via_material in the relation slot, per the
    source cell's own docstring) does NOT include fate. MEASURED: 8 of the 62 eligible targets
    (16 targets, 8 collision keys, e.g. (electricity_generation,water,rain) with fate in
    {CREATE,MOVE}) share a (process,via_material,whole) triple across two DIFFERENT fates. Under
    plain pk_of this SILENTLY MERGES two logically-different gaps' real-source encounters into
    ONE item's trace pool -- crossing MIN_CONFIRM via cross-GAP concatenation, not genuine
    cross-SOURCE corroboration of the SAME gap (caught empirically: FULL run v1 showed
    max_trace_count_observed=6 against a Step-1-measured per-gap ceiling of 3, traced to exactly
    this collision). Harmless in the landed source cell (VISITS_PER_GAP=6 uniform already puts
    every item far above both MIN_CONFIRM=4 and PROMOTE_MIN_EXPOSURE=8 regardless of merging) but
    load-bearing here, where crossing MIN_CONFIRM is the entire question. R_reference (the
    positive-control reproduction of the landed cell) deliberately keeps plain pk_of unmodified
    via the imported run_arm, for byte-faithful reproduction; only the NEW G_* arms use this
    disambiguated key, matching this cell's own Step-1 measurement granularity (the
    (process,via_material,whole,fate) 4-tuple)."""
    return ttl.gap_item_key(t["process"], t["via_material"], f"{t['whole']}::{t['fate']}")


def build_genuine_waves(targets: List[Dict], mat_whole_rel, proc_whole_rel, proc_mat_rel,
                        cn_mat_whole, cn_proc_mat, cn_proc_whole, kb_hits, do_causenet: bool
                        ) -> Dict[str, List[Tuple[int, str, str]]]:
    """For each gap: wave0=CSKG (always), wave1=CauseNet (only if a literal pair was measured,
    and only if do_causenet), wave2=KB-role-schema (only if a literal role hit was measured).
    go.obo excluded (measured zero contribution). Never more than one wave per source category
    -- this IS the no-templated-repeat discipline."""
    waves_by_pk: Dict[str, List[Tuple[int, str, str]]] = {}
    for t in targets:
        p, m, w = t["process"], t["via_material"], t["whole"]
        pk = pk_of_genuine(t)
        gw: List[Tuple[int, str, str]] = []
        rels = sorted(mat_whole_rel.get((m, w), set()) | {"/r/MadeOf"})
        gw.append((0, "cskg", f"CSKG external knowledge base records that {w} bridges to {m} "
                              f"via relation(s) {rels}."))
        if do_causenet:
            cn_hit = None
            if (m, w) in cn_mat_whole:
                cn_hit = ("material_whole", m, w)
            elif (p, m) in cn_proc_mat:
                cn_hit = ("process_material", p, m)
            elif (p, w) in cn_proc_whole:
                cn_hit = ("process_whole", p, w)
            if cn_hit is not None:
                kind, a, b = cn_hit
                gw.append((1, "causenet", f"CauseNet precision cache records a causal pair "
                                          f"between {a} and {b}, match type {kind}."))
        roles = kb_hits.get((p, m))
        if roles:
            gw.append((2, "kb_role_schema", f"ProPara process physics KB lists {m} among the "
                                            f"{sorted(set(roles))} terms for process {p}."))
        waves_by_pk[pk] = gw
    return waves_by_pk


def run_genuine_arm(arm_name: str, ablation_mode: str, eligible_targets: List[Dict],
                    waves_by_pk: Dict[str, List[Tuple[int, str, str]]], n_waves: int,
                    novelty_thresh: float, found_seed: int, tier_seed: int,
                    disconnect_seed: int = 0,
                    register_fn: Callable[[str, str, str], torch.Tensor] = my_gap_register_fn) -> Dict:
    """Generalizes the landed cell's own run_arm loop structure: rounds -> WAVES. A target
    participates in wave `w` iff it has real source-evidence for that wave (waves_by_pk[pk] has
    an entry with wave index w) -- NOT every eligible target every round. No organ modified;
    ablation is expressed entirely via WHICH pieces of ThreeTierLoop/TierState are used/wired,
    identical pattern to the landed cell's own run_arm."""
    eligible_sorted = sorted(eligible_targets, key=lambda t: (t["process"], t["via_material"], t["fate"], t["whole"]))
    pks = [pk_of_genuine(t) for t in eligible_sorted]

    foundation_store = HDFactStore(n_dim=FOUND_DIM, seed=found_seed, use_index=True)
    no_leak_ok = all(foundation_store.query(pk, RELATION) == [] for pk in pks)

    loop: Optional[ttl.ThreeTierLoop] = None
    tier_state: Optional[TierState] = None
    if ablation_mode == "no_middle":
        library = Library()
    else:
        loop = ttl.ThreeTierLoop(foundation_store, seed_base=tier_seed, n_dim=FOUND_DIM, relation=RELATION)
        if ablation_mode == "no_sweep":
            loop.tier_state.native_store_gen = HDFactStore(n_dim=FOUND_DIM, seed=disconnect_seed, use_index=True)
        library = loop.library
        tier_state = loop.tier_state

    checkpoints: List[Dict] = []
    for wave in range(n_waves):
        for t in eligible_sorted:
            pk = pk_of_genuine(t)
            gw = waves_by_pk.get(pk, [])
            match = next((g for g in gw if g[0] == wave), None)
            if match is None:
                continue
            _, source_tag, text = match
            cvec = context_vector(text)
            episode_id = f"{pk}|{source_tag}|w{wave}"
            if ablation_mode == "no_middle":
                library.flag(pk, episode_id, "POS", cvec, pass_idx=wave)
            else:
                loop.encounter(pk, "POS", cvec, episode_id, pass_idx=wave, also_strict=True)  # type: ignore[union-attr]
        cp = wave + 1
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

    max_trace_count_observed = max((len(library.items[pk].traces) for pk in pks if pk in library.items), default=0)
    final = checkpoints[-1] if checkpoints else {"n_foundation": 0, "n_middle": 0, "n_total_resolved": 0}
    return {
        "arm_name": arm_name, "ablation_mode": ablation_mode,
        "n_targets": len(eligible_targets), "n_eligible": len(eligible_sorted),
        "no_leak_ok": bool(no_leak_ok), "checkpoints": checkpoints, "final": final,
        "max_trace_count_observed": max_trace_count_observed,
    }


def compute_novelty_thresh(eligible_real: List[Dict]) -> Tuple[float, bool]:
    """Byte-for-byte adapted from the landed cell's own run_pipeline calibration block (same
    real-cluster-structure calibration, not re-derived logic)."""
    by_material: Dict[str, List[Dict]] = {}
    by_process: Dict[str, List[Dict]] = {}
    for t in eligible_real:
        by_material.setdefault(t["via_material"], []).append(t)
        by_process.setdefault(t["process"], []).append(t)
    ranked_materials = sorted(by_material.keys(), key=lambda m: -len(by_material[m]))
    calib_ok = len(ranked_materials) >= 2 and len(by_material[ranked_materials[0]]) >= 2
    if not calib_ok:
        return 0.15, True
    largest = by_material[ranked_materials[0]]
    second = by_material[ranked_materials[1]]
    matched_pairs = [(my_gap_register_fn(pk_of(largest[0]), ranked_materials[0], "POS"),
                      my_gap_register_fn(pk_of(largest[1]), ranked_materials[0], "POS"))]
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
    if calib.get("discriminates"):
        return calib["novelty_thresh"], False
    return 0.15, True


# =========================================================================== self-test
def run_self_test() -> Dict:
    """(a) calls the source cell's own run_self_test() -- proves the REUSED R_reference-
    equivalent mechanism sound (avoids re-deriving its ~100-line fixture). (b) a NEW tiny
    fixture isolating the MIN_CONFIRM=4 boundary: matW3 (3-member cluster, 3 traces/member,
    mirrors the REAL max-observed-source-count) must NOT retain into the middle tier at all;
    matBig (10-member cluster, 4 traces/member, combined exposure 10*4=40 >= cluster_exposure_
    floor=32) MUST cluster-promote all 10. Proves the mechanism itself is NOT broken -- real
    data falls exactly one source short (3<4) of the SAME floor this fixture clears at 4."""
    ref_result = reference_run_self_test()

    def cluster_key_fn_local(pk: str) -> str:
        return pk.split("|", 1)[0]

    def register_fn_local(pk: str, cluster_key: str, label: str) -> torch.Tensor:
        return build_instance_register(pk, pk, cluster_key, f"TEST_{label}")

    state_w = TierState(seed_base=9001, n_dim=512, relation="TESTREL_MINCONFIRM")
    for i in range(3):
        pk = f"matW3|item{i}"
        for v in range(3):
            cvec = context_vector(f"synthetic evidence trace for {pk}")
            state_w.prelim_lib.flag(pk, f"{pk}_e{v}", "POS", cvec, v)
    diag_w = update_prelim_and_generalize(state_w, cluster_key_fn_local, novelty_thresh=0.15,
                                          register_fn=register_fn_local)
    assert diag_w["newly_retained"] == 0, (
        f"SELF_TEST FAIL: matW3 members (n=3 < MIN_CONFIRM=4) must NOT retain, got {diag_w}")

    state_b = TierState(seed_base=9101, n_dim=512, relation="TESTREL_MINCONFIRM")
    for i in range(10):
        pk = f"matBig|item{i}"
        for v in range(4):
            cvec = context_vector(f"synthetic evidence trace for {pk}")
            state_b.prelim_lib.flag(pk, f"{pk}_e{v}", "POS", cvec, v)
    diag_b = update_prelim_and_generalize(state_b, cluster_key_fn_local, novelty_thresh=0.15,
                                          register_fn=register_fn_local)
    assert diag_b["newly_retained"] == 10, (
        f"SELF_TEST FAIL: matBig members (n=4 >= MIN_CONFIRM=4) must retain, got {diag_b}")
    assert diag_b["n_combined_promoted_total"] == 10, (
        f"SELF_TEST FAIL: matBig cluster (10 members * 4 traces = 40 >= cluster_exposure_floor="
        f"{PROMOTE_MIN_EXPOSURE * CLUSTER_EXPOSURE_MULTIPLIER}) must cluster-promote all 10, got {diag_b}")

    return {"reference_self_test": ref_result, "matW3_diag": diag_w, "matBig_diag": diag_b,
            "min_confirm_boundary_proven": True}


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

    print("[stage] positive-control reproduction (Gate D)", flush=True)
    pc_recovery5 = _positive_control_reproduction(targets, hop1, hop2_real, ent_idx, rel_idx,
                                                  bridge_idx, gathered_per_proc, n_ent)
    positive_control_ok = (abs(pc_recovery5 - 0.3802) <= 0.10) if run_mode == "full" else True
    print(f"[positive-control] arm3-reproduction recovery@5={pc_recovery5:.4f} "
          f"(cited=0.3802, gated={run_mode == 'full'}, ok={positive_control_ok})", flush=True)

    print("[stage] eligibility (per-cue REASON, unscrambled)", flush=True)
    eligible_real, _cache, excl_real = _eligible_targets(targets, hop1, hop2_real, ent_idx,
                                                          rel_idx, bridge_idx, gathered_per_proc, n_ent)
    print(f"[eligibility] n_eligible={len(eligible_real)} / {len(targets)} excl={excl_real}", flush=True)

    print("[stage] eligibility under SCRAMBLED hop2 (for G_scramble)", flush=True)
    eligible_scr, _cache_scr, excl_scr = _eligible_targets(targets, hop1, hop2_scrambled, ent_idx,
                                                            rel_idx, bridge_idx, gathered_per_proc, n_ent)
    print(f"[eligibility-scramble] n_eligible={len(eligible_scr)} / {len(targets)} excl={excl_scr}", flush=True)

    print("[stage] novelty-threshold calibration", flush=True)
    novelty_thresh, calib_fallback = compute_novelty_thresh(eligible_real)
    print(f"[calibration] novelty_thresh={novelty_thresh:.4f} fallback={calib_fallback}", flush=True)

    # ============================= STEP 1: MEASURE cross-source coverage =============================
    do_causenet = (run_mode == "full")
    print("[stage] CSKG cross-source scan (extra relations + direct process edges)", flush=True)
    mat_whole_rel, proc_whole_rel, proc_mat_rel, n_cskg_rows = compute_cskg_extra(materials, wholes, processes)
    print(f"[cskg] scanned {n_cskg_rows} rows; extra-relation-or-direct-edge pairs: "
          f"mat_whole={sum(1 for k,v in mat_whole_rel.items() if v - {'/r/MadeOf'})} "
          f"proc_whole={len(proc_whole_rel)} proc_mat={len(proc_mat_rel)}", flush=True)

    if do_causenet:
        print("[stage] CauseNet cross-source scan (FULL only, ~50-80s)", flush=True)
        cn_mat_whole, cn_proc_mat, cn_proc_whole, n_cn_rows = compute_causenet_pairs(materials, wholes, processes)
        print(f"[causenet] scanned {n_cn_rows} rows; mat_whole={len(cn_mat_whole)} "
              f"proc_mat={len(cn_proc_mat)} proc_whole={len(cn_proc_whole)}", flush=True)
    else:
        cn_mat_whole, cn_proc_mat, cn_proc_whole, n_cn_rows = set(), set(), set(), 0
        print("[causenet] skipped (smoke mode -- 2-wave ceiling)", flush=True)

    kb_hits, kb_path = compute_kb_role_hits(processes, materials)
    print(f"[kb-role-schema] {len(kb_hits)} (process,material) role hits from {kb_path}", flush=True)

    go_hits: Dict[str, str] = {}
    n_go_terms = 0
    if run_mode == "full":
        print("[stage] go.obo literal-name scan (audit record only; excluded from waves)", flush=True)
        go_hits, n_go_terms = compute_go_literal_hits(materials, wholes, processes)
        print(f"[go.obo] scanned {n_go_terms} terms; literal hits (process-name-only, "
              f"non-evidentiary, excluded): {go_hits}", flush=True)

    coverage_hist_all: Dict[int, int] = {}
    coverage_hist_eligible: Dict[int, int] = {}
    eligible_pks = {pk_of(t) for t in eligible_real}
    for t in targets:
        p, m, w = t["process"], t["via_material"], t["whole"]
        n_src = 1
        if (m, w) in cn_mat_whole or (p, m) in cn_proc_mat or (p, w) in cn_proc_whole:
            n_src += 1
        if (p, m) in kb_hits:
            n_src += 1
        coverage_hist_all[n_src] = coverage_hist_all.get(n_src, 0) + 1
        if pk_of(t) in eligible_pks:
            coverage_hist_eligible[n_src] = coverage_hist_eligible.get(n_src, 0) + 1
    print(f"[HEADLINE] per-gap coverage histogram, ALL {len(targets)} targets (n_sources 1..3): "
          f"{dict(sorted(coverage_hist_all.items()))}", flush=True)
    print(f"[HEADLINE] per-gap coverage histogram, {len(eligible_real)} ELIGIBLE targets: "
          f"{dict(sorted(coverage_hist_eligible.items()))}", flush=True)

    waves_by_pk = build_genuine_waves(targets, mat_whole_rel, proc_whole_rel, proc_mat_rel,
                                      cn_mat_whole, cn_proc_mat, cn_proc_whole, kb_hits, do_causenet)
    n_waves = 3 if do_causenet else 2
    max_possible_source_count = max((len(v) for v in waves_by_pk.values()), default=0)
    retain_floor_reachable_by_construction = max_possible_source_count >= MIN_CONFIRM
    print(f"[genuine-waves] n_waves={n_waves} max_possible_source_count_this_run="
          f"{max_possible_source_count} MIN_CONFIRM={MIN_CONFIRM} "
          f"retain_floor_reachable_by_construction={retain_floor_reachable_by_construction}", flush=True)

    # ============================= arms =============================
    print(f"[stage] running G_* arms (genuine encounters, n_waves={n_waves}) + R_reference "
          f"(VISITS_PER_GAP={VISITS_PER_GAP if run_mode == 'full' else VISITS_PER_GAP_SMOKE})", flush=True)
    g_full = run_genuine_arm("G_full", "full", eligible_real, waves_by_pk, n_waves, novelty_thresh,
                             SEED_FOUND_G_FULL, SEED_TIER_G_FULL)
    print(f"[arm G_full] {g_full['final']} max_trace_count_observed={g_full['max_trace_count_observed']}", flush=True)
    g_no_middle = run_genuine_arm("G_no_middle", "no_middle", eligible_real, waves_by_pk, n_waves,
                                  novelty_thresh, SEED_FOUND_G_NOMID, 0)
    print(f"[arm G_no_middle] {g_no_middle['final']}", flush=True)
    g_no_sweep = run_genuine_arm("G_no_sweep", "no_sweep", eligible_real, waves_by_pk, n_waves,
                                 novelty_thresh, SEED_FOUND_G_NOSWEEP, SEED_TIER_G_NOSWEEP,
                                 disconnect_seed=SEED_DISCONNECT_G)
    print(f"[arm G_no_sweep] {g_no_sweep['final']}", flush=True)
    g_scramble = run_genuine_arm("G_scramble", "full", eligible_scr, waves_by_pk, n_waves,
                                 novelty_thresh, SEED_FOUND_G_SCR, SEED_TIER_G_SCR)
    print(f"[arm G_scramble] {g_scramble['final']}", flush=True)

    r_visits = VISITS_PER_GAP if run_mode == "full" else VISITS_PER_GAP_SMOKE
    r_reference = run_arm("R_reference", "full", targets, hop1, hop2_real, ent_idx, rel_idx,
                          bridge_idx, gathered_per_proc, n_ent, r_visits, novelty_thresh,
                          found_seed=SEED_FOUND_R, tier_seed=SEED_TIER_R)
    print(f"[arm R_reference] {r_reference['final']} n_eligible={r_reference['n_eligible']}", flush=True)

    # ---- cardinality ----
    cardinality_ok = (len(g_full["checkpoints"]) == n_waves and len(g_no_middle["checkpoints"]) == n_waves and
                      len(g_no_sweep["checkpoints"]) == n_waves and len(g_scramble["checkpoints"]) == n_waves and
                      len(r_reference["checkpoints"]) == r_visits)

    # ---- arms-must-differ (META_RULE_AF): G_full vs R_reference asserted; G_* vs G_* EXEMPTED ----
    def _curve_digest(checkpoints):
        c = [(cp["n_foundation"], cp["n_middle"]) for cp in checkpoints]
        return hashlib.sha256(json.dumps(c).encode("utf-8")).hexdigest()

    digests = {"G_full": _curve_digest(g_full["checkpoints"]), "G_no_middle": _curve_digest(g_no_middle["checkpoints"]),
              "G_no_sweep": _curve_digest(g_no_sweep["checkpoints"]), "G_scramble": _curve_digest(g_scramble["checkpoints"]),
              "R_reference": _curve_digest(r_reference["checkpoints"])}
    assert digests["G_full"] != digests["R_reference"], (
        "META_RULE_AF VIOLATION: G_full and R_reference produced identical per-checkpoint curves")
    arms_differ_g_vs_r_ok = True
    arms_differ_exempted = [["G_full", "G_no_middle"], ["G_full", "G_no_sweep"], ["G_full", "G_scramble"],
                            ["G_no_middle", "G_no_sweep"], ["G_no_middle", "G_scramble"],
                            ["G_no_sweep", "G_scramble"]]
    g_star_all_identical = (digests["G_full"] == digests["G_no_middle"] == digests["G_no_sweep"] == digests["G_scramble"])

    # ---- verdict quantities ----
    max_trace_g_full = g_full["max_trace_count_observed"]
    retain_floor_reachable = max_trace_g_full >= MIN_CONFIRM
    g_full_combined_promotions = sum(cp["n_combined_promoted_this_pass"] for cp in g_full["checkpoints"])
    no_leak_ok = all(arm["no_leak_ok"] for arm in (g_full, g_no_middle, g_no_sweep, g_scramble, r_reference))
    # the abs-magnitude comparison against the cited 40 is only meaningful at FULL (same 121-
    # target/62-eligible population as the cited cell); a smoke subset is a genuinely different,
    # smaller population (apples-to-oranges), matching the landed source cell's own precedent for
    # positive_control_ok -- at smoke, only the scale-invariant internal check applies.
    if run_mode == "full":
        reference_reproduces_prior = (abs(r_reference["final"]["n_foundation"] - 40) <= 15 and
                                      r_reference["final"]["n_total_resolved"] == r_reference["n_eligible"])
    else:
        reference_reproduces_prior = (r_reference["final"]["n_total_resolved"] == r_reference["n_eligible"])

    elapsed = time.perf_counter() - t0

    if not positive_control_ok:
        verdict = "HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH"
        verdict_msg = (f"positive-control arm3-reproduction={pc_recovery5:.4f} outside tolerance of "
                        f"cited 0.3802 (|delta|>0.10); downstream arms untrusted")
    elif g_full_combined_promotions > 0 and no_leak_ok and reference_reproduces_prior:
        verdict = "HARD_PASS_genuine_cross_source_corroboration_load_bearing"
        verdict_msg = (f"g_full_combined_promotions={g_full_combined_promotions} (>0); genuine cross-"
                        f"source corroboration crosses the combined-evidence gate on real data; "
                        f"max_trace_g_full={max_trace_g_full} >= MIN_CONFIRM={MIN_CONFIRM}; "
                        f"reference reproduces prior (n_foundation={r_reference['final']['n_foundation']}, "
                        f"cited=40); no_leak_ok=True")
    elif (g_full_combined_promotions == 0 and not retain_floor_reachable and reference_reproduces_prior
          and no_leak_ok):
        verdict = "HARD_FAIL_thin_cross_source_not_mechanism_failure"
        verdict_msg = (f"g_full_combined_promotions=0; max_trace_g_full={max_trace_g_full} < "
                        f"MIN_CONFIRM={MIN_CONFIRM} (structural retain-floor unreachable on our current "
                        f"4 named sources -- CSKG+CauseNet+KB-role-schema max out at 3 real distinct "
                        f"sources/gap, go.obo contributes 0). Reference arm DOES reproduce the prior "
                        f"landed result (n_foundation={r_reference['final']['n_foundation']}, cited=40, "
                        f"n_total_resolved={r_reference['final']['n_total_resolved']}=="
                        f"{r_reference['n_eligible']}), proving this cell's plumbing is correct -- the "
                        f"zero is a genuine real-source-thinness finding, NOT a cell bug. Coverage (all "
                        f"121): {coverage_hist_all}. Coverage (eligible {len(eligible_real)}): "
                        f"{coverage_hist_eligible}.")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"g_full_combined_promotions={g_full_combined_promotions} retain_floor_reachable="
                        f"{retain_floor_reachable} reference_reproduces_prior={reference_reproduces_prior} "
                        f"no_leak_ok={no_leak_ok} -- inconsistent with the pre-registered clean bands, "
                        f"investigate before trusting either conclusion")

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode, "process_filter": sorted(process_filter) if process_filter else "ALL",
        "n_ent": n_ent, "n_targets": len(targets), "n_eligible": len(eligible_real),
        "n_eligible_scramble": len(eligible_scr),
        "positive_control_arm3_reproduction": pc_recovery5, "positive_control_ok": positive_control_ok,
        "positive_control_cited_prior": 0.3802,
        "novelty_thresh": novelty_thresh, "calibration_fallback": calib_fallback,
        "step1_measurement": {
            "n_cskg_rows_scanned": n_cskg_rows, "n_causenet_rows_scanned": n_cn_rows,
            "n_go_terms_scanned": n_go_terms, "go_literal_hits_excluded_non_evidentiary": go_hits,
            "kb_role_schema_path": kb_path, "n_kb_role_hits": len(kb_hits),
            "n_cskg_extra_relation_pairs": sum(1 for k, v in mat_whole_rel.items() if v - {"/r/MadeOf"}),
            "n_cskg_direct_proc_whole_edges": len(proc_whole_rel), "n_cskg_direct_proc_mat_edges": len(proc_mat_rel),
            "coverage_histogram_all_121": {str(k): v for k, v in sorted(coverage_hist_all.items())},
            "coverage_histogram_eligible": {str(k): v for k, v in sorted(coverage_hist_eligible.items())},
            "max_possible_source_count_this_run": max_possible_source_count,
            "min_confirm": MIN_CONFIRM,
            "retain_floor_reachable_by_construction": retain_floor_reachable_by_construction,
        },
        "n_waves": n_waves, "r_visits": r_visits,
        "arm_results": {"G_full": g_full, "G_no_middle": g_no_middle, "G_no_sweep": g_no_sweep,
                        "G_scramble": g_scramble, "R_reference": r_reference},
        "max_trace_g_full": max_trace_g_full, "retain_floor_reachable": retain_floor_reachable,
        "g_full_combined_promotions": g_full_combined_promotions,
        "no_leak_ok": no_leak_ok, "reference_reproduces_prior": reference_reproduces_prior,
        "cardinality_ok": cardinality_ok,
        "arm_curve_digests": digests, "arms_differ_g_vs_r_ok": arms_differ_g_vs_r_ok,
        "arms_differ_exempted": arms_differ_exempted, "g_star_all_identical": g_star_all_identical,
        "bands": {"min_confirm": MIN_CONFIRM, "cluster_exposure_floor": PROMOTE_MIN_EXPOSURE * CLUSTER_EXPOSURE_MULTIPLIER,
                  "reference_tolerance_abs": 15, "reference_cited_n_foundation": 40,
                  "positive_control_tolerance": 0.10},
    }
    return metrics


# =========================================================================== main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="reused fixture + MIN_CONFIRM-boundary fixture")
    parser.add_argument("--smoke", action="store_true", help="real pipeline, 2-process subset, CauseNet skipped")
    parser.add_argument("--timeout", type=float, default=600.0,
                        help="declared wall-time budget: smoke~20-40s, FULL~90-150s (CauseNet scan dominates)")
    args = parser.parse_args()

    if args.self_test:
        run_mode = "self_test"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_selftest")
        t0 = time.perf_counter()
        _write_start_marker(output_dir, run_mode, expected_n_units=1)
        result = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELF_TEST_PASS",
                  "verdict_msg": ("reused source-cell fixture PASS (R_reference-equivalent mechanism "
                                  "sound) + NEW MIN_CONFIRM=4 boundary fixture PASS (matW3 n=3 does NOT "
                                  "retain, matBig n=4/size=10 DOES cluster-promote all 10) -- proves the "
                                  "mechanism itself works correctly; the FULL run's expected zero is "
                                  "attributable to real-source scarcity (max 3), not a broken mechanism"),
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
    else:
        run_mode = "full"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
        process_filter = None

    _write_start_marker(output_dir, run_mode, expected_n_units=5)
    metrics = run_pipeline(process_filter, run_mode)

    if run_mode == "smoke":
        r = metrics["arm_results"]["R_reference"]
        sweep_fired = any(cp["n_combined_promoted_this_pass"] > 0 for cp in r["checkpoints"])
        discriminator_ok = sweep_fired
        if not discriminator_ok:
            metrics["verdict"] = "SMOKE_GATE_FAIL_discriminator_not_firing"
            metrics["verdict_msg"] = (f"smoke discriminator check: R_reference sweep_fired={sweep_fired} "
                                      f"-- the REUSED mechanism must fire normally at smoke scale (proves "
                                      f"THIS cell's plumbing works) before FULL dispatch; G_full is "
                                      f"analytically expected to stay at 0 at any scale and is NOT the "
                                      f"smoke discriminator")

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
