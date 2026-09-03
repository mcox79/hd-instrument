# Research drill: how the brain does copular is-a / attribute binding (2026-09-02)

Four parallel full-text literature scans (typology+cues / neural substrate / situation-model+inheritance /
equative subject-predicate+symmetry). Verdicts are PINNED-by-evidence vs OPEN/THIN. This drives the design of
`exp_copular_is_a_binding_readout_v1.py` and bounds what I may claim as brain-faithful.

## The opening move: which brain structure, and are we replicating or substituting?
The copula BE is a near-empty functional carrier; the meaning is the PREDICATION RELATION between the subject
entity and the complement. Higgins (1979) split copular clauses into predicational / specificational /
identificational / equative. Comprehension binds the complement to the subject's ENTITY NODE, but the TYPE of
binding differs and (by the adjacent evidence) routes to different substrates.

## PINNED (replicate these)
- **The surface CUE INVENTORY for typing is well-established** (Mikkelsen 2011 handbook ch.; Van Praet & Davidse
  2015, corpus N=2926). The cheapest/highest-confidence rule: **CUE 12 -- an ADJECTIVE (AP) complement can ONLY
  be predicational, no ambiguity.** Others: proper-name complement -> identity (soft, CUE 4); indefinite/bare
  common noun -> strong predicational prior (CUE 3); definite/demonstrative subject or reversibility -> identity/
  specificational (CUE 1/5); **possessive "his wife" = a GENUINE AMBIGUITY zone (~0.89%), flag not force (CUE
  10).** Base rates: ~74% predicational (49.9% adjectival + 24.4% nominal), ~11.5% ascriptive-identifying,
  ~11.5% specificational. => an empirically-grounded default: absent contrary cues, predicational.
- **ATL combinatorial property composition** (Bemis & Pylkkanen 2011, LATL ~200-250 ms) -- property attribution
  is a real combinatorial op. Predication also recruits LEFT POSTERIOR temporal cortex for the syntactic frame
  (Flick & Pylkkanen), dissociable from LATL semantics -- so "copular = LATL adjective-noun" is too simple.
- **Category "is-a" is NOT an explicit hypernym hierarchy in the brain.** The ATL hub-and-spoke model (Rogers et
  al. 2004; Patterson et al. 2007) represents category membership as EMERGENT feature-overlap/similarity in a
  distributed hub, not a symbolic taxonomic graph. Semantic dementia spares superordinate ("animal") and loses
  subordinate ("robin") -- a similarity gradient, not hierarchy traversal. **=> a distributional/feature-overlap
  is-a is MORE brain-faithful than a WordNet is-a link.** (Corrects the brief's "taxonomic hierarchy / ATL hub"
  framing: the hub is feature-overlap, not an is-a graph.)
- **Equative IDENTITY is SYMMETRIC at the representational level, and this is hippocampal.** Associative symmetry
  (Asch & Ebenholtz 1962; Kahana 2002; Rizzuto & Kahana 2001: forward/backward cued recall equal AND
  same-pair-retest correlation high -> genuinely holistic symmetric storage). The mechanism is CA3 recurrent
  auto-association (Treves & Rolls 1994). **Causal:** Bunsey & Eichenbaum 1996 (Nature) -- hippocampal lesion in
  rats abolishes BACKWARD associative access while sparing forward. **=> treating equative identity as an
  unordered/symmetric link is brain-faithful** (implemented as the symmetric-identity scoring arm).
- **Coreference reactivates hippocampal concept cells** (Dijksterhuis et al. 2024, Science) -- asserting two
  mentions pick out the same entity is a hippocampal relational operation. => identity copulas belong with the
  coref/relational system, not the property-feature store.
- **Property statement attaches to the entity node via shared-argument overlap** and is immediately usable (van
  Dijk & Kintsch 1983 textbase; Kintsch 1988 CI). Assigning a category to a discourse entity AUTO-ACTIVATES an
  associated (unstated) property ONLINE (Duffy & Keir 2004 role-noun stereotype activation) -- but GRADED/
  probabilistic (Sloman feature-overlap), NOT strict logical entailment; only high-availability entailments
  (doctor->person) inherit automatically (McKoon & Ratcliff 1992 minimalist).

## OPEN / THIN (do NOT overclaim -- flag as extrapolation)
- **The predicational-vs-identity NEURAL/PROCESSING dissociation is UNTESTED.** No ERP/fMRI/lesion study directly
  contrasts "X is a doctor" (property) vs "X is his wife / Cicero is Tully" (identity). The ATL-property vs
  hippocampal-identity split is a WELL-MOTIVATED EXTRAPOLATION from adjacent evidence, not a direct result. My
  typing claim rests on the SURFACE cue inventory (PINNED), not on a claimed neural dissociation.
- **"Comprehension does one-shot hippocampal binding of the is-a fact"** -- CLS predicts it, but no paper stages
  it for sentence-level property ascription. Treat as hypothesis.
- **Strict taxonomic inheritance for arbitrary properties** -- OPEN beyond high-frequency entailments.
- **Direct test of equative comprehension symmetry (Cicero=Tully)** -- OPEN; the memory-symmetry finding is a
  strong extrapolation, not a verified comprehension result.
- **Equative subject/predicate assignment is genuinely contested in syntax** (Mikkelsen inverse-analysis vs
  Heycock & Kroch symmetric-equative; Roy & Murez 2026 "the problem of symmetry" still open). The one CONSENSUS
  cue is discourse TOPICALITY/givenness (the more Discourse-old NP is subject). There is essentially NO online
  processing literature on it -- so the parser's equative attachment wall is a real, expected gap.

## Citation hygiene flagged by the drill
- Eichenbaum/Yonelinas/Ranganath 2007 is "The Medial Temporal Lobe and Recognition Memory" (not "...Declarative
  Memory"). For relational binding cite Cohen & Eichenbaum 1993 / Eichenbaum 2004.

## Net design consequences (what the drill changed)
1. TYPE from the surface cue inventory (AP->predicational hard gate; proper-name/definite->identity; possessive
   = ambiguity zone). Coarse pred/ident classifier is the defensible claim; the neural dissociation is not.
2. DETECT robustly from the closed-class copula + parse tree, not the fragile `cop` label (the fix).
3. Represent equative identity as a SYMMETRIC link (CA3-pinned), distinct from property attribution.
4. Do NOT sell a WordNet is-a hierarchy as the brain's mechanism -- category membership is feature-overlap; the
   distributional/grounded space is the faithful substrate for is-a inheritance (a follow-on, not built here).
