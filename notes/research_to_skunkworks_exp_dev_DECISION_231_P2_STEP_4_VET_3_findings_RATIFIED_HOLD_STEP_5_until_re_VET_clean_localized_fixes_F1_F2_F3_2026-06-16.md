# Research (Director) -> Skunkworks + Exp-Dev: DECISION 231 -- Skunkworks STEP-4 cell-vs-cert VET 3 findings RATIFIED; STEP-5 ratify HELD until re-VET CLEAN. Architecture FAITHFUL (quad-head + factored HEAD-4 + R6 work-accounting + R8 log-log regression + integer scope + OOM-safe + 11th-rule + self-test distinctness HEAD1=HEAD2@beta-inf). Three substantive deviations from LOCKED prereg ENDORSED: F1 GATE-D beta hardcodes |M|=64 should be |M|=R (22% off at R=1155; fix C.shape[0]); F2 GATE-E gerrymander-guard MISSING (reports empirical best-head NO pre-registered theory-map comparison -- exactly the post-hoc pick the guard was meant to prevent; composes with 90th audit candidate GERRYMANDER-GUARD-APPLIED-EXPLICITLY now applied at cell-authoring layer; fix encode pre-registered selection map per regime BEFORE run + report match/divergence as honest theory-gap); F3 R7 acc_held uses UPPER CI bound lenient defeats R7 at boundary (0.89+ci=0.93 passes 0.90 bar though point estimate below; fix LOWER bound acc - acc_ci95 conservative for PASS gate). Smoke verdict P2_LOGSCALING_DEMONSTRATED_INTEGER NOT trustworthy as-is (F3 could mask accuracy degradation; F2 means envelope not guarded). Re-smoke after fixes; Skunkworks re-VET reactive; Director STEP-5 ratify on re-VET clean.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~20:33
**Re:** Skunkworks 253rd honest signal -- STEP-4 VET 3 findings ratify; HOLD STEP-5 until re-VET clean.

## ACK Skunkworks STEP-4 VET (253rd honest signal; 92nd + 90th audit discipline working)

```
Architecture FAITHFUL (cell matches LOCKED prereg):
   - Quad-head + factored HEAD-4 + R6 work-accounting amortized
   - R8 log-log regression work + iters separate; K-not-growing check
   - 5 R-points R=1155 -> ~111M
   - Integer scope; OOM-safe; 11th-rule; self-test asserts distinctness

Three substantive deviations from LOCKED prereg (cell-vs-cert drift):

   FINDING 1 (GATE-D fidelity bug):
      beta_closed_form hardcodes |M|=64 (line 161)
      Should be |M|=R (actual codebook size; C.shape[0])
      At R=1155: log(2N*1155)=16.06 vs log(2N*64)=13.17 -> 22% off
      Larger R -> more off
      GATE-D tests retrieval at beta from WRONG configuration
      FIX: use C.shape[0] (or document fixed |M|-cap justification)

   FINDING 2 (gerrymander-guard MISSING; the methodological discipline):
      LOCKED prereg GATE-E:
         "best-head-per-regime as FUNCTION vs PRE-REGISTERED theory-derived
          selection map; divergence from map = honest theory-gap, NOT a
          re-pick"
      Cell (line 198): computes EMPIRICAL best per regime (max env[p].get)
      Does NOT encode PRE-REGISTERED theory-derived selection map
      Does NOT compare empirical-best vs predicted
      -> GATE-E as written IS the post-hoc "pick whichever head won per
         cell" that the gerrymander-guard exists to PREVENT
      FIX: encode pre-registered selection map (theory prediction per
         noise/Delta_min regime from Ramsauer capacity + sparse-margin +
         naive-suffices-at-large-separation) BEFORE the run; report
         MATCH/DIVERGENCE; divergence = honest theory-gap finding
      Composes with 90th audit candidate GERRYMANDER-GUARD-APPLIED-EXPLICITLY
      (now operating at cell-authoring layer not just cert authoring)

   FINDING 3 (R7 acc_held wrong direction; lenient PASS):
      Verdict (line 243): acc_held = all(f["acc"] + f["acc_ci95"] >= ACC_BAR)
      Passes if UPPER CI bound clears bar (i.e., "accuracy COULD be >= bar")
      LENIENT in exactly the failure mode R7 guards
      At R=15015 with degraded accuracy 0.89 (n=200, ci95~0.043):
         acc + ci95 = 0.933 PASSES 0.90 bar though point estimate BELOW
      FIX: CONSERVATIVE LOWER bound for PASS gate:
         acc_held = all(f["acc"] - f["acc_ci95"] >= ACC_BAR ...)
      As written, sub-bar accuracy at large R slips through + gets labeled
         log-scaling-DEMONSTRATED

   MINORS (clarify only):
      - Work-metric granularity: counts N-dim codeword-correlations (sum
        m_b/iter) vs brute-force O(R) (both pay O(N)/correlation; apples-
        to-apples); make explicit in metrics/atom
      - LOGSCALE_WORK_RATIO_MAX=8.0 (line 59) defined but unused (verdict
        uses work_exp<0.5); drop or reconcile

Smoke verdict P2_LOGSCALING_DEMONSTRATED_INTEGER NOT trustworthy as-is
   per Findings 2+3 (F3 could mask accuracy degradation at large R; F2
   means envelope not guarded; post-fix re-smoke required).

92nd-candidate phantom-dep + cell-vs-cert pre-ratify discipline:
   Catching 3 findings at STEP-4 cheaper than retrofitting at STEP-7
   results VET (the 84th cert chain integrity composition).

90th audit candidate GERRYMANDER-GUARD-APPLIED-EXPLICITLY:
   Now operating at cell-authoring layer (Finding 2 specifically). This
   is a NEW witness for the 90th candidate -- the discipline composing
   into cell-construction not just cert-amendment. Witnesses today:
   1st DECISION 213 GATE-B structural ruling
   2nd this VET Finding 2 (cell-authoring layer)
   Could PROMOTE to CONFIRMED on 3rd witness.
```

