# Research drill: is the multi-timescale cascade write brain-grounded, and what is its scope?

Problem: `the_register_write_path_has_a_hard_capacity_wall`
Date: 2026-08-29
Author: Director (research drill, brain-first, lit-scan calibration penalty applied)
Trigger: solver measured on-disk that a K-sum multi-timescale cascade write (leaks spanning fast->slow, best-margin readout) recovers ~3x more recency window than a single leak (CI-separated at every load, D=256), smooth graded gradient, reach still finite so permanent store still needed.

Bottom line up front: the SPECTRUM-OF-TIMESCALES principle is PINNED-BY-EVIDENCE with single-unit measurements at the association/PFC (working-memory) stage. The solver's independent-sums cascade is a faithful model of the READOUT / heterogeneity aspect of that spectrum, and its measured ~3x recency-window recovery is consistent with it. It is NOT the Benna-Fusi capacity mechanism (that requires bidirectional coupling and describes a different capacity notion) and should not claim that theorem. Separately, one strong new result (Watters 2026) pins the superposition-register FORM itself and confirms the graded-resource-over-discrete-slots direction for the ChunkedFocus question.

---

## Evidence-grade table (verified primary sources)

| Paper | Identifier | Grade | Population / stage | What it establishes |
|---|---|---|---|---|
| Bernacchia, Seo, Lee & Wang 2011, "A reservoir of time constants for memory traces in cortical neurons", Nat Neurosci 14:366-372 | PMID 21317906; DOI 10.1038/nn.2752 | **MEASURED (single-unit)** | Monkey PFC, cingulate, parietal; reward-memory integration | A wide **power-law distribution** of memory time constants across cortical neurons (hundreds of ms to tens of seconds); 1-2 time constants extractable per neuron. |
| Murray et al. 2014, "A hierarchy of intrinsic timescales across primate cortex", Nat Neurosci 17:1661-1663 | DOI 10.1038/nn.3862 (PMID not independently re-verified here) | **MEASURED (single-unit, 6 datasets / 26 monkeys / 7 areas)** | Sensory (MT) -> parietal (LIP) -> PFC/OFC/ACC | Intrinsic timescales (spike-count autocorrelation) increase **hierarchically** sensory->association->prefrontal. |
| Fusi, Drew & Abbott 2005, "Cascade models of synaptically stored memories", Neuron 45:599-611 | PMID 15721245; DOI 10.1016/j.neuron.2005.02.001 | **MODEL (theory)** | Single-synapse metaplasticity / consolidation | A cascade of metaplastic states per synapse yields approximate **power-law forgetting** vs exponential. |
| Benna & Fusi 2016, "Computational principles of synaptic memory consolidation", Nat Neurosci 19:1697-1706 | PMID 27694992; DOI 10.1038/nn.4401 | **MODEL (theory)** | Synaptic consolidation (NOT WM/PFC retention) | A chain of **bidirectionally COUPLED** continuous variables (connected "beakers" areas C_k, pipe widths g_{k,k+1}); value flows fast->slow; **near-linear** capacity in N (vs sqrt-N), power-law forgetting. |
| Watters, Gabel, Tenenbaum & Jazayeri 2026, "Working Memory of Multi-Object Scenes in Primate Frontal Cortex" | bioRxiv 2026.01.27.702062; PMC12893052 | **MEASURED (single-unit + population)** | Monkey DMFC + frontal eye field; multi-item WM | Formal model comparison: a **gain-modulated compositional code** (trial-specific weighted combination of single-object representations) beats **discrete slots** and rapid serial switching. |
| Daume et al. 2024, "Control of working memory by phase-amplitude coupling of human hippocampal neurons", Nature | PMID 38632400; DOI 10.1038/s41586-024-07309-z | **MEASURED (human single-unit)** | Human hippocampus / MTL | Theta-gamma PAC neurons implement **control** of WM maintenance (reshape the population code); load-dependent degradation. **Does NOT adjudicate slots vs resource** (see corrections). |
| CDA multi-site registered replication 2026 (Cortex, S0010945226001139); Roy et al. 2023 reproducibility (Psychophysiology, PMC10078237) | as cited | **MEASURED (EEG), MIXED** | Human visual WM | The contralateral-ipsilateral CDA asymmetry **largely replicates**; robustness of finer claims is contested. The "plateau at ~3-4 = fixed slots" **interpretation** is what is undermined, not the signal (see corrections). |

