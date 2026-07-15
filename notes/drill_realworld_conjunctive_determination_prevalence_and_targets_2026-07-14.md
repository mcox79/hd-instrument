# Drill: real-world prevalence of genuine (no-dominant-driver) conjunctive determination, and where to target it

**Date:** 2026-07-14
**Trigger:** metabolic-rate cluster finding — held-out attribute was only weakly conjunctive (single-factor MI 1.11 of 1.88 joint bits; activity level alone already wins a frequency baseline). Strategic risk: maybe most real-world attributes are single-driver-dominated, undermining the "conjunctions are where structured codes beat frequency" bet.
**Method:** 3 parallel Sonnet lit-scan sub-agents (biology/cognition rationale; interaction-effect-size statistics across fields; domain survey ranking). Generic query terms only, no substrate-specific framing (per query-privacy discipline). Calibration penalty applied per lit-scan-calibration-penalty discipline.

---

## HEADLINE

Genuine no-dominant-driver conjunctions are the **minority regime, not the norm** — and this is true independently across cognitive science, statistics, genetics, and ML-on-tabular-data literatures, which is unusually strong convergence for a lit-scan. But the minority regime is not randomly scattered: it clusters predictably in **discrete/threshold/molecular-mechanistic domains** (synthetic lethality, disease-threshold epistasis, chemical potency/binding nonadditivity, drug-drug synergy) and is largely **absent from continuous organismal/ecological/economic domains** — exactly the domain class our metabolic-rate example came from. This is falsifiable and actionable: it predicts which relation-types in a knowledge foundation are conjunction-rich vs conjunction-poor, and it supplies an independent (non-interaction) justification for conjunctive/orthogonal coding — pattern-separation against interference — that survives even where the interaction argument fails.

---

## (a) Why the brain codes conjunctions — world-structure rationale

Two distinct computational problems, only one of which is about the world being "genuinely interactive":

