# Research (Director) -> Orchestrator + Skunkworks + Exp-Dev: DECISION 232 -- STEP-5 RATIFY GO on Skunkworks re-VET F1/F2/F3 CLEAN (HOLD resolved per DECISION 231; cell 09726387; all 3 fixes correctly applied per diff 71d03af0 -> 09726387). NEW MINOR F2b (one-line fix; gerrymander-guard's INNER theory model): margin = (1.0 - p) * delta_min instead of (1-2p) - off_diag; cell's actual noise model `noisy_query` rotates p fraction of coords -> true-sim erodes to ~(1-p); competitor to ~(1-p)*off_diag; noise-eroded margin ~(1-p)*delta_min vs band ~3/sqrt(N). At smoke p=0.45 the old model gives 0.1 (predict sparse) while correct gives 0.55 (predict naive matching empirical) -> the reported 0.45 "divergence" is MODEL ARTIFACT not genuine theory-gap. Guard INTEGRITY intact (no post-hoc re-pick; divergence honestly reported) -> does NOT block STEP-5; BLOCKS STEP-6 until applied so full-run map_match is MEANINGFUL. This composes with 90th audit candidate (GERRYMANDER-GUARD-APPLIED-EXPLICITLY) at a DEEPER LAYER: "guard must be PRESENT AND its prediction SOUND" -- now 3rd-witness candidate: Skunkworks checking the prediction not just the presence, with explicit composition framing. PROMOTE 90th to CONFIRMED.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~20:40
**Re:** Skunkworks 254th honest signal -- STEP-4 re-VET CLEAN; STEP-5 ratify; F2b before STEP-6; 90th audit candidate 3rd witness.

## ACK Skunkworks STEP-4 re-VET (254th honest signal; deeper auditor discipline)

```
F1+F2+F3 CLEAN (HOLD resolved):
   F1 GATE-D beta_closed_form(delta_min, M) -> M=R (C.shape[0]); hardcoded
      64 removed; smoke beta_cf 28.02 -> 29.20 at |M|=R=105 (correct config)
   F2 gerrymander-guard MACHINERY: preregistered_best_head computes theory-
      derived selection map BEFORE accuracy; regime_map reports predicted
      vs empirical_best + per-regime match + map_match_fraction; divergence
      reported as honest theory-gap not re-pick; emp_best restricted to
      flat heads (HEAD-4 is GATE-F's domain). CORRECT (machinery).
   F3 R7 acc_held = LOWER CI bound (acc - acc_ci95 >= ACC_BAR); lenient
      upper bound gone.

Minors fixed: work-granularity documented; LOGSCALE_WORK_RATIO_MAX dropped;
   NOISE extended to span naive->sparse crossover (makes GATE-E
   differentiation testable at full).

Diff 71d03af0 -> 09726387 verified clean; no regressions; architecture
   unchanged.

NEW MINOR F2b: gerrymander-guard's INNER THEORY MODEL inconsistency
   (the deeper discipline -- guard valuable only if prediction is
   best-theory):

   preregistered_best_head uses:
      margin = (1 - 2p) - off_diag
      (where off_diag = 1 - delta_min)
      predict naive if margin >= 3/sqrt(N) else sparse

   Cell's actual noise model noisy_query:
      rotate fraction p of coords by random phase
      ->  true-codeword sim after noise:   ~(1-p)
          competitor sim after noise:      ~(1-p) * off_diag
          noise-eroded MARGIN:              ~(1-p) * delta_min
          vs finite-N band:                 ~3/sqrt(N)

   At smoke p=0.45:
      OLD model: (1-2*0.45)=0.1 (subtract off_diag) -> predict SPARSE
      CORRECT:   (1-0.45)*delta_min=0.55*delta_min -> predict NAIVE
                  (matches empirical)

   The reported 0.45 "divergence" in smoke regime_map = MODEL ARTIFACT,
      not a genuine theory-gap.

   FIX (one line): margin = (1.0 - p) * delta_min (predict naive if
      margin >= band; else sparse). Or derive margin from documented
      noise model explicitly.

   Guard INTEGRITY intact (no post-hoc re-pick; divergence honestly
      reported) -> does NOT block STEP-5.

   BLOCKS STEP-6 until applied so full-run map_match_fraction +
      divergences are MEANINGFUL (signals REAL theory-vs-empirical gap),
      not model-artifacts.
```

## DECISION 232 -- STEP-5 ratify GO + F2b before STEP-6

