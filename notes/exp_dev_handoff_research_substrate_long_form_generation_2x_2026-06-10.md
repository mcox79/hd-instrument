# exp_dev hand-off -- research: substrate long-form generation 2x

Filed-by: research sub-agent (claude-sonnet-4-6)
Filed: 2026-06-10
Trigger: d:/AI/hd-instrument/notes/research_drill_substrate_long_form_generation_2x_2026-06-10.md

## Pause state block

exp_dev MUST check data/orchestrator_paused.flag before any queue_add.sh calls.
These candidates are queued for when experiments are active.

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides TASK + WHY + CONTRACT + AUTONOMY to exp_dev.
It does NOT specify anchor names, sweep grids, threshold formulas, or pre-committed
cap_map decisions. exp_dev designs the experiment; research provides the framing.

---

## Anchor candidates (rank-ordered)

### Candidate 1 (HIGHEST PRIORITY): PARAGRAPH-COMPOSE smoke test

Anchor pointer: Section 7 "Anchor 1: PARAGRAPH-COMPOSE" in the research note.
Substrate-product reading: The 2x drill identified tier-2 paragraph schema + PP-225
logit-bias projection as the minimum viable generation capability. PP-225 is validated
at heldout=1.000 for fact-recall; the generation direction (substrate vector -> LLM
logit bias applied during token sampling) is the novel step. A 4-sentence paragraph
on a KB-present topic, generated via tier-2 schema composition + PP-225 projection to
logit offset, gates all downstream generation anchors. If schema completeness (all 4
sentence slots filled) and human-coherence >= 3/5 are achieved on >= 8/10 topics, the
hybrid architecture is validated for structured paragraph generation.
Tier hint: CPU smoke (local CPU, 10 topics, ~$0.50 LLM API). Sentence-level PP-225
projection is the novel operation; test at production N.
Why-now: This is the mandatory gate for STORY-COMPOSE, CODE-COMPOSE, and
LONG-DOCUMENT-COMPOSE. No downstream generation anchor should run until this passes.
Schema completeness is machine-checkable (count filled slot bindings); human coherence
requires a 5-point rubric (does the paragraph make sense as a unit?).

### Candidate 2 (HIGH): STYLE-INJECT validation

Anchor pointer: Section 7 "Anchor 2: STYLE-INJECT" and Section 2.6 "Sleep-defrag style
extraction" in the research note.
Substrate-product reading: Sleep-defrag style extraction is validated as a retrieval
primitive. The generation application -- inject the extracted style vector into the
tier-4 query composition so that generated tokens are biased toward the target register
-- is the novel step. Success criterion: automated cosine similarity of style-feature
distribution (sentence-length distribution, diction-level histogram) between a reference
style sample and a style-injected generated paragraph is >= 0.70. This is the categorical
product differentiator for brand-voice enforcement and regulated-content generation
(persistent style without in-context examples).
Tier hint: CPU medium (local CPU, 5 style exemplars, 20 generated paragraphs, automated
style-feature comparison).
Why-now: Cheap to validate (no new substrate math, just composition in the query stage).
If HARD-FAIL (cosine sim < 0.50), style injection via this mechanism does not work and
requires in-context examples (LLM baseline behavior) -- an important negative result.

### Candidate 3 (HIGH): CODE-COMPOSE schema enforcement

Anchor pointer: Section 7 "Anchor 3: CODE-COMPOSE" and Section 5.3 in the research note.
Substrate-product reading: Code is schema-governed (function schema: inputs, outputs,
docstring, body). The substrate tier-3 code schema can enforce that all structural
requirements are present before emission. The test is: generate a Python function from
a (name, inputs, outputs, docstring) specification using tier-3 code schema + PP-225
with a code-capable LLM. Success: >= 90% of generated functions (a) parse, (b) have
correct signature, (c) execute a basic test input without NameError. This is
machine-evaluatable (no human rater needed), making it the fastest high-signal anchor.
Tier hint: CPU smoke (local CPU, 20 function specifications from standard Python stdlib
tasks, automated eval via ast.parse + subprocess). 2-3 hr implementation + 1 hr testing.
Why-now: Code is the highest-value generation domain because success criteria are
machine-evaluatable. A positive result here is an immediate product capability
(substrate-assisted code generation with structural error prevention).

### Candidate 4 (MEDIUM): AUDIT-CHAIN-PARAGRAPH validation

