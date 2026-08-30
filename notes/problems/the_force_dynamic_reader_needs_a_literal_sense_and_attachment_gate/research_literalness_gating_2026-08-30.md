# Research drill: literalness gating for the force-dynamic reader (2026-08-30)

Lit-scan; each claim tagged PINNED (multi-study/causal evidence) / SUGGESTIVE (single-study or contested) /
SPECULATIVE (my synthesis, unverified). Prior-work check: substrate KB + `experiment_index.py` = NO prior arc work
on figurative/literal gating — this is novel territory for us.

## BOTTOM LINE (read first)
Your three-part conjunction (sense-frame + selectional/concreteness + attachment) is **substantially right and
brain-supported**, BUT the framing "the brain abstains on figurative, so we abstain on figurative" is **too binary and
mildly brain-UNfaithful.** The neural evidence says grounded simulation is **GRADED, not gated** (LIT > MET > IDIOM >
ABS), and the brain runs a *bleached* motor/force simulation for many metaphors. The clean "no simulation" result holds
specifically for **conventional / lexicalized-figurative / opaque-idiom** uses — which happens to be *exactly your
residual over-fire class* ("the news broke", "the deal fell through", "crushed by criticism"). So: **abstain is the
correct brain behavior for the class you actually need to catch**, but the right cut is **conventionality/sense-
competition, not figurativeness per se**, and there is a real THREE-way distinction you should build to, not two.

