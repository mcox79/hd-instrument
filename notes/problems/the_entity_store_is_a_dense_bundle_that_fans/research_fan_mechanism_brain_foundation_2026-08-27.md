# Brain-foundation research drill: the fan effect fix (DG separation vs context reinstatement)

Solver problem `the_entity_store_is_a_dense_bundle_that_fans`. Dispatched via `research` (4 parallel
lit-scans, Q1-Q4). Findings persisted verbatim-in-substance below (full sub-agent reports were long;
load-bearing content + citations kept). Each claim tagged PINNED / OUR-INVENTION / PLAUSIBLE-BUT-UNTESTED.
ASCII only.

## Q1 -- UNIFICATION: DG conjunctive pattern separation vs TCM context reinstatement

- The literature treats these as the SAME computational architecture viewed from two ends of the
  encoding->retrieval pipeline, NOT two independent mechanisms. Anatomically, item/content (lateral
  entorhinal, LEC) and spatial/temporal CONTEXT (medial entorhinal, MEC) arrive on separate perforant-path
  channels and CONVERGE on dentate gyrus granule cells -- so the DG code is conjunctive over content+context
  because that conjunction is what physically lands on the granule cell (Hargreaves et al. 2005, Science).
  Storage-side pattern separation acts on the bound content+context conjunction; retrieval-side context-
  cuing (TCM) exploits the same binding. PINNED: hippocampal trace = conjunctive code binding content to
  context (O'Reilly & Rudy 2001, Psych Rev; Rudy & O'Reilly 2001; Norman & O'Reilly 2003).
- TCM/retrieved-context theory: context is a slowly-DRIFTING vector, items bound to context at encoding,
  retrieval cued by reinstated context (Howard & Kahana 2002; Polyn/Norman/Kahana 2009 CMR). Bramao et al.
  2022 (Cereb Cortex): context reinstatement tracks retrieval competition + interference resolution in an
  AB/AC (fan-like) paradigm -- PINNED as the closest precedent to "context resolves the fan".
- The specific asymmetry "content-only sparsification FAILS while conjunctive/context-inclusive separation
  SUCCEEDS" is PLAUSIBLE-BUT-UNTESTED -- a strong, near-unavoidable implication of conjunctive coding (content-
  only DG units give identical codes for a repeated entity regardless of episode), but no single paper states
  it as a tested failure mode. (A tool-hallucinated O'Reilly&McClelland 1994 quote asserting it was CAUGHT and
  discarded by the sub-agent.)
- WHAT THIS MEANS FOR OUR BUILD: sparsify/index the CONJUNCTIVE (entity x context) code, not content alone;
  the coarse "sentence" slot is too coarse a context -- a finer temporal context IS the TCM drift.

## Q2 -- WHAT SPARSITY BUYS (capacity scaling)

- Treves & Rolls (1991 Network; 1994 Hippocampus; restated Rolls 2013): p_max ~ k*C_RC / [a*ln(1/a)], a =
  population sparseness, C_RC = recurrent synapses/cell, k~0.2-0.3. As a->0, capacity->infinity; at fixed T
  below capacity, crosstalk grows ~ a*ln(1/a) * T. Sub-agent verified the a*ln(1/a) is in the DENOMINATOR via
  two worked numeric checks (C=12000,a=0.02 -> p_max~36k; a=0.1 -> ~12k). PINNED.
- Willshaw, Buneman & Longuet-Higgins 1969 (Nature): binary heteroassociative net, ln2~0.69 bits/synapse,
  optimal active units k~log(N). PINNED (via Knoblauch/Palm/Sommer 2010 restatement).
- Norman & O'Reilly 2003 "reduces the SLOPE of interference, not to zero" -- the literal word "slope" was NOT
  found in the PDF, but it is an accurate PARAPHRASE of the papers' claim (sparse codes reduce interference-
  growth-with-T without eliminating it). Treat as paraphrase, not verbatim.
- DG biological sparsity ~1-4% (Jung & McNaughton 1993 qualitative; Diamantaki 2016 ~14% but authors call it
  an overestimate). Specific % PLAUSIBLE-BUT-UNTESTED; the 1-4% range is directionally corroborated.
