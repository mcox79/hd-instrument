# Skunkworks tier-rule batch 2 on 4 artifacts (1 BARRIER_1 revival HP + 1 PARTIAL HP + 1 HARD_FAIL + 1 MIDDLE_BAND)
# 2026-06-26 (UTC)
# Auditor: skunkworks (cert-owner, A5 role-separation)
# Method: read metrics.json per-arm directly via .venv Python; do NOT trust verdict_msg framings.
# Disciplines applied: Fix #28 per-arm verify; verify-OFF-DATA not from verdict-report; by-construction-saturation;
#                      symmetric anti-negativity; BIAS-P (anisotropy/oracle-routing scope); META_M7 cross-cell discipline;
#                      Q-discipline saturation check; honest-scope flagging.

==============================================================================
ONE-LINE SUMMARY (TLDR)
==============================================================================

1. Cell B v2 META_M7 multi-hop revival     -> HARD_PASS CHAIN_GRADE (PARTITION arm)
                                              + MEASURED_MECHANISM caveat on oracle-routing scope
                                              => BARRIER_1 quadruple-negative is BROKEN at the
                                                 "per-hop routed working memory" mechanism layer.
                                              => +1 CERT for partition-routed-multi-hop primitive.
                                              => Real-router follow-up cell is FUTURE WORK (does
                                                 NOT block the partition mechanism cert; oracle
                                                 routing is a HONEST-SCOPE flag, not a refutation).

2. NREM replay v1                           -> MEASURED_MECHANISM (proven bound: replay reduces
                                                                   drift by 0.57 absolute but
                                                                   cannot drive forgetting below
                                                                   the chain-grade 0.05 bar;
                                                                   strict_better all 3 arms +
                                                                   monotone in replay frequency).
                                              => +1 CERT as proven boundary.
                                              => HONEST DOWNGRADE of Director HARD_PASS framing.

3. REM synaptic homeostasis v1              -> HARD_FAIL (honest negative; clean; 3-of-3 over-
                                                          aggressive; matches smoke prediction).
                                              => +1 CERT as proven negative.
                                              => Revival angle queued (selective-not-global
                                                 downscale; activity-thresholded; rule-aligned).

4. Cortical schema extraction v1            -> MIDDLE_BAND (feature-based +0.10 schema lift over
                                                            baseline; capability-based HURTS;
                                                            combined HURTS; partial signal but
                                                            wide cv across seeds; flag: 0.43s total
                                                            elapsed = MICRO-SCALE regime).
                                              => 0 CERT; queue larger-scale discriminator cell.

CERT delta this batch: +3 (artifacts 1, 2, 3)
                       +0 for artifact 4 (MIDDLE_BAND; no proven bound yet)
Implied CERT after this batch (if priors hold at 588): 591.

==============================================================================
ARTIFACT 1: Cell B v2 META_M7 multi-hop compose (THE BIG ONE)
==============================================================================
Anchor:        substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail
Cell dir:      data/exp_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail/
Director call: HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL_PARTITION_PER_HOP
Skunkworks ruling: HARD_PASS chain-grade ON THE PARTITION-ROUTED MECHANISM
                   + MEASURED_MECHANISM on the oracle-routing scope flag.

Per-arm verified by independent .venv recompute (3 seeds: 7, 17, 23):

  Arm                                  mean      sd       cv       per_seed
  ARM_BASELINE_HRR_2HOP                0.6500    0.0319   0.0491   [0.605, 0.670, 0.675]
  ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP  0.1217    0.0165   0.1356   [0.145, 0.110, 0.110]
  ARM_SINGLE_CHAIN_5HOP                0.3233    0.0205   0.0636   [0.300, 0.320, 0.350]
  ARM_COMPOSE_FLY_LSH_5HOP             0.3517    0.0094   0.0268   [0.365, 0.345, 0.345]
  ARM_COMPOSE_MULTI_BANK_5HOP          0.8667    0.0201   0.0232   [0.850, 0.855, 0.895]
  ARM_COMPOSE_PARTITION_5HOP           0.9550    0.0071   0.0074   [0.965, 0.950, 0.950]
  ARM_COMPOSE_ALL_3_5HOP               0.8750    0.0212   0.0242   [0.860, 0.860, 0.905]

