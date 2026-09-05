# RESEARCH — brain-foundational basis for the curated-foundation WiC sense-discrimination channel (2026-09-05)

Focused literature confirmation (4 parallel lit-scans) for the mechanism this problem wires: the curated
meaning foundation (taxonomic sense signatures) read against context by biased-competition to discriminate
word sense on gold WiC. **The point of this note is the HONEST PINNED-vs-SPECULATIVE split** — several claims
in the surrounding docstrings do NOT survive a citation check, and I flag them so the mechanism rests only on
what is real.

## PINNED (established; the mechanism can rest on these)

1. **MFS / a context-insensitive model scores CHANCE on WiC.** Pilehvar & Camacho-Collados (2019, NAACL,
   *WiC: the Word-in-Context Dataset*) state verbatim that "a context-insensitive word embedding model would
   perform no better than a random baseline." WiC is balanced 50/50; the most-frequent-sense prior gives BOTH
   sentences the same sense → "always same" = 50.0% (their reported majority/random baseline; human ceiling
   80.0%). **This is the structural reason WiC is a sense-DISCRIMINATION task where the frequency prior — the
   dominant floor on all-words WSD (MFS F1 ≈ 0.65, Raganato et al. 2017) — is USELESS.** So the meaning line's
   recurring "MFS swamps the channel" wall cannot occur on WiC; the channel is measured cleanly.

2. **Diagnosticity weighting = Nosofsky's GCM attention weight (a FORMAL equation, not hand-waving).**
   Nosofsky (1986, *JEP:General*) Generalized Context Model: similarity s(i,j)=exp(−c·d), d with per-dimension
   attention weights w_m (Σ=1) that STRETCH the dimensions best discriminating the categories *currently being
   classified*. That is exactly "up-weight the context features that separate the candidate senses" — our
   `diagnosticity` term. Neural substrate: LIFG scales with the number of competing alternatives, not
   association strength (Thompson-Schill et al. 1997, PNAS). Implementation: attention = optimizing expected
   PRECISION (synaptic gain on prediction-error units), high-precision/diagnostic channels amplified
   (Feldman & Friston 2010). **Each component is pinned; the specific "amplify the dims separating two
   candidate WiC senses" framing is a novel synthesis of GCM (mechanism) + Thompson-Schill (substrate) +
   Feldman-Friston (implementation).**

3. **ATL amodal hub computes taxonomic/feature similarity; a DOUBLE DISSOCIATION separates it from the
   thematic/associative system.** Patterson, Nestor & Rogers (2007, *Nat Rev Neurosci*); Lambon Ralph et al.
   (2017, *Nat Rev Neurosci*, Controlled Semantic Cognition — control MODULATES the hub, does not compute a
   rival metric). Schwartz et al. (2011, PNAS) VLSM: ATL/temporal-pole lesions → TAXONOMIC naming errors;
   temporoparietal/angular → THEMATIC errors (shared variance regressed out — a real anatomical double
   dissociation). Mirman & Graziano (2012) converge. **The live WiC reader (PPR spreading activation over
   WordNet++; Collins & Loftus 1975 associative-network lineage) is the THEMATIC/associative system; sense
   discrimination is the TAXONOMIC system's job.**

4. **Homonymy (unrelated meanings) vs polysemy (related senses) are processed differently, and this predicts
   WiC item difficulty.** Rodd, Gaskell & Marslen-Wilson (2002, *JML*): many-unrelated-meanings → SLOWER
   (competition), many-related-senses → FASTER (shared core). Klepousniotou (2002, *Brain & Language*);
   Beretta, Fiorentino & Poeppel (2005, *Cognitive Brain Research*, MEG): homonym competition cost (later
   M350). Corroborated on graded data: Trott & Bergen (2021, *RAW-C*) — contextual embeddings OVERESTIMATE
   different-sense homonym similarity and UNDERESTIMATE same-sense polysemy closeness; Haber & Poesio (2021).
   **Prediction: our discrimination is easiest on homonym items (separable senses), hardest on polysemy
   (shared core) — a stratification worth reporting.**

5. **Content-addressable cue-based retrieval + exemplar/clustered-prototype representation.** Lewis & Vasishth
   (2005, *Cognitive Science*): retrieval matches stored traces by cue overlap, activation-weighted
   competition. Erk & Padó (2010, ACL): exemplar (not one-vector-per-word) models of word meaning in context.
   Reconciliation for "MaxSim vs centroid": **SUSTAIN (Love, Medin & Gureckis 2004, *Psych Review*)** — a few
   adaptively-grown cluster-prototypes (recruit on prediction error), exemplar-like when sparse, prototype-like
   when dense. This is the brain-plausible form of the substrate's own measured result (raw exemplars swamped by
   frequency; clustered multi-prototype wins) and the brief's MaxSim usage.

## SPECULATIVE / CORRECTED (do NOT rest the mechanism on these)

- **"Borman & Lupyan" is a FABRICATED citation.** It appears verbatim in
  `experiments/exp_sense_wall_breakthrough_wic_v1.py`'s docstring ("a definition is worth many contexts",
  Borman & Lupyan). No such paper exists. The real, related work is Lupyan et al. (2007, *Psych Science*) /
  Lupyan & Thompson-Schill (2012, *JEP:General*): verbal LABELS sharpen category boundaries by amplifying
  diagnostic features — MOTIVATING for the diagnosticity idea, but it is about labels, not dictionary glosses.
  **AUDIT/CODE FLAG for strategy: the fabricated citation should be corrected in that docstring.**
- **"A definition beats a context for sense-ID" has NO dedicated study, and the one directly comparable
  experiment found the OPPOSITE** (Fischer 1994: context-based learning beat dictionary-only; over-reliance on
  definitions produced usage-unconstrained meaning substitutions). So the mechanism must NOT claim
  definitions > contexts. Our claim is narrower and defensible: RICHER curated sense SIGNATURES (the KEY) make
  the CONTEXT (the query) genuinely discriminate — we are not claiming a definition beats a context.
- **"Sense-identity judgment routes specifically through the ATL taxonomic system" is an EXTRAPOLATION**, not a
  directly tested finding (the homonymy/polysemy imaging is about ACCESSING/SELECTING a meaning, not judging
  same/different sense). Treat "WiC = taxonomic task" as a well-motivated HYPOTHESIS (grounded in the
  taxonomic/thematic dissociation + homonymy/polysemy processing), not a pinned fact.
- Gentner (1983) structure-mapping and Tse et al. (2007) schema consolidation are correctly cited but are
  cross-domain analogies (comparison theory; rat spatial memory), not tests of sense grounding — background,
  not support.

## What this licenses for the build
The mechanism rests on (1) MFS-is-chance-on-WiC [pinned], (2) GCM/Thompson-Schill/Friston diagnosticity
[pinned components], (3) ATL taxonomic vs thematic dissociation [pinned], (4) homonymy/polysemy stratification
[pinned], (5) cue-based retrieval + SUSTAIN clustered prototypes [pinned]. It does NOT rest on
definitions-beat-contexts or a specific ATL-sense-identity routing (flagged speculative). The curated
foundation is the taxonomic-similarity KEY the associative live reader lacks; that is the defensible frame.