```
Director STEP-5 RATIFY GO on cell 09726387 per Skunkworks re-VET CLEAN
   on F1/F2/F3.

   Architecture intact + 3 ratified findings correctly fixed + minors
      applied + no regressions per diff.

P2 cert chain transitions:
   STEP-4 re-VET CLEAN  (Skunkworks; this DECISION ACK)
   STEP-5 Director ratify CLEAN (this DECISION; cell 09726387)
   STEP-6 Orchestrator remote dispatch:
      BLOCKED until F2b one-line fix applied + re-smoke
      Estimated wall-clock to F2b fix: <5 min (one line; correct noise-
         eroded margin model)
      Then re-smoke (verify map_match_fraction rises; the 0.45 artifact-
         divergence resolves)
      Then STEP-6 GO

   Exp-Dev: F2b fix per Skunkworks's recommended one-liner:
      margin = (1.0 - p) * delta_min  (replaces (1-2p) - off_diag)
      preregistered_best_head returns naive if margin >= 3/sqrt(N) else sparse
      Re-smoke + verify smoke divergence resolves (or remains for honest
         documented reason)
      Hand to Orchestrator STEP-6 on re-smoke clean

   Orchestrator: STEP-6 dispatch on Exp-Dev's F2b re-smoke clean +
      Director STEP-5 ratify (this DECISION). Compute LIGHT (per Exp-Dev's
      STEP-3 note: GATE-F factored cheap; GATE-E codebook bounded; remote_
      cpu_queue feasible).

   Skunkworks: STEP-7 results VET reactive on remote run complete (per
      LOCKED bands + R1-R8 requirements + gerrymander-guard map_match
      meaningful).

   Testbed: STEP-9 atom ingest reactive on STEP-8 ratify.
```

## DECISION 232a -- 90th audit candidate PROMOTES to CONFIRMED on 3rd witness

```
90th audit-discipline candidate: GERRYMANDER-GUARD-APPLIED-EXPLICITLY

Today's witnesses:

   1st (DECISION 213 GATE-B structural ruling 2026-06-16 ~19:18):
      Auditor self-corrected on own cert; gerrymander-guard applied
      EXPLICITLY at cert-amendment layer ("is the split structurally
      correct REGARDLESS of whether the resonator converged? YES...")

   2nd (DECISION 231 STEP-4 VET Finding 2 ~20:32):
      Auditor caught gerrymander-guard MISSING at cell-authoring layer
      (composes 90th into cell-construction not just cert-amendment;
      directed Exp-Dev to encode pre-registered selection map)

   3rd (this DECISION re-VET F2b ~20:40):
      Auditor checked GUARD's PREDICTION (deeper layer; guard's INNER
      theory model), not just its PRESENCE; explicit composition framing:
      "Composes with 90th-candidate gerrymander-guard discipline: the
       guard must be PRESENT AND its prediction SOUND -- I'm checking
       the prediction, not just the presence."

PROMOTE 90th candidate to CONFIRMED on this 3rd independent witness:
   Pattern progresses through layers:
      - Layer 1: applied at cert-amendment (1st witness)
      - Layer 2: caught missing at cell-authoring (2nd witness)
      - Layer 3: checked at theory-model layer (3rd witness; this DECISION)
   Each layer adds depth; the discipline composes consistently across all 3.

UPDATED AUDIT TALLY:
   89 prior CONFIRMED + 1 promotion today (91st in DECISION 225)
   + 1 promotion today (90th in this DECISION 232)
   = 90 CONFIRMED audit-discipline instance types
   Candidates today still 3: 89th + 92nd + 95th (R3-predicate)
```

## Pipeline state (post-DECISION-232)

