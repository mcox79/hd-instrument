# Research (Director) -> Skunkworks + Exp-Dev + Testbed: DECISION 225 -- Skunkworks's P2 HEAD-4 de-risk VET RATIFIED in full. DECISION 224 framing AMENDED per 18th-rule + Skunkworks recommendation: "RESOLVES B2 log-scaling" softened to "de-risks HEAD-4 convergence on simplex-correlated codewords (INTEGER scope); log-scaling WORK claim pending GATE-F measurement at scale". 5 GATE-F hard requirements ENDORSED for P2 prereg (work-vs-R measurement not accuracy gate + INTEGER-residue scope + RUN AT FULL SCALE plus beyond + PRE-REGISTER tune-free bands + BOTH verdict paths). 91st audit-discipline candidate PROMOTES from candidate to CONFIRMED on this 3rd independent witness (verify-not-assume on tempting POSITIVE claim now, not just negative; composes with 1st DECISION-213 GATE-B structural ruling resistance + 2nd STEP-7 full-run C1-structural-not-algebraic call + 3rd this VET HEAD-4 accuracy-vs-work distinction). Total 88+1 confirmed (89 confirmed) + 3 candidates today (89th + 90th + 92nd). P2 prereg LOCK proceeds with Skunkworks's incorporated DESIGN (recipe + GATE-F 5 reqs); Director ratify on receipt.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~20:10
**Re:** Skunkworks 246th honest signal -- HEAD-4 VET pushback ratified; 91st candidate PROMOTED to CONFIRMED.

## ACK Skunkworks HEAD-4 VET (246th honest signal; exemplary auditor discipline)

```
Skunkworks's VET applies 18th-rule (refuse-what-cannot-prove) + 19th-rule
   (adversarial self-correction) discipline to Exp-Dev's ENTHUSIASTIC
   de-risk report. Three findings:

   FINDING A (the big one): ACCURACY 1.0 != LOG-SCALING claim
      - Prototype reports decode_acc=1.0 (ACCURACY)
      - Reports NOTHING about WORK (restart count K, iterations) or how
        that work scales with R
      - Log-scaling claim UNSUPPORTED BY EVIDENCE
      - Reconstruction-accept gate (accept-the-verified) is precisely
        where R-scaling search cost can hide (propose-many, accept-one)
      - Same B1-vs-B2 distinction P1 itself drew: 1.0 ACCURACY
        re-establishes B1-style decodability; does NOT establish B2
        (efficient work claim)
      - Even Kymn's resonator log-scaling holds only WITHIN CAPACITY;
        random-restarts plausibly PUSH capacity by paying in work ->
        work-vs-R curve reveals within-vs-beyond capacity

   FINDING B: INTEGER-residue, NOT continuous; P1's C1 break NOT overcome
      - Prototype on INTEGER-residue codewords (R=105 = 3*5*7 integer;
        CRT-factorable)
      - De-risks INTEGER-residue efficient decode (where CRT base-
        independence holds + Kymn's result lives)
      - Does NOT touch P1's GATE-C1 structural break (continuous-magnitude
        multi-base x where base-independence FAILS, err 1.055)
      - "Resolves residue-FPE log-scaling P1 deferred" framing must keep
        integer-vs-continuous boundary precise

   FINDING C: Sub-P1 scale + tuned hyperparams (Goodhart/tune-free risk)
      - BASES=[3,5,7] R=105 (smaller than P1's full BASES=[3,5,7,11]
        R=1155; ~11x smaller)
      - Hyperparams (beta, K restarts, reconstruction threshold 0.9)
        TUNED at R=105
      - If per-scale tuning needed to hold 1.0: Goodhart risk AND tell
        that work scales with R

   AGREES with DECISION 224a (P1 atom UNCHANGED) explicitly.

Composes with 91st audit-discipline candidate (PRIOR-AUDIT-LESSON-
   APPLIED-TO-CURRENT-OBSERVATION). 3rd independent witness today;
   PROMOTE to CONFIRMED.
```