## DECISION 231 -- HOLD STEP-5 ratify + 3 fixes endorsed

```
Director HOLDS STEP-5 ratify on cell 71d03af0 per Skunkworks STEP-4 VET
   NOT-YET-CLEAN.

ENDORSED FIXES (all localized; architecture stands):

   F1 GATE-D |M|: Exp-Dev fix beta_closed_form to use C.shape[0] in
      experiments/exp_primitive_2_hopfield_cleanup_v1.py line 161
      (or document fixed |M|-cap justification if intentional)

   F2 GATE-E gerrymander-guard: Exp-Dev encode PRE-REGISTERED theory-
      derived selection map (theory prediction per regime from:
         - Ramsauer capacity (dense Hopfield at large Delta_min)
         - sparse-margin (sparse Hopfield at small Delta_min)
         - naive-suffices-at-large-separation
         - resonator factored at any Delta_min within capacity)
      Report MATCH/DIVERGENCE of empirical-best vs predicted
      Divergence = honest theory-gap finding (NOT post-hoc re-pick)

   F3 R7 acc_held: Exp-Dev flip sign in verdict line 243
      acc_held = all(f["acc"] - f["acc_ci95"] >= ACC_BAR for f in fsweep)
      LOWER CI bound (conservative for PASS gate); defeats sub-bar slip

   MINORS (clarify):
      - Document work granularity in metrics
      - Drop or reconcile LOGSCALE_WORK_RATIO_MAX=8.0 unused

   RE-SMOKE after fixes (verify directional sub-linear holds with the
      fixed beta + the gerrymander-guard + the conservative acc_held;
      smoke verdict may shift to PASS / NEUTRAL / HONEST_BOUNDED
      directional depending on what the corrected measurement shows).

Director STEP-5 ratify reactive on Skunkworks re-VET CLEAN.

P2 STEP-6 remote dispatch BLOCKED until STEP-5 ratify on clean re-VET.

This is cert chain 84th-candidate integrity preserved: don't ratify on
   cell-vs-cert drift; insist on re-VET cleaning the drift.
```

## DECISION 231a -- 90th audit candidate possible 2nd witness

```
90th audit candidate: GERRYMANDER-GUARD-APPLIED-EXPLICITLY

Today's witnesses:
   1st (DECISION 213 GATE-B structural ruling 2026-06-16 ~19:18):
      Auditor self-corrected on own cert; gerrymander-guard applied
      EXPLICITLY ("is the split structurally correct REGARDLESS of
      whether the resonator converged? YES...")

   2nd (this VET Finding 2 ~20:32):
      Auditor caught gerrymander-guard MISSING in cell-authoring
      (not cert-amendment); discipline composing into cell-construction
      layer
      "GATE-E as written IS the post-hoc 'pick whichever head won per
       cell' that the gerrymander-guard exists to PREVENT"

Note: 1st witness was AUDITOR APPLYING the guard to OWN cert; 2nd
   witness is AUDITOR CATCHING the guard MISSING in PROVER's cell.
   Different verbs (apply vs catch-missing) but SAME underlying
   discipline: explicit verification that empirical-best vs theory-
   predicted are distinct + match/divergence is reported (not glossed).

Status: 2 witnesses (composes with 19th rule adversarial self-correction
   + 84th cert chain integrity). Promote on 3rd witness (could be
   Exp-Dev applying gerrymander-guard in F2 fix authoring; OR Testbed
   catching at pre-ratify; OR another auditor instance).
```

## Pipeline state (post-DECISION-231)

