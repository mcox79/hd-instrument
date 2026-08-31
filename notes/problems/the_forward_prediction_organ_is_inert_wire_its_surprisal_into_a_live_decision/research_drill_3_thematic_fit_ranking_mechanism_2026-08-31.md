# Research drill 3 (2026-08-31): what the re-selection residual "relational structure" ACTUALLY is

Dispatched (hdi_research) after the wider-feature probe RULED OUT dimensionality (a fair 1024-d window
distributional space is WORSE than 12-d grounded for thematic ranking; nothing flat beats the parse).
Goal: resolve the residual ~0.13 to a BUILDABLE, glass-box, brain-faithful mechanism.

## The residual resolves into THREE named components (not one vague "structure")

1. **ESTIMATOR = exemplar retrieval, not prototype averaging** (already confirmed live, +0.08 CI-sep).
   Erk 2007 (EPP): score a candidate by similarity to the SEEN fillers of the predicate-role, not to
   their mean. Nosofsky: prototypes lose within-category discrimination. NEURAL: hippocampal/MTL
   episodic exemplar retrieval + pattern completion. (This is WHY our exemplar store beat the centroid.)

2. **CONDITIONING = on the AGENT / partial event, not just the verb** -- THE biggest named gap. Our
   predictor conditions on (verb, role) and THROWS AWAY the agent. Thematic fit is set by the
   COMBINATION agent+verb (McRae & Matsuki; Bicknell/Hare/Elman/McRae 2010; Matsuki 2011). Metusalem
   2012: the whole event SCHEMA is active (event-related-but-locally-wrong words get intermediate N400).
   DECISIVE: Michaelov et al. 2024 (Neurobiology of Language) -- LM surprisal predicts predicate-
   argument N400 ONLY when enriched by an AGENT-PREFERENCE principle; a flat word-context predictor
   FAILS without it. NEURAL: angular gyrus / temporoparietal event-schema composition (the context-
   updated expected-filler prototype).

3. **SIMILARITY METRIC = taxonomic/selectional (dependency), not topical (window)** -- our window-RI
   failure falsified WINDOW space, NOT distributional space. Pado & Lapata 2007: DEPENDENCY-based
   spaces (verb->object relation) beat window/bag on thematic fit; window encodes topical association
   (vessel~dock), dependency encodes paradigmatic/selectional similarity (vessel~ferry). Baroni & Lenci
   2010 (Distributional Memory): a (word, link, word) dependency tensor is the substrate. CHEAP ROUTE:
   Schwartz, Reichart & Rappoport 2015 -- symmetric-pattern ("X and Y" coordination) embeddings capture
   same-KIND similarity (SimLex 0.517 vs word2vec 0.462) from a shallow surface scan (no full parse).
   NEURAL: ATL taxonomic-similarity hub (Lambon Ralph hub-and-spoke).

## The unifying model + the neural circuit
The best classic ranker AND the brain's operation coincide in the **Structured Distributional Model**
(Chersoni/Lenci 2019): a Distributional Event Graph mined from a DEPENDENCY-parsed corpus; plausibility
= cosine(candidate filler, a CONTEXT-UPDATED expected-filler prototype conditioned on the participants
already seen). Our exemplar store is an exemplar-form SDM MINUS the context-conditioning.
CIRCUIT: RANKING = angular-gyrus event-schema composition (graded expectation given the event so far)
x ATL taxonomic-similarity metric x hippocampal episodic exemplar retrieval. We have the hippocampal
route (exemplar store); we are missing the AG agent-conditioning and the ATL dependency-similarity metric.

## THE MINIMAL BUILDABLE MECHANISM -- build FIRST: agent-conditioned exemplar retrieval (option B)
Smallest delta on what we already have (we already parse the agent):
- Build (agent_head, verb, patient_head) triples from QA-SRL (load_patient_items gives paired agent +
  patient spans per verb-entry).
- Re-selection: candidate patient score = mean over the top-3 seen patients of this verb-role, where
  "top-3" is WEIGHTED by agent-similarity sim(seen_agent, current_agent) in the grounded space. I.e. an
  exemplar version of the SDM's context-dependent expected-filler prototype.
- One-variable can-fail: hold estimator=exemplar, space=grounded fixed; ONLY new variable =
  agent-conditioning. Beat CI-sep the current verb-role exemplar re-selector (0.46) and (the real bar)
  the parse (0.59). A negative is informative: it says the residual is STRUCTURAL info the parse has,
  not plausibility a re-selector can recover.
- HONEST CALIBRATION (drill's own cap): P~0.45-0.50 that agent-conditioning recovers >= +0.05 CI-sep on
  THIS task (magnitude is a novel synthesis; gains likely concentrate on frequent agent-verb pairs; part
  of the parse's 0.59 is structural info -- attachment/animacy/literal sentence -- that NO corpus-stat
  re-selector recovers). If B stalls -> option A (a genuinely-untested DEPENDENCY-parsed similarity
  space, optionally cheapened with symmetric-pattern coordination) as B's metric.

Ranked build order (fidelity x tractability): B agent-conditioned exemplar (FIRST) > A dependency
selectional-similarity space > E whole-event-tuple exemplar retrieval > D symmetric-pattern metric >
C flat role-filler tensor (substrate, not the lever).

Key sources: Erk 2007 (ACL); Pado & Lapata 2007 (Comput. Ling.); Baroni & Lenci 2010 (Distributional
Memory); Chersoni et al. 2017/2019 (SDM); Van de Cruys 2009 (tensor SP); Schwartz, Reichart & Rappoport
2015 (symmetric patterns); McRae & Matsuki; Bicknell et al. 2010; Metusalem et al. 2012; Michaelov et
al. 2024 (agent-preference N400); dual-hub AG/ATL (Cerebral Cortex 2024); Kauf/Chersoni 2021/2023.
