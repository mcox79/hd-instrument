# FINER drill: the COMBINATION RULE, the PATH/PARTICLE slot (antonym problem), and GENERALIZATION

Research drill for `the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner`.
Date 2026-09-01. Author: hdi_research (finer brain-fidelity drill on the kernel design, one layer below the
pinned DG/CA3-pattern-separation-by-meaning verdict).
ONLINE-literature synthesis. **Lit-scan calibration penalty applied throughout** — every "should" is a
DESIGN HYPOTHESIS pending the solver's own measurement, not an inherited number; novel-synthesis confidence
capped. Glass-box / **no external LLM at inference** framing (the per-slot similarity must be the substrate's
own grounded/distributional code; nothing here calls an LLM).

**Inherited, NOT re-derived (read first):**
`.../the_reader_cannot_reason_over_its_own_situation_model_on_real_inference/research_precise_event_alignment_mechanism_2026-09-01.md`
— PINNED: event identity = a role-filler CONJUNCTION, pattern-SEPARATED by MEANING (DG→CA3; PNAS 2026
10.1073/pnas.2603114123; Carlson 1998; Zwaan event-indexing; SEM/Franklin 2020). This drill does NOT
re-open that. It goes finer on the three uncertainties that fix the actual kernel math.

**Prior-arc overlap on THIS finer question:** the sibling drill established the *what* (conjunctive-by-meaning).
No prior arc work pins the *combination-rule math* (product vs expansion), the *path-slot kernel* (discrete vs
graded/opponent), or the *cross-domain reuse* verdict. This drill is the first pass on those three.

---

## Q1 — THE COMBINATION RULE: multiplicative soft-AND (product / geometric mean) vs the literal DG sparse expansion

### The finding, in one line
**They are the SAME operation described at DIFFERENT of Marr's levels — a product/geometric-mean kernel is the
COMPUTATIONAL-level model of a conjunctive cell; a DG sparse-expansion + k-WTA is one IMPLEMENTATIONAL realization
of that same kernel — BUT they make DIFFERENT quantitative predictions, and the difference is exactly the trap
this problem keeps falling into.** So: adopt the PRODUCT first (it is the transparent, glass-box conjunctive
kernel), and treat the expansion as an optional realization to reach for only if the product under-separates —
with a hard caveat below about what the expansion must consume.

### (i) Is a product / geometric-mean a legitimate computational-level model of a hippocampal conjunctive cell? YES — four converging lines.

1. **Nonlinear mixed selectivity IS, by definition, a non-additive (interaction / product-like) combination.**
   NMS neurons respond to a combination of variables in a way that "cannot be predicted by the linear summation
   of their responses to single variables" — the defining signature is an *interaction* term, i.e. the response
   to (A∧B) is not f(A)+f(B). This is the single-neuron correlate of a conjunction, and it is precisely NOT a sum.
   NMS produces high-dimensional codes that "support a wider array of readout functions … at the expense of
   generalization" (Rigotti, Barak, Warden, Wang, Daw, Miller, Fusi 2013 *Nature* 497:585; eNeuro 2022
   dlPFC>PPC). The additive alternative is the low-dimensional code that CANNOT separate conjunctions — which is
   our incumbent's failure mode.

2. **The canonical cognitive model of GRADED conjunctive similarity — the Generalized Context Model — already
   combines per-dimension similarities MULTIPLICATIVELY (a product), not additively.** In Nosofsky's GCM (1986),
   the similarity of a probe to a stored exemplar is a **product across dimensions** of attention-weighted
   per-dimension similarities (each an exponential-decay function of distance); category strength is then a SUM
   *across exemplars* of that within-exemplar product. This is exactly our target structure: **PRODUCT WITHIN an
   event (across its roles), argmax/sum ACROSS candidate events.** GCM is the pinned, decades-validated
   computational statement that graded conjunctive matching is multiplicative-within-item. It also already
   contains the per-slot attention weights `w_r` we want to sweep.