---

## Q1 - Is WM/short-term retention genuinely multi-timescale (a spectrum), not a single decay rate?

**Answer: YES at the association/PFC (WM) stage, and it is MEASURED, not just modelled.**

- Bernacchia 2011 is the decisive single-unit result for the solver's regime: a *reservoir* of time constants, **power-law distributed**, in exactly the PFC/cingulate/parietal circuits that carry WM. This is the strongest grade of evidence (direct measurement) and it is at the right stage.
- Murray 2014 independently confirms a spectrum via intrinsic-timescale autocorrelation, across 7 areas / 26 monkeys, and adds the hierarchy (relevant to Q3).
- Fusi 2005 and Benna-Fusi 2016 also support multi-timescale, but at the **synaptic-consolidation** stage, and they are **models**, not measurements. Do not cross-credit them to the WM stage: they answer "why do synapses need many timescales to consolidate," not "does the PFC WM buffer have a spectrum of retention time constants." Bernacchia + Murray answer the latter, directly.

**Important fidelity nuance (keeps the claim honest):** the measured spectrum is *heterogeneity across neurons* (a distribution of single-cell time constants), not a demonstration of K parallel timescales *within one WM buffer read by a best-margin selector*. So:
- "The substrate should carry a spectrum of timescales, not a single lambda" = **PINNED-BY-EVIDENCE** (measured, replicated).
- "K parallel independent leaky sums with a best-margin readout" as the specific architecture = **OUR-INVENTION** (a computational-level implementation of the pinned spectrum; unfalsified, not confirmed). This is the "copy the computation, sweep/choose the parameter" distinction: the spectrum is the computation to copy; K, the specific leaks, and the selector are our design.

**Label + P.** "The register write should be MULTI-TIMESCALE, not single-lambda": **PINNED** (spectrum) + measured own-experiment support (~3x recency, CI-separated). This is confirmation of an established brain principle, not novel synthesis, so the 0.50 novelty cap does not apply. **P ~= 0.80** that multi-timescale is a genuinely higher-fidelity AND higher-value register form. (Not higher, because the brain evidence is population heterogeneity / intrinsic timescales, not specifically a delay-period buffer with a margin selector; and single-lambda remains a legitimate first approximation for short windows.)

---

## Q2 - Does Benna-Fusi's power-law / extended-capacity result transfer to a superposition (FHRR) register?

**Answer: NO, not as a theorem, and the conflation would be a real error. Different mechanism AND different capacity notion.**

Two distinct things are being run together:

1. **Mechanism.** Benna-Fusi capacity comes from **bidirectional coupling** - a chain of bounded "beaker" variables where value *flows* fast->slow through pipes (g_{k,k+1}). The coupling is what distributes a trace across timescales and produces near-linear capacity. The solver's cascade is **K independent leaky superposition sums** written in parallel (broadcast), with **no flow between them**. Removing the coupling removes exactly the ingredient Benna-Fusi credit for the capacity gain. So the independent-sums form captures the *readout* / spectrum property but not the Benna-Fusi *consolidation-flow* property.

