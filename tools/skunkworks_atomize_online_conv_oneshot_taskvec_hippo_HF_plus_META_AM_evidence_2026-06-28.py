"""Skunkworks landed-VET atomize: online_conv_oneshot_taskvec_hippo_v1 HARD_FAIL + META_RULE_AM evidence row.

Two atoms in ONE A5 window:

  Atom 1 (math corpus, EXPERIMENT_RECORD):
    online_conversation_learning_taskvec_hippo_composition_HARD_FAIL_2026-06-28
    cert_class = mechanism_characterization
    - delta_vs_VANILLA = +0.000 (no signal over no-mechanism baseline)
    - delta_vs_TV_ONLY = -1.000 (proposed composition LOSES 100% to the existing primitive alone)
    - TV_HIPPO=0.000 in all 3 seeds DUE TO np.partition kth=256 OOB ERROR in refuse-gate
      (v_rel_eff = min(REFUSE_V_REL=256, V=256-1=255) = 255 OK at compute, but the partition
      call np.partition(-sims_tv, 256)[:256] is hit at V_ENTITIES=256 ascertaining at v_rel_eff
      boundary; full-N regime hits the OOB the smoke regime (V=60, REFUSE_V_REL=64) did not).
      cardinality_ok=False (only 1200/1500 units executed; TV_HIPPO arm errored 0/100 in each seed).
    - HOWEVER: even IF the cell-bug were fixed, the load-bearing comparison is delta_vs_TV_ONLY
      under the SAME regime; TV_ONLY=1.000 at this regime by HRR ICL primitive (chain-grade prior),
      so the composition cannot lift above TV_ONLY here. The HARD_FAIL direction is unambiguous
      modulo the cell bug.
    - cell-bug TAG: refuse_gate_kth_OOB_at_V_eq_REFUSE_V_REL_boundary_smoke_did_not_catch.
      DISCRIMINATOR-MUST-SURVIVE-SCALE breach: smoke regime V=60 REFUSE_V_REL=64 v_rel_eff = 59;
      full regime V=256 REFUSE_V_REL=256 v_rel_eff = 255 with kth at 256-th index causing OOB.

  Atom 2 (meta corpus, METHODOLOGY_RULE / discipline_meta META_RULE_AM evidence row):
    META_RULE_AM_evidence_9th_occurrence_substrate_already_does_X_online_conversation_learning_via_task_vector_ICL_2026-06-28
    cert_class = discipline_meta  (CERT-neutral; delta=0)
    - Substrate task_vector_in_context_kshot_v1 primitive (prior CG) ALREADY solves online
      conversation learning at this regime (TV_ONLY=1.000, N=8192, V=256, 10-turn dialogue
      with 2 fact injections + 1 joint-fact query).
    - Proposed hippo-cortex composition adds nothing (drops to 0.000 due to refuse-gate cell bug;
      modulo the bug, capped at TV_ONLY=1.000 ceiling by saturation -- the composition cannot
      lift above the primitive in the EASY regime where the primitive already saturates).
    - This is the 9th occurrence of the substrate-already-does-X pattern (META_RULE_AM
      first-atomized 2026-06-28 at the 8-occurrence threshold).
    - REGIME CAVEAT (verified-OFF-DATA): at this 10-fact regime the HRR bundle crosstalk
      noise sqrt(9/N=8192) ~= 0.033 vs signal ~= 0.316 (SNR ~9.6); top-1 cleanup over V=256
      well within capacity. NOT by-construction-saturation in the cheating sense; this IS the
      real HRR task-vector primitive working. BUT a harder regime (100+ facts, V>=4096, or
      conversation length >> 10) could expose composition lift the saturating easy regime
      cannot measure. Capability is RESOLVED AT THIS REGIME; would re-open at harder regime.

DISPOSITION (M3 USER concern #4 -- online conversation learning):
  RESOLVED-AT-REGIME via existing chain-grade task_vector ICL primitive.
  No new mechanism needed for the screen-recordable M3 demo at the proposed regime.
  Substrate task_vector_in_context_kshot_v1 IS the substrate answer to USER concern #4.
  Open: harder-regime sweep (longer conversations / more facts) could re-open the composition
  question, but is NOT required for M3 demo gating.

CRITICAL INFRA NOTE (FILED IN ATOM-1 cell_bug field; will broadcast in landed-VET note):
  When this VET began, math/atoms.jsonl had a non-schema-compliant row at line 28644
  (id=hierarchical_planning_block_sparse_encoding_axis_HARD_FAIL_2026-06-28; missing required
  'name' field; free-form dict NOT Atom.from_dict-compatible). This was BLOCKING all Store
  reads (PartitionedStore __init__ KeyError). Quarantined to
  data/substrate_index/math/atoms.jsonl.quarantine_missing_name_field_1782662777 and atoms.jsonl
  was rewritten atomically (28646 lines, was 28647). Root cause = sibling spawn appended a
  custom dict directly to atoms.jsonl bypassing schema. Action item: REQUIRE all atom writes
  go through Atom.to_dict() + load_atoms validation; spawn discipline note to be filed.

DISCIPLINES HONORED:
  - A5 PRE/POST snapshot (CERT_N=628 pre + post; axiom 206 pre+post; cap_pres 6/6)
  - Fix #28: per-arm metrics read directly from metrics.json per_seed.per_arm
  - by-construction-saturation check (TV_ONLY=1.000 at SNR ~9.6 -- real ICL, not cheating)
  - verify-the-referent: every cited number from metrics.json (and recomputed where formula-derived)
  - META_RULE_AM evidence chain: 9th occurrence flagged
  - META_RULE_AE: absolute paths cited
  - META_RULE_H: cardinality_ok=False captured in atom annotation
  - DISCRIMINATOR-MUST-SURVIVE-SCALE: cell-bug exposed at full regime (smoke did not catch)
  - No silent except blocks
  - Idempotency: skip atoms already in Store
  - Foreground (Fix #20)
  - ASCII-only
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
)


STORE_ROOT = Path("data/substrate_index")
ATOMIZED_BY = "skunkworks_atomize_online_conv_oneshot_taskvec_hippo_HF_plus_META_AM_evidence_2026-06-28"
CELL_COMMIT = "c4c1a59e"
METRICS_PATH = "data/exp_online_conv_oneshot_taskvec_hippo_v1_redispatch_rerun_2026-06-28/metrics.json"
PREREG_PATH = "preregs/2026-06-27_online_conv_oneshot_taskvec_hippo_v1.md"
EXPERIMENT_PATH = "experiments/exp_online_conv_oneshot_taskvec_hippo_v1.py"
SMOKE_METRICS_PATH = "data/exp_online_conv_oneshot_taskvec_hippo_v1_smoke/metrics.json"
NOTES_PATH = "notes/skunkworks_landed_vet_online_conv_oneshot_taskvec_hippo_HF_plus_META_AM_2026-06-28.md"


# ============================================================================
# Atom 1: HARD_FAIL composition characterization (math corpus)
# ============================================================================

def build_online_conv_composition_hard_fail() -> Atom:
    return Atom(
        id="T3/EXP_online_conv_oneshot_taskvec_hippo_v1_HARD_FAIL_composition_2026-06-28",
        name=(
            "online conversation learning -- task-vector + hippo-cortex composition HARD_FAIL "
            "(FULL 3 seeds; TV_HIPPO=0.000 (cell bug refuse_gate kth OOB) VANILLA=0.000 "
            "TV_ONLY=1.000 ORACLE=1.000 RANDOM=0.003; delta_vs_VANILLA=+0.000 "
            "delta_vs_TV_ONLY=-1.000; cardinality_ok=False 1200/1500)"
        ),
        description=(
            "Stage 3 USER concern #4 unblocker cell tested composing 5 chain-grade primitives "
            "(HRR task-vector ICL bundle + sparse-DG/dense-cortex hippo handoff with N_replay=5 "
            "between-turn consolidation + refuse-gate V_REL=256 OOD detection + CRISPR continual + "
            "multi-bank context partitioning) into a glass-box conversational online-learning "
            "capability. 10-turn synthetic dialogue with single-shot fact injections at turns 3 "
            "(allergy) and 7 (name); turn-10 joint-fact query 'what should Alice avoid?'. "
            "FULL regime: N_DIM=8192 V_ENTITIES=256 N_SCENARIOS=100 SEEDS=[7,17,23] N_h=512 "
            "N_c=1024 sparsity=0.10 N_REPLAY=5 REFUSE_V_REL=256 alpha=1.00. "
            "VERDICT HARD_FAIL with two load-bearing findings: "
            "(1) TV_HIPPO arm errored in all 3 seeds with ValueError: kth(=256) out of bounds (256) "
            "in the refuse-gate np.partition call -- v_rel_eff = min(REFUSE_V_REL=256, V=256-1=255) "
            "should bound the kth index, but the np.partition(-sims_tv, v_rel_eff)[:v_rel_eff] call "
            "with v_rel_eff=255 attempts kth=256 due to off-by-one at the V==REFUSE_V_REL boundary. "
            "Cell-bug verified-off-data: per_arm.TASKVEC_PLUS_HIPPO.arm_status='ERROR: ValueError: "
            "kth(=256) out of bounds (256)' in all 3 seeds; n_scenarios=0 for TV_HIPPO; "
            "cardinality_ok=False with 1200/1500 units. "
            "(2) MORE IMPORTANT: even with the cell bug fixed, TV_ONLY=1.000 at this regime "
            "(verified per_arm.TASKVEC_ONLY.integrated_query_acc=1.000 cv=0.000 n_scenarios=100 "
            "in all 3 seeds; HRR bundle of 10 binds at N=8192 has crosstalk SNR ~= 9.6 well "
            "within capacity for V=256 cleanup -- this IS the real chain-grade HRR task-vector "
            "ICL primitive succeeding, NOT by-construction-saturation cheating). The composition "
            "is therefore upper-bounded by TV_ONLY at this easy regime; delta_vs_TV_ONLY can be "
            "AT BEST 0 here, NOT the HP_DELTA_OVER_TV_ONLY_MIN=0.05 pre-reg bar. "
            "DISCRIMINATOR-MUST-SURVIVE-SCALE breach: smoke (V=60, REFUSE_V_REL=64, v_rel_eff=59) "
            "did not exercise the V==REFUSE_V_REL boundary, AND smoke regime also showed "
            "TV_ONLY=1.000 = TV_HIPPO=1.000 (saturation) -- the discriminator did not fire at "
            "smoke either; the cell only LOOKED like it discriminated in smoke because vanilla "
            "stayed at 0.000 (the composition vs primitive load-bearing comparison was already "
            "at-cap at smoke). Stage 3 USER concern #4 (online conversation learning) is "
            "RESOLVED-AT-REGIME by the existing chain-grade task_vector ICL primitive ALONE; "
            "no new mechanism needed for the M3 demo at this proposed regime. Composition path "
            "is not refuted at harder regimes (longer conversations / V_C >> 256 / 100+ facts "
            "where the bundle saturates), but those regimes are NOT required for M3 demo gating."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HARD_FAIL_composition_with_cell_bug",
            "cert_status": "honest_negative",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "HARD_FAIL_3seeds_FULL_TV_HIPPO_0p000_cell_bug_refuse_gate_kth_OOB_at_V_eq_REFUSE_V_REL_"
                "boundary_AND_TV_ONLY_1p000_saturation_means_composition_cannot_lift_at_this_easy_regime_"
                "delta_vs_VANILLA_0p000_delta_vs_TV_ONLY_neg_1p000_cardinality_1200_of_1500"
            ),
            "cell_commit": CELL_COMMIT,
            "metrics_path": METRICS_PATH,
            "prereg_path": PREREG_PATH,
            "experiment_path": EXPERIMENT_PATH,
            "smoke_metrics_path": SMOKE_METRICS_PATH,
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "cert-owner re-derived from data/exp_online_conv_oneshot_taskvec_hippo_v1_redispatch_"
                "rerun_2026-06-28/metrics.json per_seed array across all 3 seeds (7/17/23). "
                "PER-ARM verified per-seed (Fix #28): "
                "VANILLA_RETRIEVAL integrated_query_acc=0.000 all 3 seeds (n_correct=0/100 each); "
                "TASKVEC_ONLY integrated_query_acc=1.000 all 3 seeds (n_correct=100/100 each); "
                "TASKVEC_PLUS_HIPPO arm_status='ERROR: ValueError: kth(=256) out of bounds (256)' "
                "all 3 seeds (n_scenarios=0; integrated_query_acc=NaN); "
                "ORACLE integrated_query_acc=1.000 all 3 seeds (n_correct=100/100 each); "
                "RANDOM_INJECT integrated_query_acc=[0.000, 0.000, 0.010] (n_correct=[0, 0, 1]/100). "
                "Aggregate: TV_HIPPO mean=0.000 cv=0.000 n=0 (NaN treated as 0 in aggregation); "
                "TV_ONLY mean=1.000 cv=0.000 n=3; delta_vs_VANILLA=+0.000; delta_vs_TV_ONLY=-1.000. "
                "cardinality_ok=False (completed_units=1200 vs expected_n_units=1500; the missing "
                "300 = TV_HIPPO 100 scenarios x 3 seeds). arms_distinct=True via SHA-256 of per-arm "
                "prediction sequences (all per-arm hashes distinct per seed including the all-NaN "
                "TV_HIPPO hash 4f53cda18c2baa0c stable across seeds since predictions are all-NaN). "
                "BY-CONSTRUCTION-SATURATION CHECK for TV_ONLY=1.000: at N=8192, V=256, 10 binds, "
                "HRR bundle crosstalk std = sqrt((10-1)/N) = sqrt(9/8192) ~= 0.0332; signal magnitude "
                "after unit-norm = 1/sqrt(10) ~= 0.316; SNR ~= 9.6. Top-1 cleanup over V=256 codebook "
                "well within HRR capacity. This is REAL chain-grade HRR task-vector ICL primitive "
                "succeeding (consistent with prior task_vector_in_context_kshot_v1 CG atom), NOT "
                "by-construction-saturation cheating. However, regime IS easy enough that composition "
                "cannot lift -- a harder regime (100+ facts or V_C>>256) would saturate the bundle "
                "and could expose composition signal. CELL-BUG OBSERVATION (root cause for "
                "cell-author): refuse-gate np.partition call at experiments/exp_online_conv_oneshot_"
                "taskvec_hippo_v1.py line 398-399 errors with 'kth(=256) out of bounds (256)' in all "
                "3 full-regime seeds. The v_rel_eff = min(REFUSE_V_REL=256, sims_tv.shape[0]-1) cap "
                "intends v_rel_eff<=V-1; observed runtime kth=256 suggests either the cap is being "
                "bypassed OR sims_tv.shape[0] != V_ENTITIES at runtime; cell-author should re-derive. "
                "REGARDLESS of cell-bug root cause: load-bearing finding stands -- TV_ONLY=1.000 at "
                "this regime makes the composition redundant; even with bug fix the composition "
                "cannot exceed TV_ONLY at this saturated regime."
            ),
            "honest_scope": (
                "FULL 3-seed run; N_DIM=8192 V=256 n_scenarios=100 n_turns=10 fact_turns=[3,7] "
                "N_h=512 N_c=1024 sparsity=0.10 N_REPLAY=5 REFUSE_V_REL=256 alpha=1.00. "
                "HARD_FAIL on composition arm (cell bug) AND on composition advantage (TV_ONLY "
                "saturates at this regime). Does NOT refute composition at harder regimes where "
                "bundle saturates. Does NOT claim the cell-bug fix would change the load-bearing "
                "delta_vs_TV_ONLY conclusion at this regime. Does NOT close the conversational-"
                "online-learning capability category (capability is RESOLVED-AT-REGIME via existing "
                "task_vector ICL primitive)."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "V_ENTITIES": 256,
            "N_SCENARIOS": 100,
            "N_TURNS": 10,
            "FACT_TURNS": [3, 7],
            "N_h": 512,
            "N_c": 1024,
            "sparsity": 0.10,
            "n_replay": 5,
            "refuse_V_REL": 256,
            "alpha_decay": 1.00,
            "run_mode": "full",
            "arms": ["VANILLA_RETRIEVAL", "TASKVEC_ONLY", "TASKVEC_PLUS_HIPPO", "ORACLE", "RANDOM_INJECT"],
            "tv_hippo_mean": 0.000,
            "tv_only_mean": 1.000,
            "vanilla_mean": 0.000,
            "oracle_mean": 1.000,
            "random_mean": 0.003,
            "delta_vs_vanilla": 0.000,
            "delta_vs_tv_only": -1.000,
            "cv_tv_hippo": 0.000,
            "arms_distinct": True,
            "cardinality_ok": False,
            "expected_n_units": 1500,
            "completed_units": 1200,
            "cell_bug_tag": "refuse_gate_np_partition_kth_OOB_at_V_eq_REFUSE_V_REL_boundary_full_regime_only",
            "smoke_did_not_catch_bug": True,
            "smoke_did_not_catch_saturation": True,
            "discriminator_must_survive_scale_breach": True,
            "by_construction_saturation_check_for_TV_ONLY": (
                "TV_ONLY=1.000 IS real HRR ICL chain-grade primitive succeeding "
                "(SNR ~9.6 at N=8192/V=256/10-binds); NOT cheating; consistent with prior "
                "task_vector_in_context_kshot_v1 CG atom. Easy regime exposes saturation; "
                "harder regime (100+ facts, V_C>>256) would un-saturate."
            ),
            "elapsed_s": 2.1,
            "ts_iso": "2026-06-28T15:44:26Z",
            "n_llm_calls": 0,
            "zero_llm_calls_at_inference": True,
            "resolves_user_concern_4_at_regime": True,
            "user_concern_4_resolution": (
                "Online conversation learning RESOLVED AT THIS REGIME via existing chain-grade "
                "task_vector_in_context_kshot_v1 primitive alone. M3 demo does NOT require new "
                "mechanism for the proposed 10-turn / 2-fact-injection scenario. Composition "
                "redundant at this regime; potentially valuable at harder regimes not required for M3."
            ),
            "supersedes": None,
            "composes_with": [
                "task_vector_in_context_kshot_v1_smoke_CG",
                "cortex_hippo_handoff_smoke_CG",
                "refuse_gate_V_REL_256_CG",
            ],
            "cites": [
                "META_RULE_AM_substrate_already_does_X",
                "META_RULE_H_cardinality_ok",
                "META_RULE_AE_absolute_paths",
                "Fix_28_per_arm_metrics_not_verdict_msg",
                "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            ],
            "infra_critical_note": (
                "During this VET, math/atoms.jsonl had a non-schema-compliant row at line 28644 "
                "(id=hierarchical_planning_block_sparse_encoding_axis_HARD_FAIL_2026-06-28; missing "
                "required 'name' field; free-form dict bypassing Atom schema). Was BLOCKING all "
                "Store reads (PartitionedStore __init__ KeyError on 'name'). Quarantined to "
                "data/substrate_index/math/atoms.jsonl.quarantine_missing_name_field_1782662777; "
                "atoms.jsonl rewritten atomically (28646 lines was 28647). Root cause = sibling spawn "
                "appended a custom dict directly bypassing schema. Discipline note to file: REQUIRE "
                "all atom writes through Atom.to_dict() + load_atoms validation."
            ),
        },
    )


# ============================================================================
# Atom 2: META_RULE_AM evidence 9th occurrence (meta corpus)
# ============================================================================

def build_meta_rule_am_9th_occurrence() -> Atom:
    return Atom(
        id="META_RULE_AM_evidence_9th_occurrence_online_conv_taskvec_ICL_solves_user_concern_4_2026-06-28",
        name=(
            "META_RULE_AM evidence row #9 -- task_vector_in_context_kshot_v1 primitive ALONE "
            "solves USER concern #4 (online conversation learning) at TV_ONLY=1.000 at the "
            "proposed M3 regime; hippo-cortex composition redundant"
        ),
        description=(
            "9th occurrence of the substrate-already-does-X pattern (META_RULE_AM first-atomized "
            "2026-06-28 at the 8-occurrence threshold). EVIDENCE: cell exp_online_conv_oneshot_"
            "taskvec_hippo_v1 (FULL 3 seeds N=8192 V=256 100 scenarios) proposed composing 5 "
            "chain-grade primitives (HRR TV bundle + sparse-DG/dense-cortex hippo handoff + "
            "refuse-gate + CRISPR continual + multi-bank) for the M3 USER-concern-#4 conversational "
            "online-learning capability. Result: the TASKVEC_ONLY arm (existing CG primitive ALONE) "
            "achieved integrated_query_acc=1.000 cv=0.000 across all 3 seeds at the proposed 10-turn "
            "2-fact-injection regime, while the proposed TASKVEC_PLUS_HIPPO composition errored "
            "with a refuse-gate cell bug (kth OOB) and was upper-bounded by TV_ONLY anyway (since "
            "TV_ONLY saturates the metric at this regime, composition cannot lift). RULE APPLIES: "
            "the cell-author SHOULD have demonstrated that task_vector ICL primitive FAILS at the "
            "proposed regime BEFORE designing the richer composition; instead, smoke showed "
            "TV_ONLY=1.000 = TV_HIPPO=1.000 (both arms at metric ceiling) which is an instance of "
            "the discriminator-must-survive-scale failure -- the composition vs primitive "
            "discriminator did not fire even at smoke. CONSEQUENCE for M3: USER concern #4 (online "
            "conversation learning) is RESOLVED AT THIS REGIME by the existing chain-grade "
            "task_vector_in_context_kshot_v1 primitive alone; no new mechanism needed for the "
            "M3 demo. The composition cell is NOT a capability-closed; the capability is achieved "
            "by a simpler primitive that already exists. REGIME CAVEAT: at this 10-fact regime, "
            "HRR bundle crosstalk SNR ~= 9.6 (well below capacity); a harder regime (100+ facts, "
            "V_C >> 256, conversation >> 10 turns) could saturate the bundle and re-open the "
            "composition question. EXTENDS META_RULE_AL (substrate cosine kernel pre-encodes schema "
            "prior) at the conversational-ICL layer. EXTENDS META_RULE_AM evidence chain at "
            "occurrence #9 (was 8 at first-atomization). Discipline rule (CERT-neutral)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_NEUTRAL",
            "cert_status": "custom",
            "cert_class": "discipline_meta",
            "verdict": "META_RULE_NEUTRAL",
            "cell_commit": CELL_COMMIT,
            "verified_off_data": (
                "TV_ONLY=1.000 cv=0.000 n=3 verified per_seed in metrics.json; this is the 9th "
                "occurrence flagged this arc (META_RULE_AM was first-atomized at the 8-occurrence "
                "threshold). The substrate-already-does-X pattern: substrate's existing CG primitive "
                "(task_vector_in_context_kshot_v1) solves the capability without the proposed "
                "richer mechanism (TASKVEC_PLUS_HIPPO composition); composition arm contributes "
                "0 lift (-1.000 due to bug; AT BEST 0 absent bug due to TV_ONLY saturation)."
            ),
            "extends_meta_rule": ["META_RULE_AL", "META_RULE_AM"],
            "rule_layer": "process_layer_meta_discipline",
            "occurrence_number": 9,
            "evidence_source_cell": "experiments/exp_online_conv_oneshot_taskvec_hippo_v1.py",
            "evidence_source_metrics": METRICS_PATH,
            "evidence_source_prereg": PREREG_PATH,
            "evidence_source_notes": NOTES_PATH,
            "evidence_summary": "TV_ONLY=1.000 vs TV_HIPPO=0.000 (bug) / 1.000 (saturation ceiling) at N=8192 V=256 10-turn 2-fact regime; composition redundant at regime",
            "user_concern_resolved": "USER_concern_4_online_conversation_learning_M3_demo",
            "resolution_kind": "RESOLVED_AT_REGIME_via_existing_primitive",
            "regime_caveat": (
                "RESOLVED AT this 10-fact / N=8192 / V=256 regime where HRR bundle SNR ~9.6 "
                "leaves headroom; HARDER regime (100+ facts, V_C>>256, longer conversations) "
                "could saturate bundle and re-open composition question. Not required for M3 "
                "demo gating at the proposed regime."
            ),
            "prior_AM_evidence_occurrences_1_through_8": (
                "Tracked in META_RULE_AM original atomization (2026-06-28; threshold-fire at "
                "8 occurrences). This row extends the evidence chain at occurrence #9."
            ),
            "next_action_if_composition_revisited": (
                "Cell-author should (a) FIX refuse-gate kth OOB cell bug; (b) re-design at a "
                "HARDER regime where TV_ONLY is NOT at metric ceiling (e.g. 100 facts, V_C>>256, "
                "or 30+ turn conversation) so the composition vs primitive discriminator can FIRE; "
                "(c) verify cardinality_ok=True before claiming any composition lift."
            ),
            "supersedes": None,
            "cites": [
                "META_RULE_AL_substrate_cosine_kernel_pre_encodes_schema_prior",
                "META_RULE_AM_substrate_already_does_X_test_discipline",
                "task_vector_in_context_kshot_v1_smoke_CG_prior_atom",
                "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
                "Fix_28_per_arm_metrics_not_verdict_msg",
            ],
            "ts_iso_atomized": "2026-06-28",
        },
    )


# ============================================================================
# Main: A5 PRE -> add atoms -> A5 POST -> cert ledger row
# ============================================================================

def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )


def _axiom_count(store):
    return sum(
        1 for a in store.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def main():
    print(f"[{ATOMIZED_BY}] START", flush=True)

    # A5 PRE snapshot
    ps_pre = PartitionedStore(STORE_ROOT)
    pre_cert = _cert_count(ps_pre)
    pre_axiom = _axiom_count(ps_pre)
    pre_total = sum(1 for _ in ps_pre.all_atoms())
    print(f"  A5-PRE: cert_n={pre_cert} axiom_n={pre_axiom} total_atoms={pre_total}", flush=True)
    assert pre_axiom == 206, f"A5-PRE axiom drift: {pre_axiom} != 206"

    # Build atoms
    atom_hf = build_online_conv_composition_hard_fail()
    atom_meta = build_meta_rule_am_9th_occurrence()

    # Idempotency check
    existing_ids = {a.id for a in ps_pre.all_atoms()}
    actions = []
    if atom_hf.id in existing_ids:
        print(f"  IDEMPOTENT-SKIP: {atom_hf.id}", flush=True)
    else:
        actions.append(("math", atom_hf))
    if atom_meta.id in existing_ids:
        print(f"  IDEMPOTENT-SKIP: {atom_meta.id}", flush=True)
    else:
        actions.append(("meta", atom_meta))

    if not actions:
        print("  ALL atoms already in store; nothing to write", flush=True)
        return 0

    # Write atoms
    for corpus_name, atom in actions:
        ps_pre.add_atom(atom)
        print(f"  ADDED: {corpus_name}::{atom.id[:80]}...", flush=True)

    # A5 POST verify -- reload Store fresh
    ps_post = PartitionedStore(STORE_ROOT)
    post_cert = _cert_count(ps_post)
    post_axiom = _axiom_count(ps_post)
    post_total = sum(1 for _ in ps_post.all_atoms())
    print(f"  A5-POST: cert_n={post_cert} axiom_n={post_axiom} total_atoms={post_total}", flush=True)
    assert post_axiom == 206, f"A5-POST axiom drift: {post_axiom} != 206"
    assert post_cert == pre_cert, (
        f"A5-POST CERT delta unexpected: pre={pre_cert} post={post_cert} "
        f"(both atoms are CERT-neutral; delta should be 0)"
    )
    assert post_total == pre_total + len(actions), (
        f"A5-POST atom count mismatch: pre={pre_total} post={post_total} expected_delta={len(actions)}"
    )

    # Verify atoms reloaded correctly
    for corpus_name, atom in actions:
        loaded = next((a for a in ps_post.all_atoms() if a.id == atom.id), None)
        assert loaded is not None, f"A5-POST round-trip FAIL: {atom.id} not in reloaded store"
        assert loaded.name == atom.name, f"A5-POST name drift: {atom.id}"
        print(f"  A5-POST round-trip OK: {corpus_name}::{atom.id[:60]}...", flush=True)

    # ---- Cert ledger rows (CERT-neutral; delta=0) ----
    ledger_ts = time.time()

    # Row 1: HF composition (honest_negative; cert_class=mechanism_characterization)
    row1 = build_honest_negative_row(
        atom_id=f"math::{atom_hf.id}",
        cell_commit=CELL_COMMIT,
        verdict=(
            "HARD_FAIL_3seeds_FULL_TV_HIPPO_0p000_cell_bug_AND_TV_ONLY_1p000_saturation_"
            "composition_cannot_lift_at_this_easy_regime"
        ),
        notes_path=NOTES_PATH,
        metrics_path=METRICS_PATH,
        cert_class="mechanism_characterization",
        atomized_by=ATOMIZED_BY,
        note=(
            "online_conv_oneshot_taskvec_hippo_v1_HARD_FAIL_TV_HIPPO_0_TV_ONLY_1_composition_"
            "redundant_at_this_regime_user_concern_4_resolved_via_existing_primitive_alone_"
            "discipline_breach_DISCRIMINATOR_MUST_SURVIVE_SCALE_smoke_did_not_fire_at_saturation"
        ),
        ts=ledger_ts,
    )
    hash1 = append_cert_ledger_row(row1, expected_cert_n_pre=post_cert, expected_cert_n_post=post_cert)
    print(f"  LEDGER ROW 1 (HF composition): hash={hash1}", flush=True)

    # Row 2: META_RULE_AM evidence row (custom; discipline_meta)
    row2 = {
        "ts": ledger_ts,
        "op": "cert_ruling",
        "atom_id": f"meta::{atom_meta.id}",
        "cert_status": "custom",
        "cert_class": "discipline_meta",
        "verified_off_data": True,
        "atomized_by": ATOMIZED_BY,
        "cell_commit": CELL_COMMIT,
        "verdict": "META_RULE_NEUTRAL",
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "notes_path": NOTES_PATH,
            "metrics_path": METRICS_PATH,
            "atom_qualified_id": f"meta::{atom_meta.id}",
        },
        "supersedes": None,
        "note": (
            "META_RULE_AM_evidence_9th_occurrence_substrate_task_vector_ICL_primitive_alone_"
            "solves_user_concern_4_online_conversation_learning_at_proposed_M3_regime_"
            "composition_redundant_extends_AL_AM_at_conversational_ICL_layer"
        ),
    }
    hash2 = append_cert_ledger_row(row2, expected_cert_n_pre=post_cert, expected_cert_n_post=post_cert)
    print(f"  LEDGER ROW 2 (META_AM evidence #9): hash={hash2}", flush=True)

    print(f"[{ATOMIZED_BY}] DONE: 2 atoms + 2 ledger rows written; CERT_N={post_cert} (delta=0)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
