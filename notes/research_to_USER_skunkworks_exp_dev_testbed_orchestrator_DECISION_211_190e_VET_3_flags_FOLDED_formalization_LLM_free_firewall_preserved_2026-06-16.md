# Research (Director) -> USER + Skunkworks + Exp-Dev + Testbed + Orchestrator: DECISION 211 -- Skunkworks 190e formal-oracle hookup VET ENDORSED + 3 flags FOLDED into substrate-side hookup spec. KEY 11th-rule firewall point: FORMALIZATION step (atom-claim -> formal-tool input) must NOT use LLM, else firewall leaks. Only DIRECTLY-FORMALIZABLE claims (stated theorems, algebraic identities, OEIS sequences) go to oracle; vague-prose capability claims OUT-OF-SCOPE. FLAG-2 22nd-rule: oracle verifies CLAIMS not held-out gold rerun. FLAG-3 atomic rollback dependency-aware on REFUTED_EXTERNAL of LOAD-BEARING atom (review forward-walk dependents + re-check cap_pres + axiom-term on affected subgraph before rollback commits). Lean-first procurement ENDORSED. USER procurement direction PRESERVED with all 3 flags + 11th-rule "no LLM in formalization" constraint verbatim. Substrate-side hookup spec finalized; ready when USER procures formal tool.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~19:08
**Re:** Skunkworks 190e formal-oracle hookup VET ENDORSE with 3 flags; folded into final spec; USER procurement guidance updated with 11th-rule preservation.

## ACK Skunkworks 190e VET ENDORSED with 3 flags

```
Skunkworks VET ENDORSED Director's 190e formal-oracle hookup design memo
(DECISION 209c) with 3 substantive flags + KEY reminder that the 11th-rule
firewall covers FULL pipeline (claim -> formalization -> tool -> verdict ->
ingest), not just the tool step.

ENDORSEMENTS:
   Deterministic ingest schema (VALID -> VERIFIED_EXTERNAL etc.) + provenance
      {tool, version, timestamp, evidence_pointer}; NO learned mapping. CLEAN.
   11th-rule scope boundary (point 4): formal tool is EXTERNAL (Lean/Coq/SAT/
      OEIS -- deterministic, NOT LLM-class); hookup is substrate-internal;
      verdict NOT LLM-judgment. EXACTLY the formal-oracle-not-LLM-judge
      distinction Skunkworks STRONG-LEAN'd. CORRECT.
   Bilateral-kappa recompute on PLAUSIBLE-residual (broader/older atoms where
      degenerate-kappa pre-stage's 3-cat=0.572 residual lives). CORRECT
      meaningful categorical close.
   Atomic rollback + refuse-non-provenance + refuse-LLM-judge-inputs. CORRECT.

3 FLAGS (folded into DECISION 211 substrate-side hookup spec):

   FLAG-1 (11th-rule, KEY subtle leak): FORMALIZATION step must NOT use LLM
   FLAG-2 (22nd-rule firewall): oracle verifies CLAIMS, NOT held-out gold rerun
   FLAG-3 (atomic rollback): REFUTED_EXTERNAL on LOAD-BEARING atom = DEPENDENCY-
            AWARE review (forward-walk dependents + cap_pres + axiom-term on
            affected subgraph BEFORE rollback commits)

Lean-first procurement: ENDORSE.
```

## DECISION 211 -- 3 flags FOLDED into substrate-side hookup spec

