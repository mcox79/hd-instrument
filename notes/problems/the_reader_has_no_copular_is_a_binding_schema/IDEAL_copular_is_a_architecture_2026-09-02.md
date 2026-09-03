# The IDEAL brain-faithful copular is-a binding system -- full architecture, status, and research gaps

Synthesized from the 4-lane drill (`research_copular_is_a_binding_2026-09-02.md`) + the measured process map.
This is the ideal END-STATE; each stage marks brain structure, PINNED/OPEN, what we BUILT, and the GAP. It is the
plan the submission's NEXT STEPS point at, and it is where "research where there are gaps" lives.

## The 6-stage pipeline (text -> answerable, inheritable "what/who is X")

### Stage 1 -- DETECT the predication  [BUILT]
- **Brain (PINNED):** the copula BE is a closed-class FUNCTIONAL CARRIER; predication is detected transparently,
  keyed on the predicate not the copula (copula omission is grammatically selective -- Matchin & Hickok; agrammatism
  double-dissociation). So detection must NOT depend on a fragile label.
- **Built:** `robust_cop` fires on the closed-class copula + parse tree (not the `cop` label). +0.146 read-back CI-sep.
- **Gap:** 13/73 identity clauses (hardest equatives/clefts/specificational-inversions) still undetected. A parser-
  fidelity residual, not a mechanism gap.

### Stage 2 -- TYPE the clause (Higgins)  [BUILT, partial cue set]
- **Brain (PINNED):** the referential status of the complement NP sets predicate <e,t> vs referent <e> (Mikkelsen
  2005; Partee). Cue inventory PINNED: AP->predicational (CUE 12, hard gate); proper-name/demonstrative->identity
  (4/5); indefinite->predicational (3); reversibility->specificational/identity (1); possessive = AMBIGUITY zone
  (10, ~0.89%); pronominalization it/that vs he/she (2); information structure given/new (7).
- **Built:** glass-box classifier, 0.969 coarse (pred vs ident) using AP/proper-name/definiteness cues.
- **Gap (the IDEAL upgrade, buildable now):** implement the FULL cue inventory and **DEFER on the possessive
  ambiguity zone** (flag, don't force -- the brain doesn't force it either). CUE 5 (demonstrative subject), CUE 2
  (tag-question pronoun), CUE 1 (reversibility test). Prototyped as the enhanced classifier below.

### Stage 3 -- BIND the typed complement to the entity node  [BUILT for 3a; 3b/3c partial]
- **3a predicational ADJECTIVAL -> scalar PROPERTY** (Maienborn Kimian state; Bemis & Pylkkanen LATL property
  composition). **Built:** routes to `hdlab.state_register` (persistence + cancellation). PINNED.
- **3b predicational NOMINAL -> is-a CATEGORY membership.** Binding BUILT; the is-a LINK into semantic memory is
  Stage 4. PINNED that the complement attributes a category to the entity node.
- **3c identificational -> SYMMETRIC IDENTITY link (X == Y).** **Brain (PINNED):** hippocampal CA3 recurrent
  auto-association stores the link SYMMETRICALLY (Rizzuto & Kahana 2001; Bunsey & Eichenbaum 1996 lesion abolishes
  BACKWARD access); coref reactivates hippocampal concept cells (Dijksterhuis 2024). **Built:** typed + symmetric
  SCORING (recovers reversals). **Gap:** the identity link is not yet MERGED into the coreference system (Stage 5).

### Stage 4 -- INHERIT (the is-a payoff)  [NOT built -- prototyped + gap surfaced below]
- **Brain (PINNED):** assigning a category to a discourse entity AUTO-ACTIVATES an associated property ONLINE
  (Duffy & Keir 2004 role-noun stereotype activation), GRADED by feature-overlap (Sloman 1993), only for
  high-availability entailments (McKoon & Ratcliff 1992 minimalist: "doctor->person" yes, rare properties no). The
  ATL hub represents category membership as EMERGENT FEATURE-OVERLAP, **NOT a symbolic hypernym hierarchy** (Rogers
  2004; Patterson 2007; SD spares superordinate, loses subordinate = a similarity gradient).
