# Research -> Testbed + Skunkworks: F4 LANGUAGE BRIDGE QUEUED -- Curry-Howard NLI via FraCaS section 1 + 8-10 language-foundation type-atoms

**From:** Research (linchpin)  **Date:** 2026-06-13 late evening
**Re:** Drill 3 (math-to-language bridge) landed. Filing forward queue item. NOT a NOW dispatch -- Exp-Dev is loaded with F1 work. F4 work queues behind first F1 verdict.

## Drill 3 HEADLINE

B1 type-theoretic Curry-Howard NLI bridge ranks highest of 5 candidates. P_deflated=0.45. Cheap decisive test = FraCaS section 1 (74 items, Generalized Quantifiers; ~1 CPU day).

USER bet (`if math then language`) is empirically testable via this bridge. The bridge respects USER 11th rule (substrate-on-its-own; no LLM dependence). HARD-PASS criteria sharp: >=50pct accuracy on FraCaS section 1 at 0 false-accept (substrate's soundness story transferred to language).

## What substrate must add (minimal scope)

### 8-10 language-foundation type-atoms (atom-author pattern reuse from Phase-4 13-operator-atom ratification)
1. `utterance` (base; language analog of `vector`)
2. `discourse_referent` (DRT)
3. `speech_act` (illocutionary classification)
4. `scope_island` (quantifier scoping boundary)
5. `presupposition`
6. `anaphor_link`
7. `quantifier_scope`
8. `illocutionary_force`
9. `polarity`
10. `temporal_anchor`

These are textbook from DRT (Kamp/Reyle) + Montague + Categorial Grammar; NOT arbitrary. Type-graph terminates here for language as 15 mathematical foundations terminated for math.

### 1 new operator
`to_logical_form(utterance) -> typed_expression` -- GATED BY CHTV-1 (refuses if untypable). Following 18th rule: substrate REFUSES utterances it cannot type, just as it refuses promotions it cannot prove.

### 1 new measurement
`nli_accuracy_at_zero_false_accept` -- language analog of DISTILLATION_RATIO; substrate's score on NLI at the constraint FP==0.

### 1 new ingest path
FraCaS corpus (346 items total; section 1 = 74 items) as typed-pair atoms. Public NLI benchmark; held-out by design.

## Why B1 over B2-B5

- **B2 (word-as-atom)**: standard VSA NL; substrate gains little beyond baseline; capacity-cliff risk at L>20. RANK 4.
- **B3 (linguistic_capability tag)**: routing not capability; complements B1 but does not test the bridge. RANK 3.
- **B4 (knowledge-graph entities-as-atoms)**: representation choice not capability test. RANK 5.
- **B5 (LM as operator)**: **VIOLATES USER 11th rule**. DEFER until substrate-standalone proven. RANK 2 in principle but RULED OUT for now.

**B1 advantages:** cheap (74 items); decidable inference (FraCaS section 1 = Generalized Quantifiers, single-premise, no training); proof-shape MATCHES L6-PROOF backward-chaining at depth 1-3; soundness story (CHTV-1 1.0 precision) transfers directly; falsifier is sharp.

## Execution queue (NOT YET DISPATCHED)

Gating condition: at least 1 F1 verdict back (Exp-Dev E-S1/E-S2/E-S3 or canonical rerun) BEFORE F4/B1 starts. Reason: do not split Exp-Dev attention; F1 measurement currently the highest-priority capability gate.

### When F4/B1 queues:

**Step 1 (Skunkworks; ~1 hr):** draft 10-atom language-foundation JSONL in Phase-4-ratification shape (`skunkworks_language_atom_candidates.jsonl`). Same pattern that worked for 13 substrate-operator atoms in Phase 4.

**Step 2 (Testbed; ~30 min):** ratify + ingest 10 language-foundation atoms with SPECIALIZES edges to existing math foundations (e.g. `utterance SPECIALIZES vector`; `discourse_referent SPECIALIZES set`; `quantifier_scope SPECIALIZES bounded_linear_operator`). Same atomic-commit pattern.

**Step 3 (Testbed; ~2-4 hr):** implement `to_logical_form` operator. CHTV-1 gated. Refusal-on-untypable.

**Step 4 (Exp-Dev; ~4-6 hr):** FraCaS section 1 ingest (74 typed pairs); run L6-PROOF FINDER as NLI prover; compute `nli_accuracy_at_zero_false_accept`. HARD-PASS = >=50pct accuracy at 0 FP. HARD-FAIL = <30pct OR any FP.

**Step 5 (Research):** synthesize F4 verdict; scorecard Row 4 (Goal 4) and LAKATOS F4 floor update.

Total: 1-2 days CPU after gating clears.

## Reservations

- **R1.** USER 11th rule: NO LLM-assist in step 3 (`to_logical_form`). Must be substrate-internal lexical-to-typed-expression mapping. If we cannot build this without LLM, the bridge fails honestly and we report it -- substrate is not yet language-capable.
- **R2.** 10th rule verify-before-asserting: report ACTUAL FraCaS accuracy, not predicted. P_deflated=0.45 means even-money outcome.
- **R3.** 22nd rule Lakatos external floor: FraCaS is the external floor for F4. Public benchmark. Held out by design.
- **R4.** Substrate composition story: if NLI HARD-PASS, USER bet "if math then language" gets first empirical evidence at small scale (74 items). NOT yet "LLM-class mastery" (Goal 1) but the START of F4.

## What gets queued IF F4/B1 PASSES

- FraCaS sections 2-9 (272 more items; full benchmark)
- SNLI / SICK small-scale (10K-pair NLI corpora)
- F4 LAKATOS floor proposal: "substrate language inference >= chance baseline + 0.10 at 0 FP on FraCaS"

## What gets queued IF F4/B1 FAILS

- Honest disclosure: substrate's math-to-language bridge does not transfer naively
- Reformulate via B3 (capability_registry routing) or alternative bridge
- Possible: introduce a tight learned-vector layer (USER architectural decision; would require revisiting 11th rule)

## Cross-references

- Drill 3 output: this turn (no separate artifact per Orchestrator denser-fewer)
- Phase 4 13-atom ratification pattern: `notes/testbed_to_research_exp_dev_PIVOT_PHASE_4_*`
- 18th rule (refuses what cannot prove): memory `substrate_closed_loop_OPERATIONAL_step_3_*`
- L6-PROOF FINDER: memory `substrate_L6_PROOF_FINDER_HARD_PASS_*`
- USER bet "if math then language": memory `substrate_USER_decisions_2026_06_13_*`
- 22nd rule external floor: memory `substrate_USER_decisions_2026_06_13_*`
- Public benchmarks: FraCaS (Cooper et al. 1996) / SNLI (Bowman 2015) / SICK
- B1 lit basis: Lambek typelogical grammars / Moortgat / Categorial-Grammar SEP entry

---

**Testbed + Skunkworks:** F4 LANGUAGE BRIDGE QUEUED behind first F1 verdict. B1 Curry-Howard NLI via FraCaS section 1 (74 items, 1-2 days CPU). Substrate adds 10 language-foundation type-atoms (utterance + discourse_referent + speech_act + scope_island + presupposition + anaphor_link + quantifier_scope + illocutionary_force + polarity + temporal_anchor) + `to_logical_form` operator CHTV-1 gated + `nli_accuracy_at_zero_false_accept` measurement + FraCaS ingest. HARD-PASS 50pct at 0 FP. Reservation R1: substrate-internal `to_logical_form` (USER 11th rule). If R1 cannot be honored, fail honestly.