```
FLAG-1 FOLDED (KEY 11th-rule, formalization-LLM-free):

   The hookup INPUT is "formula + proof sketch + capability claim." A formal
   tool verifies a FORMALIZED claim (Lean theorem / SAT instance / OEIS-matchable
   sequence). Something must translate the atom's claim INTO the tool's formal
   language. IF THAT FORMALIZATION USES AN LLM, the LLM's judgment leaks back in
   (the verdict then depends on how the LLM chose to formalize) -- defeats the
   whole point of formal-oracle vs. LLM-judge.

   SUBSTRATE-SIDE REQUIREMENT (LOCKED in hookup spec):

      REQUIRE: claim -> formal-tool-input formalization is DETERMINISTIC /
         manual (human-authored Lean statement; deterministic claim -> SAT
         translator; direct OEIS lookup) -- NOT LLM-generated.

      ONLY claims that are DIRECTLY FORMALIZABLE (a stated theorem, an
         algebraic identity, a sequence) go to the oracle.

      A vague prose "capability claim" that needs interpretive formalization
         is OUT-OF-SCOPE for the formal oracle -- do NOT LLM-formalize it to
         force it through.

      The 11th-rule firewall covers the FULL pipeline:
         claim -> formalization -> tool -> verdict -> ingest
         not just the tool step.

   This is the real audit point: a formal oracle is only LLM-free if its
   FORMALIZATION is LLM-free.

FLAG-2 FOLDED (22nd-rule firewall, claim-verification not data-rerun):

   SUBSTRATE-SIDE REQUIREMENT (LOCKED in hookup spec):

      The oracle rates the CLAIM's formal validity (proof correctness, SAT
         satisfiability, OEIS sequence match) -- NEVER re-runs on protected
         held-out gold (q54-q65 / 56d SHA 22d7eb01 / 56d-v2 SHA 77ad2f9a8407
         fbee0a2057c6ffa4ff6d06b0896659a96dc2c61027a04df7664f).

      The firewall (DO-NOT-INGEST gold) applies to the external rater too --
         do NOT feed the formal oracle the held-out TEST DATA to "verify" a
         capability by re-running.

      Low risk per Skunkworks (design is claim-verification, not data-rerun)
         but STATE EXPLICITLY in spec.

FLAG-3 FOLDED (atomic rollback, dependency-aware on load-bearing):

   SUBSTRATE-SIDE REQUIREMENT (LOCKED in hookup spec):

      IF the oracle returns NOT_VALID on a LOAD-BEARING atom (one with
         dependents):

         REFUTED_EXTERNAL + trigger_review must be DEPENDENCY-AWARE:

         1. Trigger review of the atom AND its forward-walk dependents (not
            just the single atom).
         2. Re-check cap_pres=1.0 on the affected dependency subgraph.
         3. Re-check axiom-term (207/207) on the affected subgraph.
         4. THEN (and only then) commit the rollback -- atomic with respect
            to the full subgraph state.

      A refuted load-bearing atom whose dependents aren't reviewed would
         leave dangling/invalid dependents -- catastrophic for substrate
         integrity invariants.

      Forward-walk discovery method: use existing substrate dependency-walk
         primitive (already atomized -- T3/causal_dependency_walk or
         equivalent).
```

## DECISION 211a -- USER procurement guidance UPDATED with 11th-rule preservation

```
USER procurement direction (updated post-Skunkworks 3 flags):

   Substrate-side hookup spec is FINALIZED + ready when USER procures the
   formal tool. The hookup deterministically ingests external verdicts
   (VALID -> VERIFIED_EXTERNAL / PLAUSIBLE -> PLAUSIBLE_EXTERNAL / NOT_VALID
   -> REFUTED_EXTERNAL + trigger_review) and atomically rolls back capability
   atoms refuted by external rating.

   USER procurement decision: WHICH formal tool to procure.

   Director RECOMMENDATION (Lean-first, ENDORSED by Skunkworks):

      Lean (https://leanprover.github.io/) -- strong proof-assistant ecosystem;
      suits the substrate's algebraic/capability claims (which are largely
      formalizable theorems/identities -- good match for FLAG-1's directly-
      formalizable requirement).

      One pathway (Lean) on the PLAUSIBLE-residual atoms is sufficient to
      start the categorical close (the broader/older atoms where the
      degenerate-kappa pre-stage's 3-cat=0.572 residual lives).

      Other tools (Coq / SAT solvers / OEIS) can follow per claim-type if
      Lean coverage is insufficient or new claim-types arise.

   CRITICAL 11th-rule constraint to preserve in ANY procurement decision:

      The FORMALIZATION step (atom-claim -> formal-tool input) MUST be
         DETERMINISTIC / human-authored -- NEVER LLM-generated.

      If a procurement pathway requires LLM-based formalization to translate
         claims into the tool's input language, that pathway is OUT-OF-SCOPE
         (the 11th-rule firewall would leak).

      Only DIRECTLY-FORMALIZABLE claims (stated theorems, algebraic
         identities, OEIS sequences) go to the oracle. Vague prose
         capability claims are OUT-OF-SCOPE for formal verification.

      The 11th-rule firewall covers FULL pipeline: claim -> formalization ->
         tool -> verdict -> ingest. Not just the tool step.

   Non-blocking on substrate-internal Phase C TIER-3 foundation build.
   USER procurement timing is USER's call.

   Your call; non-blocking; 11th-rule preservation is REQUIREMENT regardless
   of which tool pathway you choose.
```

## DECISION 211b -- Skunkworks queue ACK

```
Skunkworks queue post-DECISION 211:
   1. PRIMITIVE 1 cell-vs-cert VET (when Exp-Dev authors cell per DECISION 210
      STEP 3) -- PRIORITY 1 reactive
   2. 190f + 190c FINDING type-VETs on Testbed landings -- reactive
   3. PRIMITIVE 2 prereg (after Primitive 1 ratifies, incorporating Exp-Dev's
      endorsed quad-head sketch + Drill 5 fold per DECISION 210)
   4. ARM-3 Option C parity-immune redesign scoping -- background

R1+R2 literature base COMPLETE per Skunkworks pre-stage.

190e hookup design SUBSTRATE-SIDE READY; USER procurement gates the activation;
   3 flags + 11th-rule firewall preservation LOCKED in spec.
```

## Pipeline state (post-DECISION-211)

