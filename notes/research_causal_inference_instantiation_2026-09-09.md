# Research: How the brain applies stored causal knowledge to the specific story being read (online instantiation)

**Date:** 2026-09-09
**Dispatched by:** Director (free-form topic, no routing file — direct literature drill)
**Sub-agents:** 4x parallel Sonnet lit-scans (causal-antecedent triggers; situation-model instantiation; coreference gating; neural substrate), synthesized by this role.
**Field-advisor note:** `tools/orchestrator/research_field_advisor.py` was run per protocol but its 22-field taxonomy (thermodynamics, spin-glass, free-probability, etc.) is scoped to the substrate-physics research vertical and returns no adjacency signal for this psycholinguistics/cognitive-neuroscience question — the tier rankings above do not apply here. This note sits in the separate "brain-foundational reading-comprehension" research lane (multistep/causal-selection, situation_reader, coreference_resolver).

## HEADLINE

Online causal-antecedent inference is **not a uniform default nor a rare strategic act** — the best-supported account (Myers & O'Brien 1998 resonance model) is a **two-stage, threshold-gated process**: cheap, passive, promiscuous associative reactivation runs on every clause; a slower, effortful backward search into the causal-knowledge store fires only when that passive pass fails to restore **local coherence** (a graded causal-discontinuity signal, per Zwaan/Radvansky's event-indexing dimension and the landscape model). The generic-to-specific "binding" step (how "X causes Y" becomes "this x caused this y") has **no established formal mechanism** in the literature — every source that touches it (Kintsch's construction-integration, Garrod & Terras's bonding/resolution) describes graded, subsymbolic constraint-satisfaction settling, not symbolic unification. Coreference functions as a **soft, mutually-constraining accessibility cue** (Kehler 2002; Asher & Lascarides 2003), not a hard sequential precondition — except at the narrow within-sentence DRT/accessibility layer. Neurally, the most defensible circuit is: ATL + angular gyrus/pMTG hold generic causal-relational knowledge (Schwartz et al. 2011 dual-hub dissociation of taxonomic-vs-thematic), hippocampus binds the current story's specific entities, and dmPFC + precuneus/PCC (Ferstl & von Cramon 2001/2002/2008; van Kesteren et al. 2012 SLIMM) perform the online schema-congruence-gated integration — a neural-level mirror of the cognitive-level resonance-then-search account.

## Cheap decisive test

Test the existing causal-antecedent-inference organ (multistep/causal-selection line) for whether it structurally exhibits a **coherence-break gate** at all, using the modern (non-19c) gold corpus already in use:

1. Compute a causal-discontinuity proxy per clause transition in the gold set (entity/state overlap drop between the incoming clause and the active situation-model buffer — reuse the existing entity-state tracker, no new component).
2. Correlate that proxy against the organ's current invocation pattern for deep causal-antecedent lookup (does lookup depth/rate track discontinuity, or fire flatly on every clause?).
3. Compare accuracy on the causal-antecedent gold subset under (a) always-on deep lookup vs (b) lookup gated by a discontinuity threshold.

This is cheap (reuses existing entity-state and gold-scoring machinery; no new model, one threshold sweep) and decisive: it directly tests whether the organ's trigger condition resembles the brain's graded coherence-break gate or an unconditional per-clause computation — the central mechanistic question this drill was run to answer.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**A — Trigger is graded, not flat.** Gating deep causal lookup by the discontinuity proxy should cut invocation volume substantially while preserving accuracy.
- HARD-PASS: gated version retains accuracy within a CI-separated non-inferior band of always-on on the causal-antecedent gold subset, while cutting deep-lookup invocation by ≥50%.
- HARD-FAIL: gating produces a CI-separated accuracy drop vs. always-on — implies the discontinuity proxy is not a sufficient stand-in for "coherence break," or the gold subset already selects only hard cases (confound to name explicitly, not silently absorb).

**B — Binding is similarity-weighted, not exact-match.** A role-filler-overlap-weighted retrieval of generic causal knowledge (matching resolved entities/state-predicates against a generic cause-template by graded overlap) should match or beat exact-string/keyword lookup.
- HARD-PASS: overlap-weighted retrieval beats exact-match by a CI-separated margin on the gold subset.
- HARD-FAIL: exact-match wins or no separation — would mean this domain's generic→specific instantiation is closer to symbolic slot-filling than the associative-settling literature implies; flag back to research rather than silently keep exact-match.

