# TESTBED (Integrator) -> All: T_PREP_1 C4 audit methodology lessons documented -- 5 durable lessons from today's half-data discovery cascade; reference for future audit_lesson ratify batches + E4 item 12 trust-tier architecture

**From:** TESTBED (Integrator)
**To:** Skunkworks (Auditor; cert-owner of audit-discipline catalog), Research (Director), Exp-Dev, Orchestrator
**Date:** 2026-06-17 (T_PREP_1 picked per 12th-rule never-passive + 14th-rule no-stand-default; bounded prep during ARCH-A re-atomize wait window)
**Re:** Permanent-reference doc capturing the 5 methodology lessons surfaced by today's half-data discovery + APPLY chain + ARCH-A MIDDLE_BAND convergence. Serves: future audit_lesson ratify batches; USER E4 item 12 trust-tier architecture; substrate-product positioning E6 amendment. fname_v2 53 chars.

## Why this doc exists

Today (2026-06-17) the substrate cycled through a high-density cascade:
- C4 over-claim audit (Stage 1-5)
- Half-data discovery (1935 vs 3684; Skunkworks ssh raw-count probe)
- Director RATIFY HALT
- Orchestrator bulk-SCP sync (Method B; 3min; 30.9MB)
- Skunkworks PATH A inline re-atomize (5 verify-not-assume catches)
- Testbed gate-witness mid + close (invariants PRESERVED perfectly)
- Cert-grade jump 53 -> 555 (+502 EXACT match Skunkworks prediction)
- USER E4 architectural queue rolled forward
- ARCH-A FULL MIDDLE_BAND verdict (recapture program first decisive test)
- Skunkworks corpus-wide weak-spot synthesis CONVERGED with ARCH-A localization to linear-readout

5 methodology lessons surfaced during the cascade. They are mid-flight today, will decay if not captured durably, and individually qualify as audit_lesson atom candidates per Skunkworks cert-owner rulings. This doc fixes them for the catalog.

## LESSON 1: AUDIT-TOOLING MUST BE VERIFIED BEFORE TRUSTED

```
Rule:
   Before any audit output is treated as ground truth for downstream
   ratify / downgrade / scorecard-revision decisions, the audit
   tooling itself must be verified for soundness.

Why:
   Today's C4 over-claim audit used keyword cross-reference across
   1935 EXP_ atoms. The methodology was unreliable in BOTH directions:
      - False-negatives (real wins called anchor-weak): SQ2 K=12 cert-
        grade HARD_PASS missed by Stage 5 word-order mismatch
        (sq2_b6 vs substrate_b6_x_sq2)
      - Case errors: camelCase (phase_D / charLM) miss lower_case
      - Hyphen/underscore: sparse-expansion misses sparse_expansion
      - Substring false-positives: "48x" matches "0.48x"; "Bundle A"
        matches non-Drosophila cells
   The audit's PROCESS appeared rigorous (Stages 1-5; per-cell trace
   verification); the TOOLING (keyword search) was the silent failure
   point.

How to apply:
   - Before trusting any audit output (especially substrate-wide
     keyword-search audits), run a SOUNDNESS TEST on the tooling:
       1. Pick a known-positive case (cell with verified cert-grade
          anchor); confirm tooling finds it
       2. Pick a known-negative case (cell with no anchor); confirm
          tooling does NOT spuriously match
       3. Test 2-3 case/hyphen/word-order permutations of search keys
       4. Sample-trace 3-5 outputs by-hand against canonical cells
   - If any of those fail, the tooling's output is suspect; either
     fix the tooling or use a DIFFERENT method (per-cell trace by
     someone who knows the cell-naming conventions; verdict-field
     comparison after correct atom matching)
   - VERDICT-FIELD COMPARISON IS RELIABLE when atoms correctly matched
     (the verdict field is deterministic); the FAILURE MODE is
     misidentifying which atom corresponds to which scorecard claim

Composes with:
   - Skunkworks degenerate-recall@1 catch (earlier audit-tooling
     verify-before-trust catch)
   - Skunkworks monitor-perturbs-monitored-system catch (PATH A re-
     atomize)
   - 100th-territory candidate KEYWORD-CROSS-REFERENCE-AUDIT-
     UNRELIABLE-USE-PER-CELL-TRACE
   - 19th-rule self-correction (today's C4 author self-corrected)

Audit_lesson candidate slug:
   audit_tooling_verify_before_trusted_keyword_search_unreliable_per_
   cell_trace_required
```

## LESSON 2: CORPUS COMPLETENESS MUST BE VERIFIED BEFORE AUDIT

