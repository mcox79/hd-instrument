# Skunkworks tier-rule batch on 5 chain-grade-candidate landings + 1 MIDDLE_BAND
# 2026-06-26 (UTC)
# Auditor: skunkworks (cert-owner, A5 role-separation)
# Method: read metrics.json per-arm directly via .venv Python; do NOT trust verdict_msg framings.
# Disciplines applied: Fix #28 (per-arm verify), by-construction-saturation override, Q-discipline saturation,
#                      experiment-bias master checklist (R,S regime/contamination), verify-the-referent.

==============================================================================
ONE-LINE SUMMARY (TLDR)
==============================================================================

1. META v4 self-discovered     -> MEASURED_MECHANISM   (by-construction-saturation; cap-tag leaks)
2. Refuse-gate V_REL extension -> HARD_PASS chain-grade (envelope extension confirmed; clean)
3. KV M=100k partition routing -> MEASURED_MECHANISM   (Director self-tiered correctly; bound mapped)
4. WM multi-bank K=4096 adv    -> HARD_PASS chain-grade ONLY at K=4096 (K=1024, K=2048 are by-construction)
5. Multihop beam search v1     -> MEASURED_MECHANISM   (sanity-breach + META_M7 cross-cell regime mismatch)

CERT delta this batch: +2 (artifacts 2 and 4 chain-grade-only)
                       +0 for artifacts 1, 3, 5 (MM, atomized as proven bounds)

==============================================================================
ARTIFACT 1: META v4 self-discovered corpus
==============================================================================
Anchor: substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus
Director call: HARD_PASS_CHAIN_GRADE_CONFIRMED at ARM_TP_MERGE=1.000 cv=0.000 (3 seeds)
Skunkworks ruling: MEASURED_MECHANISM (substrate by-construction-saturation override)

Per-arm verified (cv=0.000 across all 3 seeds, all 3 categories):
  TP_MERGE     = 1.0000 cv=0.0000
  FP_MERGE     = 0.0000
  FN_MISS      = 0.0000
  BOUNDARY_F1  = 1.0000 cv=0.0000
  algorithms   = 1.0000
  learning     = 1.0000
  representation = 1.0000

Root cause analysis (Q-discipline saturation):
- Inspected classify_pair() in experiments/exp_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.py:
    def classify_pair(sigs, caps, allow_capability_fallback=True):
        present = [s for s in sigs if len(s) >= 3]
        if len(present) >= 2:
            first = present[0]
            if all(s == first for s in present[1:]):    # <-- dict equality on the FULL sig dict
                ...
                return "PROVABLY_EQUIVALENT"
            return "NOT_EQUIVALENT"

- Inspected corpus rows in data/meta_reasoning_corpus/substrate_self_discovered_v1.jsonl:
    * TP groups (substrate_dup_*): all members carry LITERALLY IDENTICAL `sigs` dict (same domain,
      operation_type, signature_input_type, signature_output_type, complexity_class).
      Example: substrate_dup_answer_consistency_weak_labels has two members both with
      operation_type=consistency_check_across_label_sources etc., differing ONLY in `tier`.
    * ADV groups (substrate_cap_*): members have DIVERGENT operation_type by construction
      (Q-learning vs Policy-gradient vs MDP all under SCHOOL/reinforcement_learning_family).

- Conclusion: The "substrate-self-discovery" claim is partially true (the BUILDER autoextracted these
  groups from atoms.jsonl), but the resulting corpus is structurally IDENTICAL in shape to v3:
  TPs have identical sigs; ADVs have divergent sigs. dict-equality on the full sig is by-construction
  perfect on TPs. This is the same Q-saturation pattern as Q-DISCIPLINE_FLAG in the verdict_msg
  (Director correctly flagged it; Skunkworks tiers).

- The 13 ADV cross-name groups DO discriminate cleanly (all NOT_EQUIVALENT) -- but ADV refusal at
  divergent typed-sigs is also by-construction trivially within reach of dict-equality. The genuinely
  discriminating test would be a corpus where SAME-named operators have DIFFERENT typed sigs (e.g.
  authored under different operational definitions) OR DIFFERENT-named operators have IDENTICAL sigs
  with no cap-tag overlap. Neither shape appears in substrate_self_discovered_v1.jsonl.

