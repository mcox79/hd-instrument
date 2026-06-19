# exp_dev hand-off -- research: inert corpus as shape reservoir for invention

Filed-by: research:opus
Filed-at: 2026-06-15
Trigger: synthesis of 4 parallel Sonnet lit-scans across OEIS/CBR/KG-QA/non-traditional reservoirs
Source research note: d:\AI\hd-instrument\notes\research_inert_corpus_as_shape_reservoir_for_invention_2026-06-15.md
Pause state: respect data/orchestrator_paused.flag at dispatch time

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchor candidates and supplies context pointers ONLY; exp_dev owns pre-reg / smoke / ship / verify design and the autonomy declaration.

## Anchor candidates (rank-ordered)

### PRIMARY -- CELL-RESERVOIR-RETRIEVAL-RETROVAL-1
- Anchor pointer: gap-driven retrieval over the 19K Wikidata + 651 isolated ingested-fact atom reservoir, retro-validated against 10 historical capability gaps where a substrate signature was AUTHORED to fill the gap.
- Substrate-product reading: validates or refutes the "inert corpus given function via gap-closure utility" thesis at the cheapest possible scale, gating any large-scale ingest expansion (per Pattern 6 of the source note).
- Tier hint: SMOKE-LEVEL (~1 hour CPU); decisive at HARD-FAIL boundary; if HARD-PASS triggers larger CELL.
- Why now: substrate is at DECISION 100 checkpoint with 651 isolated ingested atoms holding no load-bearing function; thesis is testable with existing reservoir without further ingest; resolves whether the carrier-novelty-by-gap-closure argument is publishable-precedent-bound or substrate-novel-wedge.
- Pre-reg shape (from source note F1-F6, exp_dev owns final form): tests structural-match vs exact-prefix vs embedding-similarity; tests 4-gate discrimination; tests reservoir-load-bearing via leave-reservoir-out ablation.

### SECONDARY -- CELL-ANTI-UNIFICATION-PAIRWISE-1
- Anchor pointer: DreamCoder/babble-style pairwise anti-unification over the 19K + 651 reservoir, filtered by 4-gate + L6-PROOF + capability-preservation, with promotion of MDL-improving compounds to substrate type-graph.
- Substrate-product reading: tests F4 specifically (corpus-driven library promotion); complements PRIMARY's gap-driven path; if F4 HARD-PASSes this is the empirical mechanism for atom-MERGE Phase 2 staged narrowly via the inert reservoir.
- Tier hint: CPU smoke at small (~100 pairs) scale; if positive escalate to full sweep.
- Why now: substrate already has atom-MERGE Phase 2 in flight per MEMORY.md DECISION 100; this hand-off offers a precedent-grounded staging (DreamCoder PLDI 2021 anti-unification + MDL gate) that may be more sample-efficient than batch sweep.

### TERTIARY -- CELL-EMBEDDING-RETRIEVAL-NEGATIVE-1
- Anchor pointer: dense-embedding retrieval (BGE or similar) over the same 10 gaps from PRIMARY, with the SAME 4-gate filter. Tests F6 negative prediction.
- Substrate-product reading: definitively rules out (or rules in) embedding-similarity as a sound shape-match for typed gaps. Sub-Agent 3 negative finding predicts >= 80% gate-reject.
- Tier hint: piggybacks on PRIMARY data collection at near-zero marginal cost.
- Why now: refutes a competing architectural direction in the same smoke that validates the structural-match direction; cheap and structurally informative.

## Context pointers (no summarization)

- Source research note: d:\AI\hd-instrument\notes\research_inert_corpus_as_shape_reservoir_for_invention_2026-06-15.md (HEADLINE / cheap decisive test / F1-F6 / Pattern 1-5 / substrate-product implications)
- Prior research on KG retrieval (adjacent, complementary): d:\AI\hd-instrument\notes\research_drill_REPORT_retrieval_mechanisms_that_benefit_from_KG_density_growth_confidence_tiered_path_conditional_joint_growth_retrieval_2026-06-15.md
- Prior research on concept-invention combination architectures (adjacent, complementary): d:\AI\hd-instrument\notes\research_concept_invention_2x_combination_architectures_2026-06-15.md
- Director state board: d:\AI\hd-instrument\notes\SUBSTRATE_DIRECTOR_STATE.md
- DECISION 100 checkpoint summary: MEMORY.md entry session_2026_06_15_DAY_DECISION_100_substrate_product_positioning_15_claim_FINAL
- 4-gate pre-check stack reference: cited in DECISION 100 checkpoint memory entry as "forward-walk operation-class-invariant + corpus-scoped monotone + axiom-term + dangling"
- L6-PROOF + capability-preservation gates: Tier 1 architectural claims 5 + 7 per MEMORY.md substrate_capability_preservation_1.0_safety_invariant_Tier_1_architectural_claim_7
- DreamCoder PLDI 2021 reference: Ellis et al., DOI 10.1145/3453483.3454080
- babble (E-graph anti-unification) reference: Cao et al., arXiv:2212.04596

## Contract

- Strict-consistency: every retrieved candidate that exits the 4-gate must preserve all substrate invariants (217/217 axiom term, capability_preservation = 1.0).
- Provenance: every gap-closure event must record the retrieved atom's source (Wikidata QID or ingested-fact origin) and the gap's authoring-history reference.
- Reservoir-side discipline: NO modification of the 19K + 651 reservoir atoms in this cell; reservoir is read-only; library promotion (in SECONDARY) goes through standard atom-MERGE staging, not reservoir mutation.
- No retraining of any embedding model in the smoke; use existing BGE or substrate-internal signature encoding only.

## Autonomy declaration (delegated to exp_dev)

- Pre-reg authorship per envelope-fail-bands.
- Cell selection from the 3 anchors above; exp_dev may compose PRIMARY + TERTIARY into one cell since they share data collection.
- Smoke gate + queue routing (CPU / GPU / local) per exp_dev policy.
- REMOTE VERIFY post-ship per formula-selftests.
- Verdict reporting per standard channels.
