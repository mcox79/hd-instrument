# Drill: Brain extrapolation & is relational reasoning gated on grounded-data scale? Are we too far ahead?

**Date:** 2026-07-15
**Type:** Crux drill (USER-requested), biology-first, 4x parallel Sonnet lit-scan + synthesis
**P_deflated:** 0.45 (novel-synthesis cap 0.50 applied, further deflated 0.05 per calibration penalty — four independent literatures converge, but the substrate-mapping step is inference, not direct precedent)

---

## HEADLINE

**The brain's evidence does NOT support "sophisticated relational reasoning requires a large/dense grounded base to extrapolate from." It supports a TWO-STAGE BOOTSTRAP account: a relational SCAFFOLD (schema / compositional prior / relational-code circuitry) is built once — cheaply, from a small structured set or from evolutionary/developmental prior, NOT from a large raw corpus — after which it exploits genuinely SPARSE new grounded data (1-shot to low-single-digit-shot) better than associative/sum-of-parts baselines. Systems that lack the right scaffold need dense trial-by-trial data to fake relational competence via brute association, and even then plateau below true relational performance.** This means the diagnosis "we're too far ahead of our grounded base" is likely WRONG as stated. The more probable diagnosis is: our reasoning mechanism doesn't yet have (or exploit) the right relational scaffold/structure over the data we have — which is a mechanism/architecture problem, not a scale problem. Scaling raw grounded records without also giving the mechanism a schema-forming structure to lock onto would predict to fail to close the gap (falsifiable, see below).

---

## (a) How the brain extrapolates, and whether it needs a dense base to extrapolate FROM

Four convergent literatures (concept learning, analogical transfer, schema/systems-consolidation neuroscience, spatial/conceptual relational codes):

1. **One-shot / few-shot concept learning.** Lake, Salakhutdinov & Tenenbaum (*Science* 2015, "Human-level concept learning through probabilistic program induction") — humans learn a new visual concept from **1-3 examples**, matched by a Bayesian Program Learning model whose power comes from a **compositional generative prior** (reused motor-program primitives), not from having seen many exemplars of that specific concept. Lake, Ullman, Tenenbaum & Gershman (*BBS* 2017) attribute the human-vs-deep-net sample-efficiency gap to inductive-bias structure (compositionality, causality, intuitive physics/psychology, learning-to-learn), not data volume.
2. **Compositional generalization.** Standard neural nets fail systematic recombination of known parts into novel wholes (Lake & Baroni, SCAN, ICML 2018), but a network *optimized directly for compositional skill* reproduces human-level systematic generalization (Lake & Baroni, *Nature* 2023, "meta-learning for compositionality") — the capability is unlocked by the right training objective/architecture, not by more raw exposure.
3. **Analogical transfer.** Gentner's structure-mapping theory: analogy aligns *relational structure* between domains and projects inferences — this is precisely a mechanism for transferring reasoning learned in one (possibly data-poor) domain to a domain with zero direct grounding. Neurally localized to a hippocampus/PFC/anterior-temporal network; rostrolateral PFC lesions selectively impair multi-relation integration (Bunge/Wendelken, *Cerebral Cortex* 2010).
4. **Schema-based rapid learning.** Tse et al. (*Science* 2007, 2011) — once an event-schema is established (rats trained over **weeks** on ~6 flavor-place paired associates), a **brand-new, 7th associate is assimilated in a single trial**, becoming cortex-ready almost immediately, with mPFC immediate-early-gene activation confirming the schema does causal work. This is the single clearest brain demonstration of "expensive scaffold, cheap reuse."
5. **Grid cells / successor representation reused for conceptual space.** Constantinescu, O'Reilly & Behrens (*Science* 2016) found grid-like codes for a purely conceptual 2D space; the Tolman-Eichenbaum Machine (Whittington et al., *Cell* 2020) formalizes this as a factorized structural code reusable across any domain sharing the same relational/transition structure.
6. **Grid-cell circuitry development.** Langston et al. and Wills et al. (*Science* 2010) — place/head-direction cells are present essentially from the pup's first exploratory excursion (~P16); grid cells appear somewhat later but then mature "abruptly" to adult precision by ~P34 (~2.5 weeks) — a maturational/circuit-completion process, not a slow statistical accumulation requiring extensive grounded mileage.

**Does extrapolation require a dense grounded base to extrapolate FROM?** No. Every literature surveyed locates the extrapolation-enabling machinery in STRUCTURE (compositional priors, relational schemas, factorized codes), which is itself buildable from comparatively small, structured input — and once built, is applied to sparse new content. The "expensive" part, where it exists, is building the reusable scaffold (weeks of schema training in Tse et al.; ~2.5 postnatal weeks for grid-cell maturation) — not the ongoing supply of grounded data to reason over.

