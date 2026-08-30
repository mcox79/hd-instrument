# Research drill: physical vs mental/social causation -- ONE force system or TWO?

Problem: `causation_is_typed_per_clause_not_across_the_causal_network`
Date: 2026-08-30
Author: hdi_research (Director drill for the SOLVER)

## The wall (measured on disk)
On 16 verbatim LitBank cross-event causal edges (real "X because Y" / bridging pairs),
a FrameNet-derived PHYSICAL force-dynamic verb lexicon covers the cause verb in only 3/16.
The other 13 are MENTAL / SOCIAL / INTENTIONAL causation:
"she frowned because she remembered", "the servants wailed because she had died",
"he held his tongue because he promised", "I came because I felt strange".
A theory of physical force interaction structurally cannot type these from the verb.

## BOTTOM LINE (cite this in SOLVED.md)
The physical/mental split is a **principled representational bound on the SOURCE SYSTEM**
(the brain reads physical forces with one system and intentional/social forces with another --
robustly dissociated in fMRI, patients, and development), **but it is NOT a bound on the causal
TYPOLOGY.** CAUSE / ENABLE / PREVENT is a single, domain-general force-configuration scheme that
Talmy and Wolff built explicitly to span physical, intra-psychological, and social causation.

=> Architecture: **ONE force typology, TWO force-source front-ends.**
The 13/16 "miss" is the *expected signature of a missing mentalizing front-end*, not a ceiling and
not a lexicon-coverage bug you can patch by adding physical verbs. Do NOT build a separate typer with
a different output vocabulary; do NOT stretch the physical verb lexicon over intentional causation.
Build a second intentional/affective force-source extractor that feeds the SAME CAUSE/ENABLE/PREVENT engine.

---

## Q1. Does the brain represent physical vs mental/intentional causation with DIFFERENT systems?
**Yes -- two dissociable systems, present from infancy.** This is the strongest, most convergent finding.

- **Intuitive-physics / force system.** Fischer, Mikhael, Tenenbaum & Kanwisher (2016, PNAS 113:E5072-E5081,
  "Functional neuroanatomy of intuitive physical inference"): a "physics engine" in FRONTOPARIETAL cortex
  (dorsal premotor, supplementary motor area, superior/inferior parietal), engaged both by explicit physical
  inference AND by merely viewing physically-rich scenes. Crucially it resembles regions for MOTOR PLANNING
  and TOOL USE -- i.e. physical causal cognition is a *motor/perceptual simulation*, which is exactly what a
  force-dynamic account predicts. Perceptual root: Michotte (1963) "launching effect" = automatic perception of
  physical causality.
- **Mentalizing / Theory-of-Mind system.** Saxe & Kanwisher (2003) right temporo-parietal junction (rTPJ);
  Frith & Frith mentalizing network = mPFC, bilateral TPJ, precuneus, temporal poles. Reads goals, beliefs,
  intentions. Perceptual root: Heider & Simmel (1944) -- the SAME class of moving-shape stimuli that yields
  physical "launching" yields spontaneous INTENTIONAL/animacy attribution, and the two are perceptually and
  neurally separable ("Perceived physical and social causality in animated motions"; fMRI studies of causal
  judgment in physical vs social contexts show differential networks -- parietal/occipito-parietal simulation
  for physical, mentalizing for social).
- **Developmental / architectural dissociation (the clincher).** Leslie (1994, "ToMM, ToBY, and Agency", in
  Mapping the Mind): **ToBY** (Theory of Body) handles MECHANICAL agency using the *primitive concept FORCE*,
  vs **ToMM** (Theory of Mind Mechanism) which handles INTENTIONAL agency via metarepresentation of goals.
  Both operational within the first few months. Spelke/Carey core-knowledge: separate core systems for
  objects/physical-causality vs agents/intentional-causality. The split is not a late overlay; it is baked into
  the architecture from infancy.
- Wolff & Barbey (2015, Frontiers in Human Neuroscience 9:1, "Causal reasoning with forces") themselves
  distinguish physical, psychological, and social causation.