## Q1 — Is grounded simulation gated by literalness? Does the brain simulate figurative too?
- **Motor simulation is GRADED, not binary-gated. PINNED.** Raposo et al. 2009 (Neuropsychologia): isolated action verb
  → strong somatotopic motor/premotor activation; same verb in a *literal* sentence → weaker; in an *idiom* ("kick the
  bucket") → **no motor/premotor activation** (only Broca's). Aziz-Zadeh et al. 2006: no somatotopic motor for
  metaphorical/idiomatic phrases. So for **opaque idioms the physical simulation is genuinely OFF.**
- **BUT metaphors DO recruit sensorimotor cortex — the brain simulates a bleached version. PINNED (contested at edges).**
  Desai review "Are Metaphors Embodied? The Neural Evidence" (2023) + Desai et al. 2011/2013: action metaphors activate
  sensorimotor regions (esp. anterior inferior parietal / action-planning) *plus* abstract semantic regions; the full
  ordering is **LIT > MET > IDIOM > ABS**. Primary-motor recruitment is **inversely related to metaphor familiarity** —
  novel/unfamiliar figurative → more simulation; conventionalized → less. Idiom findings are the live controversy
  (Boulenger et al. 2009/2012 DO find motor activation; Raposo/Desai do not); Desai's proposal is idioms route through
  basal-ganglia action-schema *selection* rather than cortical simulation (SUGGESTIVE).
- **Implication for your design:** "abstain on ALL figurative" would over-abstain relative to the brain. The brain-
  faithful readout is: full simulation on literal-physical; **bleached** simulation on novel/transparent metaphor;
  **off** on conventional/lexicalized figurative + opaque idiom. Your residual over-fires are the last bucket → abstain
  is right *there*.

## Q2 — Online neural/behavioral signature of literal vs figurative at comprehension
- **Selectional / animacy-restriction violations elicit an N400. PINNED.** Verbs violating an argument's selectional
  restriction reliably elicit N400 (semantic-integration difficulty). In metaphor with inanimate initial nouns, an
  animacy violation elicits an N400 at the verb. The "man is pregnant" rational-account ERP work (Nieuwland-style)
  shows the N400 tracks *contextualized plausibility*, not raw anomaly.
- **Access is salience-ordered, not literal-first. PINNED (behavioral) / SUGGESTIVE (ERP).** Giora's Graded Salience
  Hypothesis: the *coded/salient* meaning (conventional, frequent, familiar) is retrieved first regardless of whether it
  is literal or figurative — so for "the news broke" the figurative "became public" sense is directly salient, the
  physical-break schema is not strongly evoked. This is the psycholinguistic license for "abstain": the physical sense
  is not the one the brain foregrounds.
- **Metaphor ERP = N400 (in minimal context) then P600. PINNED.** N400 for metaphor appears mainly in minimal context
  (indexes contextual expectation mismatch); P600 (reanalysis/integration) appears with or without context. Concreteness
  effect: literal expressions evoke the normal concreteness ERP effect; metaphors show *no* sensorimotor-feature
  concreteness signature (SUGGESTIVE — single-study).
- **Take:** the online cue you want to replicate is **selectional-preference-violation → reinterpretation**. That is a
  real, dateable neural signal, and it is computable glass-box.

## Q3 — Is selectional-preference / concreteness the right formalization?
- **Yes, it is the field-standard glass-box computation, and it is brain-plausible. PINNED (as a method).**
  - Selectional-preference *violation* = metaphor cue is the classic Wilks (1978) formalization; it maps directly onto
    the N400 selectional-violation signal.
  - Resnik (1996/97) selectional preference strength = KL divergence of P(class|verb) from P(class); selectional
    association per argument class — a fully glass-box, corpus-estimable score.
  - Thematic-fit models (Erk 2007; Lenci 2011; Sayeed et al. 2016; Baroni/Padó) generalize this to distributional
    role-filler compatibility and correlate with human plausibility judgments.
  - NLP metaphor detection converges on **concreteness-abstractness of the arguments** as the workhorse feature (MOH /
    Köper & Schulte im Walde; Turney concreteness; Brysbaert concreteness norms).
- **CAVEAT — concreteness of the PATIENT alone is insufficient. SUGGESTIVE→important.** "criticism crushed him": the
  patient "him" is concrete/animate, yet it is figurative — the violation is on the **agent/antagonist** ("criticism",
  abstract). This maps cleanly onto Wolff/Talmy's **two-force structure**: check the physical-force affordance of BOTH
  the antagonist (force source/instrument) AND the agonist (patient). An abstract filler in *either* physical-force slot
  → figurative. This is a concrete, theory-grounded upgrade to a naive one-slot concreteness check.
- **Richer alternative — coercion / Generative Lexicon (Pustejovsky). PINNED that coercion has measurable cost.**
  McElree/Traxler 2001/2002: "began the book" costs extra reading time vs "read the book" (type-coercion of ENTITY→EVENT);
  context priming attenuates it. This says the brain does not just check concreteness — it *type-shifts*, at a cost, and
  context can license it. For your gate this mostly matters as: a selectional mismatch that context *licenses* (a set-up
  figurative frame) should not necessarily abstain — but for a first glass-box gate, the selectional/concreteness check
  is the right 80/20 and coercion is the refinement.

## Q4 — Is there a cleaner unifying account than the 3-part conjunction?
- **Yes — constraint-satisfaction / predictive-coding, and literalness falls out. PINNED (framework) / SPECULATIVE (that
  it dominates figurative specifically).** Comprehension = parallel satisfaction of probabilistic constraints (lexical,
  selectional, contextual); the interpretation that best satisfies them wins. Under this view **"should I run the force
  simulation?" is not a separate module** — it is the readout of whether the *physical-force interpretation* is the one
  that best satisfies the joint (sense + selectional-fit + context) constraints. Semantic control (LIFG/pMTG; Lambon
  Ralph & Jefferies controlled-semantic-cognition) is the same competition: it selects the context-appropriate,
  possibly non-dominant sense and suppresses strong-but-irrelevant ones.
- **Design consequence (my strongest recommendation):** don't build three bolted-on gates ANDed together. Build **one
  glass-box scoring function** — a force-schema *affordance score* — that the physical reader engages above threshold.
  Its terms ARE your three signals, but combined as a competition, not a conjunction:
  `engage_physical = f( P(physical-sense | context),  selectional_fit(antagonist, agonist for the FORCE schema),
   ¬idiom_unit,  attachment_confirms_slots )`.
  This is cleaner, more brain-faithful (it *is* the sense-selection competition), and it naturally gives you the graded
  (not binary) output the neural data demand — and the info-free twin (shuffled sense labels / permuted attachment)
  drops the score, satisfying your can-fail bar.

## Q5 — Force-dynamic language: figurative-vs-literal sensitivity
- **Force dynamics is DEFINED to extend to social/psychological/intrapsychological causation. PINNED (theory).** Talmy's
  force dynamics and Wolff's dynamics model (Wolff 2007, "Representing Causation", JEP:General; Wolff & Song 2003, "Models
  of causation and the semantics of causal verbs") explicitly cover physical, intrapsychological, social, and
  institutional force. "She forced him to admit", "the pressure pushed him to quit" are **genuine force-dynamic events at
  the social level**, not noise.
- **Critical design implication — this is a THREE-way cut, not two.** "she forced him" is NOT the same class as "the deal
  fell through". The former is a *transparent/novel* force mapping the brain bleach-simulates and Wolff's theory *types*;
  the latter is a lexicalized idiom the brain does not simulate. So:
  - **(A) literal physical** ("the branch broke under the weight") → full engage.
  - **(B) transparent/novel force metaphor onto social-psych causation** ("she forced him to admit") → brain runs a
    bleached force sim; the force STRUCTURE genuinely holds. For THIS problem (a *physical* reader) → abstain-physical,
    but **label it "force-dynamic, non-physical"** — a candidate for a future social-force reader — do NOT silently
    discard it as "figurative junk."
  - **(C) conventional/lexicalized figurative + opaque idiom** ("the news broke", "the deal fell through", "crushed by
    criticism" where the causal frame is idiomatic) → no force sim → **ABSTAIN.** This is your residual over-fire class.
  The selectional/concreteness check separates (A) from (C) well, and will (over-)abstain on (B) — acceptable for the
  physical reader **only if you label (B) rather than drop it.**

## RECOMMENDATION — is your mechanism right, and what to build differently
1. **Keep all three signals** (sense + selectional/concreteness + attachment) — each is PINNED to a brain system
   (controlled semantic cognition / N400-selectional-violation / dependency parse). Your instinct is sound.
2. **Re-cut the target from "figurative" to "conventional/lexicalized figurative + idiom."** That is what the brain does
   NOT simulate, and it is your residual over-fire set. This is the single biggest fidelity fix.
3. **Combine as a competition/affordance SCORE, not a hard AND of three gates** (Q4). More brain-faithful, gives graded
   output, cleaner to twin-test.
4. **Selectional check must cover BOTH force roles** (antagonist AND agonist), not just the patient — maps to Wolff's
   two-force structure and catches "criticism crushed him" (abstract antagonist) that a patient-only concreteness check
   misses.
5. **Build the THREE-way output** (physical-engage / non-physical-force-LABEL / abstain), not a binary. Route (B) to a
   labeled bin instead of discarding — it protects a future social-force organ and is more honest to the theory.
6. **Reuse, don't rebuild:** idiom/stored-unit detection = configuration-hypothesis idiom-key + a distributional
   local-context compatibility score (Katz & Giesbrecht 2006 distinguishes idiomatic vs literal *token* use by context
   similarity — glass-box, no LLM); extend the integrated `no_glass_box_verb_sense_disambiguation` machinery for the
   physical-vs-nonphysical sense decision rather than duplicating WSD.
7. **Honest caveat to record in your AUDIT UPDATE:** the brain's mechanism is *graded embodied simulation*, not a hard
   gate. Our glass-box gate replicates the *outcome* (no physical-force typing on conventional figurative) via a
   brain-plausible *computational-level* mechanism (sense + selectional competition), but it is an idealization of the
   graded implementation. That is defensible (SEM/constraint-satisfaction level) and should be stated, not hidden.

**Verdict:** mechanism CONFIRMED with one substantive refinement (conventionality/three-way, not literal-vs-figurative
binary) and one structural refinement (single affordance score over both force roles, not a three-way AND). No refutation.

## Sources
- Raposo et al. 2009, "Modulation of motor and premotor cortices by actions, action words and action sentences", Neuropsychologia — https://pmc.ncbi.nlm.nih.gov/articles/PMC4173310/ (idiom review context)
- Desai, "Are Metaphors Embodied? The Neural Evidence" (review) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10171917/
- "How the Context Matters. Literal and Figurative Meaning in the Embodied Language Paradigm" — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4274021/
- Giora, Graded Salience Hypothesis — https://en.wikipedia.org/wiki/Graded_Salience_Hypothesis ; https://www.researchgate.net/publication/248204315
- Bowdle & Gentner 2005, Career of Metaphor — https://www.sciencedirect.com/science/article/abs/pii/S0093934X13001673 (ERP test)
- Cacciari & Tabossi 1988, Configuration Hypothesis / idiom key — https://link.springer.com/article/10.3758/MC.37.4.529
- N400 metaphor / selectional-animacy violation, "Disentangling Metaphor from Context" — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4853386/ ; rational-account ERP — https://arxiv.org/pdf/2409.17525
- Constraint-satisfaction comprehension — https://www.researchgate.net/publication/271138942 ; predictive-coding sentence model — https://www.sciencedirect.com/science/article/pii/S0749596X25000981
- Pustejovsky Generative Lexicon / coercion — https://www.cs.brandeis.edu/~jamesp/classes/LING130/ELS-GL-Entry.pdf ; McElree/Traxler complement coercion cost — https://link.springer.com/chapter/10.1007/978-3-319-45977-6_8
- Resnik selectional preference strength / thematic fit — https://direct.mit.edu/coli/article/39/3/631/1440 ; https://aclanthology.org/D07-1042.pdf
- Wilks-style selectional-violation & concreteness metaphor detection — https://aclanthology.org/2020.figlang-1.30.pdf ; abstractness ERP — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7559308/
- Distributional idiom/token compositionality (Katz & Giesbrecht) — https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00442/108933
- Controlled Semantic Cognition (Lambon Ralph, Jefferies) — https://www.semanticscholar.org/paper/87a3fdc68b1e20fcbe2821be54fed91cb25ce82a ; https://direct.mit.edu/jocn/article/24/1/133/85582
- Wolff force dynamics physical vs social causation — https://philsci-archive.pitt.edu/3126/1/WolffJEPG20072.pdf ; https://www.sciencedirect.com/science/article/abs/pii/S0010028503000367