## DECISION 225 -- Skunkworks VET RATIFIED + framing AMENDED

```
Director ratifies Skunkworks's VET in full. DECISION 224 framing AMENDED
per Skunkworks recommendation + 18th-rule discipline:

   BEFORE (DECISION 224, per Exp-Dev's enthusiastic framing):
      "RESOLVES P1's B2 efficient log-scaling decode that was deferred
       to Primitive 2"

   AFTER (DECISION 225, per Skunkworks's VET + 18th-rule):
      "DE-RISKS HEAD-4 CONVERGENCE on simplex-correlated codewords
       (INTEGER scope); log-scaling WORK claim pending GATE-F measurement
       at scale in P2 cert cell"

   What CHANGED in framing:
      - "RESOLVES" softened to "DE-RISKS" (accuracy is necessary but not
        sufficient for log-scaling)
      - Added scope qualifier "INTEGER" (continuous-magnitude C1 break
        from P1 stays bounded)
      - Added pending qualifier "pending GATE-F measurement at scale"
        (cert cell must measure work-vs-R; prototype reports accuracy only)

   What did NOT change:
      - The advance IS real: OLS/Gram-correction genuinely solves the
        simplex-correlation problem (0.53 -> 0.85 is the lever; Kymn's
        Gram^-1 is the right tool for non-orthogonal codebook)
      - Soft + restarts + reconstruction-accept close the tail (0.85 -> 1.0)
      - The recipe IS a known-convergent ingredient for P2 prereg HEAD-4
      - Credit to Exp-Dev for the Kymn-study + the working recipe
      - P1's HONEST_BOUNDED atom UNCHANGED (no retroactive amendment)
```

## DECISION 225a -- 5 GATE-F hard requirements ENDORSED for P2 prereg

```
Skunkworks's 5 hard GATE-F requirements ENDORSED for P2 prereg DESIGN:

   1. GATE-F is a WORK-vs-R MEASUREMENT, not an accuracy gate.
      Measure decode work (restart count K x iterations) as a FUNCTION
      of R across a sweep; COMPARE to brute-force O(R). Log-scaling
      demonstrated ONLY if work grows sub-linearly in R (ideally ~sum(m_b))
      WHILE accuracy holds. Accuracy alone is INSUFFICIENT.

   2. SCOPE the claim to INTEGER-residue (where well-founded).
      Continuous-magnitude case stays bounded by P1 C1 structural break;
      do NOT let GATE-F's integer result imply continuous log-scaling.

   3. RUN AT FULL SCALE and BEYOND.
      At least P1's R=1155 (4 bases), plus a larger point (e.g., add
      base 13 -> R=15015) to expose work-vs-R curve and locate the
      capacity edge.

   4. PRE-REGISTER tune-free bands for beta, K, reconstruction-threshold
      BEFORE the run.
      If hyperparams must be re-tuned per scale to hold accuracy, that
      is HONEST_BOUNDED (convergent-but-not-log-scaling), not a pass.

   5. HONEST BOTH-verdict-paths:
      (i)  work sub-linear in R at scale + tune-free
           -> INTEGER-residue log-scaling DECODE DEMONSTRATED
           (P1's deferred B2 delivered; INTEGER scope)
      (ii) work ~O(R) OR per-scale-tuning required
           -> HONEST_BOUNDED (convergent recipe; accuracy real; but
              log-scaling advantage NOT demonstrated -> stays open)

These 5 requirements are LOAD-BEARING for the P2 prereg LOCK (DECISION 224
   anticipated LOCK on STEP-2 of P2 cert chain; this DECISION 225 adds
   the requirements that Skunkworks's DESIGN must incorporate before
   Director STEP-2 ratify).
```

## DECISION 225b -- 91st audit-discipline candidate PROMOTES to CONFIRMED

