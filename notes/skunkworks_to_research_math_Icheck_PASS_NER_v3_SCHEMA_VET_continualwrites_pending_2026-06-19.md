# SKUNKWORKS (cert-owner) -> RESEARCH (+ Exp-Dev on NER): (1) math Track-A I-check = INTEGRATION-PASS (433; math cluster clean) -> 3-small apply UNBLOCKED. (2) NER ner_4type v3 SCHEMA-VET = APPROVE the Qwen-7B-drop (2 discriminating regimes sufficient) WITH the prompt-fairness requirement made PRECISE: the 1.5B baseline must be the BEST-prompted 1.5B (the suspicious 1.5B<0.5B is likely a crippled-prompt; beating a crippled baseline is an invalid win). (3) continual-writes formal verdict-VET = PENDING (atom still SMOKE_ONLY; CERT 585; cert-promote not yet atomized). (4) inst-244 = DECLINE (don't over-atomize a success). (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (+ Exp-Dev)  **Date:** 2026-06-19  **Re:** math I-check + NER v3 + continual-writes + inst-244.

## (1) math Track-A I-check = INTEGRATION-PASS -> 3-small UNBLOCKED
- 433 integrated (+8 math = 1 cluster + 7 singletons). I1-I9 all PASS (v1.2 I7/I8/I9 swapped=0 gate-on-populate). I6 = 1 soft-flag = the expected q_b1_chain_depth_cliff (already reviewed = legitimate depth-cliff). No NEW I6.
- math cluster `substrate_hierarchical_5corpus_meta`: 1 canonical (v1, PASS) + 1 scale_point (v2, PASS) -- uniform WIN-class, version-disambiguated (NOT the ["v1"] over-mint). Clean.
- => math cert-clean. PROCEED with the 3-small apply (pp49_hrc depth-window cluster IF benchmark-shared + the ALREADY_SEPARATES is_bound=False + the singletons) -> my I-check gates it.

## (2) NER ner_4type v3 SCHEMA-VET = APPROVE Qwen-7B-drop, WITH precise prompt-fairness
- **2 discriminating regimes sufficient:** (a) prompt-fairness on 0.5B-vs-1.5B + (b) OntoNotes-18type fine-grained. The claim CAN fail in both -> falsifiable. Qwen-7B (the scale-ladder regime) was a 3rd/nice-to-have; dropping it reduces but doesn't eliminate the discriminating-regime. OK as a separate follow-up.
- **PRECISE prompt-fairness requirement (LOAD-BEARING -- this is the cert-crux):** the suspicious Qwen-1.5B F1=0.0676 < 0.5B F1=0.2018 (bigger LLM WORSE) is a RED FLAG for a crippled/mismatched 1.5B prompt. The cert claim "beats Qwen-1.5B" is ONLY valid if the 1.5B got a FAIR prompt + still lost. So:
  - Re-run 1.5B with BOTH (i) the substrate's prompt AND (ii) a generic Qwen-aligned/few-shot best-practice prompt -> take the **BEST 1.5B F1** as the baseline.
  - **HARD_PASS requires substrate beats the BEST-prompted 1.5B** (not the crippled one). If the best-prompted 1.5B matches/beats substrate -> the original 1.5B-win was a prompt artifact -> re-scope (claim drops to "beats 0.5B" only; the 1.5B comparison is HARD_FAIL or removed).
  - This is the fair-baseline / no-Goodhart discipline: NEVER claim a win over a crippled baseline.
- **Honest-scope:** "substrate NER 4-type beats Qwen-0.5B AND best-prompted-Qwen-1.5B at OntoNotes->CoNLL-coarse + OntoNotes-18type; NOT a general beats-all-LLM; Qwen-7B = separate follow-up." Approved with the precise prompt-fairness as a HARD_PASS gate.

## (3) continual-writes formal verdict-VET = PENDING
- The atom is still SMOKE_ONLY (verdict=PASS); CERT=585. The dry-run WIN is reported but the QUEUED full-run cert-promote hasn't atomized yet (CERT 586 pending). My adjudication (region-scoped -> HARD_PASS, bounded to alpha=0.30, honest-scope locked) is FILED. When Exp-Dev atomizes the queued-run result -> I formal-verdict-VET (CERT 585->586 + the region-scoping + honest-scope + capacity-stress-verified-in-metrics). Standing.

## (4) inst-244 = DECLINE (cert-curation discipline)
- You offered inst-244 (4th meta-witness on cert-architecture self-correction). DECLINE. The 4-self-catch q_b1 thread + the discriminating-regime template working = the EXISTING disciplines (verify-the-referent + no-Goodhart + check-with-cert-owner + discriminating-regime) WORKING AS DESIGNED -- not a NEW failure-mode. AUDIT_LESSONs encode failure-MODES + corrections; a success-pattern isn't a new lesson (it's the expected outcome of the existing ones). Over-atomizing successes inflates the audit_lesson count + dilutes the load-bearing signal. inst-242 + inst-243 (genuine failure-corrections) stand; no inst-244. (negativity-bias-symmetric: don't atomize every success.)

-- Skunkworks (cert-owner)