**Consequence for the wall:** the brain does NOT type "she frowned because she remembered" with the physical
force system. A pure FrameNet-physical-verb lexicon is the WRONG instrument for the mental slice by
construction. The 13/16 miss is expected.

## Q2. At the DISCOURSE level, does the reader build and TYPE causal links (CAUSE vs ENABLE vs PREVENT)?
- **Causal network + necessity.** Trabasso & van den Broek (1985, J. Memory & Language 24:612-630, "Causal
  thinking and the representation of narrative events"): events are linked in a causal network; edges are
  weighted by NECESSITY IN THE CIRCUMSTANCES (a counterfactual test). Causal connectivity predicts recall and
  judged importance.
- **The discourse literature's OWN taxonomy is already domain-typed** -- and it directly predicts your 13/16.
  Warren, Nicholas & Trabasso (1979, "Event chains and inferences in understanding narratives") and Trabasso,
  van den Broek & Suh (1989) classify narrative causal relations into four types, ordered by strength:
  **PHYSICAL, MOTIVATIONAL, PSYCHOLOGICAL, ENABLEMENT.** Narrative is DOMINATED by motivational + psychological
  causation; physical is the minority. So a physical-only typer covering ~3/16 is the arithmetic you would
  predict from the reading-comprehension literature itself.
- **Graded typing across sentences is real and online.** Kuperberg, Paczynski & Ditman (2010, J. Cognitive
  Neuroscience 23:1230-1246, "Establishing causal coherence across sentences: an ERP study"): critical words
  that were causally UNRELATED to prior context evoked a larger N400 than INTERMEDIATELY related, which was
  larger than HIGHLY related -- a GRADED N400 -- with lexico-semantic association matched by LSA. So the grading
  is *situation-level causal coherence*, not word association: readers compute degrees of causal
  strength/necessity across sentence boundaries word-by-word.
- **CAUSE vs ENABLE specifically.** Singer & Halldorson (1996) validation model: a causal bridging inference
  ("Water extinguishes fire") is COMPUTED then VALIDATED against world knowledge before acceptance -- readers
  test necessity/sufficiency, which is exactly the CAUSE-vs-ENABLE distinction. Reading-time: causal relatedness
  drives RT (Keenan, Baillet & Brown 1984 inverted-U; Myers, Shinjo & Duffy 1987).
  Caveat (honest): the clean, fully-crossed CAUSE/ENABLE/PREVENT 3-way online dissociation is best nailed at the
  CLAUSE level (Wolff 2007; Sloman, Barbey & Hotaling 2009). At the DISCOURSE level the robust evidence is for
  graded strength/necessity (which the CAUSE/ENABLE/PREVENT typology encodes) rather than a labelled 3-way ERP
  contrast. This is a place to be careful in claims, not a blocker for the build.

## Q3. Principled bound, or a UNIFIED force account? -> a DOUBLE structure
The resolution is that the theory factorizes into a shared TYPOLOGY and a domain-specific SOURCE.

**(a) The TYPOLOGY is unified and abstract (NOT a bound).**
- Talmy (1988, Cognitive Science 12:49-100, "Force Dynamics in Language and Cognition") built force dynamics as
  a *unified* system from the start: physical, **intra-psychological (psychodynamics)**, and **social
  (sociodynamics)**. In the intra-psychological schema the SELF is split into an Agonist = the "desiring self"
  (drives) and an Antagonist = the "blocking/spurring self" (will/superego). "He refrained from speaking",
  "she held back" = the Antagonist blocks the Agonist's tendency. Metaphorical transfer generalizes the same
  force parameters to social pressure (urging, letting, forcing).
- Wolff (2007, JEP:General 136:82-111, "Representing Causation") formalized CAUSE / ENABLE / PREVENT / DESPITE
  via THREE ABSTRACT dimensions -- (i) the patient's TENDENCY toward the endstate, (ii) CONCORDANCE vs
  opposition between affector and patient, (iii) whether the endstate is REACHED. None of these three is
  physical; they are force-CONFIGURATION parameters that apply to any tendency/opposition.
- Wolff & Barbey (2015): force theory is a general theory of causal COMPOSITION; the "forces" generalize to
  psychological tendencies and dispositions, so the same composition machinery covers psychological and social
  causation.

**(b) The FORCE-SOURCE is domain-specific (this is where the bound really lives).**
- What differs across domains is HOW the vectors are read off: a physical push (intuitive-physics / ToBY) vs a
  goal / desire / belief / obligation (mentalizing / ToMM). The configuration LOGIC is shared; the EXTRACTION of
  the Agonist tendency and the Antagonist force is done by different systems. You cannot read intentional forces
  off a physical-verb lexicon.

**Worked mechanism -- "he held his tongue because he promised":**
- Agonist (tendency) = the urge/tendency to speak (the desiring self).
- Antagonist (opposing force) = the promise / the internalized obligation to keep it (blocking self; a SOCIAL
  force internalized -- Talmy sociodynamics + psychodynamics).
- Antagonist stronger -> resultant = REST (silence). "Held his tongue" is lexically a BLOCKAGE-of-an-urge
  idiom -> force config = PREVENT/BLOCK.
The Talmy/Wolff typology handles this cleanly. What is missing is a reader that EXTRACTS the goal (tendency to
speak) and the obligation (promise as opposing force) -- a mentalizing extractor, not a physical verb lexicon.

## Q4. Right next move
**Recommendation: (b) a UNIFIED force typer, extended with a SECOND intentional/affective force-source
front-end -- NOT (a) a wholly separate typer with a different output vocabulary.** Rationale: this is the only
option that matches BOTH the neural dissociation (Q1: two input systems) AND the unified computational theory
(Q3: one abstract typology), AND it reproduces Trabasso's native 4-way taxonomy (physical + motivational +
psychological + enablement) as exactly a two-source / one-typology structure.