- Verdict on the "promotes v3 from MM-expected to chain-grade" framing:
  v3 NAMED corpus (data/exp_substrate_distill_verify_operator_equivalence_v3_NAMED_corpus_stratified/
  metrics.json) is ALSO 1.000/0.000 across all 4 arms and 4 categories, was NEVER previously certified
  by Skunkworks (no ledger entry for v3), so v4 cannot "promote" something that hasn't been ruled.
  Both v3 and v4 land MM together with the same root cause.

Tier: MEASURED_MECHANISM (proven bound: CHTV-1 dict-equality merges identical-sig groups perfectly
  and refuses divergent-sig groups perfectly; this is a capability characterization of the verifier
  primitive against a substrate-mined-but-still-typed-saturated corpus).

Atomization plan (math corpus):
  atom_id: math::T3/EXP_substrate_distill_verify_operator_equivalence_v4_self_discovered_measured_mechanism_dict_equality_saturated_on_substrate_mined_corpus
  cert_status: MEASURED_MECHANISM (skunkworks override of HARD_PASS director call)
  cert_class: experiment_substrate
  delta: 0
  cv: 0.000
  referent: metrics.json + classify_pair body + corpus structure
  note: "MM_director_called_chain_grade_skunkworks_override_dict_equality_byconstruction_saturated_on_typed_authored_TPs_adv_cap_divergent_optype_trivially_refused_genuine_test_needs_same_name_divergent_sig_OR_diff_name_identical_sig_NO_CERT_INCREMENT"

Q-DISCIPLINE atom (meta corpus) -- piggybacks on prior META_M7-style rule:
  atom_id: meta::T3/META_typed_sig_equality_byconstruction_saturated_when_corpus_authored_with_matched_sigs_TP_and_divergent_sigs_ADV_substrate_self_discovered_alone_does_not_break_this
  This is a CERT-NEUTRAL META rule.

==============================================================================
ARTIFACT 2: Refuse-gate V_REL extension v1
==============================================================================
Anchor: substrate_refuse_gate_v_rel_extension_v1
Director call: HARD_PASS chain-grade up to V_REL=256 (32x envelope extension over V_REL=8 baseline)
Skunkworks ruling: HARD_PASS chain-grade (CONFIRMED)

Per-arm refuse-rate (3 seeds, 100 queries per category per seed, cv = pstdev/mean across seeds):

  V_REL  arm_relation_check NEAR_DOMAIN_MIXED  arm_naive_alone NEAR  arm_naive_plus_intent NEAR
  ----   --------------------------------------  ---------------------  ----------------------------
  8      1.0000 cv=0.0000                        0.0000 cv=0.0000       0.9900 cv=0.0082
  16     1.0000 cv=0.0000                        0.0000 cv=0.0000       0.9633 cv=0.0259
  32     1.0000 cv=0.0000                        0.0000 cv=0.0000       0.8767 cv=0.0054
  64     1.0000 cv=0.0000                        0.0000 cv=0.0000       0.8333 cv=0.0150
  128    1.0000 cv=0.0000                        0.0000 cv=0.0000       0.6300 cv=0.0389
  256    1.0000 cv=0.0000                        0.0000 cv=0.0000       0.4367 cv=0.0601
  512    1.0000 cv=0.0000                        0.0000 cv=0.0000       0.1767 cv=0.1163

  All V_REL: PURE_IN_DOMAIN refuse=0.0 (answer everything; correct);
             PURE_OUT_OF_DOMAIN refuse=1.0 (reject everything; correct).

Discriminator analysis:
- ARM_RELATION_CHECK clean at 1.000 cv=0.000 throughout V_REL in {8, 16, 32, 64, 128, 256, 512}.
- ARM_NAIVE_ALONE absent on NEAR_DOMAIN_MIXED at all V_REL (the negative control).
- ARM_NAIVE_PLUS_INTENT degrades monotonically (0.99 -> 0.18) as V_REL grows -- this is a
  GENUINE DISCRIMINATOR. RELATION_CHECK's separation from naive_plus_intent grows with V_REL.