3. **Memory-retrieval cue combination is empirically MULTIPLICATIVE, and the additive alternative is the fan
   effect.** Parker (2019, *Cognitive Science* 43:e12715, "Cue Combinatorics in Memory Retrieval for Anaphora")
   found retrieval data "consistent with nonlinear (multiplicative) cue combination and provided evidence
   against models in which all cues combine in a linear fashion" — the contribution of each cue *depends on* the
   match of the others (a conjunction), not an independent addition. This is the direct memory-systems warrant:
   the fan effect our `content_addressable_retrieval` exhibits IS the additive-combination signature; a
   multiplicative rule is what escapes it.

4. **The implementational primitive exists: dendritic AND-gates / supralinear NMDA conjunction.** Single neurons
   physically compute AND-like, supralinear (multiplicative) conjunctions in dendrites: NMDAR-dependent
   supralinear integration and coincidence detection give "signal amplification, coincidence detection, XOR
   gating" (eLife 2024 100268; Purkinje coincidence detection PMC7771959). So "multiply the evidence for two
   features" is not an abstraction the brain lacks — it is a basic dendritic operation.

### (ii) How the product and the DG-expansion relate — and where they DIFFER (this is the load-bearing part)

- **Expansion recoding provably IMPLEMENTS a similarity kernel.** The cerebellar granule layer / DG expansion +
  threshold is formally "a kernel machine": random expansion into a higher-dimensional sparse code, followed by a
  threshold, computes an inner-product (kernel) in the expanded space that the readout reads linearly
  (Frontiers Comput. Neurosci. 2022 "Cerebellum as a kernel machine"; Babadi & Sompolinsky 2014 *Neuron*
  "Sparseness and Expansion in Sensory Representations"; Litwin-Kumar et al.). A product/soft-AND is one such
  kernel. **So the product kernel and the DG expansion are two levels of description of the SAME conjunctive
  operation** — this reconciles the sibling drill's "they are the same operation" with the implementational
  literature.

- **But they are NOT interchangeable, and predict different behaviour on the two things we care about:**

  | | multiplicative product over GRADED per-role sims (computational) | naive random expansion + k-WTA over a HOLISTIC code (implementational, done wrong) |
  |---|---|---|
  | Separation of similar events | strong (a mismatch on any role → factor → 0) | strong (that's what DG does) |
  | Paraphrase generalization WITHIN a role | **preserved by construction** (the graded per-slot `sim` keeps "exit"≈"get out") | **DESTROYED** — random projection decorrelates *everything*, including paraphrases, unless the input is already graded+structured |
  | Noise / capacity | none added | expansion *amplifies* input variability, worse with sparsity (Babadi–Sompolinsky) |
  | Glass-box | fully transparent (you can read each factor) | opaque (which projection fired?) |

- **The concrete trap (why this matters for the build):** a DG-style sparse expansion applied to the incumbent's
  12-d HOLISTIC cosine vector — or to exact-hash symbols — would reproduce EXACTLY the
  `bound_event_backbone` over-separation failure (kills paraphrase, the 0.48 symbol-tie). Random expansion is
  **structure-blind**: it separates paraphrases as eagerly as it separates true opposites. Babadi–Sompolinsky
  are explicit that a *useful* expanded sparse code "requires a nonlinear computation that incorporates
  information about the hidden structure of the compressed signals" — i.e. the expansion is only as good as the
  STRUCTURED, GRADED per-role input you feed it. **The DG stage does not substitute for the graded per-role
  code; it can only sit on top of it.**

- **The tuning knob is the SAME for both, and it is a PINNED real quantity.** "The Sparseness of Mixed
  Selectivity Neurons Controls the Generalization–Discrimination Trade-Off" (Barak, Rigotti, Fusi 2013
  *J. Neurosci.* 33:3844) — the sparseness/coding-level of the conjunctive code is a single monotone knob trading
  discrimination against generalization, with a task-dependent optimum. The 2024 *Nat. Neurosci.*
  "Semi-orthogonal subspaces … binding and generalization trade-off" (s41593-024-01758-5) confirms the same axis
  at the geometry level. **This is our soft-AND temperature / k-WTA sparsity — one and the same knob. There is a
  real optimum and it must be SWEPT, not adopted** (the biological 0.2%-ish DG sparsity is a constraint we do not
  share).