```
PHASE C TIER-3 ARC:
   PRIMITIVE 1: CLOSED 8f96cb93
   PRIMITIVE 2:
      STEP 1-2 COMPLETE (DECISION 226 LOCK + DECISION 228 R6/R7/R8)
      STEP-3 cell BUILT 71d03af0; FIXES 09726387 (F1+F2+F3 + minors)
      STEP-4 re-VET CLEAN (Skunkworks)
      STEP-5 Director RATIFY CLEAN (this DECISION; cell 09726387)
      F2b one-line fix in flight (Exp-Dev; <5 min)
      STEP-6 remote dispatch standing on F2b re-smoke clean
      STEP 7-9 standing
   PRIMITIVE 3: DEFERRED

USER 3-TIER + 4a + 4c:
   TIER 1: COMPLETE 5bcca90d
   TIER 2 PHASE 1 HARD_PASS 9da528ca (6 atoms)
   TIER 2 PHASE 2: spec authoring next (Skunkworks)
   TIER 3: DEFERRED
   TIER 4a HARD_PASS 5c881816 (5 atoms; 6th O_xunb pending)
   TIER 4c: USER scope call PENDING (alpha CONCUR recommended)

Sessions:
   Skunkworks: P2 STEP-7 results VET reactive on remote run complete;
                Tier 2 PHASE 2 spec; O_xunb 6th atom confirm; Tier 4c
                assessment delivered
   Exp-Dev: F2b one-line fix + re-smoke; hand to Orchestrator STEP-6
   Testbed: PHASE 2 receive when spec batch lands; STEP-9 P2 atom reactive
   Orchestrator: P2 STEP-6 dispatch standing on F2b re-smoke
   Research (Director): STEP-8 ratify reactive on STEP-7 VET

Substrate state: 26300 atoms / 5219 relations / 206-206 axiom-term /
   cap_pres=1.0 PRESERVED / methodology FROZEN at 24. Audit ledger:
   90 CONFIRMED (88 prior + 91st + 90th promoted today) + 3 candidates
   (89th + 92nd + 95th).
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 18th rule: don't ratify cert-chain cell with model-artifact in
  gerrymander-guard prediction (F2b blocks STEP-6 even though STEP-5
  ratify GOes; guard INTEGRITY != guard MEANINGFULNESS)
- 19th rule: auditor's discipline deepens through layers (cert-amendment
  -> cell-authoring -> theory-model)
- 90th candidate PROMOTED to CONFIRMED on 3rd independent witness today
- 84th cert chain integrity PRESERVED (STEP-5 ratify on F1/F2/F3 clean;
  STEP-6 blocked on F2b; meaningful before vs after distinction)
- 92nd candidate operating throughout
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

232 cumulative decisions. **268+ honest signals.** 90 CONFIRMED audit-discipline
instance types (88 prior + 91st + 90th promoted today) + 3 candidates (89th +
92nd + 95th). Phase C TIER-3 P2 STEP-5 RATIFIED; STEP-6 standing on F2b.

---

**Orchestrator (Custodian):** P2 STEP-6 dispatch GO on Exp-Dev F2b re-smoke
clean + this DECISION's STEP-5 ratify. Compute LIGHT (remote_cpu_queue
feasible). Then standing for STEP-7 results VET return.

**Skunkworks (Auditor):** STEP-4 re-VET CLEAN + F2b minor surfaced ACK;
90th candidate PROMOTED to CONFIRMED on 3rd witness (theory-model layer).
Standing for STEP-7 results VET reactive + post-write Tier 2 PHASE 1 +
Tier 4a VETs + O_xunb 6th atom confirm + Tier 4c assessment delivered.

**Exp-Dev (Prover):** F2b one-line fix per Skunkworks (margin = (1.0-p)*
delta_min replaces (1-2p) - off_diag); re-smoke; hand to Orchestrator
STEP-6 on clean. <5 min wall-clock estimated.

**USER:** P2 STEP-5 RATIFIED on Skunkworks re-VET CLEAN; F2b one-line minor
applied before STEP-6 dispatch (auditor going deeper -- guard PRESENT AND
prediction SOUND); 90th audit candidate PROMOTES to CONFIRMED on 3rd
witness (gerrymander-guard discipline progressing through cert-amendment ->
cell-authoring -> theory-model layers; consistent composition). Audit
ledger: 90 CONFIRMED + 3 candidates (89th, 92nd, 95th). Cert chain at
STEP-6 imminent; ~5 min wall-clock to F2b + dispatch.

Tag: DECISION_232_P2_STEP_5_RATIFY_GO_on_Skunkworks_re_VET_F1_F2_F3_CLEAN_cell_09726387_HOLD_resolved_NEW_MINOR_F2b_gerrymander_guard_INNER_theory_model_noise_eroded_margin_1_minus_p_times_delta_min_replaces_1_minus_2p_minus_off_diag_smoke_0p45_divergence_was_MODEL_ARTIFACT_not_genuine_theory_gap_guard_INTEGRITY_intact_does_NOT_block_STEP_5_BLOCKS_STEP_6_until_applied_full_run_map_match_meaningful_90th_audit_candidate_PROMOTES_to_CONFIRMED_on_3rd_independent_witness_today_theory_model_layer_composes_with_cert_amendment_1st_witness_cell_authoring_2nd_witness_AUDIT_TALLY_90_confirmed_88_prior_plus_91st_plus_90th_promoted_today_plus_3_candidates_89th_92nd_95th -- Research (Director)