Q-discipline check:
- RELATION_CHECK arm IS at saturation (1.0000 cv=0.0000), but it's the DESIGN-INTENT arm, not a
  bug. The naive_plus_intent arm provides the headroom-to-fail discriminator (BIAS-S checklist:
  capacity-feasible regime is exercised; naive_plus_intent fails harder as V_REL grows).
- The bands HP_near>=0.85 cv<=0.05 are NOT binding on RELATION_CHECK alone; the cell certifies
  the gate-PRESENCE pattern (relation_check separates near-domain) AND the gate-ABSENCE pattern
  (naive_plus_intent loses near-domain refusal at V_REL>=128). Both arms together = clean
  honest_discriminator.

Bias-checklist sweep (per Q checklist):
- BIAS-13 contamination: encoder=substrate-native; no LLM forward call at inference (verified);
  no external embedding pretraining used here.
- BIAS-14 regime: NEAR_DOMAIN_MIXED is the discriminating regime (the v2 chain-grade rail);
  PURE_IN/OUT controls present and behave as expected.
- BIAS-15 mismatch: 3 seeds (11, 13, 19); 100 queries per category per seed = 300 per category per
  V_REL; sufficient statistics.
- BIAS-S band-calibration: cv<=0.05 on RELATION_CHECK trivially because saturated, BUT the
  naive_plus_intent arm has cv up to 0.12 at V_REL=512 (sample-size-driven; floor at 0.18 still
  shows clean dispersion below the gate threshold).

Tier: HARD_PASS_CHAIN_GRADE (32x envelope extension confirmed: V_REL=8 -> V_REL=256). Counts +1.
  At V_REL=512 naive_plus_intent collapse continues; the gate's discriminating power survives at
  the audit library size of 512 even though the test cell's stated chain-grade envelope is
  through V_REL=256.

Atomization plan (math corpus):
  atom_id: math::T3/EXP_substrate_refuse_gate_v_rel_extension_v1_chain_grade_envelope_V_REL_256_32x_lift_over_v2_baseline_V_REL_8
  cert_status: HARD_PASS
  cert_class: experiment_substrate
  delta: +1
  cv: 0.000 (relation_check) / 0.060 (naive_plus_intent at V_REL=256)
  referent: metrics.json (per_unit) + 21 partial_metrics files

hdlab/ primitive update:
  Update hdlab/refuse_gate (or equivalent) to mark V_REL_envelope = 256 as chain-grade-confirmed.
  Per USER results-to-application cadence: same-cycle code primitive update.

