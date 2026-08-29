# Research drill: how the brain applies WORLD KNOWLEDGE to reference, and the glass-box no-LLM ceiling (2026-08-29)

Follow-on drill after the cross-domain GAP test proved the coref residual is `SEMANTIC_WALL_NOT_PARSE_WALL`. Four
parallel lanes (selectional plausibility/ATL hub; scripts/situation models; implicit causality/coherence; Winograd
symbolic systems). Persisted verbatim per the prior-work discipline. Full ~50-source note (strategy-side) at
`notes/research_world_knowledge_reference_resolution_glassbox_2026-08-29.md`.

## 1. MECHANISM + TIMING (layered, by grain and speed)
- **Selectional plausibility / thematic fit is graded, statistical, IMMEDIATE** (McRae, Spivey-Knowlton & Tanenhaus
  1998; Matsuki 2011 -- affects first-pass reading). **Hagoort et al. 2004 (Science):** a world-knowledge violation
  ("Dutch trains are white") gives an N400 indistinguishable from a lexical-semantic violation -- world knowledge
  integrates as fast as word meaning. Van Berkum 2003: discourse world-knowledge N400 from ~150-200ms.
- **Fast-coarse vs slow-fine are dissociable** (Paczynski & Kuperberg 2012): selectional/animacy violations disrupt
  reading earlier/harder than merely-implausible-legal events.
- **Substrate: the ATL "semantic hub"** (Patterson-Nestor-Rogers 2007; causal rTMS Pobric 2007). Implementation is
  **PDP / distributional, NOT symbolic** (Rogers, Lambon Ralph et al. 2004 Psych Review; semantic dementia = graded
  cross-category degradation, not clean edge loss).
- **Script/situation-model resolution is SLOWER** -- Garrod & Sanford two-stage BONDING (fast, structural) /
  RESOLUTION (slow, world-knowledge); Garrod & Terras 2000 (lexical first-pass, situational second-pass).

## 2. IMPLICIT CAUSALITY / COHERENCE (layered; the person-vs-person cases are situation-model, not lexical)
- Real per-verb lexical bias exists (Garvey-Caramazza 1974; Ferstl 2011 300-verb norms; Hartshorne-Snedeker 2013).
- BUT Bott & Solstad 2014/2021 (empty-slot): the lexical bias explains WHY an Explanation is expected + WHICH ARGUMENT
  SLOT -- NOT WHICH ENTITY fills it. Kehler & Rohde Bayesian `P(ref|pron) ~ P(pron|ref) x P(ref)` with a
  coherence-relation-conditioned prior; the SAME verb reverses bias by relation. Hobbs 1993 interpretation-as-abduction
  = the maximal version (cheapest logical explanation from general-knowledge axioms).
- For "Cheryl dumped her boyfriend ... Simon's advice ... he wouldn't...": "Simon" is in an ADJUNCT PP, not an argument
  of "dumped" -- a per-verb NP1/NP2 table cannot even in principle discriminate it. Needs situation-model reasoning.

## 3. WINOGRAD pre-LLM SYMBOLIC CEILING (the decisive bound; datasets kept distinct)
- Rahman & Ng 2012: 73.05% on DPR (n=564), not WSC-273. Peng-Khashabi-Roth 2015: 76.41% DPR.
- **Sharma/Vo/Baral (ASP over knowledge graphs): 82.47% (240/291) -- but HAND-BUILT per-item knowledge.** Fully-automatic
  knowledge-hunting: usable knowledge found for only 120/291 (coverage ~41%). Of 51 unsolved hand-buildable cases, 26
  needed MULTIPLE facts combined, 25 needed PROBABILISTIC/likelihood comparison -- categorical ASP structurally cannot
  express this (a real reasoning-expressiveness ceiling, separate from coverage).
- **Emami et al. 2018: 57.1% on the FULL official WSC-273 -- but via LIVE WEB SEARCH, not a static KG** (not no-LLM
  admissible -- external retrieval at inference).
- **NO fully-automatic STATIC-KG system on the complete WSC-273 is reported in the literature.** Bottleneck = knowledge
  EXTRACTION/COVERAGE (Kocijan, Davis et al. 2022 retrospective).

## 4. IS A KG FAITHFUL? No (implementation) / Yes (computational-level approximation)
The brain's semantic memory is distributional/graded (PDP), not symbolic -- a KG is NOT implementation-faithful, but IS
a legitimate COARSER computational-level approximation (like McRae cloze norms used in psycholinguistic models).
Consistent with our own positive control: the coarse 12-dim grounded space separated OBJECT-vs-OBJECT 8/8 (works where
the brain's fast coarse signal works) but is blind PERSON-vs-PERSON (where the brain needs slower, richer machinery).

## 5. BOTTOM LINE (two slices, two verdicts)
- **OBJECT/concrete-noun slice (parson-vs-mare): a glass-box selectional-plausibility mechanism plausibly recovers a
  MEASURABLE fraction** (positive control already 8/8 on objects). BUILD: a ConceptNet/CSKG (or WordNet-class)
  selectional-plausibility feature, fused via the SAME Bayesian-product machinery. **MEASURE THE ORACLE CEILING FIRST.**
- **PERSON-vs-PERSON slice (Cheryl/Simon): a real near-term bound for a static-KG SINGLE-HOP system** -- (a) ConceptNet
  likely lacks fine interpersonal-behavior facts (CSKG's ATOMIC-derived social if-then commonsense worth a coverage
  check); (b) single-hop plausibility (what the refuted coherence prior was) cannot express the multi-fact
  likelihood-weighted comparison the literature says this needs (Hobbs abduction; Kehler-Rohde). NOT unrecoverable in
  principle (Sharma proved symbolic multi-fact reasoning solves some WITH the right facts), but no automatic static-KG
  system cleared it. Test on CONSTRUCTED minimal pairs first, never the real residual directly.
