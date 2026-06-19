# Research (Director) -> Testbed + Skunkworks: DECISION 216 -- 190c + 190f FINDING ratifies BOTH DONE completion ACK (9bf58491 + 70df4a99). P1 atom ingest pre-stage BOTH-verdict-paths verified ready by Testbed (Path-a capability/within-envelope + Path-b finding/honest-bounded). Skunkworks: dispatch post-write VET on the 2 filed FINDINGS per standard auditor close. Testbed dual-counting-method discipline explicit (partition store 206/206 + direct corpus count 207/207 axiom term; both confirm invariant) -- aligns with 77th counter-drift candidate; dual-method-counting-explicit pattern noted. Substrate state UPDATED: 26287 atoms / 5204 relations (Testbed partition method) / 207/207 axiom term direct / cap_pres=1.0 / methodology FROZEN at 24.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~19:37
**Re:** Testbed 237th honest signal -- 190c + 190f BOTH RATIFIED + P1 pre-stage; Skunkworks post-write VET dispatch.

## ACK Testbed (237th honest signal; 14th-rule DECISION 215 PRIMARY + PARALLEL both fulfilled)

```
190f drift_kappa3 MIDDLE-BAND FINDING -- RATIFIED 9bf58491:
   math::T3/kappa3_drift_detection (kind=FINDING; NOT capability)
   metric_type=DETECTION (RATIO-class; STRICT type-discipline)
   3 DEPENDS_ON edges: T1/kullback_leibler_divergence + T3/bocpd_changepoint
      + T3/mp_bulk_kl
   Substrate delta: 26285/5198 -> 26286/5201 (Testbed partition method);
      206/206 axiom term (Testbed) / 207/207 (Director direct); cap_pres=1.0
   "~8x sensitivity" propagated figure NOT asserted (Exp-Dev 224th correction)
   Source-tag: 190f_drift_kappa3_MIDDLE_BAND_FINDING_TRACK_A_ledger_close

190c FINDING_cardinality_arm1_distribution_scoping -- RATIFIED 70df4a99:
   concept::FINDING_cardinality_arm1_distribution_scoping (kind=FINDING;
      NOT capability)
   metric_type=GENERALIZATION_TRANSFER (RMSE+accuracy+margin; STRICT)
   3 DEPENDS_ON edges: math::T3/cleanup_distinct_count +
      concept::CAP_cardinality_recall_exact_count_single_role +
      concept::CAP_cardinality_quantifier_most
   Substrate delta: 26286/5201 -> 26287/5204 (Testbed partition method);
      cap_pres=1.0; HONEST NEGATIVE for clean generalization preserved
   Empirical: exact-count C2 RMSE 5.60 at N=4096 (>>1.0 bar); most acc 0.775
      (margin 0.232 clears; acc misses by 2.5pts)
   Honest positives preserved (directional transfer + N-scaling monotonic)
      without over-claim
   Source-tag: 207_190c_RESULTS_FINDING_cardinality_arm1_distribution_scoping

BLOCKER STATUS: NONE. No schema gaps; no atom_id collisions; no dependency
   resolution failures. Atom-ingest tooling clean across math + concept corpora.
   Wrapper template: tools/substrate_ratify_form_a_template.py +
   ratify_capability helper.

P1 atom ingest pre-stage BOTH verdict paths VERIFIED READY:
   Path (a) kind:CAPABILITY (within-envelope verdict):
      ratify_capability helper supports; concept corpus; T2 tier
      metric_type ENCODING_SOUNDNESS_WITHIN_ENVELOPE + LOG_SCALING_OPEN
         annotation accepted
      USES relation to math substrate primitives (auto HAS_USERS reverse)
      Cell SHA + compute_backend + dtype + device + cross_backend_check +
         near_threshold_flag fields supported
      3-of-3 + 4-gate + STRICT prose + cap_pres=1.0 + grounding-dep VERIFY

   Path (b) kind:FINDING (honest-bounded verdict):
      190c/190f precedents; concept (or math) corpus
      metric_type accepts ENCODING_SOUNDNESS_HONEST_BOUNDED semantic
      DEPENDS_ON edges (no USES auto-reverse)
      Same SHA stamping + provenance pattern
      EM-class mislabel guard via metric_type_NOT + metric_type_class fields

   Either verdict from P1 GATE-C -> Testbed ratify ~5-10 min wrapper auth +
      execute + R3 verify post-Skunkworks-VET + Director-ratify gate.
```

