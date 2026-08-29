# Research drill: brain mechanism of discourse-fact resolution vs intra-sentential binding (2026-08-29)

Four parallel lit-scan lanes (hippocampal relational binding; bridging-inference computation; discourse-new-entity
vs syntax; glass-box non-LLM systems), dispatched to test whether "accumulate per-entity facts by reading + resolve
a reference by 2-hop bridge to the coherent entity" is the brain's actual mechanism, and whether it can even apply
to the MEASURED residual (gold entity freshly introduced, intra-sentential case). Sourcing caveat: several PDF
fetches failed (403 / binary); numbers marked "secondary" rest on citing sources, not primary text.

## 1. Garrod & Sanford resolution stage -- what it computes, on what, how fast
- Sanford & Garrod Scenario-Mapping-and-Focus (Garrod & Sanford 1981; Garrod, Freudenthal & Boyle 1994, JML): a
  general implicit scenario/script supplies ROLE SLOTS; a specific token is BOUND into a role; role-consistent
  bridging inferences read faster than scenario-inconsistent ones. PINNED (reading-time data, primary-adjacent).
- Kintsch 1988 (Psych Review) construction-integration: textbase vs situation model, resolved by constraint-
  satisfaction activation spreading over ONE associative network -- general-knowledge and text-specific
  propositions are NOT computationally typed apart. PLAUSIBLE / secondary (primary PDF fetch failed).
- Timing: EEG theta-band sync ~240-450ms indexes referent ACTIVATION (fast/bonding); gamma-band sync ~690-1000ms
  indexes discourse-level INTEGRATION (slow/resolution) -- PINNED two-stage split operationalizing Garrod-Sanford
  (PMID 32065957). Nieuwland/Van Berkum Nref: sustained frontal negativity from ~300ms, scales with WM span.
- SCOPE (load-bearing): the paradigm (Garrod & Sanford 1985; Garrod & Terras 2000) is built and TESTED ON
  MULTI-SENTENCE designs -- a context sentence establishes a role, a FOLLOWING sentence carries the anaphor. No
  study found applying it to same-clause-complex (intra-sentential) binding. Absence-of-evidence /
  theoretical-inference, but consistent across every source checked.

## 2. Hippocampal (entity, relation, value) binding
- Relational-memory theory (Cohen & Eichenbaum 1993; Konkel et al. 2008, "hippocampal amnesia impairs all manner
  of relational memory") -- PINNED at the general level (lesion evidence): hippocampus needed for arbitrary
  associations, cortex for item memory. Eichenbaum 2004 (Neuron) is a THEORETICAL SYNTHESIS on that base, not
  itself a new measurement.
- Direct reading evidence (new, strong): Nieuwland, Petersson & Van Berkum 2007 (NeuroImage) -- PINNED fMRI,
  hippocampal BOLD rises for pronouns resolving to a unique/coherent antecedent vs ambiguous/failed ones. A 2024
  Science concept-cell paper (author tag conflicted across lanes -- "Chen et al." vs "Dijksterhuis et al.", FLAG
  unresolved) -- PINNED single-unit: ~61 hippocampal concept cells across 12 patients reactivate when a LATER
  PRONOUN refers back to their preferred noun during reading. This is the single most direct measured circuit for
  "retrieve a bound entity to resolve a later reference" -- but it is reactivation of an entity's IDENTITY, not a
  stated arbitrary attribute-relation ("Sam is a doctor").
- Baldassano et al. 2017 (Neuron) -- PINNED fMRI, hippocampal activity at narrative event boundaries + later
  cortical pattern-reinstatement for situation-model recall.
- HONESTY CHECK: "hippocampus binds the (entity,relation,value) conjunction; neocortex integrates it" is NOT shown
  as one circuit-level result anywhere. It is a defensible bridge across three separate PINNED literatures (general
  relational binding + event-boundary consolidation + pronoun-driven concept-cell reactivation) -- itself
  OUR-INVENTION-UNDER-TEST / THEORETICAL EXTRAPOLATION. Situation models look HYBRID: cortical DMN/posterior-medial
  network carries the standing model, hippocampus engages at UPDATE/boundary and RETRIEVAL moments only.

## 3. Bridging inference -- 2-hop structure and its neural split
- No single paper states a clean two-hop "entity-fact THEN general-knowledge" split. Scenario-mapping (above) is
  the closest PINNED fit (role slot = general scenario knowledge; bound token = discourse-specific fact). Hobbs &
  Stickel weighted abduction (1993, Artificial Intelligence) treats interpretation as the cheapest proof chaining
  ANY axioms, entity-specific and generic alike, with no principled hop-count -- the 2-hop framing is
  OUR-INVENTION-UNDER-TEST gloss on Hobbs, not his explicit claim.
- Neural dissociation is real but assembled, not single-study: semantic dementia (degraded general/conceptual
  knowledge, spared episodic) vs hippocampal amnesia (reverse) -- Graham, Simons, Pratt, Patterson & Hodges 2000
  (Neuropsychologia), PINNED double dissociation at the general level. Race, Keane & Verfaellie 2015: hippocampal-
  damage patients fail pronoun-to-first-mentioned-referent linkage and lose shared-knowledge definite marking --
  PINNED, closest direct hit on OUR mechanism. Developmental-amnesia case N.C. fails novel transitive-inference
  bridging despite intact semantic knowledge (Hippocampus 2016) -- PINNED.
- Timing (PINNED, primary, exact figures confirmed): Haviland & Clark 1974 -- direct antecedent 835ms vs bridging
  1016ms (181ms slower, p<.025); 137-181ms bridging cost replicated across three experiments. Confirms bridging is
  a real, measurable, SLOW extra step vs direct reference -- consistent with retrieval-then-integrate, not proof of
  exactly two hops.

## 4. Freshly-introduced entity: syntax, not discourse facts (the critical question)
- Gernsbacher & Hargreaves 1988: first-mentioned participants accessed ~60ms faster (probe recognition) -- PINNED.
  But Hert et al. 2024 (Cognitive Science) show this "first-mention advantage" becomes NON-SIGNIFICANT for pronoun
  resolution once SUBJECTHOOD is controlled -- PINNED, and load-bearing: the apparent freshness effect is really
  reliance on the one structural cue (subjecthood) available for a brand-new referent, because nothing else exists.
- Centering Theory (Grosz, Joshi & Weinstein 1995): Cb(Un) is defined via entities realized in Un-1 -- the FIRST
  utterance of a segment has NO Cb by construction, so ranking necessarily falls to Cf/grammatical-role ordering.
  Structural, not discourse-bridging, BY DEFINITION -- nothing yet to bridge to. THEORETICAL-INFERENCE (definitional
  property, not a dedicated experiment), but Prince 1981's "brand-new" entity class (explicitly NOT inferentially
  linkable to existing discourse entities) is PINNED/definitional and points the same way.
