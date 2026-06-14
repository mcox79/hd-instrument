# Research (Director) -> Testbed (Integrator) + Skunkworks (Auditor) + Exp-Dev (Prover): DECISIONS 36-38 -- GO ingest cycle wikidata 10k scientific + Skunkworks STRICT ONLINE recount NOW + pre-register post-ingest decisive test

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~11:30
**Re:** Making the calls per USER "keep going." Three parallel work streams; all cheap; all empirically necessary.

## DECISION 36 -- Testbed (Integrator): GO INGEST CYCLE wikidata 10k scientific slice

USER originally asked about wikidata ingest. M1c temper made ingest empirically necessary at TWO levels:
- Closes Cause 1 (coverage gap; 69pct of held-out gold not ingested)
- Enlarges gap class from n=5 to n=N (robust M4 necessity test becomes possible)

### Spec

1. **Source:** Wikidata SPARQL or wikipedia 10k dump (Testbed picks best of: `tools/dl_wikipedia_10k.py` / `tools/substrate_eval_ingest_v2_composite.py` / equivalent)
2. **Topic focus:** math + physics + CS + adjacent (aligns with substrate's 28 composite type-atoms: vector_space, hilbert_space, sigma_algebra, lie_group, probability_distribution, parameter_vector, gradient, etc.)
3. **Target:** ~10,000 entity atoms; ~30-100k relation edges; cost ~1-2 CPU hr
4. **Pattern:** Phase-4 atomic ratification (same pattern that worked Tier 1+2 + 13 substrate-operator type-atoms)
5. **Output:** atoms.jsonl appended atomically; audit.jsonl logs add_atom events with `source=wikidata_scientific_v1` (or similar)
6. **Reservation R1 (USER 11th rule):** no LLM-assist in ingest; substrate-internal mapping from wikidata entities to substrate atoms; if any LLM-mapping step exists, REPLACE with deterministic rule-based mapping
7. **Reservation R2 (USER 22nd rule):** held-out integrity preserved -- DO NOT ingest the specific held-out gold atoms (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging) that we want to test against; mark these as DO-NOT-INGEST in advance to keep held-out test valid

### HARD-PASS / HARD-FAIL

- HARD-PASS: 5,000+ scientific atoms ingested cleanly + no-regression on existing capability (Tier 1+2 modules still execute on live queries + axiom termination preserved + capability_preservation=1.0 invariant maintained)
- HARD-FAIL 1: < 1,000 atoms ingested (pipeline broken)
- HARD-FAIL 2: regression on Tier 1+2 modules (capability_preservation broken)
- HARD-FAIL 3: any of the held-out gold atoms accidentally ingested (R2 violation; honest disclosure required)

### Cost

~1-2 CPU hr per Testbed estimate. Existing pipeline. Cache + audit + atomic commit.

## DECISION 37 -- Skunkworks (Auditor): STRICT ONLINE recount NOW

Per DECISION 26c (still queued for ~hours). Auditor said: "I will do the STRICT recount (executes-on-live-query only) once the integration push pauses, so the board number is honest not projected."

Integration push paused (DECISION 26); recount can run NOW.

### Spec

1. Recount Tier 1+2 modules (HMM + perceptron + NER + bayes/EM + intent_classifier + RoutedIntentClassifier) under STRICT live-query test
2. Apply no-regression + refuse-discipline + USER 11th rule gates
3. Report honest n-online / 46 (or recalculated denominator if duplicates / supersessions exist)
4. Compare to projection ~44-48pct; if STRICT count differs >5pp, explain why

### Cost

Cheap. Auditor's read-only audit pass. Output: jsonl ledger update + summary note.

### Done-definition

State board ONLINE row replaces "~44-48pct projection" with HONEST STRICT count.

## DECISION 38 -- Exp-Dev (Prover): post-ingest decisive test PRE-REGISTERED

When DECISION 36 ingest lands (HARD-PASS), Exp-Dev runs the decomposed held-out F1 test ON ENLARGED GAP CLASS.

### Pre-registered hypotheses (per USER 10th rule)

**Hypothesis H_M4:** M4 (paraphrase-invariant retrieval) is the necessary mechanism for held-out generalization.
- Prediction: IN-COVERAGE F1 stays at ~0.029 even AFTER ingest expands coverage (capability-transfer is the deeper issue; ingest doesn't fix it)
- Prediction: COVERAGE-GAP refuse-rate may or may not shift (depends on whether new gap questions are also inverted)

**Hypothesis H_INGEST:** Coverage gap is the dominant cause; M4 may not be needed.
- Prediction: IN-COVERAGE F1 lifts substantially (coverage expansion ALSO helps capability-transfer; mechanisms work better when more knowledge is around)
- Prediction: Refuse-rate stabilizes as gap class becomes larger and more representative

### HARD outcomes

After ingest lands (decisive on enlarged gap class n=N >> 5):

- **IF IN-COVERAGE F1 stays ~0.029 (H_M4 confirmed):** M4 is robustly justified; USER decision for M4 architectural investment becomes warranted
- **IF IN-COVERAGE F1 lifts substantially (H_INGEST confirmed):** Cause 3 is less distinct than the 4-cause model suggested; M4 may not be needed; ingest cycle is the right primary path
- **IF MIXED (some axes lift, others don't):** mechanism is differential per axis; need targeted M4 per axis; finer decision tree

### Cost

Same scorer + BGE cache + same scripts; just re-run after ingest. <30 min Exp-Dev.

## Strategic priority (revised; post-M1c temper + DECISIONS 36-38)

```
1. Testbed: DECISION 36 ingest cycle 10k scientific (~1-2 CPU hr)                      [Testbed]
2. Skunkworks: DECISION 37 STRICT ONLINE recount on Tier 1+2 (cheap; parallel)         [Skunkworks]
3. Exp-Dev: DECISION 38 post-ingest decisive test (pre-registered; runs after #1 lands) [Exp-Dev]
4. USER reads DECISION 38 result; decides M4 architectural investment
5. M2 cleanup_margin feasibility check (still gated on C2+CHTV cleanup ship)
```

## Updates to substrate-product positioning

State board now carries: M1 dead STANDS (top1 AUC 0.434 inverted; gate-relevant signal); M1b "all 8 features inverted" TEMPERED (small-n overstated; at n=55 flatness/peak favor in-coverage); M4 DIRECTIONALLY supported on n=5 evidence; INGEST CYCLE is precondition for robust M4 evaluation.

10 honest corrections this session (5 Auditor + 5 Prover including own-prior temper).

## Cross-references

- Exp-Dev M1c temper: `notes/exp_dev_to_research_skunkworks_M1c_TEMPERS_M1b_gap_class_only_n5_top1_inverted_stands_localization_UNTESTABLE_*`
- DECISION 26c (Skunkworks recount queued): commit `e62118ac`
- DECISION 32 decomposition: commit `ba22594c`
- DECISION 35 M1 REJECTED + M4 deferred: commit `5c026801`
- USER question on wikidata: this turn (USER full-auto authorization carries forward)
- Ingest tools: `tools/dl_wikipedia_10k.py` + `tools/substrate_eval_ingest_v2_composite.py` + `tools/substrate_evolve_auto_ingest_*`
- BGE cache (UNAFFECTED; enables fast post-ingest re-measurement): `data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz`

---

**Testbed + Skunkworks + Exp-Dev:** DECISIONS 36-38. **36 Testbed:** GO ingest wikidata 10k scientific (math/physics/CS topics; Phase-4 atomic ratification; ~1-2 CPU hr; do-NOT-ingest the 4 held-out gold atoms active_inference + free_energy_principle + predictive_coding + CAP_pos_tagging per 22nd rule). **37 Skunkworks:** STRICT ONLINE recount on Tier 1+2 modules NOW (parallel to ingest; cheap; replaces ~44-48pct projection with honest count). **38 Exp-Dev:** pre-registered post-ingest decisive test (decomposed held-out F1 on enlarged gap class n=N>>5; H_M4 vs H_INGEST hypotheses; predictions reported per 10th rule; runs after Testbed ingest HARD-PASS).
