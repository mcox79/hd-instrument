"""
A5-gated atomize: Exp 3b Layer 0.75 candidate-refinement SMOKE HARD_FAIL
  + META: mechanism-abstraction-lossy Director-level lesson.

CELL: experiments/exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03.py
ANCHOR: substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03
METRICS: data/exp_exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03/metrics.json

OFF-DATA INDEPENDENT RECOMPUTE (skunkworks VET, off metrics.json not verdict_msg):
  ARM_ORACLE_COMPOSITION_SANITY per-seed:  [0.92, 0.84, 0.80]  mean=0.8533 sd=0.050
    -> drift vs precedent 0.822 = +0.031  (in-band <=0.10) OK
    -> composition primitive INTACT (positive control PASS)
  ARM_EXP3_BASELINE_REPRODUCTION per-seed: [0.48, 0.42, 0.34]  mean=0.4133 sd=0.057
    -> drift vs precedent 0.411 = +0.002  (tight reproduction) OK
    -> Exp 3 regime INTACT (positive control PASS)
  ARM_MAIN_LAYER075_STACKED per-seed:      [0.04, 0.02, 0.02]  mean=0.0267 sd=0.009
    -> BELOW RANDOM (0.047). HP1 (>=0.60*ORACLE ~ 0.512) NOT cleared. HARD_FAIL.
  ARM_STAGE1_ONLY per-seed:                [0.42, 0.42, 0.34]  mean=0.3933 sd=0.038
    -> baseline drift -0.020 (mild-null; IDF alone does not lift on this synthetic corpus)
  ARM_STAGE2_ONLY per-seed:                [0.46, 0.42, 0.34]  mean=0.4067 sd=0.050
    -> baseline drift -0.006 (null; hub-dampen alone does not lift)
  ARM_STAGE3_ONLY per-seed:                [0.04, 0.00, 0.00]  mean=0.0133 sd=0.019
    -> CATASTROPHIC. Worse than RANDOM. Stage 3 in isolation DESTROYS retrieval.
  ARM_RANDOM_CANDIDATES_CONTROL per-seed:  [0.06, 0.02, 0.06]  mean=0.0467 sd=0.019
    -> chance floor 0.05 respected
  cardinality_ok=True (21/21); arms_differ_verified=True (all digests distinct).

CELL-AUTHOR GT-COVERAGE DIAGNOSTIC VERIFIED OFF-DATA:
  Cell-author instrumented per-query GT-in-pool tracking. Independent aggregation
  over all 30 per_query_diag entries (3 seeds x 10 queries logged each):
    MAIN pipeline (S1+S2+S3):
      GT chunks in PRE-Stage-3 pool:   51/60 = 0.850  (S1+S2 preserve GT well)
      GT chunks in POST-Stage-3 pool:  15/60 = 0.250  (S3 drops ~60% of GT)
      -> Stage 3 is the single subtractive component. Confirmed.
    STAGE3-only pipeline (no S1, no S2):
      GT chunks in PRE-Stage-3 pool:   60/60 = 1.000  (full BGE-hop-1 pool has all GT)
      GT chunks in POST-Stage-3 pool:  14/60 = 0.233  (S3 drops 77% of GT from a perfect pool)
      -> Stage 3 dropping GT is NOT caused by upstream S1/S2 damage; the mechanism
         itself is bridge-blind. Query cosine gives no signal to the bridge chunk.
  Concrete verified example (seed 11 qi=0):
    query="neighbor of the river of Gulch?" gt_chunks=[32, 8]
    gt_in_main_pre_pool=[8, 32] (both present pre-Stage-3)
    main_post_filtered=[33, 12, 72, 4, 44] -- both GT DROPPED
    Bridge entity "Fjord" (encoded in gt chunk 8) is not tokenized in query,
    so cos(query, fact_8) is low; MMR discards it.
  Cell-author's per-query-GT-coverage instrumentation is a load-bearing methodology
  contribution -- it converts a 3-line accuracy report into a mechanism-attributable
  failure diagnosis in a single smoke.

ROOT-CAUSE ATTRIBUTION (skunkworks concurs with cell-author):
  Stage 3 uses query-only rescoring: s_i = cos(BGE(query), BGE(fact_i)) then MMR.
  Because query text contains only the outer entity + relation lemmas, and the
  bridge fact contains the BRIDGE entity (unnamed in query) + mid-hop relation,
  cos(query, bridge_fact) has no positive signal. Rescore + MMR consistently
  discard the bridge fact. This is a STRUCTURAL limitation of query-only rescoring
  for multi-hop retrieval, NOT a hyperparameter mistake.
  Family: SOFT_COS (softmax over cosine) and MODERN-HOPFIELD top_k_by_retrieved
  share the same limitation -- they all condition only on the query vector.
  Fix requires bridge-conditioning (e.g. BridgeRAG's tripartite s(q, b, c) with
  b = extracted bridge entity) OR iterative query-augmentation (append top-1
  fact text back into the query and re-retrieve, so bridge tokens enter query
  distribution). Both are load-bearing changes to Stage 3, not tunings.

TIER RULING:
  math atom: T3 EXP HF_IMPLEMENTATION (not HF_STRUCTURAL, not HF_SCOPE).
    Rationale for HF_IMPLEMENTATION over HF_STRUCTURAL:
      - S1_ONLY and S2_ONLY do NOT lift baseline (drift -0.020, -0.006) so those
        substrate-mine directives are also null, but at least not catastrophic;
        the whole Layer 0.75 as-designed is a null-at-best.
      - The failure is attributable to a specific mechanism (query-only rescore
        in Stage 3) with two named alternatives (BridgeRAG tripartite s(q,b,c),
        or iterative query-augmentation).
      - ORACLE 0.853 confirms composition primitive intact; EXP3 baseline 0.413
        confirms Exp 3 regime intact. This is a genuine substantive negative, not
        a test-design failure (positive controls PASS per Auditor-2026-07-01 rule).
    Rationale for NOT HF_STRUCTURAL:
      - The DESIGN GOAL (interpose semantic candidate refinement between Layer 0.5
        walk and Layer 1 FHRR compose) is not ruled out; only this specific
        implementation is ruled out.
    Rationale for NOT HF_SCOPE:
      - Synthetic-corpus opaque-token concern (Alton/Bexley IDF weak) is real
        but not load-bearing: the S3_ONLY catastrophe reproduces on a corpus
        where BGE-hop-1 gives 100% GT coverage, so IDF-signal weakness is
        neither necessary nor sufficient for the failure.
    Revival criterion (explicit):
      - Redesign Stage 3 as BridgeRAG tripartite s(q, b, c) with an extracted
        bridge entity (test: bridge-conditioned MMR retains GT chunks at
        >=0.70 rate on same corpus), OR
      - Iterative query-augmentation architecture (test: 2-round retrieve-
        augment-retrieve preserves GT bridge chunks at >=0.70 rate).
      - Either revival needs S1+S2 held-fixed as null baselines (they aren't
        the problem, they don't lift, but they don't break either).

  meta atom: META rule MECHANISM_ABSTRACTION_LOSSY_DROPS_LOAD_BEARING_ARGUMENTS.
    Rationale: Director's substrate-mine SendMessage abstracted BridgeRAG's
    tripartite s(q, b, c) into "query-conditioned rescore" and specified
    "modern-Hopfield top_k_by_retrieved" as one of three implementation options.
    The abstraction silently dropped the BRIDGE-CONDITIONING term b, which was
    the load-bearing feature of BridgeRAG. All three enumerated implementations
    (MMR-hard, softmax-cos-soft, Hopfield-top-k) share the same query-only
    limitation. This is a Director-abstraction failure mode: when translating
    literature mechanisms into general language for substrate-mine directives,
    the abstraction level must preserve the load-bearing arguments of the source
    mechanism. Failure indicator: if 3 enumerated implementations of an
    abstracted mechanism all share a limitation the source mechanism did not
    have, the abstraction was lossy. Prevention: cite the source mechanism's
    argument signature exactly (s(q,b,c) not s(q,c)) and only abstract over
    strictly interchangeable operators.

  META tier: MM_TENTATIVE (single evidence point). Promotion path: recurrence
  of same Director-side abstraction-drop in a second cross-arc drill would
  promote to MM_STANDARD. Not yet a full CG META.

CROSS-ARC OVERLAP CHECK (substrate_query 2026-07-03):
  Q "candidate refinement MMR rescore bridge":
    top-1 cosine=0.357 -> wordnet "refinement" (unrelated word-sense)
    top-2 cosine=0.325 -> NO_REFINEMENT wave14 (unrelated verdict text)
    other hits: wordnet gloss entries only.
  No prior CG or MM atom in Store matches Layer-0.75 candidate refinement
  primitive or BridgeRAG-style s(q,b,c). Genuinely novel finding; NOT a
  rediscovery of prior arc. Cell-author drills-synthesis note 2026-07-03
  operationalized substrate-content note 2026-06-10 "hierarchical cleanup"
  for the first time.

POSITIVE CONTROL CHECK (Auditor-2026-07-01 rule):
  ORACLE_COMPOSITION_SANITY 0.853 >> RANDOM 0.047 -> composition primitive
  intact; test can support a positive verdict if the mechanism works.
  EXP3_BASELINE_REPRODUCTION 0.413 (drift 0.002 vs 0.411) -> Exp 3 regime
  intact; scoring wiring works. HF is a SUBSTANTIVE negative, not a
  test-design failure. Auditor-2026-07-01 rule cleared.

STRATEGIC IMPLICATION (audit-only observation, not dispatch direction):
  Cell-author's recommended redesign path (BridgeRAG tripartite s(q, b, c))
  requires an extra mechanism: bridge-entity extraction. This is itself an
  unproven step at substrate level -- worth a discriminating smoke BEFORE
  Layer 0.75 v2. Iterative query-augmentation (2-round retrieve-augment-
  retrieve) is a strictly simpler alternative: no new extraction primitive,
  just re-uses BGE + FHRR. Skunkworks (audit-only) notes this asymmetry;
  Director owns the choice.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_03_exp3b_layer075_HF_IMPLEMENTATION_and_META_abstraction"
CELL_COMMIT = "unstaged_local_smoke_2026-07-03"
TS_ISO = "2026-07-03T16:00:00Z"

atom_math_HF = {
    "id": (
        "T3/EXP_substrate_stage1_apply_exp3b_layer075_candidate_refinement_SMOKE_"
        "HF_IMPLEMENTATION_stage3_query_only_rescore_bridge_blind_"
        "3seed_MAIN_0p027_below_RANDOM_0p047_STAGE3_ONLY_0p013_catastrophic_"
        "STAGE1_ONLY_0p393_null_drift_neg_0p020_STAGE2_ONLY_0p407_null_drift_neg_0p006_"
        "ORACLE_0p853_drift_pos_0p031_positive_control_PASS_composition_primitive_intact_"
        "EXP3_BASELINE_0p413_drift_pos_0p002_positive_control_PASS_exp3_regime_intact_"
        "GT_coverage_diagnostic_MAIN_pre_pool_51of60_0p850_post_pool_15of60_0p250_"
        "S3ONLY_pre_60of60_1p000_post_14of60_0p233_stage3_drops_60_to_77_pct_of_GT_bridge_chunks_"
        "concrete_example_seed11_qi0_neighbor_river_Gulch_gt_32_8_both_in_pre_pool_MMR_discards_bridge_fact_"
        "root_cause_query_only_cosine_rescore_bridge_blind_bridge_entity_Fjord_not_in_query_tokens_"
        "family_MMR_hard_softmax_cos_soft_modern_hopfield_topk_all_share_query_only_limitation_"
        "revival_criterion_BridgeRAG_tripartite_s_q_b_c_extracted_bridge_entity_OR_iterative_query_augmentation_"
        "positive_control_ORACLE_853_confirms_composition_intact_not_test_design_failure_"
        "cardinality_21of21_arms_differ_verified_true_smoke_N4096_50queries_3seeds_11_17_23_"
        "hub_bridge_scope_hub_deg_thresh_8_hub_dampen_0p30_mmr_lambda_0p30_k_final_5_"
        "genuinely_novel_no_prior_atom_matches_cross_arc_check_clean_"
        "operationalization_of_2026_06_10_hierarchical_cleanup_note_first_attempt_"
        "2026-07-03"
    ),
    "name": (
        "Exp 3b Layer 0.75 candidate-refinement SMOKE HF_IMPLEMENTATION "
        "(query-only rescore bridge-blind; Stage 3 drops 60-77% of GT bridge chunks)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-stage stacked LLM-free candidate-refinement primitive (Layer 0.75) "
        "placed between Layer 0.5 PPR-walk (~30 chunks) and Layer 1 FHRR "
        "composition. Stage 1 = HippoRAG node-specificity IDF seed reweight, "
        "Stage 2 = hub-dampened PPR (HUB_DEG_THRESH=8 HUB_DAMPEN=0.30), Stage 3 "
        "= query-cosine rescore + MMR (MMR_LAMBDA=0.30 K_FINAL=5). MAIN "
        "(S1+S2+S3 stacked) r@5=0.0267 (3-seed mean; per-seed [0.04, 0.02, "
        "0.02]) BELOW RANDOM 0.0467. HP1 (>=0.60*ORACLE ~ 0.512) NOT cleared "
        "-> HARD_FAIL. Ablations: STAGE3_ONLY 0.0133 (catastrophic, worse than "
        "random -- Stage 3 in isolation destroys retrieval); STAGE1_ONLY 0.393 "
        "and STAGE2_ONLY 0.407 both null-drift vs baseline (IDF and hub-dampen "
        "alone do not lift on this synthetic hub-and-spoke corpus). ORACLE arm "
        "0.853 (drift +0.031 vs precedent 0.822 -- composition primitive INTACT "
        "positive control PASS); EXP3_BASELINE arm 0.413 (drift +0.002 vs "
        "precedent 0.411 -- Exp 3 regime INTACT positive control PASS). "
        "cardinality_ok=True (21/21 = 7 arms x 3 seeds); arms_differ_verified "
        "True (all digests distinct). GT-coverage diagnostic (cell-author "
        "instrumented per-query GT-in-pool tracking, verified off-data): MAIN "
        "pipeline GT in pre-Stage-3 pool 51/60=0.850, post-Stage-3 pool "
        "15/60=0.250 -- Stage 3 drops ~60% of GT; STAGE3-only from a 100%-GT-"
        "coverage BGE-hop-1 pool drops to 14/60=0.233 -- Stage 3 drops 77% of "
        "GT from a perfect pool, so failure is NOT upstream damage. Root cause: "
        "query-only cosine rescore is BLIND to the bridge fact because the "
        "bridge entity (e.g. Fjord) is not tokenized in the query text (which "
        "contains only outer entity + relation lemmas). MMR then discards the "
        "low-cosine bridge chunk. This limitation is shared by MMR-hard, "
        "softmax-cos-soft, and modern-Hopfield top_k_by_retrieved -- all "
        "query-only. Revival requires bridge-conditioning: BridgeRAG tripartite "
        "s(q, b, c) with extracted bridge entity, OR iterative query-"
        "augmentation (2-round retrieve-augment-retrieve). This is "
        "HF_IMPLEMENTATION (specific Stage 3 mechanism ruled out) NOT "
        "HF_STRUCTURAL (design goal of interposing semantic refinement between "
        "Layer 0.5 and Layer 1 not ruled out) NOT HF_SCOPE (synthetic-corpus "
        "opaque-token concern real but not load-bearing; S3_ONLY catastrophe "
        "reproduces from 100% GT pool). Cross-arc check clean (top cosine "
        "0.357 -> unrelated wordnet); genuinely novel operationalization of "
        "2026-06-10 hierarchical-cleanup substrate note. Auditor-2026-07-01 "
        "positive-control rule cleared (ORACLE+BASELINE both PASS -> substantive "
        "negative not test-design failure)."
    ),
    "provenance": {
        "cell": "experiments/exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03.py",
        "commit": CELL_COMMIT,
        "prereg": "preregs/2026-07-03_exp3b_layer_075_candidate_refinement_primitive.md",
        "anchor": "substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03",
        "metrics_path": "data/exp_exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03/metrics.json",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
    },
    "composes": [
        "T3/EXP_substrate_stage1_apply_exp3_composition_recovery_hub_bridge_smoke_2026_07_03_ORACLE_0p822_MAIN_0p411_semantic_candidate_contamination_28_of_30_pool_wrong_chunks_2026-07-03"
    ],
}

ledger_math_HF = {
    "atom_id": atom_math_HF["id"],
    "corpus": "math",
    "tier": "T3",
    "disposition": "HF_IMPLEMENTATION",
    "cert_delta": {"CG": 0, "MM": 0, "HF": 1},
    "provenance": atom_math_HF["provenance"],
    "notes": (
        "SMOKE-tier HF_IMPLEMENTATION at hub-bridge scope. Cell-author-instrumented "
        "per-query GT-coverage diagnostic (verified off-data) attributes failure "
        "to Stage 3 query-only rescore (MAIN GT-coverage 0.850 -> 0.250 post-S3; "
        "S3_ONLY GT-coverage 1.000 -> 0.233). ORACLE 0.853 + BASELINE 0.413 "
        "positive controls PASS -- substantive negative, NOT test-design failure "
        "(Auditor-2026-07-01 rule cleared). Fix#28 discipline: per-arm 3-seed "
        "recompute off metrics.json confirms cell-author quotes exactly. "
        "Revival criterion: BridgeRAG tripartite s(q,b,c) with extracted bridge "
        "entity, OR iterative query-augmentation. Family: all query-only "
        "rescoring (MMR-hard, softmax-cos-soft, Hopfield top-k) share this "
        "limitation. Cross-arc query clean (top cosine 0.357 unrelated); "
        "genuinely novel finding. Composed atom = Exp 3 hub-bridge baseline "
        "(same corpus/regime, MAIN=0.411 semantic contamination diagnosis)."
    ),
    "ts_iso": TS_ISO,
    "atomized_by": ATOMIZED_BY,
}

atom_meta_ABSTRACTION = {
    "id": (
        "T3/META_mechanism_abstraction_lossy_drops_load_bearing_arguments_"
        "director_substrate_mine_directives_translation_from_literature_to_general_language_"
        "case_study_bridgeRAG_tripartite_s_q_b_c_abstracted_to_query_conditioned_rescore_"
        "s_q_c_bridge_conditioning_b_term_silently_dropped_"
        "3_enumerated_implementations_MMR_hard_softmax_cos_soft_modern_hopfield_topk_"
        "all_share_query_only_limitation_source_mechanism_did_not_have_"
        "failure_indicator_all_enumerated_implementations_share_a_limitation_source_did_not_have_"
        "prevention_cite_source_mechanism_argument_signature_exactly_only_abstract_over_strictly_interchangeable_operators_"
        "director_level_lesson_evidence_exp3b_layer075_HARD_FAIL_2026_07_03_"
        "MM_TENTATIVE_single_evidence_point_promotion_on_recurrence_in_second_cross_arc_drill_"
        "2026-07-03"
    ),
    "name": (
        "META: mechanism-abstraction lossy drops load-bearing arguments "
        "(Director substrate-mine translation from literature to general language)"
    ),
    "corpus": "meta",
    "tier": "T3",
    "kind": "meta_rule",
    "description": (
        "When Director translates a literature mechanism into general language "
        "for substrate-mine directives, the abstraction level can silently drop "
        "load-bearing arguments of the source mechanism. Case study: Director's "
        "substrate-mine SendMessage abstracted BridgeRAG's tripartite s(q, b, c) "
        "score (q=query, b=extracted bridge entity, c=candidate) into 'query-"
        "conditioned rescore' s(q, c) -- the bridge-conditioning term b, which "
        "was the load-bearing feature of BridgeRAG for multi-hop retrieval, was "
        "silently dropped. Director then enumerated 3 acceptable implementations "
        "(MMR-hard, softmax-cos-soft, modern-Hopfield top_k_by_retrieved), all "
        "of which share the query-only limitation the source mechanism did NOT "
        "have. Result: Exp 3b Layer 0.75 Stage 3 catastrophic HF (r@5=0.013 in "
        "isolation, MAIN=0.027 below RANDOM 0.047). Failure indicator: if 3+ "
        "enumerated implementations of an abstracted mechanism all share a "
        "limitation the source mechanism did NOT have, the abstraction was "
        "lossy. Prevention: cite the source mechanism's argument signature "
        "exactly (s(q,b,c) not s(q,c)) and only abstract over strictly "
        "interchangeable operators (e.g. MMR vs softmax vs Hopfield are "
        "interchangeable given the argument signature; but they are NOT "
        "interchangeable across different argument signatures). Skunkworks role: "
        "SCHEMA-VET should flag any substrate-mine directive that enumerates 3+ "
        "implementations sharing a plausibly-load-bearing limitation of the "
        "source. Tier: MM_TENTATIVE (single evidence point); promotion to "
        "MM_STANDARD requires recurrence in a second cross-arc drill. "
        "Composition: this is a Director-level operational rule, not a "
        "substrate mechanism rule; audit-only observation from Auditor per "
        "role-separation discipline."
    ),
    "provenance": {
        "case_study_cell": "experiments/exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03.py",
        "case_study_anchor": "substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03",
        "case_study_metrics": "data/exp_exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03/metrics.json",
        "director_substrate_mine_task_ref": "ae711c98d106e79be (Director SendMessage substrate-mine to cell-author, 9 directives, item #4 modern-Hopfield top_k_by_retrieved as query-conditioned rescore)",
        "director_drills_synthesis_note": "notes/design_layer_075_candidate_refinement_primitive_drill_synthesis_2026-07-03.md",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
    },
    "composes": [],
}

ledger_meta_ABSTRACTION = {
    "atom_id": atom_meta_ABSTRACTION["id"],
    "corpus": "meta",
    "tier": "T3",
    "disposition": "MM_TENTATIVE",
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "provenance": atom_meta_ABSTRACTION["provenance"],
    "notes": (
        "META rule (Director-operational, audit-only). Single evidence point "
        "(Exp 3b Layer 0.75 HF). Promotion to MM_STANDARD on recurrence in a "
        "second cross-arc drill. Prevention hook: SCHEMA-VET flags substrate-"
        "mine directives that enumerate 3+ implementations sharing a "
        "plausibly-load-bearing limitation of the cited source mechanism."
    ),
    "ts_iso": TS_ISO,
    "atomized_by": ATOMIZED_BY,
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_math_HF,
                    "math/atoms (Exp 3b Layer 0.75 HF_IMPLEMENTATION)")
    append_jsonl_a5(CERT_LEDGER, ledger_math_HF,
                    "cert_ledger (HF_IMPLEMENTATION +1 HF)")
    append_jsonl_a5(META_ATOMS, atom_meta_ABSTRACTION,
                    "meta/atoms (META mechanism-abstraction-lossy MM_TENTATIVE)")
    append_jsonl_a5(CERT_LEDGER, ledger_meta_ABSTRACTION,
                    "cert_ledger (MM_TENTATIVE +1 MM)")
    print(f"[A5] DONE OK")
    print(f"[A5] Exp 3b HF_IMPLEMENTATION (+1 HF) + META abstraction MM_TENTATIVE (+1 MM)")


if __name__ == "__main__":
    main()