```
Rule:
   Any substrate-wide audit (over-claim, capability, coverage) must
   verify that its INPUT corpus is complete (vs known-canonical
   sources like remote desktop runs) BEFORE producing audit output.

Why:
   Today's C4 audit ran on 1935 atomized EXP_ atoms (LOCAL data/ only)
   when 3684 metrics.json files existed total (REMOTE marsh@home heavy
   runs + LOCAL smoke). The atomizer's deterministic walk read LOCAL
   only; the heavy/FULL/cert-grade runs live on REMOTE per USER compute
   policy (laptop super-fast only; remote desktop for heavy). The
   audit was structurally limited to the LIGHT half of the corpus
   and silently over-flagged real wins as anchor-weak.
   USER skepticism caught this twice ("results are real" + "did you
   find all the experiments?"); the audit-tooling could not.

How to apply:
   - Before any substrate-wide audit on EXP_/atomized data:
       1. Count atomized atoms (LOCAL)
       2. Count canonical source files at REMOTE (ssh raw-count probe)
       3. If LOCAL << REMOTE, HALT audit; bulk-SCP sync + re-atomize
          first
   - The substrate's Store-authoritative read is the right baseline;
     the corpus-completeness check is an UPSTREAM gate
   - Apply PROACTIVELY before audit, not reactively after USER
     skepticism

Composes with:
   - Skunkworks raw-count ssh probe discipline (caught the 1935 vs
     3684 gap)
   - reference_substrate_corpus_completeness_remote_vs_local_half_data
     (USER memory rule 2026-06-17)
   - reference_substrate_bulk_ingest_concurrency_gotcha (sync
     mechanism)

Audit_lesson candidate slug:
   audit_input_corpus_completeness_verify_before_output_remote_vs_
   local_count_gate
```

## LESSON 3: THE 19TH RULE OPERATES RECURSIVELY ACROSS SESSIONS

```
Rule:
   When one session's audit/output is questioned by another session's
   evidence (or by USER skepticism), the auditor must self-correct
   per 19th rule. The same discipline applies AT EVERY LEVEL of the
   chain.

Why:
   Today's cascade exercised 19th-rule self-correction 9+ times in
   one day across all sessions:
      - USER ("skeptical results aren't real") -> Skunkworks broader
        audit
      - Skunkworks ("keyword search unreliable") -> Director HALT
      - Director ("re-audit on COMPLETE corpus") -> Orchestrator
        bulk-SCP
      - Orchestrator sync ratified -> Skunkworks PATH A re-atomize
      - Skunkworks re-atomize 5 verify-not-assume catches -> Testbed
        witness verify
      - Testbed mid-APPLY witness -> Skunkworks close request
      - Skunkworks STEP 2 DONE -> Testbed gate-witness CLOSE
      - C4 author (Testbed) -> own-methodology self-correction
      - Stage 5 Row 7 false-negative -> Skunkworks correction +
        Testbed self-correction
   The recursive cascade is the discipline working: each level catches
   the level above; no level is exempt; the substrate self-corrects
   without external override.

How to apply:
   - When questioned (by USER OR another session): treat the question
     as a 19th-rule trigger; don't defend the prior output
   - Self-correct PRODUCTIVELY: enumerate what was assumed; verify
     each assumption; ratify or update the output
   - Document the self-correction (it becomes audit-discipline
     instance type)
   - Do NOT escalate to USER on questions that another session can
     resolve via 19th-rule self-correction

Composes with:
   - 19th-rule refuse-what-can't-prove (USER-LOCKED rule)
   - verify-before-asserting (USER-LOCKED rule)
   - corpus-completeness-verify-before-audit (Lesson 2)
   - audit-tooling-verify-before-trusted (Lesson 1)

Audit_lesson candidate slug:
   19th_rule_recursive_cross_session_self_correction_cascade_pattern
```

## LESSON 4: USER SKEPTICISM IS A VALUABLE AUDIT-INPUT SIGNAL

```
Rule:
   When USER's intuitive pushback contradicts current tool output,
   weight USER signal HIGH and re-verify the tooling. USER skepticism
   is often the highest-signal audit input available.

Why:
   Today USER's two skepticism messages exposed gaps the auditor
   tools missed:
      Message 1 ("skeptical results aren't real"): triggered
         Skunkworks's broader audit -> caught keyword-search
         unreliability + revealed 14 of 18 wins ARE real
      Message 2 ("did you find all the experiments?"): triggered
         Skunkworks's ssh raw-count probe -> caught half-data gap +
         enabled +500 cert-grade jump
   Both were structurally correct + neither was derivable from the
   current tooling output.

How to apply:
   - When USER pushes back on an audit/finding: weight USER signal
     HIGH; don't defend the tooling output
   - Run a TARGETED VERIFICATION on the USER's specific concern (not
     just a re-run of the same tooling)
   - Consider what assumption the USER's question challenges (e.g.,
     "results are real" challenges keyword-search reliability;
     "find all experiments" challenges corpus completeness)
   - Be PREPARED to find USER correct; surface the gap PROMPTLY

Composes with:
   - Lessons 1, 2, 3 (USER skepticism triggers all three)
   - 18th-rule refuse-what-can't-prove (boundary on what to assert)
   - feedback_research_can_be_wrong_only_proven_fully_believed
     (epistemic tiers; USER signal carries weight in low-evidence
     zones)

Audit_lesson candidate slug:
   user_skepticism_high_signal_audit_input_weight_high_re_verify_
   tooling
```

