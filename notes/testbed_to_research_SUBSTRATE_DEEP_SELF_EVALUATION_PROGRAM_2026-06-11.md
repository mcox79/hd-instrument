# Testbed -> Research: substrate-on-substrate as a DEEP SELF-EVALUATION PROGRAM

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** User-locked strategic intent for the substrate self-index

## User direction (verbatim)

> "What I want to do with the substrate on substrate is deeply evaluate it to learn more, gain insights, improve it etc"

This sharpens what "find better solutions" meant. The substrate self-index isn't a comparative-vs-LLM benchmark with a single answer; it's a **persistent self-evaluation research instrument** that generates insights, surfaces failure modes, proposes refinements, and feeds the next research cycle. The construct improves the substrate, not just measures it.

## Reframing batch 02 findings

Findings #3 reported "Q1/Q2/Q4 EMBEDDING_DRIFT FIXED" as if that closes a loop. Under the deep-self-evaluation frame, those results are the **first measurement**, not the verdict. They unlock the next set of questions:

- Which refinement (description vs algebra_category vs concept_links vs relations) carried the most lift? Decompose the 81 -> 58 finding drop by attribution.
- Is the fhrr_unbind / fhrr_bind cluster (Q1 + Q5) genuinely tight, or is the 0.12 gap between them in the top-3 hiding a representation collision?
- What does spectral observability on the 60-atom codebook say about saturation / well-spread / cluster gap? Does it agree with structural intuition?

These are NEW questions surfaced BY the substrate evaluating itself. None are LLM-answerable.

## Proposed deep self-evaluation modes (8 layers; pick which Research wants prioritized)

### Layer 1: Structural attribution
For each query: what fraction of the lift comes from (a) refined description, (b) algebra_category, (c) USES / DUAL relations, (d) EQUIVALENT_UNDER cross-domain edges? Run the query 5 ways:
1. Pre-batch-02 (semantic only on batch 01 descriptions)
2. Refined description + tier/corpus tags (no algebra-vec, no relations)
3. + algebra_vec composite
4. + structural relations
5. + cross-domain equivalences

Decomposes Findings #3 into causal contributions. Tells us which dimension of the foundational tool is doing the work.

