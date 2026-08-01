"""A5-gated LOCAL-ONLY atomize: two atoms closing the encoder-representation-lever campaign.

AUDIT-ONLY (hdi_skunkworks), independent .venv recompute off metrics.json for BOTH cells (raw per-seed
units.jsonl-derived values, not verdict_msg strings). No experiment authored/dispatched by this auditor.

ATOM A (seq 29596, math, CHAIN_GRADE, cert_delta +1): exp_encoder_alltype_transfer_stress_v1.py HARD_PASS.
  Independent recompute of all 3 conditions x 3 query types x 3 seeds from raw units matches every stored
  per_type_mean/lift number exactly. Drift control = 0.0 in every (condition, type, seed) cell -- frozen1 vs
  frozen2 bit-identical, so the eval is deterministic and the encoder-swap mechanism does not leak. All 3
  conditions (C1 harder-difficulty n_mods=16, C2 disjoint held-out eval-draw, C3 independent entity-file
  streaming-commit addressing harness) clear the pre-registered GENERALIZES band (lift>=0.05 on >=2/3 types
  incl >=1 non-coref type). CAVEAT (rides the atom): C3's a_name_maintenance lift is MARGINAL -- mean lands
  exactly at the 0.05 floor with high seed variance (cv=0.816, per-seed [0.10, 0.05, 0.00]) -- but C3's own
  generalizes_here criterion does not depend on that type: b_competitive_coref (+0.175, cv=0.31) and
  c_overwrite (+0.072, cv=0.19) independently clear >=2-types-incl-non-coref on their own. C3 shares the
  underlying decode_dataset_slots("role_attn") token-filler-decode primitive with C1/C2/base_loop (expected,
  since the object under test -- encoder representation quality -- sits upstream of all three addressing
  routes); what IS architecturally independent in C3 is the ENTITY-ADDRESSING/retrieval mechanism itself
  (nearest-committed-file streaming cosine matching, calibrate_tau + _assign_commit, verified in
  exp_situation_model_assembly_entity_file_v1.py lines 211-310) vs the WM-slot role_attn-binding route
  C1/C2/base_loop use. This is a legitimate distinct addressing architecture, not a leaked re-test of the
  same mechanism. VERDICT: CONFIRMED CHAIN_GRADE. The certified minimal-unfreeze encoder break (atom 29593)
  is a real, robustly-generalizing representation lever for ENTITY-ADDRESSED comprehension -- survives
  harder difficulty, a disjoint eval draw, and an independently-architected addressing mechanism, multi-seed,
  drift-controlled. Composes 29593 (the break), 29594 (compositional wiring), 29595 (base_loop all-type lift,
  SCOPED single-harness VET) -- THIS atom is what promotes 29595's single-harness scope to a
  cross-harness/cross-difficulty/cross-draw generalization claim.

ATOM B (seq 29597, math, MEASURED_MECHANISM, cert_delta +1): exp_encoder_generic_vs_entity_addressed_v1.py
  landed MIDDLE (correct application of its own pre-registered gate: ent_geom_interpretable=False because
  mean ENT-slot geometry delta=0.0175 < ENT_GEOM_MIN=0.02, itself dragged below floor by seed19's regression
  to -0.0033 -- ENT geometry is NOT robustly reproduced this run, in contrast to the larger swing (~0.053)
  atom 29593 cited under a different measurement config; this discrepancy is flagged OPEN, not resolved).
  Independent recompute confirms every stage_mean/geom_mean number from raw per-seed units exactly. Beyond
  the cell's own MIDDLE verdict, three findings survive independent scrutiny and are what this atom banks:
  (1) P (placement) DECODE lift +0.086, robust all 3 seeds (0.080-0.091), clears LIFT_MIN comfortably.
  (2) S (state) DECODE lift +0.020, robust all 3 seeds (0.017-0.025), stays under LIFT_MIN -- BUT this raw
      comparison is CONFOUNDED by a near-ceiling frozen baseline (S frozen=0.951, headroom only 0.049).
      Headroom-normalized closure (41%) is comparable to P (45%), ENT (48%), MARK (49%) -- the pre-registered
      raw-lift-threshold framing of "S stays flat" is a CEILING ARTIFACT at the decode-accuracy level, not
      clean evidence the retrain skips non-entity representation. This is an honest downward correction of
      the draft framing proposed at spawn time ("an orthogonal non-entity decode stays flat").
  (3) STATE-slot GEOMETRY (within-minus-cross cosine, NOT ceiling-bound -- frozen ~0.28-0.29, comparable
      headroom to ENT) robustly WORSENS by -0.0405 (per-seed -0.0394/-0.0389/-0.0432 -- tight, all-seed-
      consistent, larger in magnitude than ENT's own noisy +0.0175 mean delta). This IS a real, non-artifact,
      directed finding: the entity-focused fine-tune measurably degrades state-slot representational
      separability even while state DECODE accuracy stays flat/ceiling-shielded. This is the single most
      solid piece of evidence in the cell for a genuine capacity-reallocation tradeoff, independent of the
      confounded raw-S-decode-lift framing.
  Decode-level entity evidence (ENT +0.132 tight 0.129-0.134 all seeds, MARK +0.084 tight-ish 0.064-0.105,
  entity_consistency +0.129 tight 0.104-0.154) independently corroborates the entity-addressed lift via
  DECODE accuracy, separate from the noisy geometry probe -- so "entity representation improved" is NOT in
  doubt; only the specific within-minus-cross ENT-geometry MAGNITUDE this run is underpowered/noisy.
  VERDICT: the cell's pre-registered ENTITY_ADDRESSING_SPECIFIC band (clean dissociation: entity geometry
  sharpens, non-entity stays flat) does NOT cleanly hold -- P's headroom-normalized lift undercuts a hard
  entity/non-entity decode dissociation, and ENT geometry itself fails to reproduce robustly this run.

  COORDINATOR FRAMING CORRECTION (2026-07-31, applied before atomizing): the state-flat/geometry-worsens
  result must NOT be read as "the encoder lift is not domain-general" or as evidence of an intrinsic ceiling
  on what's improvable. The fine-tune's objective was entity-consistency ONLY -- state was never a training
  target, and state's decode metric started near-ceiling (0.951) regardless. So this result shows FREE/
  AUTOMATIC transfer does not happen (training skill X does not lift an untrained orthogonal skill Y for
  free) -- it says NOTHING about whether Y (state) is improvable if DIRECTLY trained. A separate FAIR test
  (train an independent skill with real headroom, check it lifts + stacks without clobbering the entity-
  consistency win) is the correct way to settle trainability and is out of scope for THIS cell/atom.

  TIER: MEASURED_MECHANISM (proven-bound), not CHAIN_GRADE -- the original spawn-drafted claim overclaimed a
  clean domain boundary; the recompute supports a narrower, still genuine, mechanism characterization, framed
  as NO-FREE-LUNCH / directed-improvement, not as a ceiling. NOT atomized as ENTITY_ADDRESSING_SPECIFIC,
  GENERIC, or "not domain-general"; atomized as the STATE-GEOMETRY no-free-lunch finding with the ceiling-
  confound correction on S-decode and the untrained-skill caveat explicitly on record.
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

def iseq(o):
    try: return int(o.get("seq"))
    except Exception: return -1

# ---- PRE-GATE ----
atom_lines = [l for l in open(ATOMS, encoding="utf-8").read().splitlines() if l.strip()]
parsed = [json.loads(l) for l in atom_lines]
existing_ids = {o.get("atom_id") for o in parsed if o.get("atom_id")}
assert not any("\r" in l for l in atom_lines[-5:]), "existing atoms carry CR"
ledger_lines = [l for l in open(LEDGER, encoding="utf-8").read().splitlines() if l.strip()]
lp = [json.loads(l) for l in ledger_lines]
meta_atoms = [json.loads(l) for l in open("data/substrate_index/meta/atoms.jsonl", encoding="utf-8").read().splitlines() if l.strip()]
STORE_HEAD = max(max(iseq(o) for o in parsed), max(iseq(o) for o in lp), max(iseq(o) for o in meta_atoms))
assert STORE_HEAD == 29595, f"expected store head 29595, got {STORE_HEAD}"
SEQ_A, SEQ_B = 29596, 29597
parent_ids = {29593, 29594, 29595}
have_parents = {iseq(o) for o in parsed} & parent_ids
assert have_parents == parent_ids, f"missing parent atoms: {parent_ids - have_parents}"
assert not any("alltype_transfer_stress" in o.get("anchor_name", "") for o in parsed), "A already atomized"
assert not any("generic_vs_entity_addressed" in o.get("anchor_name", "") for o in parsed), "B already atomized"
print(f"PRE-GATE OK: store head {STORE_HEAD}; parents 29593/29594/29595 present; NEW_SEQ {SEQ_A}/{SEQ_B}.")

# ---- OFF-DISK independent recompute: cell A (generalization stress) ----
MA = json.load(open("data/exp_encoder_alltype_transfer_stress_v1/metrics.json", encoding="utf-8"))
assert MA["verdict"] == "HARD_PASS" and MA["run_mode"] == "lite"
QT = ("a_name_maintenance", "b_competitive_coref", "c_overwrite")
NON_COREF = ("a_name_maintenance", "c_overwrite")
CONDS = ("c1_harder", "c2_heldout", "c3_indep")
unitsA = MA["units"]
assert len(unitsA) == 3, "cardinality"
max_drift_A = 0.0
recompute_A = {}
for c in CONDS:
    recompute_A[c] = {}
    clears = []
    for qt in QT:
        vals = [u["conditions"][c]["lift"][qt] for u in unitsA]
        mean = sum(vals) / 3.0
        stored = MA["bands"]["conditions"][c]["per_type_mean"][qt]["lift"]
        assert abs(mean - stored) < 1e-9, f"mismatch {c}/{qt}: {mean} vs {stored}"
        drifts = [u["conditions"][c]["drift"][qt] for u in unitsA]
        max_drift_A = max(max_drift_A, max(abs(d) for d in drifts))
        recompute_A[c][qt] = mean
        if mean >= 0.05:
            clears.append(qt)
    clears_nc = [q for q in clears if q in NON_COREF]
    assert len(clears) >= 2 and len(clears_nc) >= 1, f"{c} does not generalize per recompute"
assert max_drift_A == 0.0, "drift control non-zero"
print("OFF-DISK OK (A): all 3 conditions x 3 types x 3 seeds recomputed from raw units; matches stored "
      "per_type_mean exactly; max_drift=0.0; all 3 conditions independently clear >=2 types incl non-coref.")

# ---- OFF-DISK independent recompute: cell B (generic vs entity) ----
MB = json.load(open("data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json", encoding="utf-8"))
assert MB["verdict"] == "MIDDLE" and MB["run_mode"] == "lite"
unitsB = MB["units"]
assert len(unitsB) == 3, "cardinality"
stages_recompute = {}
for st in ("S", "P", "ENT", "MARK", "entity_consistency"):
    vals = [u["stages"][st]["lift"] for u in unitsB]
    mean = sum(vals) / 3.0
    stored = MB["bands"]["stage_mean"][st]["lift"]
    assert abs(mean - stored) < 1e-9, f"mismatch {st}: {mean} vs {stored}"
    stages_recompute[st] = {"mean": mean, "per_seed": vals}
geom_recompute = {}
for gk in ("ent", "state"):
    vals = [u["geom"][gk]["delta"] for u in unitsB]
    mean = sum(vals) / 3.0
    stored_key = "%s_delta" % gk
    stored = MB["bands"]["geom_mean"][stored_key]
    assert abs(mean - stored) < 1e-9, f"mismatch geom/{gk}: {mean} vs {stored}"
    geom_recompute[gk] = {"mean": mean, "per_seed": vals}
# headroom-normalized closure (the ceiling-confound check)
headroom = {}
for st in ("S", "P", "ENT", "MARK"):
    fz = MB["bands"]["stage_mean"][st]["frozen"]
    lift = MB["bands"]["stage_mean"][st]["lift"]
    hr = 1.0 - fz
    headroom[st] = {"frozen": fz, "lift": lift, "headroom": hr, "frac_closed": lift / hr if hr > 0 else float("nan")}
assert abs(headroom["S"]["frac_closed"] - 0.412) < 0.005
assert abs(headroom["P"]["frac_closed"] - 0.447) < 0.005
assert abs(headroom["ENT"]["frac_closed"] - 0.481) < 0.005
# ent-geometry not robust across seeds (seed19 regresses to negative) -- the reason MIDDLE fired
assert geom_recompute["ent"]["per_seed"][2] < 0.0, "expected seed19 ENT geom regression"
# state geometry robustly negative, all seeds, tight
assert all(v < -0.03 for v in geom_recompute["state"]["per_seed"]), "state geom not all-seed-consistent"
assert (max(geom_recompute["state"]["per_seed"]) - min(geom_recompute["state"]["per_seed"])) < 0.006
max_drift_B = max(abs(u["stages"][st]["drift"]) for u in unitsB for st in ("S", "P", "ENT", "MARK"))
assert max_drift_B == 0.0
print("OFF-DISK OK (B): stage/geom means recomputed from raw units match stored exactly. Headroom-normalized "
      "closure: S=%.3f P=%.3f ENT=%.3f MARK=%.3f (S is CEILING-CONFOUNDED, not cleanly flat). ENT-geometry "
      "per-seed=%s (seed19 regresses negative -> explains MIDDLE). STATE-geometry per-seed=%s (all-seed "
      "negative, tight, NOT ceiling-bound, NOT an artifact)." % (
          headroom["S"]["frac_closed"], headroom["P"]["frac_closed"], headroom["ENT"]["frac_closed"],
          headroom["MARK"]["frac_closed"], [round(v, 4) for v in geom_recompute["ent"]["per_seed"]],
          [round(v, 4) for v in geom_recompute["state"]["per_seed"]]))

# ---- KB overlap check (substrate_query.sh, run before atomizing) ----
KB_CHECK = ("substrate_query.sh 'encoder retrain entity addressing generalization harder difficulty "
    "held-out independent harness geometry tradeoff' -> top cosine=0.2686 (unrelated note chunk); all hits "
    "< 0.30. Not a rediscovery.")

cellA_sha16 = hashlib.sha256(open("experiments/exp_encoder_alltype_transfer_stress_v1.py", "rb").read()).hexdigest()[:16]
preregA_sha16 = hashlib.sha256(open("preregs/2026-07-31_encoder_alltype_transfer_stress_v1.md", "rb").read()).hexdigest()[:16]
metricsA_sha16 = hashlib.sha256(open("data/exp_encoder_alltype_transfer_stress_v1/metrics.json", "rb").read()).hexdigest()[:16]
cellB_sha16 = hashlib.sha256(open("experiments/exp_encoder_generic_vs_entity_addressed_v1.py", "rb").read()).hexdigest()[:16]
preregB_sha16 = hashlib.sha256(open("preregs/2026-07-31_encoder_generic_vs_entity_addressed.md", "rb").read()).hexdigest()[:16]
metricsB_sha16 = hashlib.sha256(open("data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json", "rb").read()).hexdigest()[:16]
assert cellA_sha16 == "4158cdcd2d03f436" and preregA_sha16 == "3a7fbef1f921e86c" and metricsA_sha16 == "08e42584e90263e9"
assert cellB_sha16 == "d3a36a3edf84133d" and preregB_sha16 == "3e03955a9d2d9046" and metricsB_sha16 == "324638c432101384"

ts = time.time(); ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(); ts_day = "2026-07-31"

# ================= ATOM A =================
AID_A = ("math::encoder_alltype_transfer_stress_v1_CHAIN_GRADE_CERTIFIED_ENTITY_ADDRESSED_LEVER_GENERALIZES_"
    "across_harder_difficulty_n_mods16_disjoint_heldout_eval_draw_and_independent_entity_file_streaming_commit_"
    "addressing_harness_multi_seed_drift_controlled_max_drift_0p0_all3_conditions_clear_lift_ge_0p05_on_ge2_of_3_"
    "types_incl_non_coref_c1_a_name_0p108_b_coref_0p142_c_overwrite_0p231_c2_a_name_0p200_b_coref_0p150_c_"
    "overwrite_0p203_c3_a_name_0p050_MARGINAL_cv0p82_b_coref_0p175_c_overwrite_0p072_ROBUST_c3_generalizes_on_"
    "b_and_c_alone_independent_of_marginal_a_name_promotes_29595_single_harness_scope_to_cross_harness_claim_"
    "composes_29593_29594_29595_LOCAL_ONLY_2026_07_31")
assert AID_A not in existing_ids

HEADLINE_A = ("CHAIN_GRADE (CERT +1). exp_encoder_alltype_transfer_stress_v1.py HARD_PASS, independently "
    "recomputed off-disk (all 3 conditions x 3 query types x 3 seeds match stored per_type_mean exactly; "
    "max_drift=0.0 in every cell). The certified minimal-unfreeze entity-consistency encoder break (atom "
    "29593) GENERALIZES beyond the single base_loop harness atom 29595 scoped to: C1 harder difficulty "
    "(n_mods 8->16, strictly lower token-copy transfer probability) lift a_name=+0.108 b_coref=+0.142 "
    "c_overwrite=+0.231, all clear; C2 disjoint held-out eval-instance draw (same held-colors pool, "
    "independent RNG stream) lift a_name=+0.200 b_coref=+0.150 c_overwrite=+0.203, all clear; C3 an "
    "INDEPENDENTLY-ARCHITECTED entity-addressing harness (exp_situation_model_assembly_entity_file_v1's "
    "streaming nearest-committed-file cosine-matching addressor, calibrate_tau + _assign_commit -- NOT the "
    "WM-slot role_attn-binding route C1/C2/base_loop share) lift b_coref=+0.175 c_overwrite=+0.072 robustly "
    "clear, a_name=+0.050 lands exactly at the pre-registered floor with high seed variance (cv=0.82, "
    "per-seed 0.10/0.05/0.00) but C3's generalizes_here does not depend on it -- b_coref+c_overwrite alone "
    "satisfy >=2-types-incl-non-coref. CAVEAT: C3 shares the underlying decode_dataset_slots('role_attn') "
    "token-filler-decode primitive with C1/C2 (expected -- the object under test, encoder representation "
    "quality, is upstream of all addressing routes); independence is specifically in the entity-ADDRESSING "
    "mechanism, verified by reading exp_situation_model_assembly_entity_file_v1.py lines 211-310. VERDICT: "
    "the encoder break is a real, robustly-generalizing representation lever for ENTITY-ADDRESSED "
    "comprehension, not a base_loop-harness-specific artifact. SCOPE (does not drop): absolute comprehension "
    "is NOT solved by this lever (coref abs still ~0.65, below 0.70 PROVEN_MIN in the parent arc); this is a "
    "proven-generalizing REPRESENTATION IMPROVEMENT, not a solved capability. Composes 29593 (the break), "
    "29594 (compositional wiring), 29595 (single-harness base_loop lift, SCOPED) -- this atom is what "
    "promotes 29595's scope from single-harness to cross-harness/cross-difficulty/cross-draw.")

key_metrics_A = {
    "cell_verdict": "HARD_PASS", "auditor_tier": "CHAIN_GRADE_generalization_confirmed", "cert_delta": 1,
    "recompute_per_condition_per_type_lift": recompute_A,
    "max_drift": max_drift_A,
    "c3_a_name_maintenance_marginal": {"mean": 0.05, "per_seed": [0.1, 0.05, 0.0], "cv": 0.816,
        "note": "exactly at LIFT_MIN floor; c3 generalizes_here NOT dependent on this type"},
    "c3_robust_types": {"b_competitive_coref": {"mean": 0.175, "cv": 0.309}, "c_overwrite": {"mean": 0.0716, "cv": 0.189}},
    "c3_independence_note": ("shares decode_dataset_slots('role_attn') filler-decode primitive with C1/C2 "
        "(expected/upstream-shared); independent specifically in entity-ADDRESSING mechanism (streaming "
        "nearest-committed-file cosine match vs WM-slot role_attn binding), verified by reading source lines "
        "211-310 of exp_situation_model_assembly_entity_file_v1.py"),
    "absolute_comprehension_not_solved": "coref abs ~0.65 < 0.70 PROVEN_MIN in parent arc -- this is a lever, not a solved capability",
    "kb_overlap_check": KB_CHECK,
    "cell_sha16": cellA_sha16, "prereg_sha16": preregA_sha16, "metrics_sha16": metricsA_sha16,
}

atomA = {
    "atom_id": AID_A, "seq": SEQ_A, "op": "atomize", "corpus": "math",
    "tier": "CHAIN_GRADE", "cert_status": "chain-grade",
    "grade": "CHAIN_GRADE_encoder_lever_generalizes_harder_difficulty_heldout_draw_independent_harness_c3_marginal_caveat",
    "verdict": "HARD_PASS", "anchor": "encoder_alltype_transfer_stress_v1",
    "anchor_name": "encoder_alltype_transfer_stress_v1",
    "cell": "experiments/exp_encoder_alltype_transfer_stress_v1.py",
    "cell_content_sha256_16": cellA_sha16,
    "prereg": "preregs/2026-07-31_encoder_alltype_transfer_stress_v1.md", "prereg_sha256_16": preregA_sha16,
    "metrics_path": "data/exp_encoder_alltype_transfer_stress_v1/metrics.json", "metrics_sha256_16": metricsA_sha16,
    "module": ("encoder_break_generalization_stress_3_conditions_harder_difficulty_heldout_draw_independent_"
        "entity_file_addressing_harness_multi_seed_drift_controlled"),
    "headline": HEADLINE_A, "key_metrics": key_metrics_A,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY independent recompute (.venv, off raw per-seed units.jsonl-derived "
        "fields in metrics.json, NOT verdict_msg): all 9 (condition x type) mean lifts recomputed exactly "
        "match stored per_type_mean; max|frozen2-frozen1| drift = 0.0 across all 27 (condition,type,seed) "
        "cells; independently verified C3's addressing mechanism is architecturally distinct by reading "
        "exp_situation_model_assembly_entity_file_v1.py source (calibrate_tau/_assign_commit, streaming "
        "nearest-committed-file cosine addressing)."),
    "composes_seq": [29593, 29594, 29595], "corrects_seq": [], "amends_seq": [29595],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": STORE_HEAD,
    "store_head_at_write_note": f"max seq across math+meta atoms + cert_ledger = {STORE_HEAD} at write; assigned {SEQ_A}",
    "honest_scope": ("Absolute comprehension is NOT solved: coref abs ~0.65 stays below the parent arc's 0.70 "
        "PROVEN_MIN. This is a proven-generalizing REPRESENTATION-QUALITY LEVER for entity-addressed "
        "comprehension, not a solved capability. C3's a_name_maintenance type is a marginal pass (mean "
        "exactly at the 0.05 floor, cv=0.82) -- do not cite it alone as evidence; cite b_competitive_coref "
        "(+0.175) and c_overwrite (+0.072) for C3, which independently satisfy the generalization bar."),
    "framing_correction": ("Amends 29595 (SCOPED to a single base_loop-harness measurement) -- THIS atom is "
        "the promotion from single-harness to cross-harness/cross-difficulty/cross-draw generalization. Do "
        "not cite 29595 alone as evidence the lever generalizes; cite 29596 for the generalization claim."),
    "fairness_verdict": ("FAIR. Pre-registered bands fixed before running (LIFT_MIN=0.05, N_TYPES_MIN=2, "
        "DRIFT_MAX=0.01, non-coref requirement). Drift control (frozen1 vs frozen2, two independently "
        "constructed extractor instances) is bit-identical in every cell -- the swap mechanism does not leak "
        "and the eval is deterministic, so lift is attributable ONLY to the ckpt swap. C1 strictly harder by "
        "construction (n_mods 8->16, lower token-copy probability). C2 uses a disjoint RNG stream on the same "
        "zero-train-leakage held-colors pool. C3 reuses a genuinely different, independently-authored entity-"
        "addressing mechanism (not written for this test)."),
    "revival_criteria": ("Further promotion: (1) a 4th, even-more-independent harness (e.g. a genuinely "
        "different sentence syntax, not just modifier-pool extension) would further de-risk the 'still "
        "base_loop-family templates' residual scope caveat; (2) naturalistic (non-synthetic) text validation "
        "remains the load-bearing open item per 29593's own scope. DEMOTE trigger: if a future independent "
        "harness with a genuinely different rendering grammar shows lift collapse, revisit this atom's "
        "generalization claim."),
    "primitive_assessment": ("No new primitive introduced by this VET -- this is a generalization AUDIT of "
        "the primitive already banked at 29593 (minimal-unfreeze top-1-layer encoder fine-tune). The finding "
        "is that the primitive's benefit is not harness-bound."),
    "promote_verdict": "GENERALIZATION_CONFIRMED_promotes_29595_scope_deploy_decision_still_PENDING_naturalistic_validation_per_29593",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atomA))

# ================= ATOM B =================
AID_B = ("math::encoder_generic_vs_entity_addressed_v1_MEASURED_MECHANISM_NO_FREE_LUNCH_NOT_A_CEILING_"
    "entity_consistency_only_objective_does_NOT_automatically_lift_an_UNTRAINED_orthogonal_skill_state_"
    "decode_flat_plus0p020_raw_CEILING_CONFOUNDED_frozen0p951_headroom0p049_closure0p41_comparable_to_P0p45_"
    "ENT0p48_MARK0p49_state_geometry_within_minus_cross_robustly_WORSENS_neg0p0405_all3seeds_tight_neg0p039_"
    "neg0p039_neg0p043_NOT_ceiling_bound_frozen0p28_real_directed_no_free_lunch_cost_NOT_evidence_of_intrinsic_"
    "unimprovability_state_was_never_trained_by_this_objective_trainability_UNTESTED_here_separate_fair_test_"
    "pending_P_placement_entity_adjacent_decode_lift_plus0p086_robust_partial_extension_ENT_geometry_ITSELF_"
    "not_robust_this_run_seed19_regresses_negative_neg0p0033_dragging_mean0p0175_below_0p02_interpretability_"
    "floor_MIDDLE_verdict_correctly_applied_per_own_prereg_gate_composes_29593_amends_draft_claim_LOCAL_ONLY_"
    "2026_07_31")
assert AID_B not in existing_ids

HEADLINE_B = ("MEASURED_MECHANISM (CERT +1, proven-bound). exp_encoder_generic_vs_entity_addressed_v1.py "
    "landed MIDDLE -- correct application of its own pre-registered gate (ENT-slot geometry delta mean=0.0175 "
    "< ENT_GEOM_MIN=0.02, dragged below floor by seed19 regressing to -0.0033; ENT geometry is NOT robustly "
    "reproduced this run, in contrast to the larger ~0.053 swing atom 29593 cited under a different "
    "measurement config -- this discrepancy is flagged OPEN, unresolved). Independent recompute confirms "
    "every stage/geom mean exactly. Three findings survive scrutiny: (1) P (placement) decode lift +0.086, "
    "robust all 3 seeds (0.080-0.091). (2) S (state) decode lift +0.020, robust-but-flat all 3 seeds "
    "(0.017-0.025) -- CONFOUNDED by a near-ceiling frozen baseline (0.951, headroom only 0.049); headroom-"
    "normalized closure (41%) is comparable to P (45%)/ENT (48%)/MARK (49%), so the raw-lift 'S is flat' "
    "framing is a CEILING ARTIFACT at the decode-accuracy level, not clean entity-specificity evidence -- "
    "honest downward correction of the spawn-drafted claim. (3) STATE-slot GEOMETRY (within-minus-cross "
    "cosine, NOT ceiling-bound, frozen ~0.28-0.29) robustly WORSENS by -0.0405, all 3 seeds tight and "
    "consistent (-0.0394/-0.0389/-0.0432) -- larger and MORE reproducible than ENT's own noisy +0.0175 mean. "
    "This IS a real, non-artifact, directed finding: the entity-focused fine-tune measurably degrades "
    "state-slot representational separability even while state decode accuracy stays flat/ceiling-shielded. "
    "Decode-level entity evidence (ENT +0.132 tight 0.129-0.134, MARK +0.084, entity_consistency +0.129 tight "
    "0.104-0.154) independently corroborates entity-addressed improvement via decode accuracy, separate from "
    "the noisy geometry probe -- entity representation genuinely improved; only the specific ENT within-"
    "minus-cross MAGNITUDE this run is underpowered/noisy (n=1 seed regression). VERDICT: the pre-registered "
    "ENTITY_ADDRESSING_SPECIFIC band (clean dissociation) does NOT cleanly hold -- P's headroom-normalized "
    "lift undercuts a hard decode-level entity/non-entity boundary, and ENT geometry itself is not robust "
    "this run. FRAMING (coordinator-corrected before atomizing): what DOES hold robustly is a NO-FREE-LUNCH "
    "finding, NOT a ceiling finding -- training the entity-consistency-only objective does not automatically "
    "lift an UNTRAINED, orthogonal skill (state) for free, and state-slot geometry pays a real, measured, "
    "directional cost. This is NOT evidence state (or any non-entity skill) is intrinsically unimprovable: "
    "state was never a training target here AND started near-ceiling on decode, so trainability of state (or "
    "any orthogonal skill) if DIRECTLY trained is UNTESTED by this cell -- a separate fair test (train an "
    "independent skill with real headroom, verify it lifts + stacks without clobbering the entity-consistency "
    "win) is the correct instrument for that question. TIER: MEASURED_MECHANISM, not CHAIN_GRADE and not the "
    "spawn-drafted HARD_FAIL/entity-specific/not-domain-general framing -- narrower, still genuine, framed as "
    "directed-improvement/no-free-lunch, not as a capability ceiling.")

key_metrics_B = {
    "cell_verdict": "MIDDLE", "auditor_tier": "MEASURED_MECHANISM_no_free_lunch_untrained_orthogonal_skill", "cert_delta": 1,
    "recompute_stage_lift": stages_recompute, "recompute_geom_delta": geom_recompute,
    "headroom_normalized_closure": headroom,
    "max_drift": max_drift_B,
    "ceiling_confound_correction": ("spawn-drafted claim framed S-decode as 'stays flat' evidence of "
        "entity-specificity; recompute shows S frozen=0.951 leaves only 0.049 headroom, and the 41% "
        "headroom-normalized closure is comparable to P/ENT/MARK (45-49%) -- raw-lift framing alone is a "
        "ceiling artifact, corrected here"),
    "state_geometry_no_free_lunch_cost": {"mean_delta": geom_recompute["state"]["mean"],
        "per_seed": geom_recompute["state"]["per_seed"], "frozen_range_not_ceiling_bound": "0.275-0.294",
        "all_seed_consistent": True, "robust_directed_cost_finding": True,
        "NOT_a_ceiling_claim": True,
        "coordinator_correction": ("state was never a training target of the entity-consistency-only "
            "objective, and its decode metric started near-ceiling (0.951) -- this shows training X does "
            "not automatically lift untrained orthogonal Y for free (no-free-lunch), NOT that Y is "
            "intrinsically unimprovable. Trainability of state if DIRECTLY trained is UNTESTED here; a "
            "separate fair test (train an independent skill with real headroom, verify lift+stack without "
            "clobbering entity-consistency) is the correct instrument, out of scope for this cell.")},
    "ent_geometry_not_robust_this_run": {"mean_delta": geom_recompute["ent"]["mean"],
        "per_seed": geom_recompute["ent"]["per_seed"], "seed19_regresses_negative": True,
        "below_interpretability_floor_0p02": True,
        "open_discrepancy": "atom 29593 cited a ~0.053 swing under a different measurement config; not reconciled here"},
    "entity_decode_robust_independent_of_geometry_probe": {
        "ENT_lift": stages_recompute["ENT"], "MARK_lift": stages_recompute["MARK"],
        "entity_consistency_lift": stages_recompute["entity_consistency"]},
    "P_lift_robust_entity_adjacent_partial_extension": stages_recompute["P"],
    "kb_overlap_check": KB_CHECK,
    "cell_sha16": cellB_sha16, "prereg_sha16": preregB_sha16, "metrics_sha16": metricsB_sha16,
}

atomB = {
    "atom_id": AID_B, "seq": SEQ_B, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_no_free_lunch_untrained_orthogonal_skill_NOT_a_ceiling_ceiling_confound_corrected_ent_geometry_not_robust_this_run",
    "verdict": "MIDDLE", "anchor": "encoder_generic_vs_entity_addressed_v1",
    "anchor_name": "encoder_generic_vs_entity_addressed_v1",
    "cell": "experiments/exp_encoder_generic_vs_entity_addressed_v1.py",
    "cell_content_sha256_16": cellB_sha16,
    "prereg": "preregs/2026-07-31_encoder_generic_vs_entity_addressed.md", "prereg_sha256_16": preregB_sha16,
    "metrics_path": "data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json", "metrics_sha256_16": metricsB_sha16,
    "module": ("encoder_break_non_entity_boundary_probe_state_placement_decode_plus_ENT_STATE_within_minus_"
        "cross_geometry_frozen_vs_tuned_ceiling_confound_analysis"),
    "headline": HEADLINE_B, "key_metrics": key_metrics_B,
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY independent recompute (.venv, off raw per-seed units.jsonl-derived "
        "fields in metrics.json): all stage/geom means recomputed exactly match stored bands. Added a "
        "headroom-normalization check NOT present in the cell's own verdict logic (fraction of available "
        "headroom-to-ceiling closed per stage) to test whether the S-decode 'flat' band decision is confounded "
        "by S's near-ceiling frozen baseline -- confirmed it is (41% closure, comparable to P/ENT/MARK "
        "45-49%). Verified state-geometry per-seed values are NOT ceiling-bound (frozen ~0.28-0.29, well "
        "below any plausible cosine ceiling) and are tight/all-seed-consistent, distinguishing this from a "
        "noise artifact."),
    "composes_seq": [29593], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": STORE_HEAD,
    "store_head_at_write_note": f"max seq across math+meta atoms + cert_ledger = {STORE_HEAD} at write; assigned {SEQ_B}",
    "honest_scope": ("Do NOT cite this atom as 'entity-addressing-specific, non-entity flat' (the spawn-"
        "drafted framing) -- that dissociation does not cleanly survive recompute (P lift is real and "
        "headroom-comparable to entity-slot lifts; ENT geometry itself failed to reproduce robustly this "
        "run). Do NOT cite this atom as evidence of an intrinsic ceiling or that non-entity/orthogonal skills "
        "are unimprovable -- state was never a training target of the entity-consistency-only objective and "
        "started near-ceiling on decode, so trainability-if-directly-trained is UNTESTED here (separate fair "
        "test pending). The load-bearing, defensible claim is narrower: a robust, all-seed-consistent, non-"
        "ceiling-bound NO-FREE-LUNCH cost to state-slot representational geometry from the entity-focused "
        "fine-tune (training X does not automatically lift untrained orthogonal Y). ENT-geometry-as-a-metric "
        "needs a rerun with more seeds/larger NCTX before it is safe to cite standalone (this run's mean is "
        "noise-dominated, driven negative by 1 of 3 seeds)."),
    "framing_correction": ("Spawn-drafted target claim ('S stays flat ... geometry mildly degrades', framed "
        "as evidence the lift 'is NOT domain-general/uniform') is corrected on three points: (1) 'S stays "
        "flat' at the raw-lift level is a ceiling artifact (S frozen already 0.951), not clean entity-"
        "specificity evidence -- downgraded per symmetric anti-negativity/anti-overclaim discipline. (2) "
        "'mildly degrades' undersells the state-geometry finding, which is LARGER in magnitude (-0.0405) and "
        "MORE reproducible (tight across seeds) than the entity-geometry uptick it was meant to be compared "
        "against (+0.0175, itself not robust). (3) COORDINATOR CORRECTION: the result must not be framed as "
        "'not domain-general' / a ceiling on improvability -- state was UNTRAINED by this objective and "
        "already near-ceiling, so this is a no-free-lunch (no automatic transfer) finding, not a trainability "
        "verdict; a separate direct-training fair test is the correct instrument for that open question."),
    "fairness_verdict": ("FAIR gate design (pre-registered LIFT_MIN/GEOM_FRAC_MIN/GEOM_FRAC_FLAT/ENT_GEOM_MIN "
        "fixed before running; drift control bit-identical, max_drift=0.0 -- eval deterministic, no leak). "
        "The cell's own MIDDLE verdict is the CORRECT mechanical output of its gate given ENT_GEOM_MIN=0.02 "
        "not clearing (0.0175). This atom does not dispute the mechanical verdict; it adds a headroom-"
        "normalization cross-check the pre-reg did not include, which materially changes the SUBSTANTIVE "
        "interpretation of the S-decode-flat result specifically."),
    "revival_criteria": ("(1) A SEPARATE, already-in-flight fair test: train an independent (state-adjacent "
        "or otherwise orthogonal) skill DIRECTLY, with real headroom, and check whether it lifts + stacks "
        "without clobbering the entity-consistency win -- this is the correct instrument to settle "
        "trainability; this atom's no-free-lunch finding neither confirms nor rules that out. (2) Rerun this "
        "cell with more seeds (5+) and/or larger GEOM_NCTX to determine whether ENT geometry robustly clears "
        "ENT_GEOM_MIN with more statistical power -- would resolve the open discrepancy against atom 29593's "
        "larger cited swing. (3) A decode-accuracy-based (not geometry-based) non-entity-vs-entity headroom-"
        "normalized comparison, run as the PRIMARY discriminator instead of raw lift, would give a cleaner "
        "test than this cell's own gate. (4) If a rerun shows state-geometry degradation does NOT replicate, "
        "DEMOTE this atom's no-free-lunch claim to noise."),
    "primitive_assessment": ("No new primitive; this is a boundary-characterization probe of the primitive "
        "banked at 29593. Finding: the fine-tune's benefit is not a uniform 'rising tide' onto UNTRAINED "
        "orthogonal skills -- training entity-consistency does not automatically lift an untrained skill "
        "(state) for free, and state-slot geometry pays a small but real, reproducible cost. This is a no-"
        "free-lunch finding about AUTOMATIC transfer, NOT a statement about whether state (or any orthogonal "
        "skill) is improvable if directly trained -- that remains open and is being tested separately."),
    "promote_verdict": "MEASURED_MECHANISM_no_free_lunch_finding_NOT_a_ceiling_trainability_of_orthogonal_skills_open_separate_fair_test_pending",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atomB))

# ---- A5 WRITE: atoms.jsonl (both atoms, one write) ----
new_line_A = json.dumps(atomA, ensure_ascii=False)
new_line_B = json.dumps(atomB, ensure_ascii=False)
assert "\r" not in new_line_A and "\n" not in new_line_A
assert "\r" not in new_line_B and "\n" not in new_line_B
new_text = "\n".join(atom_lines + [new_line_A, new_line_B]) + "\n"
d = os.path.dirname(os.path.abspath(ATOMS))
fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
with open(tmp, "w", encoding="utf-8", newline="") as f:
    f.write(new_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, ATOMS)
raw = open(ATOMS, "rb").read()
assert b"\r\n" not in raw, "CRLF doubling in atoms.jsonl"
v = [json.loads(l) for l in open(ATOMS, encoding="utf-8").read().splitlines() if l.strip()]
assert len(v) == len(atom_lines) + 2
assert v[-2]["atom_id"] == AID_A and v[-2]["tier"] == "CHAIN_GRADE" and v[-2]["cert_delta"] == 1
assert v[-1]["atom_id"] == AID_B and v[-1]["tier"] == "MEASURED_MECHANISM" and v[-1]["cert_delta"] == 1
print(f"ATOMS OK: {len(atom_lines)} -> {len(v)}; seq {SEQ_A} CHAIN_GRADE +1, seq {SEQ_B} MEASURED_MECHANISM +1; no CRLF.")

# ---- A5 WRITE: cert_ledger.jsonl (both) ----
ledgerA = dict(atomA)
ledgerA["decision"] = ("CHAIN_GRADE CERT +1. Independent recompute of the generalization-stress cell confirms "
    "HARD_PASS: all 3 conditions (harder-difficulty, disjoint held-out draw, independent entity-addressing "
    "harness) clear the pre-registered lift>=0.05 on >=2/3 types incl non-coref, drift-controlled (max_drift="
    "0.0), matching every stored number exactly from raw per-seed units. Promotes 29595's single-harness "
    "SCOPED lift to a cross-harness/cross-difficulty/cross-draw generalization claim for the certified "
    "minimal-unfreeze encoder break (29593). One caveat rides the atom: C3's a_name_maintenance type is "
    "marginal (mean exactly at floor, high cv); C3's own pass does not depend on it.")
ledgerA["note"] = (f"AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off metrics.json raw units, not "
    f"verdict_msg. Hashes: cell {cellA_sha16}, prereg {preregA_sha16}, metrics {metricsA_sha16}. Composes "
    f"29593/29594/29595; amends 29595's scope.")
ledgerB = dict(atomB)
ledgerB["decision"] = ("MEASURED_MECHANISM CERT +1. The cell's own MIDDLE verdict is mechanically correct "
    "(ENT-slot geometry delta 0.0175 < 0.02 floor, driven by a seed19 regression). Independent recompute adds "
    "a headroom-normalization check the pre-reg lacked: S-decode's raw 'flat' result is a ceiling artifact "
    "(41% headroom-normalized closure, comparable to P/ENT/MARK 45-49%), so the spawn-drafted ENTITY_"
    "ADDRESSING_SPECIFIC dissociation framing does NOT survive cleanly. What DOES survive: a robust, all-"
    "seed-consistent, non-ceiling-bound directed WORSENING of state-slot representational geometry (-0.0405, "
    "tight -0.039/-0.039/-0.043) from the entity-focused fine-tune. COORDINATOR CORRECTION applied before "
    "atomizing: this is banked as a NO-FREE-LUNCH finding (training the entity-consistency-only objective "
    "does not automatically lift an UNTRAINED, near-ceiling orthogonal skill for free), explicitly NOT as "
    "evidence the lift 'is not domain-general' or of any intrinsic ceiling on improvability -- trainability "
    "of state (or any orthogonal skill) if directly trained is UNTESTED here and is being tested separately. "
    "Banked at MEASURED_MECHANISM rather than the originally-drafted HARD_FAIL/entity-specific/not-domain-"
    "general tier.")
ledgerB["note"] = (f"AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off metrics.json raw units. "
    f"Hashes: cell {cellB_sha16}, prereg {preregB_sha16}, metrics {metricsB_sha16}. Composes 29593. Corrects "
    f"the spawn-drafted claim framing (ceiling-confound on S-decode; ENT-geometry non-replication flagged "
    f"open; NO-FREE-LUNCH not ceiling framing per coordinator correction 2026-07-31).")
for led in (ledgerA, ledgerB):
    json.loads(json.dumps(led))
led_lines = [json.dumps(ledgerA, ensure_ascii=False), json.dumps(ledgerB, ensure_ascii=False)]
for l in led_lines:
    assert "\r" not in l and "\n" not in l
new_led = "\n".join(ledger_lines + led_lines) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_led); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
assert b"\r\n" not in open(LEDGER, "rb").read(), "CRLF doubling in ledger"
vl = [json.loads(l) for l in open(LEDGER, encoding="utf-8").read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 2
assert vl[-2]["atom_id"] == AID_A and iseq(vl[-2]) == SEQ_A
assert vl[-1]["atom_id"] == AID_B and iseq(vl[-1]) == SEQ_B
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seq {SEQ_A}/{SEQ_B}; +1/+1 cert_delta; no CRLF.")
print(f"DONE. atom_id_A={AID_A}")
print(f"DONE. atom_id_B={AID_B}")
print("LOCAL-ONLY. no origin push; no remote persist.")