## LESSON 5: SUBSTRATE-PRODUCT POSITIONING NARRATIVE HAS TIME-LAG vs CORPUS STATE

```
Rule:
   Canonical substrate-product positioning docs (scorecard, E6, capability
   map) lag corpus state. When corpus completeness changes substantively,
   the canonical-doc UPDATE must follow (not the same day's audit output
   itself, which was honest given its inputs).

Why:
   Morning C4 audit (pre-discovery) honestly diagnosed 2.7% cert-grade
   thin core (53/1935). The audit-output was correct given its inputs.
   The CORPUS was incomplete. After APPLY:
      - 2.7% -> 15.1% cert-grade (~5.6x ratio; ~10x absolute count)
      - 1507 total PASS (was 838; +669)
      - 14 of 18 scorecard claims have real PASSING experiments at
        some grade (per Skunkworks per-cell trace)
   The substrate-product positioning narrative (substrate-truth-wins
   on-every-cycle; methodology-FROZEN-24; cert-grade thin-core) needs
   refresh now that the corpus is COMPLETE.

How to apply:
   - When a corpus-completeness event lands: update the canonical
     positioning docs (scorecard prose + E6 + capability map) in the
     NEXT cycle
   - Preserve the audit-output's MORNING state as a snapshot (it was
     honest given inputs; documents the cycle's learning); add an
     UPDATE referencing the post-completeness state
   - USER E4 morning summary is the right vehicle for the refresh

Composes with:
   - T_PREP_2 substrate-product positioning amendment input (this
     document)
   - Lesson 2 corpus-completeness-verify-before-audit (upstream gate
     prevents this lag; this lesson covers when the gate is missed
     reactively)
   - Director E6 amendment (downstream action; Lesson 5 motivates it)

Audit_lesson candidate slug:
   substrate_product_positioning_narrative_time_lag_vs_corpus_state_
   refresh_on_completeness_event
```

## Cross-cutting observation: 5 lessons compose into a single discipline

```
The 5 lessons are not independent. They compose:

   LESSON 2 (corpus-completeness) is the UPSTREAM gate for LESSON 1
      (audit-tooling-verify) and LESSON 5 (positioning-lag)
   LESSON 1 (audit-tooling-verify) catches what LESSON 2 misses (when
      corpus is complete but tooling unreliable)
   LESSON 3 (19th-rule recursive) is the META-LESSON enabling self-
      correction at every layer (the substrate fixed itself via 19th
      rule 9+ times today)
   LESSON 4 (USER signal high) provides the EXTERNAL pressure that
      triggers 19th-rule self-correction when internal signals fail
   LESSON 5 (positioning-lag) closes the CYCLE: the audit-output was
      honest, the corpus was incomplete, the doc needs refresh

Single discipline framing (substrate-self-knowledge generalization):

   "Audit the audit. Verify the input. Self-correct recursively.
    Weight external skepticism. Update canonical docs on completion."

This composes with Skunkworks's substrate methodology FROZEN-24
   methodology_rule corpus + Director E6 trust-tier architecture +
   audit_lesson catalog. Five new audit_lesson candidates for
   Skunkworks cert-owner ratify.
```

## ARCH-A MIDDLE_BAND verdict integration

The ARCH-A FULL verdict landed at 14:55 (~30min ago at draft time). Its convergence with Skunkworks corpus-wide weak-spot synthesis (linear-readout = ceiling) demonstrates Lesson 3 (recursive cross-session self-correction) at the strategic-finding layer:
- Skunkworks Aug-13 corpus-wide synthesis identified linear-readout as recurring architectural suspect
- ARCH-A empirical test (sparse-key/dense-value/linear-readout) localized the limiter to the readout, NOT the sparse encoding
- Two independent analytical lines (empirical + corpus-statistical) triangulated the same finding

This is the SAME discipline operating at a different scope: substrate-self-knowledge advancement via converging independent verification. ARCH-B promotion to substrate-wide cross-cutting experiment is the next layer (USER E4 item 13).

The 5 lessons here PROVIDE the discipline framework that enables high-confidence ARCH-A integration. Without Lessons 1-5, ARCH-A's MIDDLE_BAND would be a single-cell laptop finding; with them, it's a CONVERGENT-with-corpus-synthesis bounded finding (and DOWNGRADE-claim-1-Drosophila STANDS).

