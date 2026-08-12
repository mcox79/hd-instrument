# Research: Additive vs Compositional Value of Growing Comprehension Competencies — and How to Measure It

Filed by: research (Sonnet, single-pass, no child agents per USER instruction)
Date: 2026-07-31
Trigger: motivating result — competency #2 (thematic roles) added to competency #1 (entity identity) with EXACT no-interference (entity metrics byte-identical) but only +0.015 on blended overall-comprehension metric, despite climb_role=0.045 (roles competency itself clearly learned).

KB-check: `tools/director_kb_query.py` timed out (>60s, likely cold embedding-model load) on two attempts; not re-run a third time per time budget. Manual dedup against last 5 status_log `research_delivery` entries + field advisor found no exact-topic collision. Closest adjacent prior note: `notes/research_construction_acquisition_order_seed_and_ladder_2026-07-31.md` (developmental ORDER of competencies: reference→roles→coreference→non-canonical-order→...). This note is complementary — it addresses MEASUREMENT of value as competencies are added, not acquisition order. Also builds on `notes/research_cross_frame_entity_stability_lever_2026-07-31.md` (entity mechanism) and the voice-invariant-role notes (role mechanism).

---

## HEADLINE

**VERDICT: COMPOSITIONAL / MULTIPLICATIVE, not additive — and the +0.015 blended-metric result is very likely a MEASUREMENT ARTIFACT (dilution), not evidence the role competency has low value.** The strongest single piece of evidence is Gough & Tunmer's (1986) Simple View of Reading, `RC = D × LC` — decoding and language comprehension combine **multiplicatively**, not additively, and a near-zero score in either factor collapses the product regardless of the other factor's strength. Kintsch's Construction-Integration (C-I) model gives the mechanism: comprehension is a two-phase process (construction → integration) that ends in constraint-satisfaction over a **situation model**, i.e., partial component representations only become "comprehension" once integrated into a unified whole — an unintegrated correct-but-idle role representation contributes ~0 to any query that doesn't require it, and a lot to queries that do. This is structurally a **bottleneck/AND-gate**, not a **sum**.

---

## Cheap decisive test (pre-registered, run before further competency work)