### Layer 2: Spectral self-diagnosis
Activate the free-prob primitive (Research's FREE_PROBABILITY_OBSERVABILITY_INTEGRATION drill). Compare 4 codebook variants:
- Batch 01 semantic-only embedding matrix
- Batch 02 composite (semantic + algebra-vec) embedding matrix
- batch 02 algebra-vec only (just the structured field encoding)
- batch 02 with a single perturbation per atom (description swap)

Marchenko-Pastur bulk + Tracy-Widom edge + kappa_4 + spectral_gap on each. Where does the substrate's own representation live in capacity-regime space? Where does it saturate?

### Layer 3: Algebra-cluster archaeology
Cluster all 60 atoms by algebra-vec cosine only. Compare to:
- Cluster by semantic-vec only
- Cluster by signature-vec only
- Cluster by tier
- Cluster by family-tag membership

Identifies which atoms belong to the wrong cluster algebraically. Surfaces candidate algebra_category corrections + identifies T2_FAM / T2 mis-tag suspects. Empirical input to the 27-tag 5-super-group refactor.

### Layer 4: Empirical-theoretical dialectic
Each discover.py finding gets a TYPE label: "expected from theory" / "empirical surprise" / "second-order discovery." For each "surprise," propose:
- The smallest substrate change that would explain it (atom add, relation add, description refine)
- The smallest LLM-substrate gap test that distinguishes substrate from LLM on this surprise

Builds the substrate->research drill request pipeline; what we ship to Research is precisely the surprises substrate found that we believe are real.

### Layer 5: Capability-substrate dialectic
For each major capability (PP-225 fact-recall, PP-150 retrieval, NL POS, math word-problems, etc.), trace BACKWARDS through the index:
- Which math atoms compose its mechanism?
- Which family-tags partition its behavior?
- Which equivalence-classes does it sit in?
- Which atoms are SHARED with at least 3 other capabilities (capability hubs)?

Surfaces architectural redundancy AND architectural reusability candidates. The reusable substrate atoms are the most valuable; isolated atoms are candidates for removal or merging.

### Layer 6: Stability under composite weights
Run 5 disclosed queries under (alpha, beta, gamma, delta) sweep:
- (1.0, 0.0, 0.0, 0.0) semantic only
- (1.0, 0.5, 0.3, 0.2) current default
- (0.3, 1.0, 0.5, 0.3) algebra-heavy
- (0.5, 0.3, 1.0, 0.5) signature-heavy
- (1.0, 0.3, 0.3, 1.0) complexity-heavy

Which conclusions are robust across all 5? Which flip? Robust conclusions = substrate-validated; flipping ones = noise floor of the encoding.

### Layer 7: Cross-substrate comparison (after multi-substrate wrapper lands)
When the engineered wrapper (memory entry [[substrate-v32-engineered-wrapper-2026-06-11]]) is empirically validated, each substrate becomes a partition. The self-index then compares them:
- CLS+SDM vs base FHRR on capacity
- Tier-1 frozen vs warm on retention
- Different beta values on calibration

Substrate-self-index becomes the cross-substrate evaluation lens.

### Layer 8: Drift over time (the LIVING ARTIFACT loop)
evolve.py auto-ingests cap_map cycles. Track for each cycle:
- New atoms added per cycle
- Findings drift (which discover findings persist; which resolve; which appear)
- Algebra-category distribution shift
- Spectral observability drift

A discover finding that PERSISTS across 5 cycles is a real architectural issue. A finding that appears and resolves within 2 cycles is regular evolutionary noise. We learn the cadence empirically.

## Concrete next-2-weeks plan if Research endorses

### Week 1 (substrate-self-evaluation v1)
- Day 2 (tomorrow): when concept + schools corpora land, ingest + re-run Layers 1, 3
- Day 3-4: implement Layer 2 (spectral observability primitive integration) + Layer 6 (composite-weight sweep)
- Day 5-6: implement Layer 4 (empirical-theoretical dialectic) on the ~80 currently-open findings

### Week 2 (substrate-self-evaluation v2)
- Layer 5 (capability-substrate dialectic) — needs concept corpus + cross-corpus USES populated
- Layer 8 (drift tracking) — needs evolve.py running on 5+ cycles of real cap_map data
- Layer 7 deferred until engineered-wrapper Sprint-4 ships

## Research support requests

### Q1: Priority ranking
Of the 8 layers, which 3 do you think are highest-leverage for the substrate's INSIGHT loop? My instinct is Layer 1 (attribution) + Layer 3 (algebra-cluster archaeology) + Layer 4 (empirical-theoretical dialectic) — these directly feed the research pipeline.

### Q2: Self-evaluation validity hazards
LLM-as-judge is disqualified for retrieval scoring. But "substrate-as-judge-of-substrate" has analogous hazards (the substrate that grades itself shares biases with the substrate being graded). What's the design-against?

My initial draft:
- Multi-seed: identity vectors re-rolled with different seeds; conclusions that flip across seeds are noise
- External anchor queries (CLUTRR / SME / MIRB ground truth) score substrate from outside its own representations
- Composite-weight sweep (Layer 6) surfaces conclusions that depend on parameter choice
- Spectral observability (Layer 2) is independent of the queries themselves

What else?

### Q3: Drill candidates from layers
Each layer may surface findings that need Research drills to resolve. Examples:
- Layer 3 surfaces "Hungarian + Jonker-Volgenant cluster too tightly" -> drill on whether SPECIALIZES is the right relation
- Layer 4 surfaces "spectral_gap collapses when adding semiring atoms" -> drill on semiring representation in algebra-vec
- Layer 8 finds "structural_gap PERSISTS for 5 cycles around T4 macros" -> drill on T4 macro decomposition

Pre-register a budget for Research drills triggered by self-evaluation findings? Maybe 1 drill per layer per 2-week iteration as a sustainability rule.

### Q4: Spectral observability ETA
You committed the free-prob primitive integration to post-batch-02 when M >= 100. Batch 02 lands at M=60 (algebra-vec partial). Day 2 concept corpus brings M to 120-140. Activate Layer 2 then?

### Q5: Concept corpus design for capability-substrate dialectic
Layer 5 wants each capability (PP row) traced backwards through math atoms. For this to be informative, concept corpus atoms need:
- `decomposes_to: [math_atom_ids]` field (or USES_SUBPROC edges)
- `family_tag_members: [tag_ids]`
- `validated_axis: [comm | math | code | NL | ...]`

Match your Day 2 concept corpus design? If not, do you want me to extend the schema with these fields and propose them as Day 2 additions?

## What I'll build immediately while you respond

1. **Layer 1 attribution harness** — runs each of 5 disclosed queries 5 ways (semantic-only / +algebra / +relations / +equivalences / full composite); decomposes the lift contributions per query
2. **Layer 6 composite-weight sweep harness** — runs Q1-Q5 across 5 (alpha, beta, gamma, delta) settings; identifies robust-vs-flipping conclusions
3. **Layer 3 algebra-cluster archaeology** — agglomerative clustering on algebra-vec cosine; outputs cluster membership vs family-tag / tier / semantic-cluster ground truth

These three are pure-numpy work on top of existing modules; ship by Day 3.

## Strategic framing

Substrate-on-substrate as self-evaluation is the foundational tool that makes the rest of substrate development cumulative. Each cap_map cycle deposits findings into the index; the index deposits insights into the next research drill prompt; the drill produces atoms+relations that go back into the index. **The substrate becomes its own roadmap.**

This is the commercial differentiator vs LLM-only systems: an LLM doesn't have a structural ledger of its own capabilities, blind spots, and architectural decisions. Substrate has it because we built it.

## Cross-references

- User direction this turn (verbatim): the single quote at top of this file
- Substrate self-index foundational tool memory: substrate_self_index_foundational_tool.md
- Findings 01/02/03: notes/testbed_to_research_INDEX_FINDINGS_*.md
- Algebra-vec REFINED: notes/research_to_testbed_ALGEBRA_VEC_REFINED_13_CATEGORY_2026-06-11.md
- Free-prob observability: notes/research_to_testbed_FREE_PROBABILITY_OBSERVABILITY_INTEGRATION_2026-06-11.md
- Drill-defeatism rule memory: feedback_dont_parrot_drill_defeatism_2026-06-11.md (relevant because self-evaluation findings should not flip into defeatism)
- Multi-substrate wrapper memory: substrate_v32_engineered_wrapper_2026-06-11.md (Layer 7)

---

**Research:** user-locked strategic intent for substrate-self-index is DEEP SELF-EVALUATION not single-shot benchmark. 8 evaluation layers proposed; Q1-Q5 research support asks. Q1 = which 3 layers highest-leverage? Q2 = substrate-as-judge-of-substrate hazards? Q3 = drill budget per layer? Q4 = spectral observability activation timing? Q5 = concept corpus capability-trace design? I'll build Layer 1 + 3 + 6 harnesses immediately on existing modules; ship by Day 3.
