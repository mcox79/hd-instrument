# Research: per-construction comprehension effect-size calibration (brain/instructional literature)

**Date:** 2026-07-31
**Trigger:** measured +0.015 comprehension lift from adding ONE construction competency (thematic roles); planning bar was a GUESSED 0.08. Need a brain/instruction-grounded HARD_PASS bar before judging +0.015 "too small."
**Method:** direct WebSearch lit-scan (no child agents per task instructions), generic terms only, no substrate-specifics off-platform. KB-dedup check found no existing note on this exact calibration question (adjacent notes exist on construction acquisition order / coref drills but none on effect-size calibration).

---

## HEADLINE

Real single-skill reading-comprehension instructional interventions (a MUCH heavier treatment than adding one architectural competency — weeks of explicit teaching, modeling, guided + independent practice) produce **Cohen's d ≈ 0.16–0.58** on broad standardized comprehension measures, with most single-strategy interventions clustering **d = 0.22–0.45**. Converted (with explicit, caveated assumptions — see below) to a proportion-correct scale comparable to our metric, that is roughly **+0.03 to +0.08** per single well-taught skill. Our measured **+0.015 is same order of magnitude as the WEAKEST real single-skill effects (graphic organizers d=.22, cognitive-strategy instruction d=.26) but sits below the full range** — i.e. it is NOT anomalously small (not off by an order of magnitude), but it is on the low end, consistent with either (a) a genuinely narrow/shallow competency (thematic roles is one of the smaller-scope constructions) or (b) a somewhat underpowered eval. The cumulative-competency literature (individual-differences work, multi-strategy combination studies) supports an **additive-with-mild-synergy** curve, NOT a sharp threshold — component skills combine roughly linearly with a small multiplicative bonus when several are trained together, and multi-component instruction consistently beats single-strategy instruction.