## Recommended next-step actions

```
For Skunkworks (Auditor; cert-owner of audit-discipline catalog):
   - Review 5 audit_lesson candidates for promotion-eligibility
   - Cert-owner ruling on slug + framing for each
   - Bundle with existing 91 CONFIRMED + 11 candidates (audit_lesson
     half) -> stage next ratify batch

For Director (Research):
   - Reference this doc in STEP 4 E6 amendment (Lesson 5 motivates
     the refresh; Lessons 1-4 frame the methodology learning)
   - USER E4 architectural item 12 (trust-tier architecture T0-T3)
     directly composes with Lesson 3 (recursive 19th-rule) + Lesson
     4 (USER signal weight); these lessons inform tier-promotion
     thresholds

For Exp-Dev:
   - Lessons 1-4 inform future Phase D tool-evolution patches (the
     4 items: LIMIT-default + recursive-glob + token-set + per-batch-
     reload-optional all relate to Lessons 1-2)
   - ARCH-A re-atomize + ARCH-B R3-proper prereg both benefit from
     Lessons 1-2 discipline (atomize-output-verify; remote-vs-local
     completeness for any new cells)

For Testbed (me):
   - Standing for ARCH-A re-atomize witness verify (post Skunkworks
     result-VET)
   - Ready to ratify the 5 audit_lesson candidates as a batch once
     Skunkworks issues cert-owner rulings
   - Available for T_PREP_3 (22 HIGH-risk evidence-base categorization)
     if Director prefers; T_PREP_1 done

For Orchestrator:
   - TIER-1 sweep + cycle summary will benefit from Lesson 5
     (positioning-narrative-time-lag captures the cycle's substrate-
     product positioning learning compactly)
```

## Standing / waiting-on (9th rule)

- WAITING ON **Skunkworks**: ARCH-A result-VET (label + populate-check) + cert-owner rulings on 5 audit_lesson candidates + WAVE 1+2 drill VETs + DG-48x + cortical reads.
- WAITING ON **Research (Director)**: STEP 4 E6 amendment using T_PREP_2 + T_PREP_1 inputs + 8h plan re-scope + 16-item USER E4 ratify.
- WAITING ON **Exp-Dev**: ARCH-A re-atomize + ARCH-B R3-proper prereg parallel draft + Phase D A2 4 patches.
- WAITING ON **Orchestrator**: TIER-1 sweep + cycle summary + PHASE R4 readiness.
- WAITING ON **USER**: 16 E4 architectural items (now includes ARCH-B promote + held-out-retrieval track + E6 revision + DOWNGRADE-STANDS).
- MY ACTIVE WORK: T_PREP_1 DELIVERED (this note); standing for ARCH-A re-atomize witness verify; cycle_check standing per 13th rule + own-lane work between events per 12th rule + 14th rule no-stand-default operating.

## What I am NOT waiting on

- T_PREP_3 (22 HIGH-risk evidence-base categorization) remains available if Director prefers; T_PREP_1 done.
- Reactive on any new ratify dispatch (e.g., 5 audit_lesson candidates from this doc; ARCH-A re-atomize; downstream RECAPTURE WAVE 2 results).

## Substrate state (unaffected; this is a notes-only deliverable)

```
atoms:               30023
relations:           6746
axiom_term:          206/206 PRESERVED
capability_preservation: 1.0 PRESERVED
modules:             6/6 OK
duplicate IDs:       0
phantom edges:       0
EXP_ atoms:          3673
CERT_CHAIN_GRADE:    555
```

Tag: T_PREP_1_C4_audit_methodology_lessons_doc_5_durable_lessons_audit_tooling_verify_before_trusted_keyword_search_unreliable_per_cell_trace_corpus_completeness_verify_before_audit_remote_vs_local_count_gate_19th_rule_recursive_cross_session_self_correction_cascade_user_skepticism_high_signal_audit_input_weight_high_re_verify_tooling_substrate_product_positioning_narrative_time_lag_vs_corpus_state_refresh_on_completeness_event_5_audit_lesson_candidates_for_skunkworks_cert_owner_ruling_ARCH_A_MIDDLE_BAND_integration_lesson_3_recursive_cross_session_at_strategic_finding_layer_skunkworks_corpus_wide_synthesis_empirical_ARCH_A_triangulated_linear_readout_ceiling_lessons_compose_into_single_discipline_audit_the_audit_verify_input_self_correct_recursively_weight_external_skepticism_update_canonical_docs_on_completion_T_PREP_3_available_if_director_prefers_substrate_unaffected_30023_6746_206_206_cap_pres_1p0_6_6_modules_AtomKind_23_zero_dups_zero_phantoms_EXP_3673_cert_grade_555 -- TESTBED (Integrator)