### Q1 VERDICT (PINNED vs OUR-INVENTION + implication for the kernel)
- **PINNED:** conjunctive selectivity is non-additive; the computational form is a PRODUCT/geometric-mean of
  per-feature graded similarities (GCM; NMS; multiplicative cue combination; dendritic AND). Expansion recoding
  implements a conjunctive kernel but is structure-blind and only as good as its graded input. Sparseness/sharpness
  is a single generalization↔discrimination knob with a task-dependent optimum.
- **OUR-INVENTION-UNDER-TEST (sweep):** the exact functional form (product vs geometric-mean vs
  softmin/log-sum with a temperature `β`); the per-role weights `w_r`; whether a DG expansion is needed AT ALL.
- **IMPLICATION — adopt the PRODUCT, do NOT lead with the expansion.** Kernel:
  `score(cue, ev) = Π_{r ∈ shared roles} sim(cue_r, ev_r) ** w_r` — a geometric mean / weighted product over
  roles PRESENT on both sides (drop a missing role so it stays partial-cue robust). The product IS the
  computational-level conjunctive cell and it is fully glass-box (you can read the per-role factor that killed a
  candidate). **The DG sparse expansion is a fallback realization to try ONLY if the product under-separates at
  the best achievable per-slot resolution — and if you build it, it MUST consume the structured graded per-role
  code, never the holistic 12-d vector (else it reproduces the exact-hash over-separation failure).** One knob
  (`β` / sparsity), swept on the generalization↔discrimination frontier — do not run two.

---

## Q2 — THE PATH/PARTICLE SLOT and THE ANTONYM PROBLEM

### The finding, in one line
**The antonym problem is REAL and well-documented: a plain grounded/distributional COSINE on the particle slot
will FAIL to separate in↔out (they share syntactic frames → near-identical distributional vectors). The
brain-faithful treatment of the particle is NOT a graded content-cosine — it is either a DISCRETE CATEGORICAL
match or an OPPONENT-CODED bipolar axis. The per-slot kernel must be HETEROGENEOUS: closed-class path/particle
gets a discrete/opponent kernel; open-class content roles (verb/patient) keep the graded cosine.**

### (i) The antonym problem is genuine, not a worry
Distributional semantics has a named, chronic failure here: "antonyms (hot vs. cold) … can appear as similar as
genuine synonyms under cosine similarity" because opposites "appear in nearly identical linguistic contexts,
merely differing in implicit negation" ("the water is hot" / "the water is cold" share the frame). Documented
fixes all involve *changing the geometry* — counter-fitting (push antonym pairs apart, pull synonyms together;
Mrkšić et al.), Polarity-Inducing LSA, and "a vector space where antonyms lie on opposite sides of a sphere:
synonyms ≈ +1, antonyms ≈ −1." **PINNED for our build: a raw grounded/distributional cosine on "in" vs "out"
will NOT deliver the criterial separation this whole problem needs — the very failure the incumbent exhibits.
The separation must be BUILT into the particle kernel; it cannot be assumed from the distributional space.**

### (ii) How the brain represents spatial opposites — two brain-faithful options, both non-cosine
1. **CATEGORICAL (Kosslyn) spatial relations — DISCRETE, prepositionally lexicalized.** The brain distinguishes
   *categorical* spatial relations ("discrete spatial relations frequently lexicalized by locative prepositions"
   — in/out/on/off/above/below; left-hemisphere-biased) from *coordinate* relations (fine metric distance;
   right-hemisphere-biased) (Kosslyn; Jager & Postma; PMC2933471; ScienceDirect S1053811912001061). Categorical
   spatial relations are ABSTRACT equivalence classes — exactly a discrete criterial feature. This directly
   licenses treating the particle as a **discrete category**, not a point in a metric space.