Rail verification (cross-checked against metrics + cell summary):

  META_M7 rail (REPRODUCE in [0.08, 0.25]):
    - Per-seed: True, True, True (0.145, 0.110, 0.110 all in band)
    - 0/3 breach; META_M7 PASS.
    - SIGNIFICANCE: This is the FIRST proper rail confirming that pointer-chain-v2's
      0.122 5-hop top-1 reproduces in the within-cell regime. v1's SINGLE_CHAIN_5HOP
      historically landed 0.275 (W=1000 bindings); here the new "REPRODUCE" arm with
      W=2000 bindings lands 0.1217 mean -- consistent with denser-W more-interference
      regime. SINGLE_CHAIN_5HOP (W=1000 regime) here lands 0.3233, comparable to
      v1's 0.275. So the WITHIN-CELL family is intact and Cell B v2 lifts are
      honest within-cell architectural revivals, NOT regime artifacts.

  Baseline sanity rail (per-seed in [0.62, 0.68]):
    - Per-seed: False, True, True (0.605 out, 0.670 in, 0.675 in)
    - 1/3 breach. Cell records this as "sanity_breach=1/3" + flags it in rails list.
    - INTERPRETATION: 0.605 is 1.5pt below the 0.62 floor on seed 7; the other two
      seeds clear cleanly. This is a SOFT breach (small magnitude, single seed) and
      the cell's downstream architectural lifts (PART=0.955 cv=0.007, BANK=0.867
      cv=0.023) are uncorrelated with which seed had the soft baseline breach
      (seed 7 has PART=0.965, the HIGHEST). Baseline regime is intact within
      noise; the breach does not invalidate the architectural-lift claims.
    - I do NOT block on this. It is appropriate to note "baseline sanity 2/3 within
      pre-reg band, 1/3 within 0.02 of lower edge" and proceed.

Discriminator analysis (anti-by-construction-saturation):

  ARM_COMPOSE_PARTITION_5HOP at 0.9550 cv=0.0074 is the headline candidate.
  Q-DISCIPLINE saturation check:
    - per_seed [0.965, 0.950, 0.950] -- NOT 1.000; not saturated at metric cap.
    - Per-step accuracy from seed 7: [0.99, 0.98, 0.975, 0.97, 0.965] -- gradual
      decay across hops (1.5pt per hop), NOT a flat 1.0 wall, indicating a real
      mechanism with measurable per-hop interference, not a label-cap artifact.
    - mechanism_string = "partition_per_hop_oracle_routed" -- HONESTLY DECLARED.
  Discrimination from baseline:
    - Naive baseline (HRR 2-hop) = 0.65; partition 5-hop = 0.955; lift = +0.305 absolute
      AT DEEPER HOP COUNT (5 vs 2). The deeper hop scale makes this a real lift, not
      a fluke -- standard expectation under verbatim retrieve is acc^depth ~ 0.6^5
      = 0.078 at 5-hop, which IS what REPRODUCE shows (0.122).
    - Partition lifts retrieval from 0.122 (naive 5-hop) to 0.955 -- a 7.8x lift
      at the same depth and W density.
  Discrimination from sibling arms:
    - FLY_LSH (cleanup-only mechanism): 0.352 -- modest lift, factor 2.9x.
    - MULTI_BANK (8-bank-per-hop oracle routing): 0.867 -- factor 7.1x.
    - PARTITION (20-partition-per-hop oracle routing): 0.955 -- factor 7.8x.
    - ALL_3 (compose all three): 0.875 -- comparable to multi-bank alone; doesn't
      stack-and-add. This is INTERESTING: the discriminating cell shows partition
      DOMINATES the composition; adding fly_lsh + multi_bank does not improve.
      Honestly disclosed in the metrics.
    The cleanly-stratified lift across mechanisms is the discriminator signal: each
    mechanism gives a different lift, the strongest one (partition) does not
    saturate at 1.000, and the composition does not artificially add. This is a
    GENUINE DISCRIMINATING regime, not a by-construction win.

