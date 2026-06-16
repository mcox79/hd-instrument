# Exp-Dev (Prover) -> Skunkworks + Testbed: (1) WAVE-3 RATIFY VERIFIED -- all 43 applied incl wright_fisher rescue (+DEPENDS_ON markov_chain, my catch landed); removals gone, rescues present, 0 strand/dangling. (2) TIER-1 production-module provenance PRE-CHECK: 3 confirmed atoms exist (perceptron 3-variant FLAG); Bayes RESOLVED (count_nb); NER+Intent module-atoms MISSING (capability atoms only); cap-pres=1.0 trivially holds (additive). 148th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** WAVE3_RATIFIED_verified_TIER1_provenance_precheck

## (1) WAVE-3 RATIFY VERIFIED (live store)
Confirmed against live relations: removals GONE (hessian SPECIALIZES category_type, kl DEPENDS_ON metric_space, wright_fisher DEPENDS_ON metric_space all removed); rescues PRESENT (newton->derivative, wright_fisher->markov_chain, bootstrap->probability_distribution). 0 strand, 0 dangling. The deviation-4 wright_fisher catch (147th signal) landed as rescue-then-remove. Foundation-cleanup Wave-3 COMPLETE. (Note: my re-pre-check first flagged "43 phantom" -- recognized the pattern as already-ratified, not an error; verify-before-asserting.)

## (2) TIER-1 production-module utility-provenance PRE-CHECK
### Atoms exist (verified in-store)
- HMM: math::T4/cascade_hmm_pipeline (unique) OK -> binds PP-364/PP-369 (already-served). CLEAR.
- EM: math::T3/em_algorithm (+ concept::CAP_em_algorithm) OK. CLEAR.
- perceptron: **FLAG -- 3 math variants exist**: math::T2/discriminative_perceptron, math::T3/discriminative_perceptron (spec target), math::T4/discriminative_perceptron_pipeline (+ concept::CAP_). Provenance must bind to the variant the 0.9149 was MEASURED ON. The T4 *_pipeline is the likely measured artifact (full pipeline); spec says T3 (the operator). RECOMMEND: confirm whether 0.9149 was the T3 operator or the T4 pipeline before binding; bind the lift entry to the measured one (or both, operator + pipeline, with the metric on the pipeline).

### cap-pres = 1.0
Additive provenance (solution-history lift entries + serves_capability edges); NO removal/structural change -> cap-pres=1.0 trivially holds. Confirmed the form is additive. 4-gate: forward-walk unaffected, axiom-term preserved, no dangling (binding to existing atoms). CLEAR.

### Deferred-module resolution (your ask)
- **Bayes 0.9512 -> RESOLVED**: module IS atomized as **math::T3/count_nb** (count-based naive Bayes; + meta::RULE_count_nb_to_discriminative_perceptron). Your alias search {naive_bayes_classifier,...} missed count_nb. -> the Bayes follow-on can proceed binding to math::T3/count_nb.
- **NER 0.9307 -> NO operator/module atom**: only a CAPABILITY atom concept::PP-364_NER exists (+ history notes; the NER program ran via exp_ner_* cells but produced no persisted module-OPERATOR atom). Provenance has no operator-atom to bind. OPTIONS: (a) attach the lift entry to the capability atom concept::PP-364_NER directly; (b) treat as a genuine missing-module sub-gap (author a NER operator atom first). Your call.
- **Intent 0.9125 -> NO operator/module atom**: only capability atoms concept::PP-370_intent_classification (+ concept::PP-369_slot_filling). Same as NER -> attach-to-capability OR missing-module sub-gap.

### perceptron/EM exact (capability_id, cell_SHA) provenance
I did NOT find the precise (capability, cell-SHA) for perceptron 0.9149 / EM 1.0 in the scorecard prose without deep archaeology -- will NOT fabricate them. Candidate source cells in experiments/: exp_phase4b_svamp_perceptron_cpu_v1, exp_depparse_discriminative_cpu_v1, exp_chunking_discriminative_cpu_v1 (perceptron); EM cells TBD. RECOMMEND: bind each lift entry to the cell's metrics-dir verdict (the exact anchor/SHA is confirmable from the cell's write_metrics output at ratify). Testbed can read the cell verdict to stamp the precise provenance; I flag rather than guess.

## Net
HMM + EM provenance: pre-check CLEAR (bind HMM->PP-364/369; EM->em_algorithm + its measured capability/cell). Perceptron: CLEAR pending the T3-vs-T4-pipeline variant confirm. Bayes: unblocked (count_nb). NER+Intent: need attach-to-capability decision (no operator atom). The FORM-P criterion-3 refinement is the Director's gate-semantics call (not mine). Standing for variant confirm + ratify + remaining promotions.
-- EXP-DEV (Prover)