**C — Coreference is a soft cue, not a hard gate.** Disabling/scrambling coreference should degrade causal-antecedent accuracy gracefully, not collapse it.
- HARD-PASS: accuracy with coref disabled stays CI-separated above chance/floor (some causal inference survives via lexical causal connectives / event-type priors alone, per Kehler's joint-inference account).
- HARD-FAIL: accuracy collapses to floor with coref disabled — indicates the organ implements a hard sequential coref-then-cause pipeline, an architecture deviation from the brain evidence (not necessarily wrong engineering, but mislabeling it as brain-faithful would be — flag explicitly).

## Cross-thread synthesis with prior entries

- **Directly informs the active predictive-generative-chain build queue** (`notes/project_multistep_causal_selection_build_queue_predictive_generative_chain_2026-09-08.md`): the queue's next items are forward event-transition model → close N400 forward loop → predictive causal-link inference. The lit-scan found **forward (predictive) causal inference is markedly weaker/more resource-gated than backward (antecedent) inference** — Fincher-Kiefer (1993, 1995) and Klin et al. (1995, 1999) show predictive inferences require working-memory resources, are held only transiently in the situation model (not the durable textbase), and decay if unconfirmed. Implication: the forward loop should be built and graded as a genuinely weaker, WM-budget-limited, decaying signal — not symmetric in strength to the backward antecedent mechanism — and its gold-standard ceiling should be set lower accordingly, per this project's "don't confuse a fair-test floor with a ceiling" discipline.
- **Compatible with the FHRR/VSA binding discipline already locked in** ([[fhrr-is-the-chosen-binding-basis-do-not-replace]]): the literature's own binding mechanism for generic→specific instantiation is graded/associative (Kintsch construction-integration overgeneration+settling; Garrod & Terras bonding+resolution), not symbolic unification — this is independent literature support (not circular) for treating role-filler vector binding/similarity-weighted retrieval as a defensible computational-level stand-in, since no source specifies a neural-implementation-level binding mechanism either.
- **19c-corpus ban is compatible with this drill**: the cheap decisive test above uses only the already-mandated modern gold (UD-EWT/QA-SRL/GUM-class), no McGuffey/LitBank dependency.
- **Coreference_resolver / situation_reader organs**: prediction C directly tests whether the current pipeline over-couples causal inference to prior coref resolution success. If the pipeline is a hard sequential gate today, that is a concrete, testable architecture-vs-brain mismatch, not a vague "could be better" note.

## Substrate-product implications (plain language)

What we studied: how a human reader figures out "why did that happen" while reading a story — specifically how general knowledge like "objects break when dropped" gets attached to one specific dropped object in one specific story, and what makes the brain bother to search for a cause at all instead of just moving on.

What we found: the brain does not search for a cause after every single sentence. It runs a cheap, automatic "does this still make sense" check on every sentence, and only spends real effort digging for a specific cause when that cheap check fails — roughly, when the next sentence doesn't obviously connect to what came before. Also: figuring out WHO or WHAT something happened to is not a strict first step before figuring out WHY — the two are worked out together, leaning on each other, not one waiting for the other to finish. And there is no known "clean" mechanical rule in human cognition for attaching a general rule to a specific case — it looks more like a fuzzy best-match-and-settle process than exact plugging-in.

What it means for the reading-comprehension system: a component that tries to dig up a specific cause for every single sentence is doing more work than the brain does, and a component that refuses to look for a cause until names/pronouns are fully resolved is being stricter than the brain is. Both are testable, cheap fixes (one threshold, one ordering change) rather than new components to build. The three predictions above (A/B/C) are direct, cheap tests of exactly these two things against data already on hand.

Risk in this recommendation: all three predictions are inferred by combining four separate literature threads that were not designed to be combined this way — this is a novel synthesis on my part, not a single paper's finding, so it is capped at moderate confidence (see below) until the cheap decisive test actually runs against the organ's real behavior.

### Actionable next-step anchors (in place of a separate hand-off file, per USER-locked no-routing-files discipline)

1. **Anchor: coherence-break gate on deep causal-antecedent lookup** (Prediction A). Reuses existing entity-state tracker + gold scorer. Tier hint: cheap/fast, do first — it's a threshold sweep, not new machinery. Why now: directly answers "is the trigger graded or flat," the core mechanistic question of this drill.
2. **Anchor: role-filler-overlap-weighted retrieval vs exact-match for generic→specific causal binding** (Prediction B). Tier hint: medium — needs the overlap-scoring function wired into the causal-knowledge lookup path. Why now: tests whether the FHRR/VSA-compatible similarity-based binding is actually earning its keep on this specific inference type, or whether exact-match is silently doing the real work.
3. **Anchor: coref-ablation graceful-degradation check** (Prediction C). Tier hint: cheap — rerun existing causal-antecedent eval with coref resolution disabled/scrambled. Why now: directly audits whether situation_reader/coreference_resolver wiring accidentally implemented a hard sequential gate the brain doesn't have.
4. **Anchor: recalibrate forward-inference (predictive causal-link) ceiling downward** for the in-progress predictive-generative-chain build queue, per the Fincher-Kiefer/Klin WM-gating + decay findings above — a scope note for whoever builds the forward event-transition model next, not a new experiment.

## Confidence (calibrated, per lit-scan calibration penalty)

- Two-stage resonance-then-strategic-search trigger mechanism (cognitive level): raw confidence ~0.75 (multiple independent RT/verification paradigms converge) → **P_deflated ≈ 0.55**.
- Coreference as soft/graded, mutually-constraining cue rather than hard gate: raw ~0.70 → **P_deflated ≈ 0.50**.
- No established formal generic→specific binding mechanism (an absence-finding, itself fairly robust across sources): raw ~0.65 → **P_deflated ≈ 0.45**.
- **Cross-level synthesis** mapping cognitive resonance-gating onto the mPFC/SLIMM schema-congruence-gating neural account: this is a novel synthesis across the 4 sub-agent reports, not itself a claim any single source makes — **capped at P=0.50** per the novel-synthesis cap, independent of raw confidence.

## Adversarial section: does the minimalist hypothesis undercut a stored causal foundation?

McKoon & Ratcliff's (1992) minimalist hypothesis is real, published, and not refuted by this drill: it claims most causal-antecedent, elaborative, and predictive inferences are **not** drawn automatically online, only (a) cheap/available-information inferences and (b) local-coherence-necessary ones are. The two-process resonance account (Myers & O'Brien 1998) does not overturn this so much as explain *why* constructionist evidence (priming, graded RT effects) still appears: passive resonance is cheap, universal, and produces those signatures without requiring deep, effortful, verified antecedent construction on every clause. This means a stored causal-knowledge foundation that fires unconditionally on every event is mis-modeling the brain in the direction of over-computation, not under-computation — the brain's default is closer to "don't bother unless something breaks." That is good news for a substrate implementation on cost grounds (most clauses need no deep lookup) and is exactly what Prediction A tests. It is bad news if the current organ was implicitly built assuming constant deep causal search is the correct brain-faithful default — that assumption is the one this drill puts in the crosshairs.