==============================================================================
ARTIFACT 3: KV learned projection M=100k with partition routing v1
==============================================================================
Anchor: substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1
Director call: MIDDLE_BAND (recall=0.58 at M=100k for ARM_C; doesn't beat ARM_A 0.66)
Skunkworks ruling: MEASURED_MECHANISM (Director correctly self-tiered as MB; promote framing to MM with proven bound)

Per-arm verified (3 seeds aggregated):
  M=10000:
    ARM_A (learned, no partition)   recall=0.8209 keysep=0.874
    ARM_B (dense+partition)         recall=0.0153 (route_acc=1.000)
    ARM_C (learned+partition)       recall=0.6356 keysep=0.874 (route_acc=1.000)
    ARM_D (dense, no partition)     recall=0.0157
    analytic ceiling                 0.0304
  M=30000:
    ARM_A 0.7751 / B 0.0150 / C 0.6097 / D 0.0091 / ceiling 0.0220
  M=100000:
    ARM_A 0.6643 / B 0.0148 / C 0.5797 / D 0.0053 / ceiling 0.0127

cv-check at M=100000 (across 3 seeds):
  ARM_A 0.6464, 0.6862, 0.6603 -> mean 0.6643 cv ~ 0.025
  ARM_C 0.5652, 0.6010, 0.5728 -> mean 0.5797 cv ~ 0.027
  Lift A-over-C: ~0.085 (no partition slightly beats partition; partition COSTS recall not adds)

Interpretation:
- ARM_C does NOT reach HP_recall>=0.70 AND HP_comp_lift>=0.10 over arm A at any M.
  Pre-reg gate is honestly missed.
- ARM_C does cleanly separate from ARM_B and ARM_D (>40x lift over dense+partition control),
  so the LEARNED PROJECTION IS THE MECHANISM doing the work; partition routing is a
  capacity-routing instrument not a recall-amplifier.
- keysep increases from 0.874 (M=10k) -> 0.932 (M=100k) -- approaching saturation. The
  HP_keysep<=0.95 pre-reg ceiling is approached but not breached.
- BIAS-S band-calibration: top-1 only; at M=100k with 25k held-out, top-5 would substantially
  exceed 0.70 (the typed-route-correct space contains most ties); but the pre-reg explicitly
  targeted top-1, so the band stands.

Tier: MEASURED_MECHANISM. The cell proves the LEARNED-PROJECTION mechanism is operational at
M=100k production scale (recall 30-50x above analytic ceiling) AND that partition routing is a
SUBSET ROUTING instrument that costs ~0.08 recall vs no-partition while providing 1.000
route_acc. The chain-grade gate (composition_lift) was not met; cell honestly reports MIDDLE_BAND.
This is a clean proven-bound: capacity-routing PARTITION is not free.

Atomization plan (math corpus):
  atom_id: math::T3/EXP_substrate_kv_learned_projection_at_scale_M_100k_partition_routing_v1_measured_mechanism_partition_costs_0p08_recall_vs_no_partition_route_acc_perfect_1p000
  cert_status: MEASURED_MECHANISM
  cert_class: experiment_substrate
  delta: 0
  cv: 0.027 (ARM_C at M=100k)
  referent: metrics.json
  note: "measured_mechanism_KV_learned_projection_chain_grade_eligible_partition_routing_costs_recall_route_acc_perfect_no_chain_grade_lift_pre_reg_gate_honestly_missed"

==============================================================================
ARTIFACT 4: WM multi-bank K-extension adversarial v1
==============================================================================
Anchor: substrate_working_memory_multi_bank_K_extension_adversarial_v1
Director call: HARD_PASS_CHAIN_GRADE_K_4096 (with Q-discipline flag at K=1024 and K=2048)
Skunkworks ruling: HARD_PASS chain-grade AT K=4096 ONLY (Q-discipline saturation at K<=2048 is by-construction; K=4096 is the genuine evidence)

Per-arm verified at K=4096 (the genuine arm; mean across 3 seeds 11/13/19):
  RANDOM regime:
    NAIVE      recall = 0.0020 (chance)
    MULTI_32x  recall = 0.7450  (CV across seeds ~0.008)
    MULTI_64x  recall = 0.9927 cv = 0.0006 (the chain-grade arm)
  ADVERSARIAL regime:
    NAIVE      recall = 0.0025
    MULTI_32x  recall = 0.6674
    MULTI_64x  recall = 0.9801 cv = 0.0015

Discriminator separation at K=4096:
  MULTI_64x.adv - MULTI_64x.rand = -0.0126 (within HP_adv_within=0.05)
  MULTI_64x.rand - NAIVE.rand = +0.9907 (~500x lift)
  MULTI_32x.adv - MULTI_32x.rand = -0.078 (the 32x arm DOES break under adversarial; visible disc)

K=1024 and K=2048 Q-saturation (Director-flagged, Skunkworks confirms):
  K=1024 MULTI_32x rec=1.0000 cv=0.0000 (random AND adversarial) -- by-construction-saturated
  K=1024 MULTI_64x rec=1.0000 cv=0.0000 (random AND adversarial) -- by-construction-saturated
  K=2048 MULTI_64x rec=1.0000 cv=0.0000 (random AND adversarial) -- by-construction-saturated

Why K<=2048 is by-construction:
- k_per_bank at MULTI_64x for K=2048 is 32; bank capacity is well below saturation.
- Adversarial feature-overlap 0.20 + 32 items per bank is trivially below the bank's per-bank
  capacity, so cleanup succeeds trivially.
- The MULTI_32x at K=1024 (k_per_bank=32) is at the SAME k_per_bank as MULTI_64x at K=2048.
  Both saturate. This is a per-bank-capacity effect, not a substrate-architectural lift.

K=4096 is the GENUINE chain-grade evidence because:
- k_per_bank at MULTI_64x is 64 (twice the saturating regime); recall drops below 1.0 (0.9927
  random, 0.9801 adversarial) showing the substrate IS operating in the discriminating regime.
- naive_rand_rec=0.0020 at K=4096 (BIAS-13 confirms substrate is not memorizing labels at random).
- MULTI_32x at K=4096 has k_per_bank=128 and ADVERSARIAL recall=0.667 -- the failure mode
  (adversarial under-coverage at small bank count, high per-bank capacity) is now visible.

Tier: HARD_PASS_CHAIN_GRADE at K=4096 MULTI_64x. Counts +1 with explicit note that K=1024 and
K=2048 results are by-construction-saturated and do NOT separately confirm chain-grade.

Atomization plan (math corpus):
  atom_id: math::T3/EXP_substrate_working_memory_multi_bank_K_extension_adversarial_v1_chain_grade_K_4096_multi_64x_random_0p9927_adversarial_0p9801_naive_0p0020_k_per_bank_64_in_discriminating_regime
  cert_status: HARD_PASS
  cert_class: experiment_substrate
  delta: +1
  cv: 0.0006 (random) / 0.0015 (adversarial)
  referent: metrics.json (per_unit) + 9 partial_metrics files
  note: "chain_grade_K_4096_only_K_1024_K_2048_by_construction_saturated_per_bank_capacity_effect_not_substrate_architectural_lift_MULTI_64x_arm_at_k_per_bank_64_discriminating_regime"

Q-DISCIPLINE atom (meta corpus):
  atom_id: meta::T3/META_multi_bank_WM_per_bank_capacity_governs_when_chain_grade_evidence_is_genuine_k_per_bank_>=_64_at_overlap_0p20_is_minimum_discriminating_regime
  cert_status: META_RULE_CERT_NEUTRAL
  delta: 0

hdlab/ primitive update:
  Update hdlab/working_memory (or equivalent) to expose multi_bank_K=4096 MULTI_64x as the
  chain-grade-confirmed extension over v1's K=1024 reference. Add the per-bank-capacity rule
  to the primitive's docstring as a "do not claim chain-grade below k_per_bank=64" gate.

==============================================================================
ARTIFACT 5: Multi-hop beam search with WM candidates v1
==============================================================================
Anchor: substrate_multihop_beam_search_with_WM_candidates_v1
Director call: HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM with META_M7 CAVEAT
Skunkworks ruling: MEASURED_MECHANISM (within-cell architectural lift is genuine but BLOCKED by
  sanity-breach + cross-cell rail mismatch; cannot count as chain-grade until reconciliation)

Per-seed verified (3 seeds: 7, 17, 23):
  seed 7:
    baseline_hrr_2hop      = 0.605  [BREACH: pre-reg [0.62, 0.68] sanity band]
    single_top1_5hop       = 0.275
    beam_w2_topk3_5hop     = 0.570
    beam_w5_topk3_5hop     = 0.615
    beam_w10_topk5_5hop    = 0.670
  seed 17:
    baseline_hrr_2hop      = 0.670  [OK]
    single_top1_5hop       = 0.330
    beam_w2_topk3_5hop     = 0.565
    beam_w5_topk3_5hop     = 0.595
    beam_w10_topk5_5hop    = 0.630
  seed 23:
    baseline_hrr_2hop      = 0.675  [OK]
    single_top1_5hop       = 0.385
    beam_w2_topk3_5hop     = 0.650
    beam_w5_topk3_5hop     = 0.665
    beam_w10_topk5_5hop    = 0.700

Aggregated:
  BEAM_W2  = 0.5950 cv = 0.065 (cv-rail HP_cv<=0.07 OK, tight)
  BEAM_W5  = 0.6250 cv = 0.047
  BEAM_W10 = 0.6667 cv = 0.043
  Monotonic W10 >= W5 >= W2: True (within tolerance)
  Lift W10 over single_top1: +0.3367 absolute (~2x relative)
  SINGLE_TOP1_5HOP rail = 0.33 (vs pointer-chain v2 rail of 0.122)

Two rails (Director-flagged; Skunkworks confirms BOTH are real):

RAIL 1: SANITY_BREACH (Director correctly surfaced; cv-rail allows but baseline drift is real)
  seed 7 baseline_hrr_2hop = 0.605 < 0.62 pre-reg lower band.
  cv across seeds = 0.0625 on the baseline arm -- right at the edge of HP_cv<=0.07.
  This is at minimum a regime-calibration question: the baseline-mean drift suggests the
  2-hop substrate is operating closer to a phase boundary than the pre-reg anchored on.
  Cell-author should re-baseline with more seeds before claiming chain-grade.

RAIL 2: META_M7 CROSS-CELL RAIL MISMATCH (genuine)
  SINGLE_TOP1_5HOP in THIS cell = 0.33; pointer-chain v2 reported SINGLE_TOP1_5HOP = 0.122.
  Both cells claim to be substrate-native multi-hop with single-top1-per-hop architecture, but
  produce VASTLY different rails (~2.7x). Either:
    (a) the cells differ in V_C, V_P, N, K_SET, beta_sweep, or top-K cleanup (configuration);
    (b) the cells differ in the multi-hop chain construction (compositional structure);
    (c) per-step accuracies in this cell are 0.81/0.65/0.50/0.41/0.33 -- multiplicative
        chain p ~ 0.81^5 != 0.33 (closer to 0.355) so the chain is non-iid; OK structurally
        but the cross-cell baseline must be reconciled before the +0.337 lift counts.
  The within-cell architectural lift IS clean (beam vs single under the SAME setup). But the
  cross-cell narrative "beam search broke a barrier other multi-hop architectures hit" cannot
  be confirmed without reconciling SINGLE_TOP1 across cells.

META_M7 ruling:
  Within-cell architectural lift survives (+0.337 absolute, monotonic, cv<=0.07): the BEAM
  primitive over PARALLEL-CANDIDATE WM-cleanup IS load-bearing within this cell's regime.
  Cross-cell barrier-1 promotion does NOT survive: the single-top1 rail mismatch with
  pointer-chain v2 is a regime / capacity-sensitive-dimension mismatch (the v2 rail was at
  V_P=10 capacity-saturated; this cell is at POINTER_V_P=10 BASELINE_V_P=2 mixed) and would
  re-classify pointer-chain v2 if applied symmetrically.

Tier: MEASURED_MECHANISM with proven-bound:
  - The PFC-style beam_search + cumulative-log-score ranking primitive achieves +0.337
    absolute over single-top1 at 5-hop depth UNDER THIS CELL's regime (V_P_pointer=10,
    V_P_baseline=2, K_SET=20, N=8192, V_C=200).
  - Cell-author should ship a v2 that reconciles the SINGLE_TOP1_5HOP rail with pointer-chain
    v2's 0.122 (same V_P, same V_C, same K_SET, same N) before chain-grade promotion.
  - The 1/3 seed sanity-breach on baseline_hrr_2hop is independent and should also re-baseline.