**Test**: Partition the existing/planned query set into (a) role-INDIFFERENT items (name-maintenance items that don't require thematic-role disambiguation to answer) and (b) role-CRITICAL items (competitive-coreference / overwrite items where two candidate entities are only disambiguated by agent-vs-patient role). Recompute the blended metric split by these two buckets, with-roles vs without-roles.

- **HARD-PASS** (compositional/bottleneck confirmed, +0.015 is a dilution artifact): role-CRITICAL bucket shows a **large** lift (predict ≥0.15–0.25 absolute, i.e. 10–15x the blended lift) while role-INDIFFERENT bucket shows ~0 lift (≤0.02). This reproduces the Simple-View-of-Reading signature: a component only pays off where the task's structure requires it.
- **HARD-FAIL** (additive confirmed, roles genuinely low-value): role-CRITICAL bucket lift is also small (≤0.03, same order as blended), i.e. even on items that supposedly REQUIRE role information, the role competency isn't cashing in. This would mean the +0.015 is real and roles are weakly useful even where they should matter most — a genuine capability gap, not a measurement artifact.
- **MIDDLE-BAND**: role-CRITICAL lift is moderate (0.05–0.15) — partial compositional signal, worth a second design pass (see below) before concluding either way.

This test uses data/metrics you already have logged (no new training run) — it should be near-zero-cost to run before any further competency (#3 coreference) work is designed.

---

## 1. Biology/psycholinguistics drilled

### 1.1 Simple View of Reading (Gough & Tunmer 1986) — the direct answer to additive-vs-multiplicative

`RC = D × LC` (Reading Comprehension = Decoding × Language/Listening Comprehension), each factor scaled 0–1. Confirmed via web search (readingrockets.org, structural-learning.com, journals.sagepub.com/doi/10.1177/074193258600700104 — the original Gough & Tunmer 1986 "Decoding, Reading, and Reading Disability"). Key properties, all directly relevant:
- **Multiplicative, not additive**: "a weakness in one area impacts the outcome... if either skill is zero, the entire product is zero." A component near zero doesn't get averaged away by a strong partner — it zeroes the whole output on tasks that need both.
- **No compensation between components** — this is the opposite of what a blended additive metric implicitly assumes (that a gain in component B can offset/average against component A regardless of task structure).
- This is the field's canonical answer to "how do you aggregate two comprehension sub-skills" and it is emphatically NOT a weighted sum.

Deflation note: Simple View of Reading is about DECODING × COMPREHENSION at the whole-reading-system level, not about two comprehension sub-competencies (entity-ID and role-ID) both inside "comprehension." The generalization from D×LC to competency-A×competency-B within comprehension is an ANALOGY, not a direct citation match — flagged as strategic-read, not literature-proven at that grain. But the qualitative lesson (bottleneck/AND-structure between components that jointly gate a downstream product) transfers cleanly because both are cases of a pipeline where one stage's OUTPUT is a necessary INPUT to the next stage's function.

### 1.2 Kintsch Construction-Integration model — the mechanism for WHY it's multiplicative/bottlenecked

C-I (Kintsch 1988, 1998; Kintsch & Rawson chapter, sites.pitt.edu/~perfetti) has three representation levels: **surface structure** (words/syntax) → **textbase** (propositions, locally connected) → **situation model** (integrated mental model, fused with prior knowledge). Two phases:
- **Construction**: activates a loosely-connected, over-inclusive network of candidate propositions/word senses (including irrelevant ones) — this is closest to what independent per-competency representations look like (entity reps + role reps existing in parallel, unintegrated).
- **Integration**: a constraint-satisfaction spreading-activation process prunes incoherent activations and strengthens mutually-consistent ones into the final situation model — this is where separate representations are FUSED into the thing that actually answers a comprehension query.

Implication: two components (entity-ID, role-ID) that are each separately "correct" in the construction phase contribute to comprehension **only through what integration does with them**. If the query/probe doesn't exercise the constraint-satisfaction that needs BOTH signals together, a correct-but-unintegrated role signal is functionally inert for that query — exactly what would produce a small blended lift with byte-identical entity metrics (no interference, but also little synergy captured by the blend).

Deflation: C-I is a model of within-sentence/paragraph micro-processing, largely validated via reading-time and recall-probe studies, not directly measured as "additive vs multiplicative accuracy gain from adding a skill module" — again an architecture-level analogy, moderately strong (P~0.55 as literal mechanism match) but very strong as a qualitative argument for compositional aggregation over additive blending.

### 1.3 Construction-grammar parasitism / scaffolding (Tomasello)

Confirmed via search (Tomasello "Construction Grammar for Kids," MPI EVA PDF; academia.edu Construction Grammar and First Language Acquisition): children build item-based "verb island" constructions first, then generalize by analogy to more abstract constructions — later, more abstract constructions are built ON TOP OF earlier item-based ones ("children move by analogy from item-based phrases... to richer constructions"). This is consistent with — but the search results explicitly note they found no direct hit on the word "parasitic" — the general construction-grammar claim (Goldberg, Diessel) that complex constructions (relative clauses, passives, multi-clause coordination) formally and developmentally PRESUPPOSE simpler constituent constructions (NP, transitive clause) as their building blocks; you cannot represent a passive-voice role-reversal without first having a stable transitive-clause role representation to invert.

Direct relevance to your library: cross-sentence coreference (planned competency #3) is definitionally parasitic on entity representations (a pronoun/np needs an ANTECEDENT ENTITY to resolve to — competency #1) and, for competitive/role-based disambiguation ("the boy chased the girl... she caught him" — who is "she"?), on thematic-role representations (competency #2) to know WHICH entity plays WHICH part in the current clause, hence which one satisfies gender/role/plausibility constraints on the pronoun. This is a hard **presupposition** relationship, not merely additive: without #1 there is nothing to corefer TO; without #2 many hard cases (role-competitive coreference) are unresolvable in principle no matter how good coreference-machinery itself is.

Deflation: the "presupposition" argument is logically airtight for the STRUCTURAL claim (coref needs an entity representation to exist) but the strength of the DEPENDENCY on roles specifically (vs. e.g. recency/gender heuristics alone) is graded and item-dependent — only role-COMPETITIVE coreference items strictly need #2; many easy coref items (unambiguous gender, no competing antecedent) don't. This item-dependence is exactly why blended aggregate metrics wash out compositional effects — most items in a naturalistic blend don't require the harder joint mechanism.

### 1.4 Perfetti Lexical Quality Hypothesis / Verbal Efficiency Theory — bottleneck vs additive at the mechanism level

Confirmed via search (academia.edu "From Verbal Efficiency Theory to Lexical Quality"; researchgate "Lexical Quality Hypothesis"). Key claims:
- Higher-order comprehension (sentence integration, inference) **depends on** efficient/accurate lower-level lexical access — a classic layered/gating dependency, not parallel-additive contribution.
- "The lexical bottleneck account of reading posits that lexical quality shapes both the time course and the EFFECTIVENESS of context use" — i.e., a weak lower component doesn't just subtract a fixed amount from comprehension, it changes how MUCH the higher-level machinery can even use context/other signals (a multiplicative-style interaction, component B's marginal value depends on component A's level).
- This is a second independent literature (individual-differences reading research) converging on the same qualitative structure as Simple View of Reading: components GATE each other rather than summing.

### 1.5 Zwaan & Radvansky Event Indexing Model (situation-model updating) — from training knowledge, not separately web-confirmed this pass, flagged accordingly

Event Indexing Model (Zwaan, Magliano & Graesser 1995; Zwaan & Radvansky 1998) proposes readers track five situational dimensions simultaneously — **protagonist/entity**, space, time, causation, intentionality/motivation — and comprehension updates (measured via reading-time cost) occur when a NEW sentence shifts one or more of these dimensions relative to the current situation model. Entity-tracking and (agent/patient-role-flavored) protagonist-tracking are explicitly two of the five monitored dimensions, and the model's central claim is that comprehension COST/DIFFICULTY is driven by DISCONTINUITY across dimensions jointly — i.e., the situation model is a genuinely multi-dimensional integrated object, and a probe that only exercises one dimension (pure entity re-ID) will not reveal the model's sensitivity to a second dimension (role) unless the probe is specifically constructed to require joint tracking (e.g., role reversal combined with entity continuity — which is exactly what "competitive coreference" items are). This is a direct theoretical argument for exactly the measurement redesign recommended below. Confidence flagged lower (P~0.45) since not independently re-verified via search this pass (search returned only NLP/coreference-resolution engineering hits, not the cognitive-psych original); recommend a follow-up citation check if this claim becomes load-bearing for a HARD-PASS threshold.

---

## 2. Why the +0.015 is small: measurement artifact vs capability issue

Given the above, the diagnosis is: **primarily a measurement (aggregation) issue, with a residual open question about whether the role competency is ALSO under-trained.**

Reasoning:
1. Byte-identical entity metrics with/without roles is strong evidence of clean modularity (no destructive interference) — rules out "roles broke something."
2. climb_role=0.045 on the role-specific metric shows the role competency itself DID learn something real and non-trivial in isolation.
3. The blended "overall" metric spans 3 query types (name-maintenance, competitive-coreference, overwrite) — per the Simple-View / C-I / Event-Indexing arguments above, only a SUBSET of these items (plausibly just "competitive-coreference," and only the role-competitive subset of it) structurally REQUIRES the role signal to be answered correctly. If, say, only 20-30% of blended items are role-critical, then even a large true effect on those items (e.g. 0.15-0.30 absolute) gets diluted by averaging with the 70-80% of items where role information is causally irrelevant to the answer — arithmetically producing a small blended delta. This is the textbook additive-blend-hides-compositional-effect failure mode the cited literature predicts.
4. This is NOT yet proven — it's the falsifiable HARD-PASS/HARD-FAIL prediction in the Cheap Decisive Test above, which should be run on already-logged metrics before concluding either way. If the role-critical subset ALSO shows only a small lift, then the diagnosis flips to a genuine capability issue (the role competency, though "learned" on its own isolated metric, isn't yet functionally USABLE by the integration/query-answering machinery — which would itself be a valuable, differently-actionable finding, closer to a wiring/integration gap than a training gap).

---

## 3. Recommended measurement redesign

**Stop scoring the growing library primarily on a blended additive metric. Move to a two-tier measurement:**

**Tier A — Modularity/non-interference check (keep this, it's working and important):** per-competency isolated metric (entity_consistency, climb_role, etc.) plus a hard no-interference gate (earlier competencies' metrics must stay ~byte-identical when a new one is added). This protects against regressions and is itself brain-inconsistent-with-additive-blend but IS consistent with modular, separately-trainable "construction competencies" (per the growing-library-of-competencies framing already adopted) — keep it as a SAFETY gate, not the value metric.

**Tier B — Composition/bottleneck value metric (NEW, primary "is this competency worth having" signal):** hand-construct or auto-tag a **composition-requiring item subset** per new competency — items that are, by construction, UNANSWERABLE (or answerable only at chance) without the new competency's signal jointly with prior ones. Score value as the delta on THIS subset, not the full blend. This is the direct analogue of Simple-View-of-Reading's D×LC structure applied at the competency-library level: report competency value as "lift on the AND-gated subset," and treat the full blended score as a secondary sanity/regression check only.

**Concrete design for competency #3 (cross-sentence coreference, requires entity+roles):**

1. **Tag every coref item at construction time by REQUIRED-COMPETENCY-SET**, not after the fact:
   - Tier 0 (entity-only): single unambiguous antecedent, no competing referent, no role ambiguity. Should be solvable by #1 alone.
   - Tier 1 (role-competitive): two+ candidate antecedents distinguished ONLY by which one filled which thematic role in the referring clause (e.g., "The boy chased the girl. She stopped and turned around." — resolving "she" requires knowing who was agent/patient, not just who exists). Requires #1 AND #2 jointly — this is the compositional/bottleneck bucket.
   - Tier 2 (role-reversal-under-coref): antecedent clause is passive/non-canonical order AND coref crosses it (compounds the still-open voice-invariant-role wall from prior notes) — deliberately the hardest bucket, should be near-chance until BOTH entity+role+voice-invariance are solid.
2. **can-fail HARD-PASS / HARD-FAIL for competency #3, using the bottleneck framing (not additive margin):**
   - **HARD-PASS**: Tier-1 (role-competitive coref) accuracy ≥0.70 AND Tier-1 accuracy with roles-competency ABLATED (or pre-role-competency checkpoint) falls to ≤0.55 (near a no-role-info baseline/chance-adjusted floor) — i.e., demonstrate the AND-gate empirically: coref only works when roles are present, on exactly the items that need it. Tier-0 items should show no regression (≥ pre-coref baseline, modularity check from Tier A).
   - **HARD-FAIL**: Tier-1 accuracy stays ≤0.55 even WITH roles present (coref can't cash in the role signal it's given — an integration/wiring gap, not a training-data gap), OR Tier-1 accuracy is high but changes negligibly (≤0.05) between roles-present and roles-ablated (would mean the model is solving Tier-1 items via some OTHER shortcut — e.g. recency — not actually using role information; a construction-validity failure of the item set itself, flagged in [[feedback_synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data_2026-07-17]]).
   - **MIDDLE-BAND**: Tier-1 lift from roles is present but modest (0.10–0.20 absolute) — partial compositional use, worth drilling whether it's a training-amount issue (role competency undertrained) vs a genuine partial-dependency (some Tier-1 items solvable via recency alone even without roles).

3. **Change the HARD_PASS metric definition going forward**: from "additive margin on blended overall score" to **"lift on the AND-gated (bottleneck) subset, ablation-verified."** The ablation check (with vs without the dependency competency, on the SAME held-out bottleneck items) is the critical addition — it's what turns "correlation with a hard subset" into a genuine causal/compositional demonstration, and it's cheap (just needs the pre-roles checkpoint you already have banked).

---

## 4. Substrate-product implications

- The growing-library-of-competencies framing (already adopted, feedback slug `feedback_comprehension_is_a_growing_library_of_construction_competencies...`) is validated at the MECHANISM level by construction-grammar parasitism (§1.3) — competencies genuinely do build hierarchically, so "modular, separately-learnable, non-interfering" is the right shape.
- But the VALUE claim about a library needs the bottleneck reframe: a competency's product-relevant value shows up on tasks that STRUCTURALLY REQUIRE it, not as a uniform lift across all comprehension. This matters directly for glass-box interpretability too — a bottleneck metric gives you a legible causal story ("coref fails specifically on role-competitive items, and specifically because role info isn't reaching the coref mechanism") vs. a blended score which is diagnostically mute.
- Immediate action before starting competency #3 build: re-score the ALREADY-LOGGED #1+#2 metrics split by the role-critical/role-indifferent item partition (the Cheap Decisive Test above) — this is near-zero-cost and will directly settle whether the current +0.015 undersells the role competency's real value or accurately reflects a genuine weak spot, before any further roles-competency investment is made.

---

## Citations (verified count: 5 web-confirmed / 1 training-knowledge unconfirmed-this-pass)

Verified via WebSearch this session:
1. Gough, P.B. & Tunmer, W.E. (1986). "Decoding, Reading, and Reading Disability." *Remedial and Special Education*, 7(1). https://journals.sagepub.com/doi/10.1177/074193258600700104 — Simple View of Reading, RC=D×LC, multiplicative structure confirmed.
2. Kintsch, W. — Construction-Integration model; three-level representation (surface/textbase/situation model), construction+integration phases, constraint-satisfaction. Confirmed via multiple secondary sources incl. Kintsch & Rawson chapter (sites.pitt.edu/~perfetti/PDF/Kintsch%20&%20Rawson.pdf) and readlite.in summary.
3. Tomasello, M. — "Construction Grammar for Kids" (MPI EVA); verb-island constructions, item-based-to-abstract generalization by analogy. https://www.eva.mpg.de/documents/... confirmed.
4. Perfetti, C. — Lexical Quality Hypothesis / Verbal Efficiency Theory; lexical bottleneck account, comprehension depends on efficiency of lower-level access. Confirmed via academia.edu "From Verbal Efficiency Theory to Lexical Quality."
5. (Search infrastructure note) — Simple View of Reading secondary confirmations: readingrockets.org, structural-learning.com, gcu.edu blog, lexialearning.com — consistent multiplicative-structure description across all.

Not independently re-verified this pass (training-knowledge, flagged, recommend follow-up if load-bearing):
6. Zwaan, R.A., Magliano, J.P. & Graesser, A.C. (1995); Zwaan, R.A. & Radvansky, G.A. (1998). Event Indexing Model — five situational dimensions (protagonist, space, time, causation, motivation), situation-model updating on dimensional discontinuity. Search returned only NLP-engineering hits, not the cognitive-psych originals.

## P_deflated

P(compositional/multiplicative verdict is correct, applied at our specific competency-library grain) = **0.55** (down from a naive high-confidence read given: (a) Simple View analogy is cross-grain, (b) C-I mechanism match is architecture-level not literal, (c) Event Indexing citation unconfirmed this pass, (d) lit-scan calibration penalty −0.15 to −0.20 applied per standing discipline). Capped well below 0.50 novel-synthesis ceiling is NOT triggered here since this is lit-grounded convergent-evidence synthesis, not novel mechanism invention — 0.55 reflects genuine multi-literature convergence (4 independent psycholinguistic literatures all point the same direction) offset by cross-grain analogy risk.

P(the Cheap Decisive Test, once run on existing logged metrics, will show the HARD-PASS pattern — large lift on role-critical subset, ~0 lift on role-indifferent subset) = **0.45** (genuinely uncertain pending the actual re-slice; this is the falsifiable prediction, not asserted as already-true).