- Timing dissociation (PINNED): Sturt 2003 (JML) -- structural (Principle-A-class) constraints applied WITHIN
  first-pass fixations, too fast for discourse-model retrieval. Within-clause coreference elicits an immediate
  P600; between-clause coreference elicits a delayed N400 (Camblin/Gordon/Swaab-line ERP work, secondary-sourced)
  -- intra-sentential binding runs on a categorically faster timescale than inter-sentential situation integration.
- CONVERGENT VERDICT (no single decisive experiment, four independent lines agree): a freshly-introduced,
  intra-sentential antecedent is resolved by FAST STRUCTURAL cues NOT BY CHOICE but BY NECESSITY -- the situation-
  model/discourse-fact machinery has nothing to retrieve yet, and Garrod-Sanford's own resolution paradigm was
  never tested (nor plausibly intended to apply) within that configuration.

## 5. Glass-box (non-LLM) systems: does fact-accumulation + bridging recover hard cases?
- Hobbs/TACITUS abduction (1993): two bottlenecks reported (secondary characterization, no primary number
  recovered) -- axiom/knowledge-coverage incompleteness, and combinatorial abductive-search cost worsening with KB
  size.
- Script/schema systems (SAM/FRUMP/PAM): hand-authored scripts, no per-entity fact memory EXTRACTED from text, and
  textbook-documented failure to scale via knowledge acquisition. No reference-resolution accuracy numbers survive.
- Structural/salience baselines actually reported: Hobbs 1978 syntactic algorithm -- PINNED 88.3% (no selectional
  constraints) / 91.7% (with) on 300 pronouns, but on the MULTI-CANDIDATE (genuinely hard) subset ONLY, accuracy
  drops to 82% -- direct proof that easy/single-candidate cases inflate whole-corpus numbers. Lappin & Leass 1994
  (RAP, salience-based, PINNED) -- 86% on 360 pronouns, ~4pt over the Hobbs baseline; NOT a fact-driven system.
- Bridging-specific systems: Poesio, Vieira & Teufel 1997 WordNet-relation bridging resolution -- secondary-
  characterized as "mediocre," knowledge/lexical-coverage-limited. Later rule-based ISNotes-era bridging systems
  beaten by learned systems by only modest margins (~0.1-10.5 F1), implying the rule-based ceiling was real but
  not catastrophic.
- CROSS-CUTTING: every source naming a bottleneck names KNOWLEDGE COVERAGE/EXTRACTION, not the reasoning step
  itself, as primary (abductive search cost is a secondary compounding factor). NO source found reporting success
  specifically on hard/anti-typical (non-salience-following) cases -- the literature as searched does not appear
  to isolate hard-case performance from easy-case performance at all. This is a gap, not a result to lean on.

## BOTTOM LINE
1. PARTLY: "accumulate per-entity facts by reading + resolve by bridging to the coherent entity" IS the brain's
   real mechanism for genuine INTER-SENTENTIAL reference (Sanford-Garrod scenario mapping, Haviland-Clark timing
   cost, hippocampal concept-cell reactivation to pronouns) -- but it structurally CANNOT be the mechanism for a
   freshly-introduced, intra-sentential antecedent: by definition (Centering's Cb-absence, Prince's brand-new
   class) and by measured timing (fast structural ERP/eye-tracking vs slow discourse-integration ERP/eye-tracking)
   there is no discourse fact yet to retrieve at the moment that case must resolve.
2. This means the MEASURED anti-typical coref residual (freshly-introduced entity, intra-sentential) is very
   likely the WRONG population to validate a fact-store+bridging build against -- confirming the problem brief's
   own hunch with a mechanistic reason, not just a distributional one.
3. DESIGN CONSTRAINT: gate the fact-store/bridging operator by discourse age of the candidate (>=1 prior
   accumulated predicate-argument fact, AND not same-clause-complex as the pronoun) before invoking it; build and
   measure its win on that DIFFERENT, inter-sentential, fact-decisive population (bridging inference, next-event
   prediction, QA) rather than re-targeting the intra-sentential residual, where the brain's own mechanism -- and
   ours -- has nothing yet to bridge to.