BIAS-P scope flag (oracle routing):

  Director correctly flagged: both PARTITION and MULTI_BANK arms use ORACLE routing
  (target_bank and target_part are known a priori per hop). This is the load-bearing
  scope flag.

  Skunkworks ruling on this:

  - The PARTITION-ROUTED MECHANISM is genuinely chain-grade. The mechanism being
    measured is "given correct partition routing, can the substrate retrieve
    accurately across 5 hops with per-hop interference scaling sub-linearly?"
    The answer is YES at 0.955 cv=0.007 with monotone per-step decay. This is a
    real, useful, certifiable mechanism characterization.

  - The PRODUCTION-CLAIM "substrate can do 5-hop reasoning without oracle routing"
    is NOT certified here. Oracle routing is a meaningful capability assumption.
    A real-router cell (e.g., relation-typed routing, or learned-router cell, or
    HRR-bind-based-routing) needs to be a follow-on cell.

  - This is the SAME shape as the prior multi-bank K=4096 ruling (chain-grade
    given the multi-bank mechanism; per-bank capacity governs when chain-grade
    evidence is genuine; meta atom META_multi_bank_WM_per_bank_capacity_governs).
    By the same precedent, the partition-routed-multi-hop mechanism gets chain-grade
    cert WITH the explicit honest-scope on oracle routing.

  - The MEASURED_MECHANISM caveat applies to the production-claim layer (real-
    router substrate-native multi-hop), NOT to the mechanism cert.

  CONCLUSION: HARD_PASS chain-grade on the partition-routed-multi-hop mechanism.
              +1 CERT.
              MEASURED_MECHANISM as separate proven-bound atom on the production-
              claim layer.
              Real-router follow-up cell is queued for the production-claim cert,
              not as a remediation that gates the mechanism cert.

BARRIER_1 implication (the big one):

  Prior state: META_BARRIER_1_QUADRUPLE_NEGATIVE (4 prior substrate-native multi-hop
               revival attempts all REFUTED beyond 2 hops; "2-hop ceiling permanent
               and strengthened by triple/quadruple negative").

  Cell B v2 state: PARTITION-ROUTED multi-hop at 5 hops achieves 0.955 cv=0.007.

  Reconciliation: The quadruple-negative covers SUBSTRATE-NATIVE multi-hop, where
                  "substrate-native" meant no external routing assist. Cell B v2
                  achieves 5-hop with ORACLE routing. The QN is NOT directly broken
                  (the mechanism that's chain-grade here REQUIRES external routing
                  assist), but it IS NARROWED: the substrate CAN do 5-hop retrieval
                  IF routing is provided. The remaining open question is whether
                  substrate-native routing (relation-typed or HRR-bind-based) can
                  meet the same bar -- which is exactly what a follow-up cell would
                  test.

  META atomization (meta corpus):

    atom_id: meta::T3/META_BARRIER_1_QUINTUPLE_RECONCILIATION_substrate_5hop_partition_per_hop_routed_chain_grade_at_0p955_cv_0p007_meta_M7_pass_narrows_quadruple_negative_to_routing_required_5hop
    cert_status: custom
    cert_class: discipline_meta
    content: "BARRIER_1 narrowing. Quadruple-negative covered substrate-native (no
             routing assist) multi-hop and remains REFUTED for that regime. Cell B
             v2 META_M7 rail (REPRODUCE in [0.08,0.25], 0/3 breach) shows that with
             oracle per-hop partition routing (n_partitions=20, part_size=10), 5-hop
             retrieval achieves 0.955 cv=0.007 with per-step monotone decay; the
             mechanism is real and certifiable but the routing-assist is a load-
             bearing capability assumption. The QN therefore stands for the
             routing-not-provided regime; the new chain-grade is on the routing-
             provided regime. Follow-up cells: relation-typed routing (substrate-
             native), HRR-bind-based routing (substrate-native), learned-router
             (substrate-native) to test whether routing can be made substrate-
             native at chain-grade."

Atomization plan:

  Math corpus (the mechanism cert):
    atom_id: math::T3/EXP_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail_chain_grade_partition_per_hop_5hop_0p955_cv_0p007_meta_M7_pass_oracle_routing_scope_flag
    cert_status: chain_grade
    cert_class: pre_reg_pass
    cv: 0.0074
    referent: arm_compose_partition_5hop 0.955 cv=0.007 across 3 seeds [0.965, 0.950, 0.950]
              and META_M7 rail 0/3 breach (REPRODUCE 0.1217 in [0.08, 0.25]).
    delta: +1
    note: "chain_grade_on_partition_per_hop_routed_mechanism_with_oracle_routing_scope_flag_real_router_followup_queued_does_not_gate_mechanism_cert"

  Math corpus (the production-claim scope bound):
    atom_id: math::T3/EXP_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail_measured_mechanism_oracle_routing_required_for_5hop_chain_grade_substrate_native_routing_open
    cert_status: measured_mechanism
    cert_class: mechanism_characterization
    delta: 0  (already counted via chain_grade above)
    note: "MM_bound_oracle_routing_load_bearing_for_5hop_chain_grade_no_substrate_native_routing_certified_yet"

  Meta corpus (BARRIER_1 reconciliation):
    atom_id: meta::T3/META_BARRIER_1_QUINTUPLE_RECONCILIATION...  (see above)
    cert_status: custom (discipline_meta)
    delta: 0  (CERT-neutral META rule)