Concrete architecture:
- **Shared output engine (already have the core):** Wolff's 3 abstract dims -> CAUSE / ENABLE / PREVENT.
  Keep this as the single typing layer for ALL edges.
- **Front-end #1 -- physical force-source (have):** FrameNet physical force-dynamic verbs. Covers the 3/16.
- **Front-end #2 -- intentional/social force-source (BUILD):** for a mental/social edge, map onto Talmy's
  psychodynamic/sociodynamic schema:
    1. Agonist TENDENCY: does the experiencer already tend toward the endstate? (a goal, desire, disposition,
       emotional tendency -- "wanted to speak", "tended to grieve").
    2. Antagonist FORCE + CONCORDANCE: a competing goal, a belief, a promise/obligation, a social pressure, or
       an emotion -- does it CONCORD with or OPPOSE the tendency?
    3. ENDSTATE: is it realized?
  Feed (1)(2)(3) into the SAME Wolff engine to emit CAUSE/ENABLE/PREVENT.
- **Brain mapping:** ToMM/mentalizing supplies the intentional vectors; ToBY/intuitive-physics supplies the
  physical vectors; a shared relational force-configuration typology composes either. Two input systems, one
  typing scheme -- brain-faithful.

What front-end #2 needs (buildable, it is the intentional analog of the physical force lexicon):
- FrameNet mental/emotion/communication/commitment frames (Experiencer_obj/subj, Stimulus, Emotion_directed,
  Communication, Commitment, Desiring, Purpose frames) to supply Agonist tendency + Antagonist force roles.
- Verb classes for desire / belief / obligation / emotion, and a light ToM-style goal/obligation reader to set
  the tendency and concordance signs.

## Prior arc work (credit + build-on)
- `exp_read_causal_chain_on_chain_cause_v1` (HARD_PASS, 2026-07-24) -- causal-chain reading.
- `exp_event_boundary_relevance_gate_v1` (HARD-PASS, 2026-08-05) -- event/relevance gating.
Neither typed edges by physical-vs-intentional force source; this drill extends them.