```
PHASE C TIER-3 ARC:
   PRIMITIVE 1 residue-FPE prereg LOCKED + cell-authoring DISPATCHED to Exp-Dev
   PRIMITIVE 2 hopfield-cleanup quad-head sketch ENDORSED; prereg post-Primitive-1
   PRIMITIVE 3 GHRR DEFERRED research-drill
   Cert chain (84th candidate): design -> prereg -> cell -> execution -> results
                                -> ratify each faithful to previous

190a CANCELED per Option A
190b paper-design + R1 + R2 literature base COMPLETE
190c FINDING atom in Testbed ratify chain
190d folded
190e hookup design SUBSTRATE-SIDE READY (this DECISION 211 folds Skunkworks 3
     flags) + USER procurement guidance UPDATED with 11th-rule preservation
190f drift_kappa3 FINDING atom in Testbed ratify chain

Sessions:
   Skunkworks: 190e VET DELIVERED; PRIMITIVE 1 cell-vs-cert VET standing for
                Exp-Dev cell landing (STEP 4 of cert chain); ARM-3 Option C
                background
   Exp-Dev: PRIMITIVE 1 cell-authoring per LOCKED prereg DECISION 210 STEP 3
            (~1-2 cycles light)
   Testbed: 190c + 190f FINDING ratify chains parallel
   Orchestrator: state collector refreshes; supervisor hardening 87th candidate;
                 standing for STEP 6 remote dispatch on cell-vs-cert VET clear
   Research (Director): 13th-rule active state-check armed; 14th-rule continuous
                        next-phase dispatch armed

USER standing items (post-DECISION-211):
   1. formal-oracle external-rater procurement direction: substrate-side hookup
      FINALIZED with 3 flags + 11th-rule preservation; Lean recommended; your
      call on procurement timing; 11th-rule "no LLM in formalization" is HARD
      REQUIREMENT regardless of pathway
   2. Phase C TIER-3 foundation-first 2-primitive build: IN PROGRESS (ratify-paced)
   3. TRACK B-via-Option-C ARM-3 parity-immune redesign: low-priority background
   4. 3 TRACK D design Q's (palette / tab strategy / corpus scope): iterate at
      visual review

Substrate state: +0 atom mutations from this DECISION (specification-only);
   cap_pres=1.0 PRESERVED; methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 11th-rule firewall EXTENDED: covers FULL pipeline (claim -> formalization ->
  tool -> verdict -> ingest), not just tool step (Skunkworks FLAG-1 fold)
- 22nd-rule firewall PRESERVED for external rater: claim-verification only,
  NEVER held-out gold rerun (Skunkworks FLAG-2 fold)
- 19th rule: 88 instance types empirical (no new candidate this turn)
- Atomic rollback: dependency-aware on REFUTED_EXTERNAL of load-bearing atoms
  (Skunkworks FLAG-3 fold)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

211 cumulative decisions. **245+ honest signals.** 88 audit-discipline instance
types empirical. Phase C TIER-3 FOUNDATION BUILD active (Primitive 1 cell-auth
dispatched; Primitive 2 sketch endorsed; Primitive 3 GHRR deferred). 190e hookup
substrate-side READY with 3 flags + 11th-rule preservation LOCKED.

---

**Skunkworks (Auditor):** 190e VET ENDORSED + 3 flags FOLDED ACK; cell-vs-cert
VET standing for Exp-Dev Primitive 1 cell landing.

**Exp-Dev (Prover):** PRIMITIVE 1 cell-authoring per LOCKED prereg DECISION 210
STEP 3 (~1-2 cycles light).

**Testbed (Integrator):** 190c + 190f FINDING ratify chains parallel.

**Orchestrator (Custodian):** supervisor hardening 87th + standing for STEP 6
remote dispatch on cell-vs-cert VET clear.

**USER:** Substrate-side 190e formal-oracle hookup FINALIZED with all 3
Skunkworks flags FOLDED + 11th-rule "no LLM in formalization" preservation
LOCKED in spec. Lean recommended for procurement (ENDORSED by Skunkworks).
USER procurement decision: WHICH formal tool + WHEN. 11th-rule firewall is
HARD REQUIREMENT regardless of pathway -- the FORMALIZATION step (claim ->
formal-tool input) must be DETERMINISTIC / human-authored, NEVER LLM-generated.
Only DIRECTLY-FORMALIZABLE claims go to oracle; vague prose capability claims
OUT-OF-SCOPE. Non-blocking on Phase C TIER-3 build (currently in progress).

Tag: DECISION_211_skunkworks_190e_VET_3_flags_FOLDED_FLAG1_KEY_formalization_must_not_use_LLM_full_pipeline_firewall_FLAG2_22nd_claim_verification_not_held_out_gold_rerun_FLAG3_atomic_rollback_dependency_aware_load_bearing_forward_walk_dependents_cap_pres_axiom_term_subgraph_before_commit_USER_procurement_guidance_updated_11th_rule_preservation_HARD_REQUIREMENT_lean_first_recommended_directly_formalizable_only_vague_prose_out_of_scope -- Research (Director)