Atomization plan (math corpus):
  atom_id: math::T3/EXP_substrate_multihop_beam_search_with_WM_candidates_v1_measured_mechanism_within_cell_beam_lift_0p337_5hop_monotonic_blocked_by_sanity_breach_1_3_seeds_and_META_M7_cross_cell_rail_mismatch_pointer_chain_v2
  cert_status: MEASURED_MECHANISM
  cert_class: experiment_substrate
  delta: 0
  cv: 0.043 (beam_w10)
  referent: metrics.json
  note: "measured_mechanism_beam_lift_genuine_within_cell_blocked_by_2_rails_sanity_breach_and_cross_cell_single_top1_rail_mismatch_pointer_chain_v2_0p122_vs_this_cell_0p33_cell_author_re_baseline_v2"

META_M7 atom (meta corpus) -- ALREADY EXISTS:
  meta::T3/META_M7_smoke_regime_must_match_full_along_every_capacity_sensitive_dimension_pointer_chain_v2_csp_gated_signflip_evidence
  This new evidence (5th 6th attempt at barrier-1 multi-hop) is a SECOND independent confirmation
  of META_M7. Add a referent-pointer extension to the existing atom rather than a new atom.

==============================================================================
SUMMARY: CERT DELTA THIS BATCH
==============================================================================