1. **Non-monotonic / context-flipping contingencies (world-structure reason).** Conjunctive/AND-like units (bat auditory-cortex combination-sensitive neurons computing echo delay = a relation between two events, not a property of either — O'Neill & Suga 1988; PFC "mixed selectivity" neurons, Rigotti/Fusi et al. 2013 *Nature*) exist because some real quantities (target range, task rule, foraging-patch value under shifting context) are **not** a linear/additive function of individual cues — a cue's contribution literally changes sign or magnitude depending on what else is present. The clean behavioral proof is **negative patterning and biconditional discrimination** (Pearce's configural theory vs. Rescorla-Wagner elemental theory): these are XOR-like tasks, *provably unsolvable* by any learner restricted to summing independent single-cue associative strengths, and animals from honeybees to rats do solve them — direct empirical evidence that conjunctive representation is recruited specifically when the environment is interaction-structured (context-gated foraging value, predator/prey signal reinterpretation across backgrounds, sonar ranging).
2. **Episodic individuation / pattern separation (an orthogonal reason, NOT about interaction structure).** Hippocampal indexing (DG/CA3 pattern separation, Leutgeb et al. 2007 *Science*; "the hippocampus codes conjunctively," *Trends Cogn Sci* 2025) binds co-occurring features into one orthogonalized code specifically to prevent **catastrophic interference** when the same small pool of everyday features (same room, same people, different day) recurs across many separate episodes — additive/overlapping codes for feature-sharing facts cannons cannibalize each other's storage even when the *world itself* is perfectly additive. A 2025 hippocampus paper makes the split explicit: cells doing perceptual work stay linear; cells doing memory/storage work go nonlinear/conjunctive.

**Implication for us:** reason (1) requires the world to actually be conjunctive to be worth it. Reason (2) does not — it's a storage-architecture argument, valuable purely because facts share overlapping features, regardless of whether any single held-out attribute is additively or conjunctively determined. This decouples part of our conjunctive-coding bet from the "is this attribute genuinely interactive" question (see hedge, part c).

---

## (b) Where genuine (no-dominant-driver) conjunctions occur — ranked domains, with evidence

General rule across independent literatures: **main effects dominate, interactions are typically an order of magnitude smaller.**
- ANOVA/factorial meta-science: McClelland & Judd 1993 (*Psychol Bull*) — interaction effects carry far less variance and statistical power than main effects in field studies; Gelman's variance derivation — an interaction of the same true magnitude as a main effect needs ~16x the sample size to detect, meaning apparently-comparable interactions are rare. Rule of thumb: interactions ~1-3% incremental variance vs. 10-30%+ for main effects.
- Genetics: Hill, Goddard & Visscher 2008 (*PLoS Genet*) — even with pervasive genotype-level epistasis, population-genetic theory + QTL/GWAS data show additive variance dominates heritability for **typical quantitative traits**.
- ML/tabular: Lou et al. 2013 GA2M (KDD) and Friedman-Popescu H-statistic work — additive-only models (GA1M) already capture most black-box accuracy on typical tabular data; interactions close a real but secondary residual gap.

Ranked domain survey (most → least genuinely conjunctive, no single dominant driver):

1. **Synthetic lethality / genetic epistasis (biology).** Purest AND-gate: gene A knockout viable, gene B knockout viable, double knockout lethal — by construction no single dominant driver (yeast BNI1/BNR1; BRCA1/PARP1 clinically). [Wikipedia: Epistasis and functional genomics; PMC5313148]
2. **Chemistry / QSAR potency-binding nonadditivity.** Nonadditive events in matched-molecular-pair analysis are the **majority regime for potency/binding data**, not an edge case: 57.8% of AstraZeneca in-house assays and 30.3% of public assays show nonadditive ("magic methyl"-style) events. Bulk physical properties (boiling point) stay additive-enough; binding/potency does not. [PMC4372821; jcheminf.biomedcentral.com/articles/10.1186/s13321-021-00525-z]
3. **Pharmacology — drug-drug synergy.** Loewe additivity is the null hypothesis and is violated in most screened drug pairs even in nominally "non-interacting" datasets — synergy/antagonism is closer to the empirical default than additivity. [PMC5808155; PMC7010330]
4. **Ecology — genuinely mixed / instant-dependent.** Hutchinson's n-dimensional niche hypervolume is a formally conjunctive model, but applied population/growth modeling still validates well against Liebig's law of the minimum (single scarcest factor dominates locally). Some co-limitation exists across space/time, but at any given instant one factor typically dominates. [Ecography 10.1111/ecog.03187; PMC9285345; PMC5528229]
5. **Economics — least conjunctive.** True Leontief (both-required, zero elasticity of substitution) complementarity is a clean theoretical conjunctive model but empirically confined to narrow niches (fixed-recipe production); the broad economy shows positive, price-responsive elasticity of substitution — additive-utility/substitutable is the norm. [Leontief production function, Wikipedia; fastercapital.com]

Disease-threshold / liability traits are a genetics sub-exception worth flagging separately: Zuk-style "limiting pathway" multiplicative-risk models and digenic examples (Hirschsprung disease, RET x NRG1 enhancer epistasis, PMC9705416) show interaction terms rivaling or exceeding single-locus effects specifically for **threshold** traits, unlike smooth quantitative traits — reinforcing that discreteness/thresholding, not biology-in-general, is the load-bearing variable.

---

## (c) Verdict + hedge

**The single-driver-dominance worry is empirically supported as the general/typical case** — across ANOVA meta-science, additive-genetic-variance theory, and GA1M-vs-black-box ML results, main effects dwarf interactions by roughly an order of magnitude in the typical dataset. Our metabolic-rate finding (activity level dominant, 1.11/1.88 joint bits) is not an unlucky draw — it is the **predictable outcome of sampling from an organismal/ecological-physiology attribute class**, which the domain survey independently ranks near the bottom (rank 4/5, "genuinely mixed but single-factor-dominant in practice/at an instant" — Liebig's law wins operationally even though niche theory is conjunctive in principle).

Genuine no-dominant-driver conjunction is **not rare in absolute terms — it is concentrated in specific, identifiable pockets**: (1) discrete/threshold/"both-required" molecular mechanisms (synthetic lethality, disease-threshold epistasis, transcription-factor combinatorial logic), (2) chemical potency/binding data (QSAR nonadditivity — majority regime, not edge case), (3) pharmacological combination effects (drug synergy — additivity is the violated null, not the default). It is comparatively **absent** from continuous organismal/ecological traits, general quantitative genetic traits, and substitutable-goods economics — exactly the domain classes that "feel" like natural, easy-to-source knowledge-foundation content but will systematically hand a frequency/dominant-factor baseline the win.

**Actionable hedge for the foundation-build target:**
1. **Pre-filter candidate held-out attributes by domain class before building around them.** Deprioritize generic organismal/physiological/ecological/economic attributes as conjunction benchmarks (metabolic-rate-style traits will recur as single-driver-dominated); prioritize sourcing relation-types from the three high-interaction pockets above — molecular/genetic epistasis-style relations, chemistry potency/binding (QSAR-adjacent) relation types, and any explicit threshold/logic-gate-structured relation (AND/OR/both-required framings) if/when curating the dense KG core or module registry.
2. **Use the single-factor-MI-vs-joint-MI triage** (exactly the metric that caught the metabolic-rate problem) as a standing gate on any candidate conjunctive-reasoning attribute before building a cell around it — cheap, already proven to work, should now be applied prospectively rather than post-hoc.
3. **Decouple the conjunctive-CODING architecture decision from the conjunctive-ATTRIBUTE-selection decision.** Per (a)-reason-2, pattern-separation/orthogonal storage remains independently justified (interference-avoidance across facts sharing overlapping features) even for single-driver-dominated attributes. The "structured codes beat frequency" value proposition does not have to rest entirely on finding genuinely-interactive attributes; it can also rest on retrieval-without-interference for a large shared-feature-pool KG, which is a real and separate win. This is a load-bearing hedge if pocket domains turn out too narrow to build a full foundation from.

---

## Cheap decisive test

Run the single-factor-MI-vs-joint-MI triage (already-built metric from the metabolic-rate analysis) across a small stratified sample of candidate held-out attributes: ~10 from "pocket" domains (molecular/genetic epistasis-style or chemistry potency-style relations available in current KG sources) vs. ~10 from "generic" domains (organismal/physiological/continuous-trait relations, matching the metabolic-rate class). Compute mean fraction of joint MI captured by the single best constituent factor in each group.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **Prediction 1 (pocket domains are genuinely conjunctive).** HARD-PASS: mean single-factor-dominance fraction in pocket-domain sample < 60%, AND at least 15-percentage-point lower than the generic-domain sample. HARD-FAIL: pocket-domain sample shows similarly high single-factor dominance (>80%) as generic domains — the domain-targeting hedge fails and a different targeting strategy (e.g., explicitly constructed/synthetic logic-gate relations rather than found data) is needed.
- **Prediction 2 (chemistry/QSAR nonadditivity generalizes to our KG content).** HARD-PASS: >=40% of sampled chemistry potency/binding-style candidate attributes show nonadditive signal under the MI decomposition (consistent with the 30.3%-57.8% AZ/public assay literature range). HARD-FAIL: <20% show nonadditivity — the published nonadditivity rate does not transfer to whatever relation-types are actually available in our sources.
- **Prediction 3 (interference-avoidance hedge holds independent of attribute interactivity).** HARD-PASS: conjunctive/orthogonal storage shows measurable retrieval-without-interference benefit in a multi-fact-storage setting even when the stored attribute itself is single-driver-dominated (i.e., the hippocampal-indexing rationale transfers even where the interaction rationale doesn't). HARD-FAIL: no measurable interference-avoidance benefit under those conditions — would mean the entire conjunctive-coding bet needs to rest on attribute-selection alone (pocket domains), with no fallback.

---

## Cross-thread synthesis

- Directly informs the **relational-capability-is-core-requirement program spine** (`project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md`): the "generalize to new relations" frontier should prioritize relation-types from the identified high-interaction pockets, not generic ones.
- Connects to the **ideal-foundation-spec** thread (2026-07-14, dense KG core + module registry): suggests the module registry should include a molecular/chemistry-mechanism module (synthetic-lethality/epistasis-style + QSAR-style relations) specifically as conjunction-rich content, distinct from the general-purpose relational core.
- Provides an independent, non-interaction justification for the **grid-code/structure-content-factorization** and **spoke-on-hub grounding** threads' emphasis on orthogonal/conjunctive binding — the pattern-separation/interference-avoidance rationale (part a, reason 2) holds regardless of this drill's verdict on attribute-level interactivity.
- Cross-checks the metabolic-rate finding itself: the domain survey (part b, ecology ranked #4/5) predicts, independently of our own measurement, that organismal/physiological traits would be single-driver-dominated. This is convergent validation, not a coincidence to worry about.

## Substrate-product implications

For the foundation-build (per PIVOT — build the ideal knowledge foundation from existing tools): when curating or generating content intended to demonstrate/benchmark conjunctive reasoning, source preferentially from molecular-mechanism (epistasis/synthetic-lethality-style), chemistry potency/binding (QSAR-style), and explicit threshold/logic-structured relation types — not generic organismal, ecological, or economic attribute data, which the evidence says will usually let a frequency/dominant-factor baseline win and understate the value of structured/conjunctive codes. Simultaneously, keep the conjunctive/orthogonal storage architecture as a first-class design choice regardless of per-attribute interactivity, since its interference-avoidance value (hippocampal-indexing rationale) is independent of whether any given held-out attribute turns out genuinely conjunctive.

## Citations (verified count: 24)

Neuroscience/cognition (11): Leutgeb et al. 2007 *Science* 10.1126/science.1135801; PMC3812781 (pattern separation review); "And yet, the hippocampus codes conjunctively," *Trends Cogn Sci* 2025, S1364-6613(25)00159-7; bioRxiv 2025.06.23.661173 (linear perceptual / nonlinear memory encoders); PMC4888374 (conjunctive input processing, CA1); O'Neill & Suga 1988 / Suga lab bat AI combination-sensitive neurons (J Neurosci 8441017); Rigotti, Fusi et al. 2013 *Nature* 10.1038/nature12160; eNeuro 2022 (DLPFC vs parietal mixed selectivity); Pearce configural theory vs. Rescorla-Wagner + PMC5352505; honeybee negative/positive patterning PMC311365; PMC6267667 (vole predator-odor context) + PMC8857938 (prey coloration context).

Interaction-effect statistics (7): McClelland & Judd 1993 *Psychol Bull*; Gelman "You need 16 times the sample size" (2018, 2023); Lakens 2020 (effect sizes/power for interactions); Hill, Goddard & Visscher 2008 *PLoS Genet* (PMC2265475); Monnahan & Kelly 2015 (PMC4422649, Mimulus epistasis exception); Lou et al. 2013 GA2M (KDD); Lengerich et al. 2020 (functional-ANOVA purification).

Domain survey (6): Wikipedia/PMC5313148 (synthetic lethality); PMC4372821 + jcheminf.biomedcentral.com 10.1186/s13321-021-00525-z (QSAR nonadditivity); PMC5808155 + PMC7010330 (drug synergy / Loewe additivity violations); Ecography 10.1111/ecog.03187 + PMC9285345 + PMC5528229 (niche hypervolume vs. Liebig's law); Leontief production function (Wikipedia); PMC9705416 (Hirschsprung RET x NRG1 threshold-trait epistasis); PMC3728313 (Zuk limiting-pathway epistasis models).

**P_deflated = 0.50** (calibration cap applied — this is a novel strategic synthesis across independent lit-scans, not a direct substrate precedent; raw cross-source convergence was strong (~0.70-0.75) but capped per [[feedback-lit-scan-calibration-penalty]]).