2. **OPPONENT coding — opposite poles / reciprocal populations.** Spatial opposites are coded by opponent
   populations across the brain: auditory azimuth (PLOS Biol 2005; Cereb. Cortex 2016 planum temporale),
   visuospatial recall/perception in medial parietal cortex ("opponent visuospatial coding," PMC12319830), and
   direction in motor cortex (Georgopoulos population vector). This is the graded generalization of option 1: an
   axis where in↔out sit at OPPOSITE poles (cos ≈ −1, per the "opposite sides of a sphere" fix), so a
   wrong-particle factor is strongly suppressive while allowing "up"≈"over" partial similarity.

3. **The particle is CLOSED-CLASS and functionally distinct from content.** Closed-class function words
   (prepositions, particles) are processed by partly dissociable neural systems from open-class content words,
   and can be selectively disrupted by brain injury while content is spared (PubMed 11115658; Neurobiology of
   Language Comprehension). Landau & Jackendoff's "what/where" division: spatial prepositions encode COARSE,
   NONMETRIC, FUNCTIONAL relations — "containment," "support/contact," "relative direction" — a "where" system
   separate from the fine-geometry "what" system (Landau & Jackendoff 1993 *BBS*; Landau 2017 *Cog Sci*
   containment/support; functional-geometric framework, Coventry). So "in"/"on" are functional-geometric
   categories (containment/support), NOT Euclidean points — a distributional cosine captures neither the
   functional geometry NOR the opposition. **Two reasons the particle slot must be handled differently from the
   content slots.**

4. **Zwaan event-indexing (inherited, reinforced):** a change in the SPATIAL dimension is itself an event
   boundary trigger — "get IN" and "get OUT" are DIFFERENT events because the spatial relation flipped. Treating
   the particle as a **discrete criterial boundary feature** is the direct implementation of that pinned model.

### Q2 VERDICT (PINNED vs OUR-INVENTION + implication for the kernel)
- **PINNED:** opposites are distributionally near — a cosine fails on them (documented). The brain codes spatial
  relations *categorically* (discrete, prepositional; Kosslyn) and/or via *opponent* populations (opposite
  poles). Prepositions/particles are closed-class, functional, coarse, dissociable from content (Landau &
  Jackendoff; closed-vs-open-class). A spatial-relation change is an event boundary (Zwaan).
- **OUR-INVENTION-UNDER-TEST (sweep/choose + MEASURE):** discrete-categorical match vs opponent-graded axis for
  the particle; the closed particle inventory (in/out/up/down/on/off/back/through/away…); whether a wrong-opposite
  contributes 0 (drop-to-zero product factor) or a negative/penalized term; how the opponent axis is built (a
  counter-fitting-style contrast projection over the grounded codes, glass-box — NOT an LLM).
- **IMPLICATION — HETEROGENEOUS per-slot kernels.** The **PATH/PARTICLE slot is a DISCRETE CATEGORICAL match**
  (same particle-category → 1; different, esp. opposite → ~0), the glass-box first cut that directly implements
  categorical spatial relations + closed-class discreteness + the Zwaan spatial-boundary rule. If you need graded
  particle similarity ("up"≈"over") while keeping in↔out maximally far, upgrade that ONE slot to an
  **opponent-coded bipolar axis** (built by contrast/counter-fitting over the grounded codes), NOT a raw cosine.
  **Content roles (verb, agent, patient) stay graded grounded cosine.** The heterogeneity itself is
  brain-faithful (closed- vs open-class dissociation) — do not force one kernel across all slots. Because the
  particle is criterial, its factor in the product must be able to drive the joint score toward zero (a discrete
  0, or an opponent term near −1) — that is the mechanism that separates "get OUT" from "get IN."

---

## Q3 — GENERALIZATION: one reusable conjunctive-alignment organ, or event-specific?