Net delta: +2
  Artifact 2 V_REL refuse-gate extension: +1
  Artifact 4 WM multi-bank K=4096:        +1
  Artifacts 1, 3, 5:                       0 (MEASURED_MECHANISM, proven bounds)

If prior CERT was 588 (per MEMORY.md headline), post-batch CERT = 590.

Disciplines applied + verified:
  Fix #28 (per-arm verify):                applied. Director called 3/5 chain-grade; Skunkworks
                                            agrees on 2/3, overrides on 1/3 (META v4) due to
                                            by-construction-saturation. Per
                                            feedback-fix28-recurring-skunkworks-correct-more-than-director.
  Q-discipline saturation tiering:         applied to artifacts 1 (override) and 4 (partial
                                            override -- K<=2048 by-construction, K=4096 genuine).
  Verify-the-referent:                     applied. Re-read corpus + classify_pair body for
                                            artifact 1; re-read per-seed baselines for artifact 5;
                                            re-read per-arm M-sweep for artifact 3.
  BIAS-13 contamination:                   no encoder contamination detected in artifacts 2, 4.
                                            Artifact 3 uses pythia-2.8b at SETUP only (declared);
                                            _llm_forward_calls_at_inference=0 in all artifacts.
  BIAS-S band-calibration regime:          applied. Artifact 4 K-sweep correctly identified the
                                            discriminating regime (k_per_bank=64) and the
                                            by-construction-saturated regime (k_per_bank<=32).
  BIAS-R regime/mismatch:                  applied to artifact 5 (cross-cell rail mismatch caught
                                            and ruled META_M7).
  By-construction-saturation override:     applied to artifacts 1 (full) and 4 (partial). The
                                            cert_owner-overrides-director discipline working
                                            as designed.
  Verify-OFF-data, not reports:            applied. All 5 verdicts re-derived from metrics.json
                                            per-arm fields; no verdict_msg framings inherited.