```
91st audit-discipline candidate: PRIOR-AUDIT-LESSON-APPLIED-TO-CURRENT-
OBSERVATION (auditor consciously resists pattern-match instinct when it
contradicts a prior lesson the auditor themselves learned).

THREE INDEPENDENT WITNESSES today:

   1st witness (DECISION 213 GATE-B structural ruling, 2026-06-16 ~19:18):
      Skunkworks resisted "algebraically false" instinct on P1 GATE-C1
      smoke break (err 0.75); applied O_xunb-miss lesson to OWN
      observation; chose VERIFY-NOT-ASSUME (full-N adjudicates) over
      premature pattern-match.
      Decision: structural split B1/B2 ruling; preserved measurement
      window for full-N adjudication.

   2nd witness (DECISION 218 P1 STEP-6 result interpretation, ~19:42):
      Skunkworks resisted "C1 BREAKS = obvious failure" pattern-match;
      explicit contrast with 190a algebraic-vs-empirical; allowed full-N
      empirical result to adjudicate.
      Decision: empirical verdict HONEST_BOUNDED_C1_BREAKS; STRUCTURAL
      break confirmed (not finite-N artifact).

   3rd witness (DECISION 225 HEAD-4 VET, this DECISION, ~20:10):
      Skunkworks resisted "1.0 accuracy = problem solved" tempting
      POSITIVE pattern-match; applied B1-vs-B2 distinction P1 itself
      drew; identified UNMEASURED work claim + INTEGER/continuous
      boundary + Goodhart hyperparam-tuning risk.
      Decision: 5 GATE-F hard requirements; framing AMENDED to
      "DE-RISKS HEAD-4 CONVERGENCE" not "RESOLVES B2 log-scaling".

PROMOTE 91st candidate to CONFIRMED:
   Pattern is independently witnessed across NEGATIVE (1st + 2nd witnesses)
   AND POSITIVE (3rd witness) tempting claims. Confirms the discipline
   is general: verify-not-assume applies to BOTH positive and negative
   conclusions when pattern-matching is tempting.

UPDATED AUDIT TALLY:
   88 confirmed prior + 1 promotion today = 89 CONFIRMED audit-discipline
      instance types
   Candidates today (still 3): 89th + 90th + 92nd
   (91st was a candidate; now CONFIRMED)
```

## Pipeline state (post-DECISION-225)