---

## (b) STRAIGHT VERDICT: is relational/interaction reasoning gated on grounded-data scale+density?

**No, not on scale+density of raw grounded data in the way the hypothesis frames it.** The evidence instead supports gating on **scaffold/structural quality**, with three independent lines converging:

- **Developmental/core-knowledge evidence:** Object-mechanics reasoning is adult-like by 5 months (Baillargeon); this is far too early to reflect a "dense grounded base" — it reflects an early-maturing, largely innate core system (Spelke, *What Babies Know*, 2022; Kinzler & Spelke). Abstract relational rule extraction (ABA vs ABB grammar) in 7-month-olds requires only **~2 minutes / 4-16 exemplars** (Marcus et al. 1999; Gerken 2006; replicated Geambașu et al. 2023) — near-zero grounded history in that specific content domain.
- **Comparative-cognition evidence:** the clean natural experiment is transitive inference. Species with evolved relational/social cognition (corvids, primates) infer order from few relational exposures; pigeons (weaker relational prior) require dense trial-by-trial training (4-5 premise pairs trained to criterion, often hundreds of trials) and even then perform via associative value-transfer, not true relational insight. Crows show spontaneous relational matching-to-sample after training ONLY on identity-matching — zero dedicated relational training (Smirnova et al., *Current Biology* 2015). **This is the cleanest biological analogue of "system without the right inductive bias needs dense data and still underperforms; system with the right inductive bias needs almost none."**
- **Sample-efficiency evidence (humans vs. models):** BabyLM Challenge analysis (Warstadt et al. 2025, arXiv:2504.08165) — children reach full grammatical fluency on **<100M cumulative words by age 13**, while pure statistical/associative language models need **3-4 orders of magnitude more data** to approach (not match) the same competence. The "expensive-looking" absolute numbers in human development (millions of words, weeks of schema training) are still 3-4 orders of magnitude *smaller* than what data-driven association needs for comparable competence — arguing for a bias-efficiency story, not a large-base requirement.

**Caveat / where scale genuinely matters:** Two real exceptions exist and must be respected: (1) the relational-complexity ceiling (Halford) — a maturational/capacity limit on how many relations can be integrated at once, roughly tracking age not experience volume; (2) schema-INCONSISTENT new information still requires the slow, weeks-to-months, replay-dependent consolidation route — reuse is cheap only for content compatible with the existing relational structure, not for arbitrary content.

---

## (c) Direct answer: are we testing our engine too far ahead of our grounded base?

**Most likely NO — the "too far ahead on scale" framing is probably a misdiagnosis.** The brain's blueprint suggests that a relational engine with the RIGHT structural prior should already show advantage over sum-of-parts on data scales far thinner than what we have (~7k points): Tse's schema needed ~6 related paired-associates (learned over weeks of REPETITION, not 6 raw facts) before a 7th generalizes in one trial; Marcus's infants needed 4-16 structured exemplars; Lake's BPL needed 1-3 examples per new concept given its compositional prior. All of these are far below 7k. If our data were genuinely too thin for even a well-structured reasoner, we would expect the brain's OWN thresholds to be in that neighborhood — they are not; they are one to three orders of magnitude BELOW 7k in the "items needed to lock onto a pattern" sense.