- WHAT THIS MEANS: score the sweep by the fan SLOPE (or capacity-at-fixed-error), NOT error at one small T.
  Expect same rising shape fanned by slope (steeper at higher a). [This VALIDATES our fan-slope metric.]

## Q3 -- RESIDUAL tracks SIMILARITY not COUNT (the brain-faithful signature)

- PINNED: pattern-separation failure tracks item-to-item SIMILARITY (graded). Leutgeb et al. 2007 (Science,
  DG rate-remapping tracks input similarity); Bakker et al. 2008 (Science, human CA3/DG lure-vs-target);
  Yassa & Stark 2011 (TiNS review; Mnemonic Similarity Task/LDI indexed by target-lure SIMILARITY, not list
  length); Kirwan & Stark 2007; Lacy 2011; Motley & Kirwan 2012; Norman 2010 ("When the average level of
  similarity between items is very high, hippocampal pattern separation can FAIL"). General connectionist
  backing: McCloskey & Cohen 1989; French 1999 (interference scales with representational OVERLAP).
- COUNT-invariance (robust to N specifically) is PLAUSIBLE-BUT-UNTESTED and the STRONG form is likely FALSE:
  classic Willshaw/Marr/Treves-Rolls capacity theory shows AGGREGATE crosstalk from many weak-overlap
  competitors can STILL grow with N even under sparse coding. Honest claim: error rises STEEPLY with
  similarity, MORE SLOWLY (flatter) with count -- NOT that count becomes irrelevant.
- OPERATIONALIZE (per MST design): SIMILARITY arm (fix N, vary target-competitor similarity -> error rises);
  COUNT arm (fix similarity distribution, vary N -> comparatively flat until aggregate-crosstalk regime).
- WHAT THIS MEANS: our residual test must show err(similarity) steep AND err(count) shallow; a flat count
  curve at ALL N would over-claim.

## Q4 -- CA3 READOUT: one-shot vs iterative attractor

- Division of labor PINNED: DG separates (sparse expansion recoding); CA3 completes (dense recurrent-
  collateral attractor, Hopfield-style graded/sparse/diluted; Treves & Rolls; Rolls 2013).
- The iterative/recurrent machinery earns its keep SPECIFICALLY under PARTIAL/DEGRADED cues. Nakazawa et al.
  2002 (Science): CA3-NMDAR KO mice recall NORMALLY from a FULL cue, fail SELECTIVELY from a PARTIAL cue --
  clean double dissociation. Neunuebel & Knierim 2014; "Signature of Attractor Dynamics in CA3" (PLOS CB):
  recurrent collaterals needed to reproduce CA3 completion for small input mismatches. PINNED.
- For a FULLY-specified cue, feedforward/one-shot readout SUFFICES; recurrent completion is not behaviorally
  NECESSARY (Rolls 2013). The one place iterative helps with a full cue = denoising a CORRUPTED/interference-
  degraded STORED trace -- discussed only qualitatively, never isolated experimentally (PLAUSIBLE-BUT-UNTESTED).
- WHAT THIS MEANS: for our EXACT (entity, slot) cue, a one-shot heteroassociative read is faithful; iterative
  CA3 completion matters only for PARTIAL/degraded cues -- which is exactly the regime where our kWTA store
  turned out to be BRITTLE without it (see SOLVED Part 3).

## NET

- The measured fan is NOT superposition crosstalk (see SOLVED diagnosis). The brain-faithful fix is a FINER
  CONJUNCTIVE temporal context (TCM continuous drift; DG conjunctive coding) + context-cued SET reactivation
  (CA3 completion under a partial cue) -- unifying Q1's two-sides-of-one-coin.
- The brief's sparse mechanism (Q2) is the correct design for the SEPARATE high-unique-load superposition
  regime; its residual is similarity-gated (Q3); and its exact-cue read is one-shot-faithful while partial-cue
  robustness needs the iterative CA3 completion (Q4) our current store lacks.