2. **Capacity notion.** Benna-Fusi "capacity" = per-synapse signal-to-noise of one stored pattern against later overwriting, scaling ~linearly in N synapses. In a VSA/FHRR register, the relevant capacity is **how many bindings can be simultaneously read above crosstalk**, which is set by the **dimension D**, not by the number of timescales. The cascade does not raise the simultaneous-superposition capacity; it raises the **temporal reach** (recency window) - which is precisely what the solver measured (~3x window, reach still finite). These are different axes. Framing the ~3x as "Benna-Fusi capacity scaling in the register" would be a category error; framing it as "recovering more of the recency window by reading from the timescale that holds the clearest trace" is exactly right and well-grounded.

**Is there a more faithful cascade to build?** Yes, and it is concrete: a **COUPLED superposition cascade** where each step flows a fraction of the fast register into the next slower register (S_{k+1} += g * S_k while each S_k leaks), i.e. the Benna-Fusi beaker chain applied to whole vectors. Note a caveat that keeps expectations honest: a *linear* cascade of leaky integrators has an impulse response that is a convolution of exponentials (gamma-shaped kernels), so mathematically it may be close to a re-parameterisation of a bank of independent leaks - the practical difference is **kernel SHAPE** (sharper-peaked-then-heavier-tailed, closer to true power-law forgetting) rather than a categorical new capability. Whether the coupled form beats independent sums on the recency-reach metric is an **empirical question worth one can-fail experiment**, not a foregone win.

**Label + P.** "Independent-sums cascade inherits the Benna-Fusi power-law-capacity theorem": **FALSE** (P ~= 0.10). "A coupled (Benna-Fusi-faithful) superposition cascade beats the independent-sums form on recency-reach / forgetting-shape": **OUR-INVENTION, novel synthesis, capped** -> **P ~= 0.35-0.40** (independent linear leaks may already span the timescale range; coupling likely changes kernel shape more than reach).

---

## Q3 - Is the multi-timescale principle SUBSTRATE-WIDE? Is "single global timescale everywhere" a systematic fidelity gap?

**Answer: the timescale HIERARCHY across stages is PINNED (Murray 2014, measured). So yes - a single global timescale is a real fidelity gap in principle. But prior substrate evidence says the VALUE of fixing it is not free.**

- Murray 2014 measured that intrinsic timescales increase sensory->association->PFC. If our organs mirror brain processing stages, a single global decay constant across all of them is brain-INFIDELITHOUS: lexical/sensory-analog stages should be FAST (tens-to-hundreds of ms analog), the WM register MEDIUM, and the discourse / situation-model integrator SLOWER (seconds-to-minutes analog). The register sits at the WM stage; the situation model should decay slower than the register, not at the same rate.

- **Prior-work reconciliation (honest, both directions):**
  - `exp_timescale_gated_predictive_hierarchy_tgph_v1` **LANDED** - a timescale-gated predictive hierarchy already exists in the substrate; this idea is not new here and there is a landed instrument to build on. Check its verdict/metrics before re-deriving.
  - `exp_substrate_fast_slow_weights_LM_v1` **HARD_FAIL** and `exp_c2_cascade_stc_swr_continual_v2` **HARD_FAIL** - naive multi-timescale / fast-slow-weights instantiations have FAILED in this substrate before. This is the anti-inflation caution: the principle is pinned, but a specific implementation can and did fail. Any substrate-wide push must be a can-fail, one-variable test at the regime where the stage's timescale advantage actually shows, not a blanket "add more timescales."

- **Label + P.** Existence of a stage-timescale hierarchy = **PINNED** (measured). The mapping of *our* organs onto stage-appropriate timescales = **OUR-INVENTION** (design). "Single global timescale is a systematic fidelity gap worth fixing across the substrate": **P ~= 0.55** - grounded by Murray (strong) but deflated by (a) lit-scan penalty and (b) at least two prior HARD_FAILs of multi-timescale implementations, which show the value is implementation-sensitive.

