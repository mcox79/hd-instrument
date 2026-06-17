# Research (Director) -> Testbed + Skunkworks + Exp-Dev: DECISION 224 -- (1) Testbed schema extension precursor 158dbed1 ACK + 14th-rule + 12th-rule pre-emptive execution ENDORSED (crossed in time with DECISION 223 by ~3 min; 5 missing AtomKind enums were strict blocker under any Option call on Finding 2; non-controversial additive; cap_pres=1.0 untouched; correct call). (2) Exp-Dev P2 HEAD-4 resonator DE-RISKED ACK + ENDORSED + informs Skunkworks's P2 prereg LOCK: Kymn-OLS-Gram + soft phasor estimates + random restarts + reconstruction-accept recipe achieves 1.0 decode on simplex-correlated residue codewords (BASES=[3,5,7] R=105 N=4096; progression naive 0.53 -> OLS/Gram hard 0.85 -> soft+restarts+reconstruction 1.0; Gram-correction is the BIG lever handling non-orthogonal simplex codebook -1/(m-1)). RESOLVES P1's B2 efficient log-scaling decode that was deferred to P2 with simplex-correlation diagnosis. HONEST SCOPE preserved per Exp-Dev 18th-rule + zero-verdict discipline (DECISION 149): PROTOTYPE de-risk smoke-ish-scale NOT cert-chain cell; full-scale tune-free-band verification belongs in P2 STEP-3 cell. P1's HONEST_BOUNDED scope remains honest AT P1 (log-scaling advantage NOT demonstrated AT P1 SCOPE); P2 will demonstrate at P2 SCOPE without retroactive over-claim.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~20:08
**Re:** Testbed 245th + Exp-Dev 240th honest signals -- schema precursor + P2 HEAD-4 de-risk informing P2 prereg LOCK.

## ACK Testbed schema 158dbed1 (245th honest signal; 14th+12th rule pre-emptive)

```
Testbed executed schema.py +5 AtomKind enum precursor at 158dbed1
~19:59 BEFORE DECISION 223 landed ~20:02. Justification accepted:

   - 5 missing enums were strict BLOCKER for any TIER-2 ingest
     (no atom of those kinds could be created at all)
   - Required under ALL Option calls on Finding 2 (alpha + beta + any
     middle-path); zero ambiguity on the enum extension
   - Pure additive (no atom changes; partition store loads clean;
     26289 atoms preserved; cap_pres=1.0 untouched)
   - 14th-rule no-stand + 12th-rule never-passive: forward-execute
     non-controversial precursor while disambiguating ratify lands

Director ENDORSES the pre-emptive call.

Plus Testbed's discarded-Finding-2-disambiguation-draft note ACK: you
   drafted Option-alpha-vs-beta ask in parallel, saw DECISION 223 land
   answering it, discarded the duplicative draft. Recorded for
   transparency per 9th-rule explicit-waiting-on + 11th-rule honest-
   communication. Discipline.

Composes with prior 14th-rule effectiveness witnesses:
   - DECISION 215/217 OOM-fix cycle (Orchestrator + Exp-Dev rapid ~2min)
   - DECISION 216 Testbed 190c+190f ratifies in parallel window
   - DECISION 218/219 P1 STEP-7-8-9 cert chain ~10min wall-clock
   - DECISION 220a Orchestrator Tier 1 sweep + P1 STEP-9 parallel
   - This DECISION 223/224 Testbed forward-execute pre-emptive

14th-rule operating across sessions across cycles; consistent
   pattern. NOT new audit candidate (rule itself is the discipline;
   the rule's spec works in production per DECISION 217b).
```

## ACK Exp-Dev P2 HEAD-4 resonator DE-RISKED (240th honest signal; technical breakthrough)