- **THE RESEARCH GAP (surfaced by this work):** symmetric distributional cosine gives RELATEDNESS (doctor~nurse~
  hospital), NOT is-a DIRECTIONALITY (doctor IS-A person, not person IS-A doctor). The brain's is-a directionality
  comes from FEATURE GENERALITY -- a superordinate has a broader/more-shared feature (context) distribution than its
  hyponyms (the distributional-inclusion / generality hypothesis; Geffet & Dagan 2005; Weeds & Weir; Santus
  entropy-based generality). So the IDEAL inheritance = a DIRECTIONAL generality measure over the feature-overlap
  space, not symmetric cosine. **Prototyped** in `prototype_isa_inheritance_feature_overlap.py`. RESULT (freq-matched
  2AFC, chance 0.5, n=12855): symmetric cosine 0.666 (weak); the proper feature-inclusion measure WeedsPrec 0.685,
  CI-separated ABOVE symmetric -- DIRECTIONALITY is the confirmed brain-faithful lever, but the gain is modest and
  glass-box feature-overlap under-delivers on is-a. **LOCATED GAP:** inheritance needs directional feature-inclusion
  (WeedsPrec/balAPinc) AND likely a hybrid with the symbolic grounded semantic graph (WordNet is-a as a static
  foundation asset). Entropy-generality gating rode the frequency confound (washes out on the matched test).

### Stage 5 -- RESOLVE the holder to a canonical ENTITY (coref)  [NOT composed end-to-end]
- **Brain (PINNED):** "what is X" queries a canonical entity across the discourse; coref reactivates hippocampal
  concept cells to bind the mention to the entity (Dijksterhuis 2024; Kurczek/Duff amnesia referential deficits).
- **Gap:** the coreference organ exists; the binding read-back is measured WITHIN-CLAUSE (holder = nsubj token). The
  full canonical-entity read-back (binding o coref, through the live `read()`) is a plumbing composition, not measured.

### Stage 6 -- PERSIST / UPDATE (state dynamics)  [BUILT]
- **Brain (PINNED):** states default-persist (Dowty temporal inertia), close on an explicit cancellation; the perfect
  is a cancellable prior (Iatridou). **Built:** `hdlab.state_register` (persistence + antonym cancellation + the
  telic two-field split). PINNED.

## The genuinely OPEN research questions (where the literature itself is thin -- do NOT overclaim)
1. **The predicational-vs-identity NEURAL dissociation is UNTESTED** -- no ERP/fMRI/lesion study contrasts "X is a
   doctor" vs "X is his wife". The ATL-property vs hippocampal-identity split is a well-motivated EXTRAPOLATION.
2. **is-a DIRECTIONALITY in the ATL hub** -- how feature-overlap encodes direction is not settled; feature-generality/
   inclusion is the leading computational proposal, tested here as the prototype. OPEN in neuroscience.
3. **One-shot (hippocampal) vs slow (cortical) binding of the is-a fact** -- CLS predicts fast availability but has
   not been staged for comprehension-time property ascription (my hypothesis, not a cited result).
4. **Equative subject/predicate assignment online** -- essentially NO processing literature; topicality/givenness is
   the syntax field's one consensus cue (Mikkelsen; Birner). This is why the equative holder residual is a follow-on.
5. **Which entailments auto-inherit** -- high-availability (doctor->person) yes; typical/rare properties are OPEN
   (minimalist boundary). The inheritance prototype tests the strong (superordinate) case only.

## What this means for optimization
- **The CORE (Stages 1-3a, 6) is built and the bar is met.** The optimization headroom is: (Stage 2) the full-cue
  typing + deferral [buildable now, prototyped]; (Stage 4) is-a inheritance via directional generality [prototyped,
  the deep lever + the real research gap]; (Stage 3c/5) identity->coref merge + canonical-entity read-back [plumbing].
- **Ranked next problems:** (1) is-a inheritance via feature-overlap generality (deepest, a new capability); (2)
  identity->coref merge (the faithful home for the identity type); (3) equative subject choice via topicality (needs
  a document corpus); (4) end-to-end through `read()` with coref-resolved entity read-back.