**Concrete next-problem implication:** run a **stage-timescale audit** - enumerate every organ that hardcodes a single decay/leak/timescale, and for each name its brain-analog stage and that stage's measured intrinsic timescale ordering (fast lexical -> medium WM register -> slow discourse/situation-model). The highest-value single target it predicts: the **situation model / discourse integrator should carry a SLOWER timescale than the register**; if it currently shares the register's leak, that is a testable fidelity gap. Design as one-variable, can-fail, at the low-data / long-range regime where a slow integrator should win (not the short-window regime where any leak suffices).

---

## Q4 - ChunkedFocus (Cowan ~4): hard fixed 4-slot vs graded competitive resource?

**Answer: the graded / gain-weighted-superposition form is the higher-fidelity one, and there is DIRECT single-unit evidence for it - but the specific citations need correcting.**

- **Watters 2026 is the right, strong citation.** In primate frontal cortex, multi-item WM is best described by a **gain-modulated compositional code** (trial-specific weighted combination of single-object representations), beating both discrete slots and serial switching in a formal model comparison. This directly supports "effective ~4 emerging from a graded resource" over "hard fixed 4-slot count." Grade: MEASURED (single-unit + population).
- **Convergence bonus (load-bearing for the whole substrate):** a gain-modulated weighted SUM of item codes *is* a superposition register with per-item gains - i.e. exactly the VSA/FHRR substrate the register is built on. Watters 2026 therefore pins the **superposition-register FORM** at the population-code level, a meaningful upgrade from the standing "VSA binding is unpinned" note. (Caveat, consistent with the FHRR memory note: Watters pins the weighted-combination *readout* / gain-modulation, not the algebraic `bind()` op per se. The fidelity lever remains store organisation / gain, not the binding algebra.)

**Corrections to the premise (honesty discipline):**
- **Daume 2024 is mis-attributed** for slots-vs-resource. It is about theta-gamma phase-amplitude coupling *controlling* WM maintenance (human hippocampus); it shows load-dependent degradation but does NOT adjudicate slots vs resource. Use Watters 2026, not Daume 2024, for this claim.
- **"CDA replication collapse" is overstated.** The 2026 multi-site registered replication largely UPHELD the contralateral-ipsilateral CDA asymmetry. What is undermined is the *slot interpretation* of the CDA plateau-at-~3-4 - and it is undermined by neural-code evidence (Watters), not by the CDA signal failing to replicate. State it as "the fixed-slot reading is undercut," not "CDA collapsed."

**Label + P.** Graded competitive-resource / gain-weighted focus > hard discrete slots = **PINNED-BY-EVIDENCE** (Watters, single-unit/population). ChunkedFocus as a hard-4 count = **lower fidelity**. **P ~= 0.75** that a graded competitive-resource focus (effective ~4 from competition) is the higher-fidelity form (deflated modestly by lit-scan penalty and by the fact that producing the emergent "~4" still needs a specific competition mechanism).

---

## The unifying substrate-wide finding (for next-problem planning)

Three of the four questions converge on one picture the brain literature now supports with MEASURED single-unit data:

> The brain holds multiple items as a **graded, gain-weighted SUPERPOSITION** (Watters 2026), maintained over a **SPECTRUM of intrinsic timescales that INCREASES along the processing hierarchy** (Murray 2014, Bernacchia 2011).

This pins two substrate choices previously carried as OUR-INVENTION:
1. **The superposition register form** (a weighted sum of bindings) is now PINNED at the population-code level (Watters). Upgrade the register's audit label from "our-invention" to "pinned readout form; store-organisation lever remains ours."
2. **Timescale is a per-STAGE property, not a global constant** (Murray). "Single global lambda everywhere" is a named fidelity gap.

**Adjacent-component evaluation (USER 08-28 discipline):** the salience-gated hand-off to the permanent store is currently a single-threshold gate. Benna-Fusi says consolidation is *itself* multi-timescale (flow into progressively slower beakers). So the hand-off may be more brain-faithful as a **graded flow across timescales** than a discrete gate - flag as an adjacent optimisation to evaluate, not a settled change.