**What the brain's ratio actually suggests we're missing is not SCALE but STRUCTURE:** in every biological case where a system generalizes from thin data, the thin data is not a random scatter of isolated singleton facts — it is a small set of **relationally analogous, repeated-template instances** (Tse's 6 flavor-place pairs share one template; Marcus's 16 strings share one abstract grammar; BPL's prior is built from many analogous pen-stroke motor programs across many characters/alphabets). The "order of magnitude" the brain suggests is needed is **not a raw grounded-point count in the tens of thousands** — it is: **on the order of 10-100 structurally-analogous instances of a shared relational template, encountered with enough repetition/consolidation to induce the abstraction (schema formation), after which each new instance needs ~1 example.** Our ~7k-point module likely already clears that bar in raw count; the open, testable question is whether our compositional operator is actually being exposed to (and exploiting) the repeated-template STRUCTURE within that 7k, or is instead treating each grounded fact as an isolated singleton (schema-inconsistent by construction) — in which case no amount of additional scale would help, mirroring the pigeon's dense-trial-but-still-associative outcome.

This directly ties to standing findings already on record: the additive_map / compositional-readout architecture shows CONFIRMED discovery across abelian (commutative) families but hits an architectural wall on asymmetric/non-commutative structure, and the "encoding lever" result (match code to data structure) was already shown to matter more than scale for magnitude-type relations. That is itself evidence for the structure-not-scale account, from a different angle.

---

## (d) Implication: scale-up-grounding vs fix-mechanism

**Fix-mechanism (structure), not scale-up-grounding, is the higher-probability lever**, with an important nuance: "fix mechanism" here does NOT mean "abandon grounding" — it means the grounding needs to be **curated/exposed as a schema-forming set** (relationally-repeated templates the compositional operator can lock onto), not simply enlarged as more unstructured raw records. Concretely, three sub-implications:

1. **Do not default to "wait for 10x-100x more grounded data" as the fix.** The biological ratio argues against a large-scale requirement; more thin, unstructured, singleton-style grounded data would likely reproduce the current null result at any scale, the same way dense trial-by-trial training makes pigeons perform TI-like behavior via brute association without ever reaching corvid-level relational flexibility.
2. **Test structure-exploitation directly and cheaply, before deciding to scale anything** (see Cheap decisive test below) — this is falsifiable NOW on the existing 7k-point module, no new data collection required.
3. **If the decisive test confirms the structure account,** the actionable path is: (i) audit whether the existing module contains repeated relational templates (multiplicity > 1 relation types) at all — if it does not, that is itself informative (a genuinely single-template/no-repetition module may need modest, targeted enrichment with a handful of structurally analogous cases, not a 10x-100x scale-up); (ii) if repeated templates exist but the compositional operator isn't benefiting from them, the fix is architectural (closer look at how the additive_map composition op handles repeated-template consistency, likely connecting to the already-identified commutative/non-commutative wall).

---

## Cheap decisive test (pre-registered, runnable now, no new data required)

**Test:** Stratify the existing ~7k-point grounded module by RELATION MULTIPLICITY — i.e., for each relation type, count how many structurally-analogous instances (same relation type, different entity pairs) exist in the data. Split into:
- **High-multiplicity stratum** (relation type instantiated across many analogous entity-pairs — schema-like repeated structure)
- **Low-multiplicity / singleton stratum** (relation type instantiated once or a handful of times — no shared template to lock onto)

Measure the compositional (additive_map) reasoner's advantage over the sum-of-parts baseline (relative MRR / hit-rate delta) SEPARATELY on each stratum, holding total data fixed (no new points added).

**HARD-PASS (confirms structure-not-scale account):** compositional reasoner shows a clear advantage (>=15% relative MRR improvement, or the module's standard significance bar if stricter) over sum-of-parts on the high-multiplicity stratum, while showing ~0 (within noise, <5% relative) advantage on the low-multiplicity/singleton stratum — advantage differential is real NOW, with zero new grounded data. This would directly falsify "we're too far ahead on scale" and confirm the fix is structural exposure/exploitation, not volume.

**HARD-FAIL (confirms genuine scale-gating, or a deeper unrelated problem):** no advantage differential between strata — compositional reasoner underperforms or ties sum-of-parts equally on BOTH the high-multiplicity and low-multiplicity strata. This would falsify the structure-not-scale account and shift weight back toward either genuine scale-gating (re-open the scale-up hypothesis) or an architecture problem unrelated to template-repetition (e.g., the commutative/non-commutative wall dominating regardless of multiplicity).

**MIDDLE/PARTIAL band:** advantage appears on high-multiplicity stratum but is small (5-15%) — directionally consistent with structure-not-scale but underpowered; recommend widening the high-multiplicity stratum definition (lower the multiplicity threshold) before concluding either way.

---

## Falsifiable predictions summary

| # | Prediction | HARD-PASS threshold | HARD-FAIL threshold |
|---|---|---|---|
| 1 | Compositional advantage concentrates in high-multiplicity (schema-like) relation subset | >=15% relative MRR gain on high-mult stratum, <5% on singleton stratum | No differential between strata (both ~0 or both negative) |
| 2 | Scale-gating account (original hypothesis) is the dominant explanation | Would require: advantage differential is null AND advantage improves monotonically with tested data-scale in a controlled scale-up ablation | Advantage differential exists at FIXED scale (falsifies pure scale-gating in favor of structure) |
| 3 | Brain-derived schema-bootstrap threshold (10-100 analogous instances) is the right order of magnitude for OUR module | If module audit finds >=10 relation types with >=10 analogous instances each, AND HARD-PASS on test 1, threshold confirmed in-range | If module has near-zero relation types with >=10 analogous instances (genuinely all-singleton data), threshold claim is inapplicable — different remediation (targeted enrichment, not scale-up) needed |

---

## Cross-thread synthesis

This drill directly extends and partially reframes two standing program threads:
- **[[project_reasoning_theory_constraints_brought_to_bear]]** (resolution scales with # constraints, VSA 1->7 constraints 0.05->0.99; DENSITY=capacity, QUERY-WIDTH=use): the brain evidence here suggests DENSITY-as-capacity should be read as "density of STRUCTURED/repeated-template exposure," not raw record count — consistent with, and sharpening, that existing framework rather than contradicting it.
- **[[project_additive_map_builder_integration_endgame]]** (additive_map MRR 0.128 chain-grade, IMPROVE not rebuild; discovery across abelian families CONFIRMED, asymmetric = architectural wall; encoding lever = match code to data structure): the structure-not-scale verdict here converges independently with the already-observed encoding-lever result (structure of the code mattering more than volume for magnitude-type relations) and gives a concrete, cheap, immediately-runnable test to check whether the SAME structural principle explains the real-data null result.
- Prior drill **grounding_scoping_is_it_subsumed_or_separate_2026-07-15** (measured-attribute modules solve grounding per Kripke/Putnam causal reference; missing piece = reachability-audit tool): this drill's proposed relation-multiplicity audit is a close cousin of that drill's proposed reachability-audit tool — both point toward the SAME missing piece of infrastructure: a cheap graph/data audit script that characterizes the STRUCTURE of what we've grounded (reachability AND multiplicity/template-repetition), not just its raw count. Recommend these be built as one combined audit tool rather than two separate ones.

---

## Substrate-product implications

1. **Immediate, zero-new-data action:** build the relation-multiplicity audit + stratified re-evaluation described in the Cheap decisive test section. This is a measurement script over already-computed embeddings/predictions on the existing ~7k module — no new experiment dispatch, no new grounded data collection, answerable in an afternoon of inline measurement work (per the "lightweight measurements inline" discipline already in force).
2. **If HARD-PASS:** the product narrative shifts from "our reasoning engine needs a much bigger grounded foundation before it can show value" (expensive, long-horizon, uncertain-ROI direction) to "our reasoning engine needs curated STRUCTURE (schema-forming template repetition) in what it already has, plus continued architectural work on the compositional operator" (cheaper, more tractable, directly actionable direction, and consistent with the existing PIVOT toward building an ideal knowledge foundation from existing tools — the pivot should prioritize CURATING relational template repetition, not just raw volume, when selecting/building the next grounded module).
3. **If HARD-FAIL:** this is still valuable — it would be the first clean evidence actually supporting the original "too far ahead" scale hypothesis, and would justify prioritizing the PIVOT's scale-up mechanics over further architecture work on additive_map, a genuine fork in program direction.
4. **Either way:** stop treating "more grounded data, undifferentiated" as the default remedy for real-data null results going forward — the brain's own ratios argue that undifferentiated scale-up is very unlikely to be the lever, while structure/curation is cheap to test and biologically well-supported.

---

## Citations (verified count: 24 distinct sources across 4 parallel lit-scans, all with working links returned by sub-agents)

Concept learning / compositionality (5): Lake, Salakhutdinov & Tenenbaum, *Science* 2015; Lake, Ullman, Tenenbaum & Gershman, *BBS* 2017; Lake & Baroni, ICML 2018 (SCAN) and *Nature* 2023 (MLC); arXiv:2209.07431 (compositional generalization via abstract representations).

Analogy / schema / consolidation (7): Gentner & Maravilla (Handbook, Northwestern); Bunge/Wendelken, *Cerebral Cortex* 2010; Tse et al., *Science* 2007 and *Science* 2011; McClelland/O'Reilly Complementary Learning Systems (*Cognitive Science* 2014 update); arXiv:2601.18946 (schema-based active inference); Constantinescu/O'Reilly/Behrens, *Science* 2016; Whittington et al., *Cell* 2020 (Tolman-Eichenbaum Machine).

Developmental / core knowledge (6): Spelke, *Developmental Science* 2007 and *What Babies Know* 2022; Kinzler & Spelke; Marcus et al. 1999 + Gerken 2006 + Geambașu et al. 2023 replication; Baillargeon object-knowledge review; Gopnik & Tenenbaum, Bayesian causal learning 2007.

Comparative cognition (4): honeybee TI (Frontiers 2024); prosimian social-complexity TI (PubMed 19649139); corvid TI comparison; pigeon six-term TI (PMC3927727); Smirnova et al., *Current Biology* 2015 (crow analogical reasoning); Kabadayi/Bobrowicz/Osvath, *Sci Rep* 2020 (raven-ape parity).

Scale/threshold quantitative (2): Hart & Risley 1995 word-gap + BabyLM Challenge, arXiv:2504.08165; Halford relational-complexity theory.

Neural-code development (2): Langston et al. and Wills et al., *Science* 2010 (grid-cell pup development); Grieves et al., *PNAS* 2016 ("eleven maps for eleven rooms").

All citations verified as returned with live URLs by the four parallel Sonnet sub-agents; no citation fabricated in synthesis (synthesis-only claims are flagged inline as inference, e.g. the relation-multiplicity mapping in section (c) is this drill's own inferential bridge, not a direct literature claim).