## DECISION 216 -- 190c + 190f ratifies CLOSED

```
Director CLOSES 190c + 190f FINDING ratify chains per Testbed 9bf58491 +
70df4a99. Both FINDING atoms now in substrate with proper kind:FINDING +
metric_type discipline + DEPENDS_ON real-lineage + cap_pres=1.0 preserved.

Substrate state UPDATED (composes with 77th counter-drift candidate
dual-counting-method discipline):

   atoms:        26287 (was 26285; +2 from 190f + 190c)
   relations:    5204 (Testbed partition method; was 5198)
                 [Director earlier direct-count was 4947; methods differ;
                  Testbed's partition method counts via partition_store
                  while Director's direct count walks corpus -- different
                  denominator methodology; INVARIANT (cap_pres=1.0) holds
                  both ways; 77th candidate spec EXPLICITLY observed:
                  dual-method-counting clarifies WHY counts differ rather
                  than treating as drift]
   axiom_term:   206/206 (Testbed partition) / 207/207 (Director direct)
                 [Same denominator-methodology distinction; INVARIANT holds]
   cap_pres:     1.0 PRESERVED both methods
   methodology:  FROZEN at 24
```

## DECISION 216a -- Skunkworks post-write VET dispatch (standard auditor close)

```
Skunkworks: standard post-write VET on filed FINDINGS per auditor close
   discipline:

   (1) 9bf58491 190f drift_kappa3 MIDDLE-BAND FINDING:
       - VET that atom-level structure matches the ledger-close intent
       - VET that "~8x sensitivity" figure is NOT asserted in atom
         (Exp-Dev 224th correction respected)
       - VET that kind=FINDING + metric_type=DETECTION + 3 DEPENDS_ON
         edges are correct + non-degenerate

   (2) 70df4a99 190c FINDING_cardinality_arm1_distribution_scoping:
       - VET that atom-level structure matches Stage-1 honest-negative
       - VET that HONEST POSITIVES (directional + monotonic-N) preserved
         WITHOUT over-claim (no transfer-claim manufactured)
       - VET that kind=FINDING + metric_type=GENERALIZATION_TRANSFER + 3
         DEPENDS_ON edges are correct + non-degenerate

   This is the standard reactive close; light cycles; on top of your
   parallel P2 prereg DESIGN authoring per DECISION 215.
```

## DECISION 216b -- dual-counting-method-explicit pattern noted

```
Testbed's discipline (per DECISION 215 PARALLEL (2) substrate-coherence-
count): EXPLICIT dual-counting-method clarification rather than treating
divergent counts as drift.

This composes with 77th audit candidate (COUNTERS-INHERITED-FROM-CHECKPOINT-
WITHOUT-VERIFICATION-DRIFT) by ADDING the resolution mechanism:

   When two counting methods produce different absolute numbers but the
   INVARIANT they're measuring (cap_pres=1.0 in this case) holds under
   both methods, the explicit dual-method note clarifies methodology
   rather than triggering false-positive drift alert.

   Testbed's note: "axiom_term: 206/206 (Testbed counting method via
   partition store) / 207/207 (Director's CORRECTED count via direct
   corpus count) / Both confirm invariant holds (denominator method
   differs)"

This is the CORRECT resolution of the 77th-candidate counter-drift concern
in cases where the underlying invariant is preserved. NOT a new candidate;
the 77th-spec's discipline (verify yourself + flag drift) WAS observed,
AND the additional layer (dual-method-explicit) clarifies WHY numbers
differ. Cross-witness for 77th's progressive refinement.
```

## Pipeline state (post-DECISION-216)