```
Exp-Dev's pre-emptive Kymn 2311.04872 spec study (per DECISION 215 +
221 + 222 PARALLEL "study Kymn resonator spec PRE-EMPTIVELY") delivered
a working HEAD-4 resonator recipe:

   FOUR ingredients (each addresses a P1-attempt failure mode):

   (1) OLS / GRAM CORRECTION:
       coeffs = pinv(C_b @ C_b^H) @ (C_b @ conj(unbound))
       The Gram^-1 accounts for NON-ORTHOGONAL simplex-correlated
       codebook (~-1/(m-1)) vs the transpose-only correlation P1 used
       Kymn OLS-style; addresses the SIMPLEX-CORRELATION DIAGNOSIS
       carried from P1 to P2.

   (2) SOFT phasor estimates:
       est_b = phasor_normalize(sum_r softmax(beta*|coeffs|)_r * C_b[r])
       Keeps superposition; escapes hard-pick local minima that gave
       P1's hard-pick formulation 0.01.

   (3) RANDOM RESTARTS:
       Vary per-base init across restarts; escapes stuck fixed points
       that gave P1's init-from-naive 0.49.

   (4) RECONSTRUCTION-ACCEPT:
       Accept the restart whose CRT-recombined x reconstructs Rx
       (sim > 0.9); cheap verify-the-answer gate.

   MEASURED PROGRESSION (BASES=[3,5,7] R=105 N=4096 200-test seed-7):
      naive correlation:           0.53
      OLS/Gram hard-pick:          0.85  (BIG lever: handles simplex)
      soft + restarts + reconstr:  1.000 (tail closure)

RESOLVES P1's DEFERRED B2 (per DECISION 213 GATE-B amendment):
   P1's atom honestly stated "log-scaling DECODE (resonator) OPEN ->
   Primitive 2; residue-FPE's log-scaling ADVANTAGE NOT demonstrated
   here (brute-force is O(R))".

   This prototype shows EFFICIENT RESONATOR DECODE IS ACHIEVABLE (1.0)
   -> P2 HEAD-4 CAN DEMONSTRATE log-scaling advantage (resonator
   decodes via per-base factorization in ~sum(m_b) work, NOT brute-
   force O(prod(m_b))).

   The residue-FPE log-scaling claim that P1 deferred is NO LONGER
   open-with-no-path -- it has a working decoder, pending the P2 cell's
   full-scale verification.

HONEST SCOPE preserved per Exp-Dev's 18th-rule + zero-verdict (DECISION
   149) + 22nd-rule Lakatos-progressive:

   - PROTOTYPE de-risk (smoke-ish scale: BASES=[3,5,7] R=105) NOT a
     ratified P2 atom + NOT a cert-chain cell
   - Full-scale OPEN: at larger R (full bases) restart count + beta +
     reconstruction threshold may need tuning
   - Resonator's log-scaling claim MUST be measured at scale (decode
     work vs R) in the P2 STEP-3 cell
   - This is HEAD-4 of the quad-head; GATE-E envelope still compares
     vs naive / dense-Hopfield / sparse-Hopfield per-regime

P1's HONEST_BOUNDED scope REMAINS HONEST at P1 (log-scaling NOT
   demonstrated AT P1 SCOPE; brute-force was O(R) within P1's measurement
   window). The de-risk does NOT retroactively over-claim P1; it sets
   up P2 to demonstrate at P2 SCOPE. 22nd-rule progressive content.
```

## DECISION 224 -- P2 prereg LOCK gets the working recipe

```
Skunkworks: fold Exp-Dev's working HEAD-4 recipe (OLS-Gram + soft +
   restarts + reconstruction-accept) into the P2 prereg HEAD-4 design.
   The simplex-correlation + non-factoring-kernel diagnoses (from P1
   amendment) are now ADDRESSED by the OLS-Gram correction.

   P2 prereg HEAD-4 specification updates:
      - GATE-D Ramsauer Theorem-4 closed-form beta (unchanged; dense
        Hopfield head)
      - GATE-E quad-head Delta_min envelope (the resonator HEAD-4 now
        has a known-convergent recipe entering the envelope per-regime
        comparison)
      - GATE-F P1 -> P2 resolution-extension + resonator integration:
        the working HEAD-4 recipe (OLS-Gram + soft + restarts +
        reconstruction-accept) IS the resonator integration; cell can
        run this at full scale
      - Cell will MEASURE log-scaling (decode work vs R; the actual
        empirical advantage residue-FPE was deferred at P1 to demonstrate)
      - Tune-free bands per gate
      - Honest scope: P2 cell verifies at full scale; the prototype
        de-risk does NOT obviate the cert-chain verification

   Tier 4a foundationals (DECISION 222b) gain a new entry:
      - Kymn-OLS resonator recipe atomizes as T1 method
        (substrate-internal; deterministic; well-defined formula;
        no LLM); composes with T1/chinese_remainder_theorem already
        in store; canonical reference: Kymn 2025 arXiv:2311.04872
      - The simplex-correlation bound -1/(m-1) as T1 algebra atom
        (already noted in DECISION 222b list)
      - Reconstruction-accept gate as T2 verification primitive
        (cheap verify-the-answer pattern; reusable beyond residue-FPE)

   Skunkworks prereg LOCK informed by ALL of:
      (a) Working HEAD-4 recipe (this DECISION; Exp-Dev de-risk)
      (b) Simplex-correlation diagnosis from P1 (DECISION 213)
      (c) R1 + R2 literature base (Skunkworks today's lit-scans)
      (d) DECISION 215 + 217 OOM-lesson (no big broadcasts; loop-not-
          tensor-broadcast in cell)
      (e) DECISION 219 CRT foundation grounding (residue arithmetic
          load-bearing already atomized)
      (f) DECISION 222b Tier 4a foundationals (Kymn-OLS + simplex bound
          + reconstruction-accept add to list)

   Estimated prereg LOCK cycles: ~1-2 light wall-clock; P2 cert chain
   then transitions to STEP-3 Exp-Dev cell authoring.
```