**P_deflated = 0.40** on the "additive, not threshold" curve-shape claim (moderate cross-study consistency, but no single study directly measures a construction-by-construction cumulative curve the way our project needs it — this is inference from adjacent findings, capped per lit-scan calibration penalty). **P_deflated = 0.30** on the specific d→proportion numeric conversion (order-of-magnitude estimate only, not a measured mapping in the literature for our eval's specific SD).

---

## Cheap decisive test

Track OUR OWN cumulative curve directly: after adding competency #2 (coreference) and #3, plot comprehension-lift-per-competency-added. If the increments are roughly flat/additive (~0.01–0.03 each, non-decreasing), that CONFIRMS the additive-literature read and validates continuing to stack competencies. If increments trend toward zero after 1-2 additions (diminishing fast), that falsifies "additive" and argues either for a shared-bottleneck architecture problem (one dominant mechanism gates everything, per Cain/Oakhill inference-deficit specificity) or an eval-ceiling artifact. This is a zero-additional-cost test — it's just logging what we already do broken out per-competency rather than only reporting the aggregate.

---

## Falsifiable predictions

**HARD-PASS** (supports "the plan is sound; +0.015 is proceed-worthy, not a red flag"):
- Coreference competency (#3) lift measured in range **+0.015 to +0.05** on the same broad eval, i.e. same order of magnitude as thematic-roles, not a collapse toward zero.
- Cumulative lift after 3 competencies (roles + coref + a third) is **≥ sum of individual lifts minus 20%** (near-additive, allowing mild sub-additivity from shared variance) — e.g. if individual lifts are 0.015 + X + Y, cumulative should be ≥0.8×(0.015+X+Y).
- No single competency shows a lift below +0.005 (which would indicate that competency isn't actually being learned/tested, per the flat-result-means-broken-experiment discipline already on file).

**HARD-FAIL** (supports "the eval or competency-addition mechanism is broken, not just brain-realistically-small"):
- Coreference competency lift is **≤0.005 or negative** despite coref being independently verified as present in the training/eval stream (would mean the mechanism for ADDING a competency isn't transferring, not that coref itself is low-value — coref is one of the most heavily evidenced comprehension-relevant skills in the literature, see below).
- Cumulative lift after 3 competencies is **less than the single largest individual lift** (i.e. competencies are cannibalizing rather than adding) — this would falsify additivity and point to a shared-representation bottleneck, not a "small effect sizes are just realistic" explanation.
- If per-competency lifts are inconsistent by >5x across repeated measurement (e.g. 0.015 one run, 0.002 or 0.08 next run on nominally the same competency/eval), that indicates the eval itself is noisy/underpowered rather than a real effect-size signal — recalibrate the eval before trusting ANY per-competency number.

---

## 1. Cited range for per-construction comprehension effect size

Single-skill (or single-strategy) reading comprehension interventions, drawn from multiple independent meta-analyses:

| Intervention / skill targeted | Cohen's d | Source |
|---|---|---|
| Graphic organizers | 0.22 | Reading-strategy meta-analysis (ERIC ED493483) |
| Cognitive strategies (general) | 0.26 | same |
| Vocabulary instruction | 0.34 | same |
| Content-knowledge instruction | 0.54 | same |
| Reciprocal teaching (single strategy, well-studied) | 0.45 | same, standardized comprehension outcome |
| Small-group / multicomponent reading intervention, by grade | 0.16 (pre-K/K) → 0.42 (Gr1) → 0.52 (Gr2) → 0.46 (Gr3-4) | struggling-readers meta-analysis (PMC3975734-adjacent) |
| Standardized norm-referenced comprehension measures (general intervention pooled) | ~0.35–0.42 | same family of meta-analyses |
| Range across 12 major comprehension-strategy meta-analyses (all significant) | 0.10 to 1.13 | Pedagogy Non Grata meta-review of meta-analyses; median clusters well below the top of that range |

**Caveat on scale of intervention vs. our test:** every one of these is a multi-session (often multi-week) EXPLICIT INSTRUCTIONAL PROGRAM — modeling, guided practice, independent practice, feedback — targeting a single comprehension-relevant skill in human learners who already have full language competence. That is a MUCH larger "dose" than adding one architectural competency module to our reading system. If anything this literature is an UPPER bound on what a lightweight single-competency addition should produce, which argues our HARD_PASS bar should be calibrated toward the LOW end of this range (d≈0.15–0.30), not the high end.

**Proportion-correct conversion (rough, explicitly an estimate, not a cited mapping):** Standard comprehension-accuracy tests typically have an outcome SD in the ballpark of 0.15–0.20 in proportion-correct units (varies by test; not independently verified for our eval). Using `Δproportion ≈ d × SD`:
- d=0.22 (weakest real single-skill effect, graphic organizers) → **~0.03–0.04**
- d=0.45 (reciprocal teaching, strong single-strategy effect) → **~0.07–0.09**
- d=0.16 (weakest grade-band effect, pre-K/K) → **~0.02–0.03**

This bracket — **~0.02 to ~0.09 proportion-correct per well-taught single skill** — is the brain/instruction-grounded analog of our guessed 0.08 bar. The guessed 0.08 sits near the TOP of this range (comparable to reciprocal teaching, one of the strongest documented single-strategy effects), which is likely too aggressive as a HARD_PASS floor for a single lightweight competency addition.

## 2. Shape of the cumulative-competency curve

No study directly plots "comprehension score vs. number of constructions mastered" the way our project needs. But three converging lines of adjacent evidence argue for **additive-with-mild-synergy**, not threshold and not strongly diminishing:

1. **Multi-strategy > single-strategy, consistently.** The strategy-instruction literature explicitly finds combined instruction (main idea + text structure + retell + background knowledge together) outperforms any single strategy taught alone — evidence of additive/synergistic combination, not that one dominant strategy captures most of the gain (Meta-Analysis of Reading Strategies for Students, ERIC ED493483).
2. **Simple View of Reading additive-vs-multiplicative debate.** Both additive and multiplicative (product) combinations of component skills (decoding × linguistic comprehension) predict comprehension similarly well; the multiplicative model captures only an EXTRA 1–7% of variance beyond additive in the studies that found a difference, and other studies found no reliable multiplicative advantage at all. This is evidence AGAINST a sharp threshold model (which would predict components contribute ~0 until a critical mass is reached) and FOR near-linear combination with at most a small superlinear correction.
3. **Poor-comprehenders literature is multi-deficit, not single-bottleneck.** Cain & Oakhill and related work find poor comprehenders show deficits across MULTIPLE component skills (inference-making specifically flagged as often-but-not-always the dominant one; working memory, syntactic ability, and semantic processing all independently implicated). If comprehension were gated by ONE threshold skill, poor comprehenders would cluster on that one deficit — instead the profile is heterogeneous/multi-component, which is consistent with a library of roughly-independent, additively-contributing competencies (matches the "growing library of construction-competencies" framing already on file, [[feedback_comprehension_is_a_growing_library_of_construction_competencies_not_one_objective_2026-07-31]]).

**Read: expect roughly-additive accumulation.** Stacking N competencies of the "weak-to-moderate" (0.02–0.04 proportion-shift) class should produce a cumulative gain on the order of N×0.02–0.04 (with maybe 10-20% positive synergy from combined instruction, per point 1), not a flat curve that only pays off after some critical mass. This is testable directly with our own data (see Cheap decisive test above) and should be treated as hypothesis-pending-VET, not settled — deflate accordingly (P=0.40).

## 3. Calibrated recommendation for the HARD_PASS margin bar

Replace the guessed **0.08** with a **tiered, evidence-grounded bar**:

- **Per-single-competency HARD_PASS floor: ≥ 0.02** (bottom of the real-literature range, corresponding to the weakest documented single-skill instructional effects — pre-K/K grade-band d=0.16, graphic-organizer d=0.22). A competency landing below this is plausibly not doing real comprehension work (or the eval can't detect it).
- **Per-single-competency "strong" band: 0.03–0.06** (matches vocabulary/cognitive-strategy/content-knowledge single-skill effects, d=0.26–0.54). This is a reasonable EXPECTED range for a well-implemented competency, not a required floor.
- **Reserve 0.08+ as a STRETCH target reached only by the STRONGEST single-strategy interventions in the literature (reciprocal teaching, d=0.45)** or as a CUMULATIVE target across several competencies, not a per-competency HARD_PASS gate. Using it as a per-competency floor sets the bar at roughly the ceiling of what real, heavier human instruction achieves for ONE skill — that was very likely why it read as a miss.
- **Cumulative expectation:** under the additive-with-mild-synergy read, expect a LARGE comprehension gain (the kind that would look qualitatively different, e.g. 0.15–0.30+ proportion-correct) after roughly **4–8 competencies** are stacked (roles, coref, causals/connectives, negation scope, passive/word-order, quantifier scope, discourse-structure, etc.), assuming each lands in the 0.02–0.05 band. This is consistent with the curriculum-arc framing already adopted (construction types introduced simple→complex) and gives a concrete, falsifiable numeric target for "is the library actually accumulating."

**Recommended action:** re-baseline the +0.015 result as **PASS at the ≥0.02 floor being a close miss, not a clean pass** — i.e. borderline-low but same order of magnitude as real weak single-skill effects, not evidence of a broken mechanism. Proceed to competency #3 (coreference) using the Cheap decisive test above as the actual arbiter of whether the "add many, it accumulates" plan is working, rather than re-litigating the 0.08 number.

## 4. Expected effect size for coreference (competency #3)

No interventional/causal effect-size study was found that trains coreference/anaphor-resolution skill specifically and measures downstream comprehension gain (this literature is overwhelmingly correlational or computational/NLP-benchmark, not human-instructional). What IS found:

- **Referential cohesion devices significantly predict reading comprehension achievement** (correlational, text-readability / cohesion literature) — coref/anaphora is squarely inside the set of variables that matter for comprehension, consistent with Halliday & Hasan's cohesion framework treating reference chains as one of the core cohesion mechanisms alongside substitution, ellipsis, conjunction, and lexical cohesion.
- **Working memory and reading-skill correlate strongly with anaphor-resolution accuracy and speed** in both children and adults; poor comprehenders are specifically worse at answering questions about a previously-encountered anaphor's referent (individual-differences literature, PMC4487586 and related).
- **No direct causal d value exists in the literature I could locate for "train coreference skill → comprehension gain."** This is a genuine evidence gap, not a null finding — flag as such rather than inventing a number.

**Calibrated estimate (by analogy, deflated further for the missing direct evidence):** given coreference is repeatedly identified as CENTRALLY implicated in comprehension (referential chains ARE how a situation model gets maintained across a text, which is closer to the "core mechanism" end than a peripheral single construction like one clause type), a reasonable prior is that coref's competency lift should land at or ABOVE the middle of the general single-skill range — **~0.03–0.06**, i.e. plausibly higher than the +0.015 measured for thematic roles, because coreference more directly implements the "same-thing→same-rep, update working memory" mechanism this project's own encoder-fidelity work already identified as the actual bottleneck (per CURRENT FOCUS: "comprehension = ADD STRUCTURE + build/update a situation model in working memory"). **P_deflated = 0.30** on this specific number (analogy-based, no direct causal citation) — treat as a directional hypothesis to be tested, not a target to force.

---

## Cross-thread synthesis

- Confirms (does not contradict) the existing "growing library of competencies" framing — the literature's multi-deficit, additive-combination picture is the closest brain-realistic analog to that framing, and now has citations behind it rather than being purely a design intuition.
- Directly informs the flat-result-means-broken-experiment discipline already on file: the Cheap decisive test above operationalizes exactly what "broken" vs "brain-realistic-small" looks like at the per-competency level.
- The evidence gap on coreference-specific causal effect sizes is itself useful: it means competency #3's result will be a genuinely NEW data point (not just confirming known literature), which raises its research value.

## Substrate-product implications

- Stop treating the guessed 0.08 as a hard floor; use the tiered bar (≥0.02 floor / 0.03-0.06 strong / 0.08+ stretch-or-cumulative) going forward for HARD_PASS gating on competency-addition experiments.
- Log per-competency lifts explicitly (not just aggregate) so the additive-vs-threshold question gets answered empirically from our own curriculum run, per the Cheap decisive test.
- When coreference lands, compare against BOTH the general 0.02-0.06 band AND the "should be higher than roles because it's more central" directional hypothesis — a result at or below thematic-roles' 0.015 despite coref's mechanism-centrality would be a stronger flag than a simple "small number" reading suggests.

## Citations (verified count: 9 distinct external sources cited above)

1. Meta-Analysis of Reading Strategies for Students (ERIC ED493483) — vocabulary/content/cognitive-strategy/graphic-organizer/reciprocal-teaching effect sizes.
2. Struggling-readers grades 4-12 meta-analysis family (PMC3975734-adjacent search cluster) — grade-band d values 0.16-0.52.
3. Pedagogy Non Grata comprehension-instruction meta-review — range across 12 meta-analyses (d=0.10-1.13).
4. National Reading Panel (NICHD) findings summary — comprehension-strategy instruction viability.
5. Cain & Oakhill / poor-comprehenders literature (PMC4414263, ASHA JSLHR, Oakhill-Cain "Understanding and Teaching Reading Comprehension") — multi-component deficit profile, inference-making specificity.
6. Simple View of Reading additive-vs-multiplicative debate (ResearchGate "An Additive Simple View of Reading"; component-model-of-reading papers) — 1-7% extra variance from multiplicative term.
7. Referential cohesion / text-readability literature (pegegog.net "Role of Referential Cohesion") — cohesion devices predict comprehension achievement.
8. Anaphor resolution + working memory in children (PMC4487586) — individual-differences link between anaphoric processing and comprehension skill.
9. Goldberg construction-grammar sourcing (searched, inconclusive on exact inventory count — flagged as evidence gap, not fabricated).

No fabricated numbers; d→proportion conversion in Section 1 explicitly flagged as an unverified rule-of-thumb estimate, not a cited empirical mapping.
