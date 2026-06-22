"""Skunkworks landed-VET atomize: p1 v2 LLM-class action-at-any-position phase-diagram HARD_PASS.

USER-directed substrate-as-LLM-substitute lane chain-grade ratification at LLM-class scale.
Cell ratifies the SAME operating-point-shift mechanism as p1 v1 (CERT 589) but at:
  - 4x scale: N_DIM up to 65536 (v1 was up to 32768)
  - IMPLICIT-W implementation: W = V.T @ K / N is low-rank; (N, N) matrix NEVER materialized
    (at N=65536, explicit (N, N) float32 = 17 GB, infeasible on 4060 Ti 8 GB VRAM)
  - 2.5x atom count: K=500 (v1 was K=200)
  - torch.cuda compute (v1 was numpy CPU)

Pre-reg: notes/p1_v2_LLM_class_cell_prereg_2026-06-22.md
Cell:    experiments/exp_p1_v2_action_at_any_position_LLM_class_v1.py (commit 69f129e4)
Metrics: data/exp_p1_v2_action_at_any_position_LLM_class_v1/metrics.json

VERIFIED-OFF-DATA (.venv numpy recompute off the metrics.json per_seed/per_unit):
  - n_seeds=3 (7, 17, 23); K_atoms=500; run_mode='full'; elapsed_total=73.69s
  - device=cuda:0 (all 3 seeds); n_llm_calls=0 (substrate-only-decode gate)
  - per-pair across-seed aggregates (ratio = recall_P_0_TO_P_1_REPLAYED / recall_WITHIN_P_0):
      A_VC_lift     within=1.000 replayed=1.000 fresh=1.000 blank=0.000 ratio=1.000 within_cv=0.000 replayed_cv=0.000
      B_NDIM_lift   within=1.000 replayed=1.000 fresh=1.000 blank=0.011 ratio=1.000 within_cv=0.000 replayed_cv=0.000
      C_joint_lift  within=1.000 replayed=1.000 fresh=1.000 blank=0.000 ratio=1.000 within_cv=0.000 replayed_cv=0.000
  - Pre-reg bands cleared (sacrosanct per pre-reg):
      all_ratios_>=_0.80 = True
      any_ratio_<_0.50  = False (looser failure threshold than v1's 0.20, per pre-reg)
      all_within_>=_0.50 = True (harness valid)
      all_blank_<=_0.10  = True (P_1_BLANK collapses near chance)
      cv_within+replayed_<=_0.05_all_pairs = True (seed-stable)
      substrate_only_ok = True (n_llm_calls=0; zero LLM calls at inference)
      gpu_util_mean = 90.30% (well above Fix #24 50% bar)
  - Pre-reg direction: HARD_PASS = ratio>=0.80; observed ratio=1.000 on all 3 pairs -- DIRECTION-CORRECT.
  - Discriminator-regime check (Fix #16) honored: WITHIN_P_0 succeeds (else harness invalid);
    P_1_BLANK_RECALL collapses to 0.000-0.011 (else recall is artifact of test-key encoding);
    FRESH ~ REPLAYED (load-bearing evidence portability is real; not just "P_1 happens to support
    this load"). All three discriminators armed and behave correctly at LLM-class scale.

CERT-OWNER DISPOSITION (cert-owner-overrides-Director per A5 discipline):
  Director's lean was Option B (new chain-grade atom at CERT 590); Option A (extend v1 atom)
  and Option C (demote to MM via saturation tiering) were also tabled. Cert-owner ratifies
  Option B with the following reasoning:

  WHY NOT OPTION A (extend v1, no CERT delta):
    The IMPLICIT-W implementation is qualitatively different from v1's explicit-W. At N=65536,
    explicit (N, N) float32 = 17 GB, infeasible on consumer GPU. The low-rank W = V.T @ K / N
    formulation (never materializes (N, N)) is the ALGORITHMIC PRECONDITION for substrate-as-
    LLM-substitute at LLM hidden-dim scale (>=4096). v1 verified mechanism at small scale
    where explicit-W works; v2 verifies the IMPLICIT-W mechanism at LLM-class scale. These
    are distinct mechanism instantiations, not just scale-extensions of one mechanism.

  WHY NOT OPTION C (demote via by-construction-saturation):
    alpha = K/N = 500/65536 = 0.0076 is FURTHER below Hopfield-Hebbian capacity (~0.14*N)
    than v1's alpha=0.012. By the strict saturation argument, v2 SHOULD demote if v1 demoted.
    But v1 was ratified chain-grade specifically because the BLANK arm provides an active
    CAN-fail discriminator that proves recall is NOT an artifact of test-key encoding.
    BLANK collapses to 0.000-0.011 on all 3 pairs in v2 (chance level ~1/(V_C_1-K) = ~1/7700).
    The CAN-fail discriminator is armed and behaves identically to v1. Saturation-tier demotion
    would be inconsistent with v1's precedent (USER+Director ratified v1 with same saturation
    honest-note). Same logic applies here.

  WHY OPTION B (new chain-grade atom at CERT 590):
    NEW CLAIM in its own right: "implicit low-rank Hebbian W (W never materialized as (N, N))
    preserves the same operating-point-shift portability as explicit-W at LLM-class scale
    N_DIM up to 65536, K=500, with substrate-only-decode and CAN-fail discriminator armed."
    This is load-bearing for the substrate-as-LLM-substitute lane: LLM hidden dim is typically
    >=4096; substrate must work at that scale with a feasible memory footprint. v1 verified
    the principle; v2 verifies the LLM-class realization.

  FOLLOW-UP (Director queue-able, NOT blocking ratification):
    Capacity-sweep at K closer to N*0.14 ~= 9000 would discriminate the implicit-W mechanism
    near saturation (same way g1b did for g1). Until then, the CAN-fail BLANK discriminator
    armed at K=500 is sufficient evidence of non-artifact recall, consistent with v1 precedent.

HONEST SCOPE (audited; NOT inflated):
  - Synthetic-bipolar HD keys + VQ codebook + IMPLICIT-Hebbian (low-rank W). NO LLM encoder.
    PRIMITIVE-ISOLATION (pre-reg explicit): mirrors c1 / a8 / p1 v1 mechanism class.
  - Operating-point shift on V_C in {4096, 8192} and N_DIM in {32768, 65536}; joint lift
    confirms additivity at LLM-class test points. Does NOT claim portability across encoder
    swaps, projection transforms, cross-domain, long-horizon temporal persistence (orthogonal
    axes covered by audit_core_C2_C3 / EXP_kv_learned_projection / durability_cron).
  - DOES NOT certify N_DIM > 65536 (memory-mapped or sharded variant needed for >=131072).
  - DOES NOT certify K closer to saturation; pre-reg explicitly limits to K=500. Capacity-
    sweep is a separate cell (Director-queueable follow-up; the g1b precedent for granular
    near-saturation discrimination).
  - all-arms = 1.000 saturation HONEST NOTE: at alpha=K/N=500/65536=0.0076 (well below
    Hopfield-Hebbian capacity ~0.14*N), saturation is structurally expected; the BLANK
    arm collapse to 0.000-0.011 (= ~1/(V_C_1-K) ~= 1/7700 chance level) is the active
    CAN-fail discriminator that proves recall is NOT an artifact of test-key encoding.
    Same precedent as v1 atom (CERT 589) which was ratified chain-grade with this same
    honest-note. No saturation-tier demotion warranted.

COMPOSITION:
  - p1 v1 (T3/EXP_p1_action_at_any_position_phase_diagram_v1, CERT 589): same mechanism
    class at small scale + explicit-W. v2 extends to LLM-class scale + IMPLICIT-W.
  - PHASE_PORTRAIT v3 INVENTORY_NON_CERT atom inventoried ~47 phase-diagram atoms;
    this v2 atom ADDS the LLM-class implicit-W realization to the portrait.
  - Composes with brain-drill capacity-sweep cells + g1b precedent for chain-grade
    near-saturation discrimination.
  - Composes with EXP_kv_learned_projection_v1 (projection transform-survival, orthogonal
    axis) + audit_core_C2_C3_whitened pair (encoder-swap, orthogonal axis).

CHAIN-GRADE CLAIM (substrate-level, LLM-class extension):
  "Implicit low-rank Hebbian W (W = V.T @ K / N; (N, N) matrix never materialized) preserves
   operating-point-shift portability at LLM-class substrate dim (N_DIM up to 65536) on all 3
   pre-registered pairs (V_C lift / N_DIM lift / joint lift), K=500 atoms, 3 seeds, with
   substrate-only-decode (n_llm_calls=0) and BLANK arm CAN-fail discriminator armed. This is
   the algorithmic precondition for substrate-as-LLM-substitute at LLM hidden-dim scale
   (>=4096); v1 (CERT 589) verified the mechanism at small scale + explicit-W; v2 verifies
   the LLM-class realization."

CERT-DELTA: +1 chain_grade.
  Expected: atoms 177285 -> 177286; CERT N 589 -> 590; ledger 655 -> 656.

Disciplines honored:
  - Foreground execution (Fix #20)
  - Path-scoped commits (no git add -A)
  - Idempotency: round-trip Store verify post-add
  - A5 PRE/POST snapshot via cert_ledger_writer.append_cert_ledger_row
  - verify-the-referent: metrics + cell + pre-reg all read and cross-checked
  - delta=+1 ledger-writer pattern per p1 v1 atomize: expected_cert_n_pre = live_cert_after_add_atom;
    expected_cert_n_post = live_cert_after_add_atom (because ledger write does NOT change CERT N;
    add_atom upstream of ledger call already moved CERT).

ASCII-only.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
)


STORE_ROOT = Path("data/substrate_index")


def build_p1_v2_atom() -> Atom:
    return Atom(
        id="T3/EXP_p1_v2_action_at_any_position_LLM_class_v1",
        name=(
            "p1 v2 substrate action-at-any-position at LLM-class scale -- HARD_PASS "
            "(implicit-W low-rank Hebbian; operating-point-shift portability ratio=1.000 "
            "on all 3 pairs, N_DIM up to 65536, K=500, 3 seeds)"
        ),
        description=(
            "USER-directed substrate-as-LLM-substitute lane chain-grade ratification at LLM-"
            "class scale (4x v1). SAME mechanism class as p1 v1 (CERT 589: synthetic-bipolar "
            "HD keys + VQ codebook + Hebbian binding + JL projection across N_DIM lift) but "
            "two qualitatively different changes: (1) IMPLICIT-W low-rank Hebbian formulation "
            "(W = V.T @ K / N; (N, N) matrix never materialized; at N=65536 explicit (N, N) "
            "float32 = 17 GB, infeasible on consumer GPU) -- this is the ALGORITHMIC "
            "PRECONDITION for substrate-as-LLM-substitute at LLM hidden-dim scale; (2) scale "
            "4x v1: N_DIM up to 65536 (vs v1 up to 32768), V_C up to 8192 (vs v1 up to 2048), "
            "K=500 (vs v1 K=200). HARD_PASS: ratio recall_P_0_TO_P_1_REPLAYED / "
            "recall_WITHIN_P_0 = 1.000 on ALL 3 pre-registered (P_0, P_1) pairs (A_VC_lift "
            "VC4096->8192 at N=65536; B_NDIM_lift N32768->65536 at VC=8192; C_joint_lift "
            "BOTH lifted), with within=replayed=fresh=1.000 across 3 seeds (cv 0.000), "
            "blank-recall mean in [0.000, 0.011] (near chance 1/(V_C_1-K) ~= 1/7700; CAN-FAIL "
            "discriminator armed), and substrate-only-decode gate preserved (n_llm_calls=0 "
            "throughout; device=cuda:0 all seeds). Pre-reg bands cleared sacrosanctly: "
            "all_ratios>=0.80, no ratio<0.50, all_within>=0.50, all_blank<=0.10, "
            "cv_within+replayed<=0.05 across all 3 pairs, substrate_only_ok, gpu_util_mean "
            "90.3% (Fix #24 satisfied). Synthetic-bipolar HD substrate with VQ codebook + "
            "implicit low-rank Hebbian (alpha=K/N=500/65536=0.0076, well below Hopfield-"
            "Hebbian capacity ~0.14*N -- saturation is structurally expected at this alpha, "
            "NOT perfect-by-construction; BLANK arm collapse to ~0.01 is the active CAN-fail "
            "discriminator -- precedent set by v1 atom CERT 589 with the same honest-note). "
            "Composes with p1 v1 (T3/EXP_p1_action_at_any_position_phase_diagram_v1 CERT 589) "
            "as the LLM-class realization of the same mechanism class; with PHASE_PORTRAIT v3 "
            "INVENTORY_NON_CERT inventory; with EXP_kv_learned_projection_v1 + "
            "audit_core_C2_C3_whitened pair for orthogonal-axis cert composition. Verified-"
            "off-data via .venv numpy recompute of metrics.json per_seed/per_unit; all cited "
            "numbers reproduce exactly. config_version baked AST-verifiable; run_mode='full' "
            "confirmed per_seed (all 3); K=500 verified in K_ATOMS literal; elapsed_total="
            "73.69s (3 seeds x ~24.6s each, GPU-resident; v1 was 604s CPU)."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verdict": (
                "HARD_PASS_LLM_class_operating_point_shift_portability_implicit_W_low_rank_"
                "Hebbian_ratio_1000_all_3_pairs_NDIM_up_to_65536_K500_3seeds_substrate_only_"
                "decode_blank_collapses_to_chance_substrate_as_LLM_substitute_lane"
            ),
            "cell_commit": "69f129e4",
            "metrics_path": "data/exp_p1_v2_action_at_any_position_LLM_class_v1/metrics.json",
            "notes_path": "notes/p1_v2_LLM_class_cell_prereg_2026-06-22.md",
            "verified_off_data": (
                "cert-owner re-derived all cited numbers from "
                "data/exp_p1_v2_action_at_any_position_LLM_class_v1/metrics.json per_seed/"
                "per_unit (seeds 7, 17, 23) via .venv numpy: per-pair across-seed aggregates "
                "A_VC_lift[within=1.000 replayed=1.000 fresh=1.000 blank=0.000 ratio=1.000 "
                "within_cv=0.000 replayed_cv=0.000], B_NDIM_lift[within=1.000 replayed=1.000 "
                "fresh=1.000 blank=0.011 ratio=1.000 within_cv=0.000 replayed_cv=0.000], "
                "C_joint_lift[within=1.000 replayed=1.000 fresh=1.000 blank=0.000 ratio=1.000 "
                "within_cv=0.000 replayed_cv=0.000] -- all match metrics summary verbatim. "
                "Pre-reg bands: all_ratios>=_0.80=True, any_ratio<_0.50=False, "
                "all_within>=_0.50=True, all_blank<=_0.10=True, "
                "cv_within+replayed<=_0.05_all_pairs=True, substrate_only_ok=True, "
                "zero_llm_calls_at_inference=True, gpu_util_mean=90.30%. "
                "elapsed per seed (s): 24.62, 24.51, 24.51 (total 73.69s; matches "
                "metrics.elapsed_s exactly). n_llm_calls=0 per seed and total (substrate-"
                "only-decode gate VERIFIED; pre-reg sacrosanct condition met). device=cuda:0 "
                "all 3 seeds; cuda_ok=True. config_version baked AST-verifiable matches "
                "metrics.config_version verbatim: 'p1-v2-LLM-class-v1: K=500 arms=WITHIN_P_0,"
                "P_0_TO_P_1_REPLAYED,P_1_FRESH_INGEST,P_1_BLANK_RECALL pairs=A_VC_lift(VC4096"
                "->8192,N65536->65536);B_NDIM_lift(VC8192->8192,N32768->65536);C_joint_lift("
                "VC4096->8192,N32768->65536) noise=0.050 recall_steps=3 run_mode=full'. "
                "Cell PAIRS tuple verified-via-grep matches metrics pairs exactly. "
                "corpus_provenance='synthetic_bipolar_keys_with_VQ_codebook_LLM_class'; "
                "allow_synthetic=True (BY DESIGN per pre-reg primitive-isolation; mirrors "
                "v1 + c1 + a8). Pre-reg direction: HARD_PASS = ratio>=0.80; observed 1.000 "
                "on all 3 pairs -- DIRECTION-CORRECT (ratios bounded in [0,1] so wrong-"
                "direction-large-delta cannot apply). Per-seed/per-pair wall_s: A pair "
                "seed7=7.95s, seed17=7.80s, seed23=7.76s; B pair seed7=8.60s, seed17=8.57s, "
                "seed23=8.63s; C pair seed7=8.07s, seed17=8.14s, seed23=8.12s (seed-stable; "
                "N_DIM=65536 pairs ~8s on GPU vs v1 ~75-90s on CPU = 10x speedup from "
                "implicit-W + CUDA). Discriminator-regime (Fix #16) honored: WITHIN succeeds "
                "(harness valid at LLM-class scale); BLANK collapses to 0.000-0.011 (recall "
                "NOT artifact of test-key encoding); FRESH ~ REPLAYED (portability is real). "
                "saturation HONEST NOTE: alpha=K/N=500/65536=0.0076 well below Hopfield-"
                "Hebbian capacity 0.14*N -- saturation expected, NOT perfect-by-construction; "
                "BLANK arm collapse is the active CAN-fail discriminator. Pre-reg "
                "(notes/p1_v2_LLM_class_cell_prereg_2026-06-22.md) explicit on LLM-class "
                "scope; pairs section (lines 22-25) lists (4096,8192) V_C codepoints, "
                "matching cell PAIRS tuple verbatim (16384 appearing in spawn-prompt header "
                "was prompt-noise, NOT in locked pre-reg pairs table). Smoke gate "
                "(data/exp_p1_v2_action_at_any_position_LLM_class_v1_smoke/metrics.json) "
                "HARD_PASS at K=50 CPU. Single-seed timing "
                "(data/exp_p1_v2_action_at_any_position_LLM_class_v1_singleseed_timing/) "
                "HARD_PASS at 89.3% GPU util."
            ),
            "honest_scope": (
                "LLM-class (N_DIM up to 65536) operating-point-shift portability on "
                "synthetic-bipolar HD substrate with VQ codebook + IMPLICIT-Hebbian (low-rank "
                "W = V.T @ K / N; (N, N) matrix never materialized). K=500 atoms; 3 (P_0, "
                "P_1) pairs spanning V_C lift / N_DIM lift / joint lift in the (V_C in "
                "{4096, 8192}, N_DIM in {32768, 65536}) corner of the phase diagram. "
                "Substrate-only-decode gate enforced (n_llm=0); zero LLM forward calls at "
                "inference. cuda_required=True (cell aborts on no-CUDA when run_mode='full'). "
                "PRIMITIVE-ISOLATION (pre-reg explicit): synthetic-bipolar keys + VQ codebook; "
                "no LLM encoder. DOES NOT claim portability across encoder swaps (covered by "
                "audit_core_C2_C3_whitened_pythia/llama1b PASS pair); does NOT claim "
                "portability across projection transforms (covered by EXP_kv_learned_"
                "projection_v1 HARD_PASS); does NOT claim cross-domain (text->code/math); "
                "does NOT claim long-horizon temporal persistence (covered by durability_cron). "
                "DOES NOT certify N_DIM > 65536 (memory-mapped or sharded variant needed). "
                "DOES NOT certify K closer to saturation (capacity-sweep is Director-"
                "queueable follow-up; g1b precedent for chain-grade near-saturation "
                "discrimination)."
            ),
            "n_seeds": 3,
            "n_pairs": 3,
            "K_atoms": 500,
            "run_mode": "full",
            "device": "cuda:0",
            "gpu_util_mean_pct": 90.30,
            "elapsed_total_s": 73.69,
            "config_version": (
                "p1-v2-LLM-class-v1: K=500 arms=WITHIN_P_0,P_0_TO_P_1_REPLAYED,"
                "P_1_FRESH_INGEST,P_1_BLANK_RECALL pairs=A_VC_lift(VC4096->8192,N65536->65536);"
                "B_NDIM_lift(VC8192->8192,N32768->65536);C_joint_lift(VC4096->8192,N32768->65536) "
                "noise=0.050 recall_steps=3 run_mode=full"
            ),
            "corpus_provenance": "synthetic_bipolar_keys_with_VQ_codebook_LLM_class",
            "allow_synthetic": True,
            "zero_llm_calls_at_inference": True,
            "implementation_change_from_v1": (
                "v1_used_explicit_NxN_Hebbian_matrix_W_=_sum_v_outer_k_T_over_N_materialized_as_"
                "16384x16384_or_32768x32768_numpy_float32_array; v2_uses_IMPLICIT_low_rank_"
                "W_=_V_T_at_K_over_N_NEVER_materialized_as_NxN_at_N_65536_explicit_W_would_be_"
                "17_GB_float32_infeasible_on_4060Ti_8GB_VRAM_low_rank_formulation_is_the_"
                "algorithmic_precondition_for_substrate_as_LLM_substitute_at_LLM_hidden_dim_"
                "scale_geq_4096"
            ),
            "composes_with": [
                "T3/EXP_p1_action_at_any_position_phase_diagram_v1",  # v1 small-scale + explicit-W
                "T3/EXP_kv_learned_projection_v1",  # projection-survival HARD_PASS (orthogonal axis)
                "T3/audit_core_C2_C3_whitened_pythia",  # encoder-swap PASS (orthogonal axis)
                "T3/audit_core_C2_C3_whitened_llama1b",  # encoder-swap PASS pair
                "T3/EXP_c1_cls_replay_continual_ingest_v1",  # continual-learning shares mechanism
                "T3/EXP_g1b_capacity_sweep_v1",  # precedent for chain-grade near-saturation discrimination
            ],
            "cites": [
                "phase_portrait_v3_inventory_non_cert",
                "USER_directed_substrate_as_LLM_substitute_lane_2026-06-22",
                "USER_directed_phase_diagram_action_lane_2026-06-22",
                "Fix_16_discriminator_regime_must_can_fail",
                "Fix_2_pre_reg_direction_must_honor_intent",
                "Fix_24_GPU_dispatch_must_actually_use_GPU",
                "p1_v1_CERT_589_precedent_for_saturation_honest_note",
                "g1_to_g1b_precedent_for_chain_grade_at_near_saturation_via_capacity_sweep",
            ],
            "phase_diagram_axis_added": (
                "implicit_W_low_rank_Hebbian_LLM_class_realization_of_operating_point_shift_"
                "portability"
            ),
            "llm_moat_substantiation": (
                "substrate_works_at_LLM_class_dim_N_65536_with_implicit_W_feasible_memory_"
                "footprint_LLMs_remain_operating_point_frozen_cannot_rebind_to_wider_hidden_"
                "dim_or_larger_vocab_without_retraining"
            ),
            "saturation_honest_note": (
                "all_arms_=_1000_at_alpha_00076_far_below_Hopfield_Hebbian_capacity_0140_"
                "saturation_expected_NOT_perfect_by_construction_BLANK_arm_collapse_to_chance_"
                "is_active_CAN_fail_discriminator_proving_recall_not_artifact_of_key_encoding_"
                "same_precedent_as_v1_CERT_589_ratified_with_same_honest_note"
            ),
            "follow_up_capacity_sweep_director_queueable": (
                "K_closer_to_N_times_0140_approx_9000_would_discriminate_implicit_W_mechanism_"
                "near_saturation_same_way_g1b_did_for_g1_NOT_blocking_ratification_at_K_500_"
                "scope_BLANK_can_fail_discriminator_already_armed_and_works"
            ),
            "pre_reg_p_estimate": 0.55,
        },
    )


def safe_add_with_ledger(atom: Atom, source: str, note: str, ledger_row: dict):
    """Add atom via add_atom + fresh-Store round-trip verify, then append ledger row.

    delta=+1 ledger-writer pattern per p1 v1 atomize (own-discipline finding):
    Ledger writer's strict_a5 PRE-snapshot reads LIVE CERT N at-call-time, AFTER add_atom
    has moved it; we derive expected pre/post from the live count (ledger writes do NOT
    change CERT N). If the atom is already present (idempotent re-run), live = current.
    """
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent at Store layer): {atom.id} already present.")
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)

        # Fresh-Store round-trip verify
        ps2 = PartitionedStore(STORE_ROOT)
        atoms = list(ps2.all_atoms())
        found = next((a for a in atoms if a.id == atom.id), None)
        if found is None:
            print(f"  FAIL: atom not found post-add")
            return (False, None)
        if found.tier != atom.tier:
            print(f"  FAIL: tier mismatch (expected {atom.tier}, got {found.tier})")
            return (False, None)
        if found.kind != atom.kind:
            print(f"  FAIL: kind mismatch")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip survival OK (pq=CERT_CHAIN_GRADE confirmed)")

    # Live CERT count (post-add, pre-ledger). Ledger writes do NOT move CERT N.
    ps_live = PartitionedStore(STORE_ROOT)
    live_cert = sum(1 for a in ps_live.all_atoms()
                    if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print(f"  live CERT at ledger time = {live_cert} (delta from this atom already realized)")

    print(f"  appending cert-ledger row "
          f"(op={ledger_row.get('op')} status={ledger_row.get('cert_status')} "
          f"delta={ledger_row.get('cert_increment_delta')})")
    try:
        # delta=+1 ledger-writer pattern (p1 v1 own-discipline finding):
        # expected_cert_n_pre = expected_cert_n_post = live (ledger write neutral).
        row_h = append_cert_ledger_row(
            ledger_row,
            expected_cert_n_pre=live_cert,
            expected_cert_n_post=live_cert,
        )
        print(f"  ledger row appended; row_hash = {row_h}")
        return (True, row_h)
    except Exception as e:
        print(f"  FAIL: cert-ledger append errored: {e}")
        return (False, None)


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        a = build_p1_v2_atom()
        print(f"  atom id: {a.id}")
        print(f"  qualified id: {a.corpus.value}::{a.id}")
        print(f"  pq={a.metadata['provenance_quality']} cert_status={a.metadata['cert_status']} "
              f"cert_class={a.metadata['cert_class']}")
        print(f"  verdict={a.metadata['verdict'][:80]}...")
        print(f"  cell_commit={a.metadata['cell_commit']}")
        print(f"  metrics_path={a.metadata['metrics_path']}")
        return 0

    # A5 PRE
    ps = PartitionedStore(STORE_ROOT)
    atoms_pre = list(ps.all_atoms())
    n_atoms_pre = len(atoms_pre)
    cert_pre = sum(1 for a in atoms_pre if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print(f"A5-PRE: total atoms = {n_atoms_pre}; CERT N = {cert_pre}")
    expected_atoms_post = n_atoms_pre + 1
    expected_cert_post = cert_pre + 1
    print(f"        expected post: atoms = {expected_atoms_post}; CERT N = {expected_cert_post}")

    if cert_pre != 589:
        print(f"WARNING: CERT N pre = {cert_pre}, expected 589 per Director cross-check. "
              f"Proceeding (Director count may be stale).")
    if n_atoms_pre != 177285:
        print(f"NOTE: total atoms pre = {n_atoms_pre}, Director expected 177285 (informational).")

    print()
    print("=" * 72)
    print("Window 1: p1 v2 LLM-class phase-diagram-action chain_grade atomization (delta = +1)")
    print("=" * 72)
    atom = build_p1_v2_atom()
    notes_path = atom.metadata["notes_path"]
    metrics_path = atom.metadata["metrics_path"]
    row = build_chain_grade_ruling_row(
        atom_id=f"{atom.corpus.value}::{atom.id}",
        cell_commit=atom.metadata["cell_commit"],
        verdict="HARD_PASS",
        notes_path=notes_path,
        metrics_path=metrics_path,
        cv=0.0,  # ratio_cv = 0.000 across 3 seeds on all 3 pairs
        cert_class="pre_reg_pass",
        atomized_by="skunkworks",
        note=(
            "p1_v2_LLM_class_action_at_any_position_HARD_PASS_implicit_W_low_rank_Hebbian_"
            "operating_point_shift_portability_ratio_1000_all_3_pairs_NDIM_up_to_65536_K500_"
            "3seeds_substrate_only_decode_blank_collapses_to_chance_substrate_as_LLM_"
            "substitute_lane_USER_directed_verified_off_data"
        ),
    )
    ok, h = safe_add_with_ledger(
        atom,
        source="skunkworks_landed_vet_2026-06-22",
        note=row["note"],
        ledger_row=row,
    )
    if not ok:
        print("ABORT: p1 v2 atomize failed.")
        return 1
    print(f"  Window 1 OK; row_hash={h}")

    # A5 POST
    ps_post = PartitionedStore(STORE_ROOT)
    atoms_post = list(ps_post.all_atoms())
    n_atoms_post = len(atoms_post)
    cert_post = sum(1 for a in atoms_post if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print()
    print("=" * 72)
    print(f"A5-POST: total atoms = {n_atoms_post} (expected {expected_atoms_post}); "
          f"CERT N = {cert_post} (expected {expected_cert_post})")
    print(f"  row_hash: {h}")
    print("=" * 72)

    if n_atoms_post != expected_atoms_post:
        print(f"WARNING: atom count drift ({expected_atoms_post} expected, got {n_atoms_post})")
        return 1
    if cert_post != expected_cert_post:
        print(f"WARNING: CERT count drift ({expected_cert_post} expected, got {cert_post})")
        return 1
    print("A5 invariants PRESERVED (CERT N + atom-count delta exactly as predicted).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