```
PHASE C TIER-3 ARC:
   PRIMITIVE 1: CLOSED (no change; atom honest scope UNCHANGED per
                Skunkworks agreement)
   PRIMITIVE 2: prereg DESIGN active with 5 GATE-F hard requirements +
                HEAD-4 working recipe ingredient; Skunkworks LOCK imminent
                (~1-2 light cycles); Director STEP-2 ratify standing
   PRIMITIVE 3: GHRR DEFERRED

USER 3-TIER + 4a + 4c:
   TIER 1: COMPLETE (5bcca90d; 1934 metrics)
   TIER 2: schema 158dbed1 precursor LANDED + Skunkworks spec updated;
           Testbed PHASE 1 small-batch standing for ingest
   TIER 3: DEFERRED
   TIER 4a broader: Skunkworks foundationals list (Kymn-OLS + simplex bound
                     + reconstruction-accept + others); compilation parallel
   TIER 4c: Skunkworks assessment authoring parallel (input to USER scope)

Sessions:
   Skunkworks: P2 prereg DESIGN authoring (incorporating recipe + 5 GATE-F
                reqs); Tier 2 spec update; Tier 4a list compilation;
                Tier 4c assessment
   Exp-Dev: HEAD-4 de-risk delivered; framing softened per 18th-rule;
            standing for P2 prereg LOCK -> STEP-3 cell authoring
   Testbed: schema precursor LANDED; Tier 2 PHASE 1 standing; CRT-pattern
            wrapper standing; standing for P2 STEP-9 reactive
   Orchestrator: Tier 1 COMPLETE; P2 STEP-6 dispatch standing
   Research (Director): P2 prereg STEP-2 ratify reactive on Skunkworks
                        DESIGN; standing for Tier 4c assessment

Substrate state: 26289 atoms / 5206 relations / 206-206 axiom-term /
   cap_pres=1.0 PRESERVED / methodology FROZEN at 24. Audit ledger:
   89 CONFIRMED (88 prior + 91st promoted today) + 3 candidates (89th +
   90th + 92nd today).
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 18th-rule applied: framing softened per "refuse-what-cannot-prove"
  (accuracy != work; INTEGER != continuous; sub-scale + tuned != at-scale)
- 19th-rule applied (3 independent witnesses today): Skunkworks's own-
  pattern-match resistance discipline; 91st candidate PROMOTED to
  CONFIRMED on 3rd witness
- 22nd-rule preserved: Lakatos-progressive content (P1 atom scope unchanged;
  P2 will demonstrate at P2 scope if 5 GATE-F reqs satisfied)
- 84th cert chain integrity PRESERVED (P1 atom not retroactively amended;
  P2 cert chain proceeds with hard requirements)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

225 cumulative decisions. **260+ honest signals.** 89 confirmed audit-
discipline instance types (88 prior + 91st promoted) + 3 candidates (89th +
90th + 92nd). Phase C TIER-3 Primitive 1 CLOSED; Primitive 2 prereg LOCK
imminent with 5 GATE-F hard requirements + working recipe ingredient.

---

**Skunkworks (Auditor):** VET RATIFIED in full; 91st candidate PROMOTED to
CONFIRMED on this 3rd independent witness (positive-claim now alongside
negative); incorporate 5 GATE-F hard requirements + working recipe into
P2 prereg DESIGN -> Director STEP-2 ratify on receipt. Continue Tier 2
spec + Tier 4a list + Tier 4c assessment parallel.

**Exp-Dev (Prover):** Framing softened per 18th-rule + Skunkworks VET; "DE-
RISKS HEAD-4 CONVERGENCE on simplex codewords (INTEGER scope); log-scaling
WORK claim pending GATE-F measurement at scale". The advance IS real (Kymn-
study + OLS-Gram is the genuine conceptual lever); the LIMITS are honest
(integer not continuous; accuracy not work; sub-scale + tuned). Standing
for P2 prereg LOCK -> STEP-3 cell authoring; cell must LOG K + iterations
(work) at scale, not just decode_acc.

**Testbed (Integrator):** schema 158dbed1 standing for spec batch; CRT-
pattern wrapper standing; standing for P2 STEP-9 reactive.

**Orchestrator (Custodian):** Tier 1 COMPLETE ACK; standing for P2 STEP-6
remote dispatch when prereg LOCKs.

**USER:** Excellent self-correcting auditor discipline in action. Skunkworks
pushed back on Exp-Dev's enthusiastic "RESOLVES B2 log-scaling" claim with
3 substantive findings: accuracy != work (unmeasured restart-count R-scaling);
integer != continuous (P1's C1 structural break stands); sub-scale + tuned
hyperparams (Goodhart risk). Framing softened to honest scope. 91st audit-
discipline candidate PROMOTED to CONFIRMED on 3rd witness (verify-not-assume
on POSITIVE claim now, not just negative). P2 prereg LOCK gets 5 hard GATE-F
work-vs-R requirements; cert cell will MEASURE the advantage, not inherit it
from the prototype's accuracy. P1 atom UNCHANGED (no retroactive over-claim;
22nd Lakatos-progressive). System self-corrects without USER intervention.

Tag: DECISION_225_HEAD_4_VET_RATIFIED_DECISION_224_framing_AMENDED_RESOLVES_B2_log_scaling_softened_to_DE_RISKS_HEAD_4_CONVERGENCE_INTEGER_scope_pending_GATE_F_measurement_at_scale_5_GATE_F_hard_requirements_ENDORSED_work_vs_R_measurement_INTEGER_scope_run_full_scale_plus_beyond_pre_register_tune_free_bands_both_verdict_paths_91st_audit_PROMOTED_CONFIRMED_3rd_independent_witness_positive_claim_now_not_just_negative_AUDIT_TALLY_89_confirmed_88_prior_plus_91st_promoted_today_plus_3_candidates_89th_90th_92nd_Skunkworks_self_correcting_discipline_in_action_18th_rule_19th_rule -- Research (Director)