### The finding, in one line
**PINNED: the hippocampal pattern-separation-then-completion + relational-binding machinery is DOMAIN-GENERAL —
it is the SAME operation the brain reuses for social/abstract relational inference, transitive ordering, cued
recall, and schema generalization. Build the aligner as ONE reusable organ (parameterized by role-schema),
parallel to the transitive-ordering/cognitive-map reuse verdict — with the calibration caveat that the OPERATION
generalizes but each domain's ROLE SCHEMA and per-slot kernels must be re-fit and re-measured.**

### Evidence
- **Domain-general cognitive map / relational system.** The hippocampal–entorhinal system codes relations across
  arbitrary, non-spatial dimensions — social rank, abstract relational knowledge, reward generalization,
  transitive inference — with the SAME place/grid-like machinery (Behrens et al. 2018; eLife 2016 "map of
  abstract relational knowledge" 17086; Tolman–Eichenbaum Machine, Whittington et al. 2020; "Transforming social
  perspectives with cognitive maps," Park et al. 2022 *SCAN* 17:939; PNAS 2024 mathematical theory of relational
  generalization in transitive inference 2314511121). This is the exact precedent for our reuse: the read-out
  organ (`transitive_ordering`) is already the brain's single general relational-integration organ; the ALIGNER
  that feeds it should share that generality.
- **Relational binding is cross-domain by construction.** Konkel & Cohen: the hippocampus creates flexible
  relational representations "that can be flexibly expressed and recombined for various cognitive demands"
  ("Relating Hippocampus to Relational Memory Processing across Domains and Delays," PMC4336790). Binding a set
  of role-fillers and separating it from similar competitors is not an event-only trick.
- **Pattern separation / completion is a GENERAL mnemonic-discrimination + retrieval operation.** DG separates
  similar inputs; CA3 completes the full pattern from a partial/degraded cue via attractor dynamics (Neunuebel &
  Knierim 2014 *Neuron* "CA3 retrieves coherent representations from degraded input"; JNeurosci 2019 holistic
  recollection via CA3 pattern completion). **"Match a paraphrased / partial cue to the right stored item, kept
  distinct from similar competitors" is the generic description of cued recall itself** — episodic event recall,
  belief/ToM item tracking, and the learner's cross-exposure schema consolidation are all instances of it. The
  hippocampus is *favored precisely when inputs are similar* (inherited PNAS-2026-by-meaning) — a property any of
  these domains needs.

### Q3 VERDICT (PINNED vs OUR-INVENTION + implication)
- **PINNED:** the separate-then-complete + relational-bind operation is domain-general; the brain reuses ONE
  relational/mnemonic system across spatial, social, transitive, and cued-recall tasks.
- **OUR-INVENTION-UNDER-TEST:** that a SINGLE glass-box implementation, re-parameterized by role-schema,
  transfers across our domains without per-domain surgery. The operation generalizing (PINNED) does NOT prove one
  frozen instance transfers — the role set, per-slot kernels, and weights are domain-specific and must be re-fit
  and re-measured. (Calibration: treat "one organ" as a design bet on the ARCHITECTURE, not a claim that a
  single tuned instance is universal.)
- **IMPLICATION — build ONE reusable organ** — a grounded conjunctive pattern-separating matcher taking a
  {role → (kernel-type, filler)} schema, reusable for episodic event recall, belief/ToM tracking, cued recall,
  and cross-exposure consolidation — exactly as `transitive_ordering` is reused as the read-out. Ship it as the
  event-alignment schema first (prove it here), expose the role-schema + per-slot-kernel choice as the
  configuration surface, and only CLAIM cross-domain reuse per domain you actually measure.

---

## Net implications for the kernel (the three decisions this drill was asked to make)

