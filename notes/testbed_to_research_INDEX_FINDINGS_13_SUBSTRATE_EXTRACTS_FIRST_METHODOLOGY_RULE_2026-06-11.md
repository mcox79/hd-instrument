# Testbed -> Research: Findings 13 -- SUBSTRATE EXTRACTS ITS FIRST METHODOLOGY RULE FROM SOLUTION HISTORY

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** Per Findings #12 Q4 / Methodology rule extraction operational

## TL;DR

Built methodology_rule_extraction() as 8th query on solution-history graph. Substrate observes its own history and surfaces transferable rules where the same (old -> new) replacement repeats across >= 3 capabilities with avg lift >= 0.10.

**First rule extracted (from substrate's own structural data, not human-written):**

> "When count_nb is current-best, try discriminative_perceptron (observed +0.299 avg lift across 5 capabilities)"
>
> Capabilities exhibiting this transition: intent_classification, code_algopattern, NER, MAWPS, MultiArith

This is a substrate-proposed meta-rule. Substrate distilled it from observing 5 capability transitions, NOT from a drill output or memory entry. It's now a candidate for the meta partition (rule-8 us-or-substrate compliant: substrate proposes; Research validates).

## Mechanism

`methodology_rule_extraction()` reads solution_history fields across all capability atoms. For each (from_solution -> to_solution) transition pair:
- Counts how many capabilities exhibit this transition
- Computes average lift across instances
- If n_capabilities >= 3 AND avg_lift >= 0.10 -> surface as candidate rule

Rule confidence = n_capabilities / total_capabilities (rough fraction).

## What the rule encodes

The 5 capabilities all show same architectural moment:
- Each had count_NB or count-features as initial baseline
- Each transitioned to discriminative perceptron over richer features
- Each lifted in the range +0.114 to +0.728 (avg +0.299)
- Each transition happened on cycle 232-234 (June 10-11 universal-discriminative-weighting moment)

Substrate sees this as a rule because the SAME architectural pattern manifests across 5 different problem domains. The rule is transferable: "if you find yourself with count_nb as current-best for any classification-style capability, switching to discriminative perceptron is likely to help."

## Substrate proposes its own meta layer

Per the 5-tier progression: Tier 3 = substrate-proposed atom candidates. This is a Tier 4 candidate: substrate-proposed METHODOLOGY rule.

The 8-layer eval program already has 6 methodology rules (drill-defeatism / literature-not-oracle / honest-attribution / Layer 1 PROT / lift > 2*SE / benchmark must break symmetry). These were ALL human-authored from drill outputs.

This new rule is the FIRST that substrate produced on its own from internal structural data. It's a Type C signal (substrate-proposed architectural change).

## Concrete next moves substrate enables

### 1. Auto-detect upgrade opportunities
When a new capability arrives with count_nb as current-best, substrate can flag: "rule R suggests trying discriminative_perceptron; based on 5 prior cases, expected lift +0.299"

### 2. Cross-capability methodology spread
For capabilities where count_nb is HISTORICAL (not current) but discriminative_perceptron isn't yet adopted, substrate could propose: "you skipped a step; the universal lever may apply"

### 3. Rule strength tracking
As more capabilities are added with histories, the rule strength (n_capabilities) grows. Substrate can report rule reliability over time.

### 4. Rule contradictions
If a capability EVER REVERTS from discriminative_perceptron back to count_nb (highly unlikely but possible), substrate flags the rule as having an exception. Methodology refinement.

## Implications for meta partition

The meta partition (currently empty) should hold:
- 6 human-authored methodology rules (from drill outputs)
- 1 substrate-extracted rule (this finding)
- (future) more substrate-extracted rules as solution histories grow

When the meta partition has both human-authored AND substrate-extracted rules, Layer 4 dialectic can apply:
- Substrate-extracted rules that align with human-authored = EXPECTED (confirms human intuition)
- Substrate-extracted rules that contradict = SURPRISE (drill trigger)
- Substrate-extracted rules with no human analog = SECOND_ORDER (genuine new methodology)

## What I want from you

### Q1: Should I file the rule as a meta partition atom?
Currently it lives in a bench_report JSON. To make it persistent + queryable as substrate structure, it should become an atom:
- qualified_id: meta::rule_count_nb_to_discriminative_perceptron
- kind: methodology_rule (new AtomKind value)
- description: the rule_text
- metadata: {avg_lift, n_capabilities, source_capabilities, extracted_date, extracted_by: "substrate"}

This would be the first meta partition atom. Want me to ingest?

### Q2: Tier 4 gate measurement clarification
Per 5-tier progression Tier 4 -> Tier 5 requires "1+ substrate-proposed architecture validated via Layer 1 + meta-evaluation methodology improved."

Is THIS finding the first Tier 4 candidate? Substrate-proposed methodology rule = meta-evaluation methodology improvement. Layer 1 validation = does adding this rule to the eval program move ranking on something? (We'd need to apply the rule to a NEW capability + see if the prediction holds.)

If yes: Tier 4 first appearance milestone met today.

### Q3: Extract more rules
Currently the threshold is min_caps=3 + min_lift=0.10. With those thresholds and 14 capability histories I get exactly 1 rule. If I lower to min_caps=2, I'd get more rules but with lower confidence:
- "When cosine_cleanup is current-best, try fhrr_unbind" (1 capability; rejected at min=2)
- (etc.)

Worth running with min_caps=2 + reporting candidates at lower confidence? Or wait for more capability histories?

### Q4: Rule decay
If a rule was extracted 6 months ago and the relevant solutions have been further superseded since, the rule should be marked stale. E.g., if discriminative_perceptron is itself replaced by something better, the count_nb -> discriminative_perceptron rule loses force.

substrate's rule extraction should re-run periodically and mark superseded rules as stale. Worth shipping?

## Cycle progression

This is Cycle #8 (Type C: substrate-proposed architectural change applied to substrate's own meta layer). The previous Cycle #7 was the solution-history schema; this is the SECOND-ORDER effect: now that solution histories exist, substrate extracts meta-rules from them.

8 cycles, 5/5 signal types, all closed. Tier 1-4 all visible Day 1+.

## Cross-references

- Findings #12 (solution-history universal-lever): notes/testbed_to_research_INDEX_FINDINGS_12_SOLUTION_HISTORIES_UNIVERSAL_LEVER_QUANTIFIED_2026-06-11.md
- solutions.py methodology_rule_extraction(): backend/substrate_index/solutions.py
- Runner: tools/substrate_methodology_extraction_run.py
- Bench: data/substrate_index/bench_reports/methodology_rules_*.json
- 5-tier progression memory
- Rule 8 substrate-content-sources memory

---

**Research:** Substrate extracted its FIRST methodology rule from its own structural data: "When count_nb is current-best, try discriminative_perceptron (+0.299 avg across 5 capabilities)." Not human-written. Substrate observed + distilled. Type C Cycle #8. Q1 ingest as meta atom? Q2 Tier 4 first appearance? Q3 lower extraction threshold? Q4 rule decay tracking?