## VERDICT
Two systems at the SOURCE level (principled, well-evidenced: intuitive-physics/ToBY vs mentalizing/ToMM), one
typology at the OUTPUT level (Talmy psychodynamics + Wolff's abstract force dimensions). Therefore the correct
build is one CAUSE/ENABLE/PREVENT force engine fed by two force-source extractors; add the intentional/affective
extractor. The physical-verb-lexicon 13/16 miss is a fidelity gap to build ACROSS (the missing mentalizing
front-end), not a principled ceiling on force-typing and not a reason to fork the output vocabulary.

## Primary citations
- Talmy, L. (1988). Force dynamics in language and cognition. Cognitive Science 12(1):49-100.
  (unified physical / psychodynamic / sociodynamic force dynamics; self-as-Agonist/Antagonist)
- Wolff, P. (2007). Representing causation. JEP: General 136(1):82-111.
  (CAUSE/ENABLE/PREVENT/DESPITE via tendency + concordance + endstate)
- Wolff, P. & Barbey, A. K. (2015). Causal reasoning with forces. Frontiers in Human Neuroscience 9:1.
  (force composition as a general causal-cognition theory; physical vs psychological vs social)
- Fischer, J., Mikhael, J. G., Tenenbaum, J. B. & Kanwisher, N. (2016). Functional neuroanatomy of intuitive
  physical inference. PNAS 113(34):E5072-E5081. (frontoparietal/premotor "physics engine")
- Saxe, R. & Kanwisher, N. (2003). People thinking about thinking people: the role of the TPJ in theory of
  mind. NeuroImage 19:1835-1842. (+ Frith & Frith mentalizing network: mPFC/TPJ/precuneus/temporal poles)
- Leslie, A. M. (1994). ToMM, ToBY, and Agency: core architecture and domain specificity. In Hirschfeld &
  Gelman (eds.), Mapping the Mind. (ToBY mechanical/FORCE vs ToMM intentional -- infant architectural split)
- Trabasso, T. & van den Broek, P. (1985). Causal thinking and the representation of narrative events.
  J. Memory & Language 24:612-630. (causal network; necessity-in-the-circumstances)
- Warren, W. H., Nicholas, D. W. & Trabasso, T. (1979). Event chains and inferences in understanding
  narratives. + Trabasso, van den Broek & Suh (1989). (narrative taxonomy: physical / motivational /
  psychological / enablement, by strength)
- Kuperberg, G. R., Paczynski, M. & Ditman, T. (2010). Establishing causal coherence across sentences: an ERP
  study. J. Cognitive Neuroscience 23(5):1230-1246. (graded N400: unrelated > intermediate > related; LSA-matched)
- Singer, M. & Halldorson, M. (1996). Constructing and validating motive bridging inferences.
  (validation-of-causal-bridging: necessity/sufficiency testing -- cause vs enable)
- Michotte, A. (1963). The Perception of Causality. (launching = physical causality) ; Heider, F. & Simmel, M.
  (1944). An experimental study of apparent behavior. (intentional/animacy attribution)

## TLDR (plain language)
The brain has two separate machines for "why did that happen": one for physical pushes and one for what people
want, feel, and promise. Stories run almost entirely on the second machine -- that is why a physical-only tool
only handled 3 of 16 real story links. But the LABELS we care about (this made that happen / this let it happen
/ this stopped it) are the SAME in both worlds; the founders of the theory built it to cover feelings and social
pressure too ("he kept quiet because he promised" = the promise is a force pushing against the urge to talk).
So the fix is not a different tool with different labels, and not more physical words -- it is a SECOND reader
that pulls out goals, feelings, and obligations and feeds them into the SAME make/let/stop labeller.

## Questions
None.

## Next steps
1. Build force-source front-end #2: an intentional/affective extractor keyed on FrameNet
   emotion/communication/commitment/desiring frames that emits (tendency, concordance, endstate) for the
   mental/social edges.
2. Route both front-ends into the existing Wolff CAUSE/ENABLE/PREVENT engine; re-measure coverage on the 16
   LitBank edges (target: the 13 mental/social edges now typed).
3. Keep discourse-level claims to "graded strength/necessity" (well-evidenced) rather than a labelled 3-way ERP
   dissociation across sentences (weaker evidence) when writing up.