1. **PRODUCT, not expansion (Q1).** Adopt the weighted geometric-mean / soft-AND product over per-role graded
   similarities as the kernel — it is the computational-level conjunctive cell (GCM / NMS / multiplicative cue
   combination / dendritic AND) and is fully glass-box. Hold the DG sparse-expansion in reserve as a fallback
   realization *only* if the product under-separates at best per-slot resolution, and *only* fed the structured
   graded per-role code (never the holistic vector — that trap reproduces the exact-hash over-separation). One
   swept knob (temperature/sparsity) on the pinned generalization↔discrimination frontier.
2. **DISCRETE (or opponent) particle, GRADED content (Q2).** Per-slot kernels are heterogeneous. Path/particle =
   discrete categorical match (upgradeable to an opponent bipolar axis if graded particle similarity is needed),
   because a raw cosine provably cannot separate the criterial opposite in↔out. Content roles stay graded
   grounded cosine. The particle factor must be able to send the product toward zero.
3. **ONE reusable organ, schema-parameterized (Q3).** Build the aligner as a general grounded conjunctive
   pattern-separating matcher (role-schema as config), reusable across event recall / belief / cued recall /
   consolidation — but claim transfer only per measured domain.

---

## Key citations (new to this finer drill)
- Rigotti M., Barak O., Warden M.R., Wang X-J., Daw N.D., Miller E.K. & Fusi S. (2013). The importance of mixed selectivity in complex cognitive tasks. *Nature* 497:585–590.
- Barak O., Rigotti M. & Fusi S. (2013). The sparseness of mixed selectivity neurons controls the generalization–discrimination trade-off. *J. Neurosci.* 33:3844–3856. **(= our soft-AND temperature / k-WTA sparsity knob; task-dependent optimum → sweep.)**
- Fusi S., Miller E.K. & Rigotti M. (2016). Why neurons mix: high dimensionality for higher cognition. *Curr. Opin. Neurobiol.* 37:66–74.
- (2024). Semi-orthogonal subspaces for value mediate a binding and generalization trade-off. *Nat. Neurosci.* s41593-024-01758-5.
- Nosofsky R.M. (1986). Attention, similarity, and the identification–categorization relationship. *JEP:General* 115:39–57. **(GCM: similarity = MULTIPLICATIVE product across attention-weighted per-dimension similarities; category strength = sum across exemplars → product-within, sum-across, our exact structure.)**
- Parker D. (2019). Cue combinatorics in memory retrieval for anaphora. *Cognitive Science* 43:e12715. **(evidence FOR multiplicative, AGAINST additive cue combination; additive = the fan effect.)**
- Babadi B. & Sompolinsky H. (2014). Sparseness and expansion in sensory representations. *Neuron* 83:1213–1226. **(expansion + threshold implements a kernel; needs STRUCTURED input; expansion amplifies noise → the caveat on feeding DG a graded, not holistic, code.)**
- (2022). Cerebellum as a kernel machine: expansion recoding in the granule cell layer. *Front. Comput. Neurosci.* 16:1062392. **(expansion recoding = computing a similarity kernel; bridges product ↔ DG-expansion as Marr levels.)**
- Kosslyn S.M. et al.; Jager & Postma (2003); Baumann/… — categorical vs coordinate spatial relations (PMC2933471; ScienceDirect S1053811912001061). **(categorical = discrete, prepositional, left-hemisphere → discrete particle kernel.)**
- Landau B. & Jackendoff R. (1993). "What" and "where" in spatial language and spatial cognition. *BBS* 16:217–265; Landau B. (2017) Containment and support. *Cognitive Science* 41. **(prepositions = coarse, nonmetric, functional relations; closed-class "where" system.)**
- Distributional antonym problem + fixes: Mrkšić et al. counter-fitting; Yih et al. Polarity-Inducing LSA; Nguyen et al. (2016) distributional lexical contrast (arXiv 1605.07766). **(cosine cannot separate opposites; separation must be BUILT into the geometry.)**
- Opponent spatial coding: Stecker/Middlebrooks (PLOS Biol 2005); medial parietal opponent visuospatial coding (PMC12319830); Georgopoulos population vector. **(opposites at opposite poles / reciprocal populations → opponent particle axis.)**
- Open- vs closed-class dissociation: Münte et al. (PubMed 11115658); Neurobiology of Language Comprehension (Springer). **(particle = closed-class, dissociable → treat differently from content.)**
- Neunuebel J.P. & Knierim J.J. (2014). CA3 retrieves coherent representations from degraded input. *Neuron* 81:416–427; holistic recollection via CA3 (JNeurosci 2019 39:8100). **(pattern completion from partial cue = cued recall = the general operation.)**
- Domain-general relational map: Behrens et al. (2018) *Neuron* "What is a cognitive map?"; Whittington et al. (2020) TEM *Cell*; Park S.A. et al. (2022) *SCAN* 17:939 social perspectives; Constantinescu/eLife 2016 (17086); PNAS 2024 (2314511121); Konkel & Cohen relational memory across domains (PMC4336790). **(one reusable relational organ across domains.)**