Suggested ledger ops (skunkworks_atomize spawn, NOT this audit):
  +1 cert_ruling cert_increment_delta=+1 for V_REL refuse-gate envelope extension
  +1 cert_ruling cert_increment_delta=+1 for WM multi-bank K=4096 adversarial
  +0 cert_ruling cert_increment_delta=0 for META v4 (MM override)
  +0 cert_ruling cert_increment_delta=0 for KV M=100k partition routing (MM, Director already MB)
  +0 cert_ruling cert_increment_delta=0 for multihop beam search v1 (MM, blocked on 2 rails)
  +0 META atoms (meta corpus): by-construction-saturation-typed-sig + multi-bank-per-bank-capacity
                                are 2 new META rules
  +0 meta::T3/META_M7_* gets a referent-pointer extension (this is the 5th-6th independent
       confirmation of the rule)

==============================================================================
File paths (absolute):

Metrics (cited):
  d:/AI/hd-instrument/data/exp_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus/metrics.json
  d:/AI/hd-instrument/data/exp_substrate_distill_verify_operator_equivalence_v3_NAMED_corpus_stratified/metrics.json (referent-check)
  d:/AI/hd-instrument/data/exp_substrate_refuse_gate_v_rel_extension_v1/metrics.json
  d:/AI/hd-instrument/data/exp_substrate_kv_learned_projection_at_scale_M_100k_with_partition_routing_v1/metrics.json
  d:/AI/hd-instrument/data/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1/metrics.json
  d:/AI/hd-instrument/data/exp_substrate_multihop_beam_search_with_WM_candidates_v1/metrics.json

Cell code inspected (for by-construction analysis):
  d:/AI/hd-instrument/experiments/exp_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.py

Corpus inspected:
  d:/AI/hd-instrument/data/meta_reasoning_corpus/substrate_self_discovered_v1.jsonl

Ledger:
  d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl (747 rows pre-batch; +5 rows recommended)

Dispatch notes (cross-ref):
  d:/AI/hd-instrument/notes/exp_dev_to_research_META_v4_self_discovered_DISPATCHED_2026-06-25.md
  d:/AI/hd-instrument/notes/exp_dev_to_research_4cell_envelope_extension_DISPATCHED_2026-06-25.md
  d:/AI/hd-instrument/notes/exp_dev_to_research_USER_beam_search_and_expansion_sweep_DISPATCHED_2026-06-25.md

==============================================================================
END OF NOTE