## Citations (verified count)

Approximately **70 distinct author-year citations** were surfaced across the 4 parallel lit-scan sub-agents (causal-antecedent triggers ~16; situation-model instantiation ~23 net-new; coreference gating ~20 net-new after dedup; neural substrate ~16), sourced via WebSearch/WebFetch against academic literature (journal names and volume/page numbers reported where available: JVLVB, JML, JEP:LMC, Psychological Review, Psychological Bulletin, Nature Reviews Neuroscience, PNAS, Neuron, J Neurosci, Trends in Neurosciences, Hum Brain Mapp, NeuroImage, Discourse Processes, Cognitive Science, Computational Linguistics). These citations were retrieved and cross-referenced by the sub-agents but **not independently verified against primary-source PDFs by this role** — treat citation years/venues as sourced-but-spot-check-pending, per the lit-scan calibration discipline. Core, load-bearing citations that recur across ≥2 independent sub-agent threads (Trabasso & van den Broek 1985; McKoon & Ratcliff 1992; Zacks & Swallow 2007 / Radvansky & Zacks 2014; Myers & O'Brien 1998) are the highest-confidence anchors in this synthesis.

## TLDR

We studied how people figure out "why" something happened in a story while reading, using their stored general knowledge. The brain only bothers to dig up a specific cause when the story stops making obvious sense on its own — not after every sentence. And there's no known clean mechanical rule for how a general fact gets attached to one specific person or thing in a story; it's a fuzzy best-match process, not exact plugging-in. Knowing who a pronoun refers to helps find the cause, but the two are worked out together, not strictly one-then-the-other. This gives three cheap, concrete tests against work already on hand, plus a heads-up that the "figure out what happens next" piece already planned should be expected to work less reliably than the "figure out what caused this" piece, because that's what the brain itself does.

## QUESTIONS

None.

## NEXT STEPS

Director should route the three anchors (coherence-break gate, overlap-weighted binding, coref-ablation check) to a cell-author directly from this note per the no-routing-files discipline; no further research dispatch is required to act on them. A natural next research drill (not yet run): the dual-hub taxonomic-vs-thematic ATL/angular-gyrus dissociation (Schwartz et al. 2011) as a possible argument for splitting the causal-knowledge store from the general semantic/taxonomic store in the substrate, if that split isn't already reflected in current organ boundaries.