---

## TLDR (plain English)
We are building the part of the reader that decides which stored moment a question is talking about — the piece
that has been grabbing the wrong one (mixing up "getting IN the shower" with "getting OUT"). This drill answered
three design questions by going to the neuroscience and the memory-science literature.

First: how should it combine the pieces of a moment (who, did-what, in-which-direction)? The answer is **multiply
them, don't add them** — require ALL the pieces to agree, so one wrong direction-word drags the whole match down.
This "multiply the evidence" rule is exactly how the brain's memory cells combine features, how the standard
model of human categorization computes similarity, and how memory actually combines retrieval cues; the "add
them up" alternative is the known blur that fools it. There is also a more literal brain trick (spreading the
code out into a huge sparse pattern) — it is the same idea at a lower level, but it is a trap here unless fed the
right ingredients, so we lead with the simple multiply rule and keep the sparse trick in reserve.

Second: the little direction words ("in" vs "out") are the hardest part, because opposites look almost identical
to a plain meaning-similarity score — a famous problem. The brain does NOT treat them as points on a smooth
meaning scale; it treats them as **discrete categories** (or as two ends of an opposites axis), and it handles
these little grammar-words with a partly different system than content words. So our matcher should treat the
direction word as a discrete on/off criterial feature, not a fuzzy similarity — while keeping fuzzy similarity
for the content words.

Third: is this matcher a one-off for events, or reusable? The brain reuses the same "keep similar memories
apart, then fill in from a hint" machinery for social reasoning, ranking, and ordinary remembering — so we
should build **one reusable part**, just like we already reuse one part for ordering — while only *claiming* it
works in a new area once we have actually measured it there.

## QUESTIONS
None for the owner. Every "should" above is flagged as a design hypothesis for the solver to measure; no decision
here requires an owner call.

## NEXT STEPS (for the solver — design hypotheses to MEASURE, not adopt)
1. Kernel = **weighted geometric-mean product** over graded per-role similarities; do NOT lead with a DG sparse
   expansion. If you later add the expansion, feed it the STRUCTURED graded per-role code, never the holistic
   vector, and use the single sparsity/temperature knob (do not run two).
2. Make the per-slot kernels **heterogeneous**: PATH/PARTICLE = discrete categorical match (or an opponent
   bipolar axis if you need graded particle similarity), content roles = graded grounded cosine. Verify directly
   that a raw cosine on the particle slot FAILS to separate in↔out on your items (the motivating control), and
   that the discrete/opponent kernel fixes it.
3. Build the aligner as **one schema-parameterized organ** (role-schema + per-slot-kernel-type as config); prove
   the event schema here; expose the config surface; claim cross-domain reuse only per measured domain.
4. Sweep the ONE knob (product temperature / sparsity) on the generalization↔discrimination frontier (Barak/
   Rigotti/Fusi) — report the frontier, do not adopt a biological constant. The particle/2nd-arg ablation
   (already in the PROBLEM bar) is the positive control that the CONJUNCTION over the criterial slot does the work.