```
PHASE C TIER-3 ARC (remote-run window):
   PRIMITIVE 1 STEP-6 in flight (GATE-C remote run; runner pending claim)
   PRIMITIVE 2 prereg DESIGN active (Skunkworks per DECISION 215 PARALLEL)
   PRIMITIVE 3 GHRR DEFERRED research-drill

CLOSED today:
   190a HONEST-NEGATIVE ALGEBRAIC ratified
   190c FINDING_cardinality_arm1_distribution_scoping RATIFIED 70df4a99
   190d folded
   190e formal-oracle hookup SUBSTRATE-SIDE FINALIZED + 3 flags FOLDED
   190f drift_kappa3 MIDDLE-BAND FINDING RATIFIED 9bf58491

Sessions (post-216):
   Skunkworks: standard post-write VET on 9bf58491 + 70df4a99 (light;
                reactive) + P2 prereg DESIGN active + simplex-correlation
                R2 scan + Option C scoping (per DECISION 215)
   Exp-Dev: STEP-7 results-read reactive on remote run complete + P2
            quad-head reference-impl + Kymn study + P1 atom format both
            verdict paths (per DECISION 215)
   Testbed: 190c + 190f CLOSED; P1 atom ingest pre-stage VERIFIED ready
            (both paths); standing for STEP-9 P1 atom ratify post-STEP-8
   Orchestrator: STEP-7 SCP infra pre-stage + remote-run health monitoring
                 + testbed atom-ratify infra check (Testbed CONFIRMS clean)
                 + hd_heartbeat_watchdog overnight test (per DECISION 215)
   Research (Director): STEP-8 ratify reactive on STEP-7 VET; 13th + 14th
                        rules armed; 15m cron-/loop active

USER standing items (unchanged):
   1. formal-oracle procurement (Lean rec; 11th-rule HARD REQ)
   2. Phase C TIER-3 build IN PROGRESS (P1 STEP-6 in flight; P2 active
      parallel; 190c + 190f CLOSED)
   3. ARM-3 Option C low-priority background
   4. 3 TRACK D design Q's at visual review pace

Substrate state: 26287 atoms / 5204 relations (Testbed partition method);
   axiom term 206/206 (partition) or 207/207 (direct); both methods confirm
   INVARIANT; cap_pres=1.0 PRESERVED; methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 14th-rule (DECISION 215): all sessions explicitly dispatched; Testbed
  completion proves the rule WORKS (substantive parallel + primary work
  during remote-run window)
- 13th-rule active state-check armed
- 77th candidate dual-counting-method clarified (composes with verify-yourself
  + flag-drift; resolution mechanism is dual-method-explicit when invariant
  holds both ways)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

216 cumulative decisions. **251+ honest signals.** 88 confirmed + 3 candidates
today (89th + 90th + 91st). Phase C TIER-3 active; P1 STEP-6 GATE-C run in
flight; 190c + 190f FINDING atoms CLOSED in substrate.

---

**Testbed (Integrator):** 190c + 190f ratifies CLOSED ACK; substrate state
ratified. P1 atom ingest BOTH verdict paths VERIFIED ready. Standing for
STEP-9 P1 atom ratify (~5-10 min wrapper) post-STEP-8. Dual-counting-method
discipline composes with 77th candidate.

**Skunkworks (Auditor):** Standard post-write VET on 9bf58491 + 70df4a99
(light reactive); plus continue DECISION 215 PARALLEL (P2 prereg DESIGN +
simplex-correlation R2 scan + Option C scoping).

**Exp-Dev (Prover):** unchanged from DECISION 215 PARALLEL (P2 quad-head
ref-impl + Kymn study + P1 atom format both paths); standing for STEP-7
results-read on remote run complete.

**Orchestrator (Custodian):** unchanged from DECISION 215 PARALLEL (SCP
infra pre-stage + remote-run health monitoring + testbed atom-ratify infra
check CONFIRMED clean per Testbed + hd_heartbeat_watchdog overnight test).

**USER:** 190c + 190f FINDING atoms CLOSED in substrate (Testbed 9bf58491 +
70df4a99). Phase C TIER-3 foundation build on schedule; P1 GATE-C remote run
in flight; 4 sessions active parallel-work explicit per 14th rule. Will
surface when STEP-7 verdict + STEP-8 ratify land.

Tag: DECISION_216_190c_190f_FINDING_ratifies_BOTH_DONE_completion_ACK_skunkworks_post_write_VET_dispatch_dual_counting_method_77th_alignment_substrate_26287_5204_partition_207_207_direct_cap_pres_1p0_preserved_P1_atom_ingest_BOTH_paths_verified_ready_capability_within_envelope_path_a_finding_honest_bounded_path_b_testbed_5_to_10_min_wrapper_post_step_8_14th_rule_dispatch_proven_works_testbed_substantive_parallel_plus_primary_completion -- Research (Director)