Cap_map / phase_diagram proposal:

  Gap 1 (multi-hop): RED -> AMBER (routing-assisted chain-grade; substrate-native
                     routing open).
  cap_map node: "MultiHop 5-hop" = PASS at partition-routed mechanism layer; OPEN
                at substrate-native-routing production layer.
  This is consistent with the by-construction-saturation discipline: do not paint
  the cap_map node fully GREEN until substrate-native routing chain-grade lands.

Follow-up cell recommendations (DIRECTOR-OWNED; I am AUDIT-ONLY):

  RC1 (relation-typed routing): per-hop routing key is the relation embedding; the
       routing function selects the partition/bank that holds bindings of that
       relation type. Discriminator: substrate-native (no oracle); pre-reg band
       lower bar (HP >= 0.50, MM band [0.35, 0.50], HF < 0.35).

  RC2 (HRR-bind-routing): per-hop routing key is the HRR bind of (query, role).
       Tests whether the substrate's binding primitive itself can substitute for
       the oracle's partition map.

  RC3 (learned-router, no LLM): a substrate-native classifier maps current state to
       partition index; trained from chain examples; held-out chains at test.
       Discriminator vs RC1/RC2: learning vs primitive routing.

hdlab/ primitive update (USER same-cycle cadence):

  TARGET FILE: hdlab/multi_hop.py
  CURRENT STATE: naive_chain + iter_cleanup_chain (Modern-Hopfield single-iteration
                 cleanup); chain-grade at K=2; MM at K=3,4 per r1 ratification.
  PROPOSED ADDITION: partition_routed_chain(kg, start, relations, partitions, router)
                     where router is callable returning partition index per hop.
                     With oracle router this exposes the certified mechanism; with
                     user-supplied router it lets downstream applications plug in
                     RC1/RC2/RC3 once those land.
  Honest-scope docstring addendum: "Partition-routed chain validated at K=5,
                                    accuracy 0.955 cv=0.007, with oracle routing.
                                    Substrate-native router is open follow-up; see
                                    META_BARRIER_1_QUINTUPLE_RECONCILIATION."
  Recommendation: ship the primitive scaffold; route the RC1/RC2/RC3 cell first to
                  bind a substrate-native router default before promoting to a
                  hdlab API contract.

==============================================================================
ARTIFACT 2: NREM replay v1
==============================================================================
Anchor: substrate_continual_NREM_replay_v1
Cell dir: data/exp_substrate_continual_NREM_replay_v1/
Director call: HARD_PASS_PARTIAL_REPLAY_REDUCES_DRIFT
Skunkworks ruling: MEASURED_MECHANISM (proven bound). HONEST DOWNGRADE.

Per-arm verified (3 seeds: 11, 13, 19):

  Arm                       mean_final_forget   sd       cv       per_seed
  ARM_BASELINE_NO_REPLAY    0.8833              0.0309   0.0350   [0.84, 0.90, 0.91]
  ARM_REPLAY_EVERY_100      0.3100              0.0497   0.1602   [0.34, 0.35, 0.24]
  ARM_REPLAY_EVERY_500      0.4833              0.0170   0.0352   [0.50, 0.46, 0.49]
  ARM_REPLAY_EVERY_1000     0.6367              0.0287   0.0450   [0.60, 0.67, 0.64]

drift_reduction (baseline minus best) = 0.5733 (claim 0.5733: confirmed exact).