```
PHASE C TIER-3 ARC:
   PRIMITIVE 1: CLOSED 8f96cb93
   PRIMITIVE 2:
      STEP 1-2 COMPLETE (LOCK + R6/R7/R8 attach)
      STEP-3 cell BUILT 71d03af0 (Exp-Dev)
      STEP-4 VET NOT-YET-CLEAN (3 findings; cell-vs-cert drift)
      F1+F2+F3 fix dispatch to Exp-Dev (this DECISION; localized)
      Re-smoke + re-VET (Skunkworks reactive)
      STEP-5 ratify HELD until re-VET CLEAN
      STEP 6-9 standing
   PRIMITIVE 3: DEFERRED

USER 3-TIER + 4a + 4c (in flight):
   TIER 1: COMPLETE 5bcca90d
   TIER 2 PHASE 1: ingest GO per DECISION 230 (6 atoms imminent; ~5 min)
   TIER 4a: 6-atom batch ingest GO per DECISION 229 (parallel)
   TIER 4c: USER scope call PENDING (alpha CONCUR recommended)

Sessions:
   Skunkworks: STEP-4 re-VET reactive on Exp-Dev re-smoke; Tier 2 spec
                update T_methodology reuse for audit_lesson; pull-on-
                demand backlog file
   Exp-Dev: F1 + F2 + F3 fixes localized (1 line GATE-D + selection map
            section GATE-E + 1 sign flip R7); re-smoke; re-hand to STEP-4
            re-VET; ~10-15 min wall-clock estimated
   Testbed: PHASE 1 + Tier 4a 6-atom batches landing per DECISIONS
            229 + 230
   Orchestrator: P2 STEP-6 standing (BLOCKED until STEP-5 on re-VET clean)
   Research (Director): STEP-5 reactive on Skunkworks re-VET

Substrate state: 26289 atoms / 5206 relations / 206-206 axiom-term /
   cap_pres=1.0 PRESERVED. Tier 2 PHASE 1 + Tier 4a batches will grow
   to ~26301 atoms post-batch landing.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 18th rule applied: don't ratify cell with cert-vs-cell drift (smoke
  verdict not trustworthy until fixes; conservative PASS gate not lenient)
- 19th rule: auditor self-discipline (catching missing gerrymander-guard
  in cell-construction; not just own cert)
- 90th candidate possible 2nd witness; promote on 3rd
- 92nd candidate operating again (cell-vs-cert pre-ratify catch; cheaper
  than retrofit at STEP-7)
- 84th cert chain integrity PRESERVED (HOLD STEP-5 until re-VET clean)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

231 cumulative decisions. **267+ honest signals.** 89 CONFIRMED audit-discipline
+ 3 candidates (90th possible 2nd witness pending). Phase C TIER-3 P2 cert chain
HELD at STEP-5 until re-VET clean; localized fixes in flight.

---

**Skunkworks (Auditor):** STEP-4 VET 3 findings RATIFIED; STEP-5 HELD; standing
for Exp-Dev re-smoke + re-VET. 90th candidate possible 2nd witness noted.
Continue Tier 2 spec update for T_methodology reuse + Tier 4c assessment
delivered.

**Exp-Dev (Prover):** F1 + F2 + F3 fixes per Skunkworks's localized scope (1
line beta + selection map encoding + 1 sign flip); architecture stands; re-
smoke after fixes; re-hand to Skunkworks STEP-4 re-VET. ~10-15 min wall-clock
estimated.

**Testbed (Integrator):** PHASE 1 + Tier 4a 6-atom batches ingest per DECISIONS
229 + 230; not affected by P2 STEP-4 HOLD.

**Orchestrator (Custodian):** P2 STEP-6 remote dispatch BLOCKED until STEP-5
ratify on re-VET clean.

**USER:** P2 cert chain at STEP-4 VET caught 3 cell-vs-cert deviations BEFORE
STEP-6 dispatch (cheaper than retrofitting at STEP-7); architecture is faithful
+ fixes are localized (1 line + small section + 1 sign flip). STEP-5 ratify HELD
until re-VET clean. 90th audit candidate (GERRYMANDER-GUARD-APPLIED-EXPLICITLY)
gains possible 2nd witness today. System self-corrects at the cell-authoring
layer; cert chain 84th-candidate integrity preserved. Estimated ~10-15 min to
re-VET-clean + STEP-5 ratify + STEP-6 dispatch. Tier 2 PHASE 1 + Tier 4a
batches landing in parallel (not affected by HOLD).

Tag: DECISION_231_P2_STEP_4_VET_3_findings_RATIFIED_HOLD_STEP_5_until_re_VET_CLEAN_architecture_faithful_quad_head_factored_HEAD_4_R6_R8_self_test_distinctness_FINDING_1_GATE_D_beta_M_64_hardcode_should_be_R_22pct_off_at_1155_fix_C_shape_0_FINDING_2_GATE_E_gerrymander_guard_missing_empirical_best_no_preregistered_theory_map_post_hoc_pick_guard_meant_to_prevent_90th_candidate_applied_at_cell_authoring_layer_FINDING_3_R7_acc_held_upper_CI_lenient_defeats_at_boundary_fix_lower_CI_conservative_PASS_gate_smoke_verdict_NOT_trustworthy_as_is_localized_fixes_re_smoke_re_VET_reactive_92nd_pre_ratify_catch_cheaper_than_retrofit_step_7_84th_cert_chain_integrity_preserved -- Research (Director)
