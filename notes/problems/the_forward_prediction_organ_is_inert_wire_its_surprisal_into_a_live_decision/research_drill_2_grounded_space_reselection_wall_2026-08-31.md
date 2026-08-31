# Research drill 2 (2026-08-31): why the grounded-space prototype flags but cannot re-select

Dispatched via hdi_research AFTER the measured wall: surprisal is a strong error FLAG (AUC 0.65) but
using it to RE-SELECT the patient (adopt the best thematic-fit candidate) HURTS at every threshold,
even in the non-canonical regime. Question: why, and what is the brain-foundational fix?

## Headline
The flag-works / re-selector-fails split is a KNOWN, principled, brain-attested dissociation, not a bug.
Violation DETECTION and plausibility RANKING are computed by different representations, in different
tissue, at different granularities. A sensorimotor centroid is the right shape for the first and the
wrong shape for the second.

## Answers (citation-backed)

**Q1 -- Why detect but not re-select?** Confirmed. Violation detection needs one coarse decision
boundary around the verb's argument distribution ("is this filler an outlier?") -- 12 grounded
dimensions (animacy/concreteness/modality) draw it well. Ranking two IN-distribution competitors needs
the distribution's fine internal metric (verb-specific, sense-disambiguated, relational), which a
mean-of-means destroys. Santus et al. 2017: cosine-to-a-prototype "conflates multiple senses"; feature-
OVERLAP beats cosine. Erk 2007: similarity-to-EXEMPLARS beats prototype/centroid SP models. McRae &
Matsuki 2009 / Erk, Pado & Pado 2010 / Chersoni et al. 2019 (Structured Distributional Model): thematic
fit is a verb-specific, context-conditioned, RELATIONAL computation; a structured event graph is SOTA.

**Q2 -- Which brain representation?** NOT the ATL sensorimotor-feature hub. Dual-hub theory: the ATL hub
(Lambon Ralph et al. 2017) codes taxonomic/feature similarity (good for "weird kind of thing" =
detection); a SECOND hub in the angular gyrus / temporo-parietal cortex codes THEMATIC/EVENT relations
(dog-bone) -- thematic-fit ranking is angular-gyrus / generalized-event-knowledge (GEK) territory
(Elman 2009; McRae & Matsuki 2009; Metusalem et al. 2012; Paczynski & Kuperberg 2012 show animacy-
violation and event-plausibility are SEPARABLE systems).

**Q3 -- The fix, ranked.** (1) HIGHEST YIELD + highest fidelity: a STRUCTURED verb-role -> grounded-
filler EXEMPLAR/relational event store (distributional event graph / role-filler binding), scored by
feature-overlap / similarity-to-exemplars, NOT distance-to-mean. Brain-faithful (GEK + angular gyrus),
SOTA (Chersoni 2019), glass-box, FHRR-compatible. THE Phase-1 meaning-supply lever. (2) Interim: wider/
higher-dim glass-box distributional features (narrows but does NOT close the gap -- Kauf 2023). (3) Full
episodic event-schema retrieval (mature form of 1). The centroid is a PROTOTYPE where the brain uses
EXEMPLAR/event memory (Nosofsky & Zaki 2002: prototypes lose within-category discrimination).

**Q4 -- Is detection-easier-than-ranking principled?** Yes, replicated. Warren & McConnell 2007:
impossible-event violations disrupt reading earlier/greater than extremely-implausible-but-possible.
Kauf et al. 2023 (Cognitive Science): near-EXACT analog at scale -- models separate impossible/possible
but NOT likely/unlikely; they organize around categorical feasibility, not probabilistic typicality.
Kuperberg role-reversal illusions: the brain itself is temporarily blind to role swaps when both
arguments are plausible.

## Frame for the enumerated negative (used in SOLVED.md)
Not "surprisal fails" -- "the centroid is the wrong ESTIMATOR CLASS (prototype) for ranking." The
forward signal is validated as a confidence/abstain FLAG (keep it, wire it). Re-selection failed because
the meaning-supply is a prototype where the brain uses a structured verb-specific event/exemplar memory.
Do NOT generalize to "forward prediction can't re-select" -- a stronger meaning representation was never
tested. Seeds the Phase-1 meaning-supply follow-on: build the structured event store as the re-selector.

Key sources: Santus et al. 2017 (EMNLP); Erk 2007 (ACL); Erk, Pado & Pado 2010 (Comput. Ling.); McRae &
Matsuki 2009; Chersoni et al. 2019 (NLE, SDM); Lambon Ralph et al. 2017 (hub-and-spoke) + dual-hub
(Cereb. Cortex 2024); Elman 2009; Metusalem et al. 2012; Paczynski & Kuperberg 2012; Warren & McConnell
2007; Kauf et al. 2023 (Cognitive Science); Nosofsky & Zaki 2002; Lynott & Connell 2020 (Lancaster).