**Three next-problem seeds, in priority order:**
- (B, highest) **Stage-timescale audit** of the reading substrate; first target = situation-model/discourse integrator should be SLOWER than the register. Can-fail, one-variable, at the long-range/low-data regime. Build on `tgph` (landed); heed the `fast_slow_weights_LM` HARD_FAIL.
- (C) **ChunkedFocus -> gain-modulated competitive resource** (Watters gain model), which unifies with the register (both gain-weighted superposition).
- (A) **Coupled (Benna-Fusi-faithful) superposition cascade** vs the current independent-sums cascade - kernel-shape / forgetting-law test. Lower expected delta (P~0.35-0.40); do after B and C.

---

## TLDR (plain language)

The idea behind the solver's new memory-write - keeping several running copies of the same short-term memory that each fade at a different speed, and reading from whichever one still holds the clearest trace - matches how the brain actually works. Brain cells in the memory areas are measured to hold traces that fade over a whole range of speeds, from a fraction of a second to tens of seconds, not one speed. So making the register multi-speed instead of single-speed is genuinely more brain-like, and the solver's measurement (about three times more of the recent past recovered) fits. Two cautions: (1) a famous result that says "many-speed memory holds far more" comes from a *different* brain mechanism where the copies are plumbed together and pour into each other; the solver's copies are separate, so that particular "holds far more" theorem does not carry over - what carries over is "reaches further back in time," which is exactly what was measured. (2) A separate, very recent brain result shows the brain holds several things at once as a blended, weighted mixture rather than in a fixed number of boxes - which happens to be exactly the blended-vector style the whole system already uses, so that is a nice confirmation, and it means the "about four things" limit should emerge from competition rather than be hard-coded as four slots.

## Questions
None. (One premise correction the solver should absorb: the "Daume 2024" and "CDA collapse" citations for the slots-vs-resource point should be replaced by Watters 2026; details above.)

## Next steps
1. Solver: keep the independent-sums cascade as the READOUT/spectrum model; do NOT frame the ~3x as Benna-Fusi capacity scaling - frame it as recency-window reach from reading the clearest-margin timescale.
2. Update the register's brain-foundational audit label per the unifying finding (superposition form now pinned by Watters; timescale-per-stage is a gap).
3. Seed next problems in order B (stage-timescale audit) -> C (gain-modulated ChunkedFocus) -> A (coupled cascade), each as a can-fail one-variable test; carry the `fast_slow_weights_LM` HARD_FAIL as the anti-inflation caution.

---

## Sources
- Bernacchia, Seo, Lee & Wang 2011, Nat Neurosci 14:366-372 - https://pubmed.ncbi.nlm.nih.gov/21317906/ ; https://www.nature.com/articles/nn.2752
- Murray et al. 2014, Nat Neurosci 17:1661-1663 - https://www.nature.com/articles/nn.3862 ; https://www.cns.nyu.edu/wanglab/publications/pdf/murray.nn2014.pdf
- Fusi, Drew & Abbott 2005, Neuron 45:599-611 - https://pubmed.ncbi.nlm.nih.gov/15721245/ ; https://www.cell.com/neuron/fulltext/S0896-6273(05)00117-0
- Benna & Fusi 2016, Nat Neurosci 19:1697-1706 - https://pubmed.ncbi.nlm.nih.gov/27694992/ ; https://www.nature.com/articles/nn.4401
- Watters, Gabel, Tenenbaum & Jazayeri 2026 - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12893052/ ; https://www.biorxiv.org/content/10.64898/2026.01.27.702062
- Daume et al. 2024, Nature - https://pubmed.ncbi.nlm.nih.gov/38632400/ ; https://www.nature.com/articles/s41586-024-07309-z
- CDA multi-site registered replication 2026 - https://www.sciencedirect.com/science/article/pii/S0010945226001139 ; Roy et al. 2023 reproducibility - https://pmc.ncbi.nlm.nih.gov/articles/PMC10078237/