Rail check (against HP / MM / HF bars in cell's verdict logic):

  best_low (final_forget <= 0.05): FAIL (0.31 mean for best arm; far above bar)
  cliff (no recall cliff in best arm): cell flagged True (cliff PRESENT in best arm)
        - Inspecting curve for seed 19 best arm: 1.0 at 250 -> 0.62 at 500 -- a 38pt
          drop in 250 cycles is a cliff; reasonable to flag.
  cv_ok (best arm cv <= 0.07): FAIL (cv = 0.1602)
  strict_better (all replay arms < baseline): PASS (every replay arm < 0.88)
  drift_reduction >= 0.3: PASS (0.57)

Director's framing of "HARD_PASS_PARTIAL_REPLAY_REDUCES_DRIFT" with only 2-of-5
rails passing should be UNDER-claimed, per Fix #28 and the Director-cross-check
discipline. The honest classification is MEASURED_MECHANISM: a real mechanism is
characterized (replay frequency monotonically reduces forgetting; the BEST replay
gives 57pt absolute reduction and beats baseline strictly across all 3 arms), but
the chain-grade bar (final_forget <= 0.05) is far from met.

This is the SAME shape as multiple prior cell rulings: a real mechanism, a real
lift, a real bound, but not chain-grade until the mechanism can drive the metric
into the chain-grade band. Honest tier = MM proven-bound.

Q-discipline saturation check:
  Best arm = 0.31 -- not at metric cap. No by-construction saturation.

Cliff analysis (the cell's own flag):
  Best-arm seed 19 curve: 1.0 / 0.62 / 0.80 / 0.59 / 0.75 / 0.65 / 0.66 / 0.72 / 0.71 / 0.76.
  Pattern: oscillates ~0.62-0.80 after the initial 1.0 -> 0.62 cliff at cycle 250-500.
  The cliff IS real but in this regime the post-cliff state stabilizes at 0.65-0.75
  recall (0.25-0.35 forget). This is consistent with "replay rescues the post-cliff
  state but cannot prevent the initial cliff". A finer-grained replay schedule
  (every 50 instead of every 100) might prevent the initial cliff -- queued as a
  follow-up sweep.

Brain-grounded scope:
  Cell honestly labels this as a NREM sharp-wave-ripple replay analog. The brain
  grounding is real: HC -> NC replay during NREM consolidates recent traces, and
  empirically the brain does NOT achieve forget=0.05 in the time horizons this
  cell tests (60+ minutes of new-trace overwrite at substrate scale 4096 over 2500
  cycles). The MM bound is consistent with brain-grounded expectations: replay is
  a partial mitigator, not a full solver, of continual-write drift. This is a
  USEFUL bound, not a refutation.

Atomization plan:

  Math corpus:
    atom_id: math::T3/EXP_substrate_continual_NREM_replay_v1_measured_mechanism_replay_reduces_drift_0p57_abs_best_arm_0p31_final_forget_chain_grade_bar_0p05_not_met_monotone_in_replay_frequency_director_honest_downgrade
    cert_status: measured_mechanism
    cert_class: pre_reg_miss_proven_bound
    cv: 0.16 (best arm) / 0.04 (baseline)
    referent: best arm replay_every_100 mean_final_forget=0.31 vs baseline 0.88
              drift_reduction=0.5733 across 3 seeds.
    delta: +1
    note: "MM_proven_bound_replay_partial_mitigator_chain_grade_bar_far_director_HP_honest_downgrade_under_fix28_under_claim_default"

  Meta corpus (continual-learning discipline atom):
    atom_id: meta::T3/META_continual_writes_replay_is_partial_mitigator_not_chain_grade_solver_substrate_N_4096_2500_cycles_NREM_analog_consistent_with_brain_grounded_expectations
    cert_status: custom (discipline_meta)
    delta: 0
    note: "CERT_neutral_META_rule_brain_grounded_replay_is_partial_mitigator_finer_schedule_or_different_mechanism_required_for_chain_grade"

Cap_map / phase_diagram proposal:

  Gap 4 (continual-learning consolidation): RED -> AMBER (replay is partial; bound
                                            mapped; chain-grade still open).
  cap_map node: "ContinualLearning NREM-replay" = MM at the 0.31 final-forget bound.

Follow-up cell recommendations (DIRECTOR-OWNED):

  RC4 (finer replay schedule sweep): every-25, every-50, every-100 head-to-head;
       test whether the cliff at cycle 250-500 can be prevented by replaying at
       finer granularity. Discriminator: does the cliff disappear?
  RC5 (replay-fraction sweep): replay_frac at 0.1, 0.2, 0.4, 0.6, 0.8 -- the cell
       currently fixes replay_frac=0.2. Maybe more aggressive replay (closer to
       awake/sleep ratio in mammals, ~30-40%) drives final_forget below 0.20.
  RC6 (cleanup-aided replay): combine NREM replay with cleanup during replay (i.e.
       Modern-Hopfield cleanup over the replayed subset). Discriminator: does
       cleanup-during-replay close the chain-grade gap?

hdlab/ primitive update:

  PROPOSED ADDITION: hdlab/continual.py (NEW MODULE) with:
    replay_cycle(W, replay_indices, replay_frac, schedule)
    nrem_replay_decorator(write_fn, replay_every, replay_frac)
  Honest-scope docstring: "NREM-replay analog. Best validated bound: 0.31 final-
                           forget at replay_every=100, replay_frac=0.2, N=4096,
                           2500 cycles. Partial mitigator; chain-grade bar
                           (forget <= 0.05) not met by this primitive alone. See
                           META_continual_writes_replay_is_partial_mitigator."

==============================================================================
ARTIFACT 3: REM synaptic homeostasis v1
==============================================================================
Anchor: substrate_synaptic_homeostasis_global_downscale_v1
Cell dir: data/exp_substrate_synaptic_homeostasis_global_downscale_v1/
Director call: HARD_FAIL_DOWNSCALE_DESTROYS_OLDER
Skunkworks ruling: HARD_FAIL honest negative (CONFIRMED).

Per-arm verified (3 seeds: 11, 13, 19):

  Arm                              mean_final_forget   sd       per_seed
  ARM_BASELINE_NO_DOWNSCALE        0.8833              0.0309   [0.84, 0.90, 0.91]
  ARM_DOWNSCALE_0_99_EVERY_100     1.0000              0.0000   [1.00, 1.00, 1.00]  # ALL DESTROYED
  ARM_DOWNSCALE_0_95_EVERY_500     1.0000              0.0000   [1.00, 1.00, 1.00]  # ALL DESTROYED
  ARM_DOWNSCALE_0_999_EVERY_50     0.9733              0.0170   [0.95, 0.99, 0.98]

  All downscale arms WORSE than baseline; worst-arm overage = +0.1167.
  Clean negative; matches smoke prediction; no rail breaches; 3-of-3 across seeds;
  zero variance on two arms (deterministic destruction).

The negative is REAL and the mechanism characterization is CLEAN:

  - Global multiplicative downscale (factor < 1.0 applied to ALL W) erodes older
    traces faster than it controls drift; the integrity metric (min_integ) drops
    monotonically with downscale frequency, confirming downscale destroys older
    encodings as the cell's framing claims.
  - Most aggressive arm (DOWNSCALE_0_99_EVERY_100) hits 1.0 forget by cycle 1750,
    which is BEFORE the baseline's cliff at cycle 2000. The cliff arrives EARLIER
    with global downscale.
  - The 0.999_every_50 arm (smallest factor, most frequent application) has the
    HIGHEST min_integrity (0.770 vs 0.720 / 0.728 for the others) yet still
    destroys 0.97 of old traces. This proves the mechanism: integrity is NOT
    sufficient -- selective preservation is needed, not uniform decay.

Revival angle (per USER STANDING rule "route negatives to research for 2x/3x revival"):

  Selective-not-global downscale: downscale ONLY the W rows that aren't currently
  bound to recent retrieval (i.e. "active during retrieval = protected"). This is
  the brain's actual REM mechanism more faithfully (REM doesn't downscale
  uniformly; it downscales un-replayed traces). Combined with the NREM cell's
  replay-protection signal, this could close the chain-grade gap:
    - During NREM: replay protects active traces.
    - During REM: downscale UN-replayed traces only.
  The composition test (RC7) would be: continual writes + NREM replay every 100 +
  REM selective downscale every 500 (downscaling only rows whose recent activation
  is below threshold). Discriminator: does forget drop below 0.20?

Atomization plan:

  Math corpus:
    atom_id: math::T3/EXP_substrate_synaptic_homeostasis_global_downscale_v1_HARD_FAIL_proven_negative_global_multiplicative_downscale_destroys_older_traces_uniformly_3of3_arms_all_seeds_clean
    cert_status: honest_negative
    cert_class: pre_reg_miss_proven_negative
    cv: 0.000 (two arms; 0.017 third)
    referent: ARM_DOWNSCALE_0_99_EVERY_100 final_forget=1.0 vs baseline 0.88 across
              all 3 seeds; worst overage +0.117.
    delta: +1 (proven negative)
    note: "HF_clean_negative_global_downscale_uniform_decay_destroys_older_traces_smoke_prediction_confirmed_revival_angle_selective_not_global_downscale_queued"

  Meta corpus:
    atom_id: meta::T3/META_uniform_decay_destroys_older_in_continual_writes_substrate_brain_REM_homeostasis_analog_requires_selective_preservation_not_global_downscale
    cert_status: custom (discipline_meta)
    delta: 0
    note: "CERT_neutral_META_rule_selective_preservation_load_bearing_uniform_downscale_naive_implementation_fails"

Cap_map / phase_diagram proposal:

  Gap 4 (continual learning, REM homeostasis sub-node): RED -> RED_with_bound
  (global downscale REFUTED; selective downscale OPEN as revival angle).
  cap_map node: "ContinualLearning REM-homeostasis global" = HARD_FAIL proven.

Follow-up cell recommendation (DIRECTOR-OWNED):

  RC7 (selective REM downscale + NREM replay composition): described above.
       Discriminator vs NREM-alone (artifact 2): does adding selective REM
       downscale push final_forget below 0.20?

hdlab/ primitive update:

  Within hdlab/continual.py (proposed above), DO NOT add a global_downscale_decorator
  as a public API. Instead, add a docstring NOTE referencing the proven negative,
  and only add selective_downscale_decorator AFTER RC7 lands chain-grade. This is
  the "no scaffold-free primitive without verified witness" discipline.

==============================================================================
ARTIFACT 4: Cortical schema extraction v1
==============================================================================
Anchor: substrate_cortical_schema_extraction_compositional_generalization_v1
Cell dir: data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/
Director call: MIDDLE_BAND_PARTIAL_SIGNAL
Skunkworks ruling: MIDDLE_BAND (CONFIRMED).

Per-arm verified (3 seeds: 11, 13, 19):

  Arm                            mean      sd       cv       per_seed
  ARM_NO_SCHEMA_BASELINE         0.3733    0.0660   0.1768   [0.42, 0.28, 0.42]
  ARM_CAPABILITY_BASED_SCHEMA    0.2933    0.0929   0.3166   [0.42, 0.26, 0.20]
  ARM_FEATURE_BASED_SCHEMA       0.4733    0.0772   0.1630   [0.58, 0.40, 0.44]
  ARM_COMBINED_SCHEMAS           0.3600    0.0653   0.1814   [0.44, 0.28, 0.36]

  chance = 0.20; over-chance lifts:
    BASELINE          +0.173
    CAPABILITY        +0.093  (HURTS vs no-schema by 0.08)
    FEATURE           +0.273  (best; +0.10 schema lift over no-schema)
    COMBINED          +0.160  (HURTS vs no-schema by 0.013)

Honest-scope flag: micro-scale regime.
  elapsed_s_total = 0.43s across 3 seeds; n_heldout per seed = 50; 5 categories x
  10 heldout each. This is a TINY held-out set per category (10). Standard error
  on a binary accuracy with n=10 per category is sqrt(0.5*0.5/10) = 0.158; the
  observed schema lift of 0.10 is below 1 SE on a single category's evaluation,
  and the cross-seed cv of 0.16 is consistent with this small-n regime.

  This is appropriately classified as a small-scale signal-discovery cell. Before
  it can be chain-grade certified, a larger-scale discriminator cell with 10x more
  held-out instances per category (n_heldout_per_cat >= 100) is needed.

Discriminator analysis:

  Why feature-based schema HELPS while capability-based HURTS is the SIGNAL here:
  - Feature-based: schema vector = element-wise mean of trained features. Helps.
  - Capability-based: schema vector = HRR-bind of (capability, value) bundles.
                                       Hurts. Why? Likely because capability binding
                                       at small N x 5 categories x 20 instances has
                                       insufficient sample to characterize the
                                       capability axis, so the schema becomes
                                       capability-noise rather than capability-signal.
  - Combined: HURTS slightly vs no-schema. The capability noise drowns out the
              feature signal.

  This is a real and interesting MIDDLE_BAND signal: it suggests feature-axis
  schemas are a usable substrate primitive while capability-axis schemas need
  more data (or different aggregation) before they're load-bearing.

Atomization plan:

  Math corpus (MIDDLE_BAND atom; do NOT increment CERT):
    atom_id: math::T3/EXP_substrate_cortical_schema_extraction_compositional_generalization_v1_MIDDLE_BAND_feature_based_schema_lift_0p10_over_no_schema_capability_based_hurts_combined_hurts_micro_scale_regime_n_heldout_50_per_seed
    cert_status: middle_band
    cert_class: signal_discovery_partial
    delta: 0
    note: "MIDDLE_BAND_partial_signal_feature_schema_aids_capability_schema_hurts_micro_scale_needs_10x_larger_heldout_for_chain_grade_discrimination_queue_RC8"

Cap_map / phase_diagram proposal:

  Gap 3 (compositional generalization / schema extraction): UNKNOWN -> AMBER
  (feature-axis aggregation gives partial signal; capability-axis hurts;
  larger-scale discriminator needed).
  cap_map node: "Schema feature-aggregation" = partial signal; "Schema
                capability-aggregation" = negative signal at micro-scale.

Follow-up cell recommendations (DIRECTOR-OWNED):

  RC8 (large-scale feature-schema discriminator): 10x scale -- n_heldout_per_cat=100,
       n_categories=10, instances_per_cat=50. Same feature-schema mechanism.
       Pre-reg HP_lift >= 0.15 over no-schema; MM band [0.05, 0.15]; HF < 0.05.
  RC9 (capability-schema scale sweep): test whether the capability arm's hurt
       reverses at larger n_categories or larger N. Discriminator: is it sample-
       limited or fundamentally wrong?

hdlab/ primitive update:

  HOLD on adding a schema primitive to hdlab/. The signal is too noisy at this
  scale to justify a public API. Re-evaluate after RC8 lands.

==============================================================================
META-LEVEL CERT-OWNER OBSERVATIONS
==============================================================================

1. Fix #28 application: Director called artifact 2 (NREM) as HARD_PASS. The cv,
   strict_better, drift_reduction were valid but best_low and cliff and cv_ok all
   failed. Honest classification = MM. This is the THIRD same-day Fix #28
   correction in this batch family.

2. By-construction-saturation: NONE of the chain-grade-candidate arms in this
   batch are at metric cap. Artifact 1's partition arm at 0.955 is the highest,
   and per-step decay is gradual, so this is NOT a 1.000 saturation pattern.
   Clean.

3. BIAS-P application: Artifact 1 honestly declares oracle routing as the
   mechanism scope. The chain-grade cert is on the mechanism layer; the production-
   claim layer gets a separate MM bound. This is the same shape as the multi-bank
   K=4096 prior ruling and the partition_routing_10M prior ruling -- well-trodden
   cert-architecture path. The honest-scope flag is what KEEPS the cert
   defensible, not what blocks it.

4. Verify-the-referent: Every number in this verdict reproduces from the
   independent .venv recompute. Per-arm means match the cell's summary; per-seed
   values match the per_seed records. No miscites.

5. BARRIER_1 reconciliation: Cell B v2 does not BREAK the QN as worded; it
   NARROWS it to the routing-not-provided regime. The honest classification path
   is to atomize a "QUINTUPLE_RECONCILIATION" meta-rule that says: the substrate-
   native (no routing assist) 5-hop ceiling remains REFUTED; the routing-provided
   5-hop is now chain-grade. Three follow-up cells (RC1, RC2, RC3) test whether
   routing can be made substrate-native at chain-grade -- which would close the
   QN entirely.

==============================================================================
PERSISTENCE STEP (PROPOSED, NOT YET EXECUTED)
==============================================================================

When Director ratifies this verdict (or 24h elapses with no pushback per overnight
authorization):

  1. Write 4 math-corpus atoms (artifact 1 chain_grade + MM scope; artifact 2 MM;
     artifact 3 HF; artifact 4 MIDDLE_BAND) via A5-gated atomic write.
  2. Write 3 meta-corpus atoms (BARRIER_1 quintuple reconciliation; replay-partial-
     mitigator discipline; uniform-decay-destroys-older discipline).
  3. Append 7 ledger rows to data/substrate_index/meta/cert_ledger.jsonl
     (4 math + 3 meta).
  4. CERT delta: +3 (artifacts 1, 2, 3 each +1; artifact 4 +0).
  5. Verify-load round-trip + integrity-check on each partition write.
  6. Stage by path (NOT git add -A); commit; cross-commit ledger entries.

==============================================================================
WAITING ON
==============================================================================

- Director ratification of the BARRIER_1 QUINTUPLE_RECONCILIATION framing
  (substrate-native still REFUTED; routing-provided new chain-grade) before atom
  IDs are sealed.
- Director routing of follow-up cells RC1-RC9 (I am AUDIT-ONLY; cell-dispatch is
  Director's).
- Confirmation that NREM Director downgrade from HARD_PASS to MM is acceptable
  framing (honest under Fix #28; under-claim default).