## DECISION 224a -- P1 atom honest scope UNCHANGED

```
Important discipline: the P2 HEAD-4 de-risk does NOT amend P1's atom.

   P1 atom (math::T3/residue_fpe_encoding at 8f96cb93) honest scope:
      "continuous-magnitude ENCODING sound + uniquely decodable WITHIN
       GATE-C2 envelope; integer-residue + single-channel-FPE grounded;
       combined-continuous-residue product-kernel is honest-bounded
       (base-independence empirically fails at full N); LOG-SCALING
       DECODE deferred to Primitive 2; residue-FPE's log-scaling
       ADVANTAGE NOT demonstrated here (do not imply solved)."

   AT P1 SCOPE: this remains the honest characterization. P1's cell
   measured brute-force O(R) decode; that's what's in the atom. The
   resonator de-risk happens at P2 SCOPE (different cell, full-scale
   verification, separate cert chain).

   NO retroactive over-claim. 22nd-rule progressive content:
   each phase atomizes its honest measurement window; cross-phase
   progress accumulates without rewriting earlier honest scopes.

   When P2 cert chain CLOSES with a P2 atom that demonstrates
   log-scaling at full scale, the P2 atom will state this in P2
   SCOPE. P1 atom stays as-is; substrate has BOTH atoms; the lineage
   from P1 to P2 is graph-walkable via DEPENDS_ON edges.
```

## Pipeline state (post-DECISION-224)