Anchor pointer: Section 7 "Anchor 4: AUDIT-CHAIN-PARAGRAPH" in the research note.
Substrate-product reading: The categorical product advantage of substrate-hybrid generation
over LLM-alone is the audit chain: for each generated sentence, the chain traces back to
(a) which tier-2 schema slot governed it, (b) which tier-3 shard provided the semantic
content, (c) which KB entry the shard derived from. This is the EU AI Act Article 12
explainability argument and the GDPR traceable-generation claim. The experiment validates
that the chain is constructible (100% of tier-2 slots traceable to KB entries) and that
the chain is accurate (spot-check: randomly select 5 generated sentences, verify the
attributed KB entry is the semantic source).
Tier hint: CPU medium (add audit-chain logging to the PARAGRAPH-COMPOSE pipeline from
Candidate 1; run on the same 10 topics). Requires Candidate 1 to PASS first.
Why-now: The audit chain is a product claim, not just a technical capability. Validating
it on even a small set of paragraphs enables the compliance-document generation pitch.

### Candidate 5 (MEDIUM): LONG-DOC-ENTITY-TRACKING gate

Anchor pointer: Section 7 "Anchor 5: LONG-DOC-ENTITY-TRACKING" and Section 6.5 in the
research note.
Substrate-product reading: The strongest product claim is that the substrate-hybrid
maintains cross-section entity coherence in long documents that exceed the LLM context
window. The experiment tests this by (a) truncating the LLM context to 512 tokens, (b)
generating a 2000-word document in 5 sections using tier-1 discourse schema + entity
tracking across sections, (c) counting coreference errors (entities introduced in section
1 referenced incorrectly or not at all in section 4). Success: < 3 coreference errors.
LLM-alone baseline (same 512-token truncation, no substrate): expected > 10 errors.
Tier hint: CPU full (local CPU, 2-3 days implementation). Requires Candidate 1 + LLM API.
Why-now: This is the most differentiated product claim and the hardest to implement.
Do not start until Candidate 1 is PASS.

---

## Context pointers (file paths, not summaries)

Research note (this drill): d:/AI/hd-instrument/notes/research_drill_substrate_long_form_generation_2x_2026-06-10.md
PP-225 validation notes: (search notes/ for PP-225 references)
PP-273 constrained creative: (search notes/ for PP-273 references)
COMP-DEPTH P0 result: (search notes/ for COMP-DEPTH references)
Schema scaffolding PP-282/284: (search notes/ for PP-282 PP-284 references)
Multi-tier shard composition: (search notes/ for multi-tier shard references)
Sleep-defrag style extraction: (search notes/ for sleep-defrag references)
Cross-domain revision validated: (search notes/ for cross-domain revision references)
Prior substrate-LLM interface handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_llm_interface_binding_2026-06-04.md
Prior substrate direct generative LM: d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_direct_generative_lm_2026-06-04.md

---

## Contract section

This handoff is triggered by a 2x operational drill on substrate long-form generation
capability. The drill found that the substrate's validated primitives (PP-225, PP-273,
COMP-DEPTH P0, schema scaffolding, multi-tier shard composition, sleep-defrag style
extraction) compose into a viable hybrid architecture where substrate drives structural
composition at tiers 1-3 and the LLM emits tokens at tier 4 via PP-225 logit-bias
projection.

The priority ranking is: Candidate 1 (PARAGRAPH-COMPOSE, gates all others) >
Candidate 3 (CODE-COMPOSE, machine-evaluatable, fastest high-signal) >
Candidate 2 (STYLE-INJECT, categorical product claim) >
Candidate 4 (AUDIT-CHAIN, compliance claim, requires C1 first) >
Candidate 5 (LONG-DOC-ENTITY-TRACKING, strongest differentiation, requires C1 first).

If Candidate 1 HARD-FAILS (< 5/10 schema-complete OR coherence < 2/5):
PP-225 logit-bias projection does not maintain sufficient semantic content for multi-
sentence paragraph generation. The generation architecture needs revision (coarser
PP-225 granularity per paragraph not per sentence, or per-section prefix embedding
instead). Do NOT proceed to downstream anchors without a diagnosis and a revised
PARAGRAPH-COMPOSE design.

If Candidate 3 HARD-FAILS (< 70% of generated functions parse):
The tier-3 code schema + PP-225 mechanism does not produce structurally valid code.
This would suggest the schema slot resolution is too coarse for code-level syntax.
Report back to Research for architecture revision.

Research does NOT authorize specific anchor names, implementation choices, or pre-reg
bands -- those are exp_dev's domain.

## Autonomy declaration

exp_dev has full autonomy over:
- Exact anchor names and queue targets (local CPU vs remote CPU vs GPU)
- Pre-registration bands (use research note Section 6 tables as starting guidance)
- Which LLM model to use for PP-225 emission (any code-capable model is acceptable)
- Whether to use existing PP-225 infrastructure or a standalone test harness
- Whether to run Candidates 1 and 3 in parallel (they are independent)
- Whether Candidate 2 (STYLE-INJECT) runs before or after Candidate 3
- Implementation of the tier-2 paragraph schema (data structure choice)
- Choice of KB topics for the paragraph generation tests
- Human rater protocol for coherence scoring (rubric design is exp_dev's call)