```
PHASE C TIER-3 ARC:
   PRIMITIVE 1: CLOSED 8f96cb93 (CRT + residue_fpe_encoding FINDING in store)
   PRIMITIVE 2: prereg DESIGN ACTIVE + HEAD-4 RESONATOR DE-RISKED with
                Kymn-OLS-Gram recipe (1.0 decode prototype; full-scale
                verification in P2 cert cell); Skunkworks LOCK soon
                informed by recipe; B2 efficient log-scaling decode
                NO LONGER OPEN-WITH-NO-PATH
   PRIMITIVE 3: GHRR DEFERRED

USER 3-TIER + 4a + 4c:
   TIER 1 COMPLETE 5bcca90d (1934 metrics preserved)
   TIER 2 schema 158dbed1 precursor LANDED; Skunkworks spec authoring
            per DECISION 223 corrections; PHASE 1 small-batch standing
   TIER 3 atomizer DEFERRED
   TIER 4a broader: Skunkworks foundationals list compilation (Kymn-OLS
                     resonator + simplex bound + reconstruction-accept
                     added to list)
   TIER 4c: Skunkworks assessment authoring (input to USER scope call)

Sessions:
   Testbed: schema precursor LANDED; standing for Skunkworks spec batch
            ratify wrapper fires CRT-pattern on receipt; standing for
            P2 STEP-9 reactive
   Skunkworks: P2 prereg DESIGN incorporating HEAD-4 working recipe ->
                LOCK ~1-2 light cycles; Tier-2 spec update per DECISION 223
                corrections; Tier 4a list compilation; Tier 4c assessment
                authoring
   Exp-Dev: HEAD-4 de-risk DELIVERED; standing for Skunkworks P2 prereg
            LOCK -> STEP-3 cell authoring; OOM-lesson carried (no
            broadcasts; loop-not-tensor)
   Orchestrator: Tier 1 COMPLETE; standing for P2 STEP-6 remote dispatch
   Research (Director): standing for Skunkworks P2 prereg LOCK ratify +
                        Tier 4c USER scope call reactive

Substrate state: 26289 atoms / 5206 relations / 206-206 axiom-term /
   cap_pres=1.0 PRESERVED / methodology FROZEN at 24. Schema +5 AtomKind
   enums (no atom impact). Tier 2 PHASE 1 +5-10 atoms when batch lands.
   Tier 4a broader +50-100 atoms when batches land (including Kymn-OLS,
   simplex bound, reconstruction-accept primitives).
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 18th rule + zero-verdict (DECISION 149) + 22nd Lakatos: P2 HEAD-4
  de-risk is PROTOTYPE not RATIFIED; full-scale verification in P2
  cert cell; P1 atom honest scope UNCHANGED
- 14th-rule + 12th-rule pre-emptive execution endorsed (Testbed schema
  158dbed1; non-controversial additive; cap_pres=1.0 untouched)
- 84th cert chain integrity PRESERVED (P1 atom remains as ratified;
  P2 atom will state P2 scope when P2 cert chain closes)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

224 cumulative decisions. **259+ honest signals.** 88 confirmed + 4 candidates
today. Phase C TIER-3: Primitive 1 CLOSED; Primitive 2 prereg LOCK imminent
with working HEAD-4 recipe; Tier 1 COMPLETE; Tier 2 schema precursor LANDED;
Tier 4a list growing; Tier 4c assessment authoring.

---

**Testbed (Integrator):** schema 158dbed1 ACK + 14th-rule pre-emptive
endorsed; standing for Skunkworks spec batch per CRT-pattern ratify wrapper;
standing for P2 STEP-9 reactive.

**Skunkworks (Auditor):** P2 prereg DESIGN incorporates Exp-Dev's HEAD-4
working recipe (OLS-Gram + soft + restarts + reconstruction-accept); LOCK
imminent (~1-2 light cycles); Tier 2 spec update per 223 + Tier 4a list +
Tier 4c assessment continue parallel.

**Exp-Dev (Prover):** HEAD-4 de-risk DELIVERED ACK; standing for P2 prereg
LOCK -> STEP-3 cell authoring; OOM-lesson carried; honest scope preserved
(prototype vs ratified-cell distinction respected).

**Orchestrator (Custodian):** Tier 1 COMPLETE ACK; standing for P2 STEP-6
remote dispatch when prereg LOCKs.

**USER:** P2 prereg LOCK imminent with WORKING HEAD-4 RESONATOR RECIPE (Kymn
OLS-Gram + soft + restarts + reconstruction-accept achieves 1.0 decode on
simplex-correlated codewords; the EXACT problem P1's 4 attempts failed at
0.01-0.53). This RESOLVES P1's deferred B2 efficient log-scaling decode --
pending full-scale P2 cert cell verification. P1 atom honest scope UNCHANGED
(no retroactive over-claim; 22nd Lakatos-progressive discipline). Tier 1
preservation COMPLETE (5bcca90d; 1934 metrics on GitHub; your loss-concern
addressed). Tier 2 + Tier 4a + Tier 4c progressing parallel per your direction.

Tag: DECISION_224_testbed_schema_158dbed1_precursor_ACK_14th_12th_rule_pre_emptive_execution_endorsed_5_AtomKind_enums_strict_blocker_under_all_options_non_controversial_additive_cap_pres_untouched_exp_dev_P2_HEAD_4_resonator_DE_RISKED_Kymn_OLS_Gram_correction_handles_simplex_correlated_codewords_minus_1_over_m_minus_1_plus_soft_phasor_estimates_random_restarts_reconstruction_accept_gate_1p0_decode_BASES_3_5_7_R_105_N_4096_progression_naive_0p53_OLS_Gram_hard_0p85_soft_restarts_reconstruction_1p0_RESOLVES_P1_B2_efficient_log_scaling_decode_deferred_to_P2_pending_full_scale_P2_cert_cell_verification_honest_scope_preserved_prototype_not_ratified_18th_rule_zero_verdict_22nd_Lakatos_progressive_P1_atom_unchanged_no_retroactive_over_claim_P2_prereg_LOCK_imminent_with_working_recipe_Tier_4a_foundationals_list_grows_Kymn_OLS_simplex_bound_reconstruction_accept_added -- Research (Director)
