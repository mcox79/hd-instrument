# Brain fidelity, the ideal system, and an end-to-end signal-loss ledger

Solver drill for `the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning`.
Consolidates five literature sub-scans (head-finding, eADM case, verb-subcategorization x3) + the measured
signal-loss audit. PINNED-BY-EVIDENCE vs OUR-INVENTION tagged throughout.

---

## 1. How the brain does who-did-what, stage by stage (the mechanism we are copying)

The brain does role assignment by **incremental, graded, parallel CUE INTEGRATION** (MacWhinney & Bates
Competition Model; Bornkessel-Schlesewsky & Schlesewsky eADM 2006, *Psych Review* 113(4)). English weights **word
order** highest; morphology/case override order only on marked constructions. Two operations precede/accompany it:

- **STAGE A -- constituent structure + HEAD identification (PINNED).** Comprehension brackets the input into phrases
  and identifies each phrase's head. English compound head = rightmost noun (**Right-hand Head Rule**, Williams
  1981 *LI* 12(2)); genitive/DP head = the possessed noun, not the possessor (Abney 1987 DP hypothesis; Chomsky
  1970; Jackendoff 1977). Neurally real and localized: high-gamma **bracket-closure** events at phrase boundaries
  (Nelson et al. 2017 *PNAS* E3669, IFG pars triangularis/orbitalis + STS), MEG phrase-level cortical tracking
  (Ding et al. 2016 *Nat Neurosci* 19:158), logarithmic constituent-size scaling in aSTS/pSTS/IFG dissociable from
  meaning via jabberwocky (Pallier et al. 2011 *PNAS* 108:2522). Left-corner parsing (Resnik 1992) is the
  best-fitting incremental strategy. **OUR-INVENTION (the one honest gap): treating head-ID and role-assignment as
  STRICTLY SEQUENTIAL stages.** The brain interleaves them (Now-or-Never bottleneck, Christiansen & Chater 2016;
  Minimal Attachment, Frazier & Rayner 1982). We build two code stages as a fine engineering approximation -- but
  the *sequencing itself* is not neurally pinned.

- **STAGE B -- graded role competition (PINNED).** eADM Phase-2 prominence/actor computation from a weighted cue
  bundle (order, case, animacy) + **verb argument-structure projection**. Verb subcategorization is retrieved and
  used **early/predictively** (Altmann & Kamide 1999 anticipatory saccades to the verb-selected theme *before* the
  noun; Trueswell et al. 1993 subcat-bias modulates garden-paths immediately; Thompson aphasia -- argument
  structure is a dissociable stored representation). Nuance: the *number/frame* dimension may be checked slightly
  later (P600) than the *thematic-fit* dimension (N400) (Friederici three-phase model).

This IS the landed `hdlab.graded_role_assigner` mechanism (additive cue activation -> softmax = the Bayesian
posterior, McClelland 2013). What it lacked before this problem: STAGE A (it treated every nominal *token* as a
candidate, so it grabbed compound modifiers / genitive possessors), and a **case** cue and a **verb-frame** cue.

---

## 2. The ideal system, and its measured ceiling

The ideal brain-faithful STRUCTURAL who-did-what selector = **STAGE A (NP-head chunk) -> STAGE B (the graded
Competition-Model organ)**. Measured on the cleaned 19c direct-object gold (n=669,
`exp_whodidwhat_ideal_structural_v1`):

| stage | acc | note |
|---|---|---|
| nearest post-verbal token (position floor) | 0.9178 | English order dominance, PINNED |
| **+ STAGE A: NP-head chunk (compound RHR + genitive DP-head)** | **0.9806** | +0.0628 CI[+0.042,+0.084] CI-sep, > null_p95 |
| + STAGE B: graded competition (the actual organ) | 0.9806 | **identical** -- order-dominant on canonical DOs, exactly the Competition Model |
| shuffled-cue-validity twin | 0.6084 | info-free LOSES (d=+0.372 CI-sep) -- the learned validities carry real signal |
| aggressive X-bar chunk (drop all ADJ/DET) | 0.9731 | **does NOT help (-0.0075 ns)** -- the simple rule is at the structural ceiling |
| gold-corrected ceiling | 0.9836 | +2 gold-frame-errors the chunker gets right (see sec 4) |

**The chunker is the whole live lever; the graded competition adds nothing on canonical DOs because word order is
already the dominant valid cue -- which is the Competition Model's own prediction, not a shortfall.** Case is wired
as an early soft cue but DORMANT (sec 3). Extending the chunker does not help: we are at the structural ceiling.

---

## 3. The CASE cue -- faithfully built, real, structurally unavailable (a brain-faithful located negative)

eADM: morphological case is an **EARLY, parallel, first-pass prominence cue** (not a late P600 repair). Competition
Model: cue validity = availability x reliability. English case is **high-reliability but near-zero-AVAILABILITY** --
marked only on the closed pronoun class (he/him, she/her, they/them, who/whom); full NPs carry zero case morphology.
Measured (`exp_whodidwhat_nphead_case_v1`):

- **0/669 orthogonal value** on the canonical-active DO gold -- case never changes the pick (the objects are
  full nouns; 0 items even have a nominative pronoun between verb and gold). Not redundant -- *structurally absent*.
- **The cue MECHANISM is real and correctly built**: on a position-neutralized 2AFC over mined pronoun clauses,
  CASE recovers the role with order removed (1.00) while its info-free shuffle is at chance (0.51), d=+0.49 CI-sep.
- **Its decisive regime is sparse**: true fronted-object (order-conflict) clauses = **59 in 120,000 sentences
  (0.05%)**. So a ~0 pooled case effect on 19c is an AVAILABILITY fact -- the theory's own prediction confirmed
  (per the drill's HARD-FAIL test), NOT a broken cue. Case's value lives in non-canonical order / wh-relatives
  (MacDonald 1994: who/whom marking eliminates the NP/S garden-path).

**Verdict:** wire case into the graded competition as an early soft cue (dormant on canonical DOs, live on the
non-canonical regime the organ targets) -- do NOT expect it to move the 19c who-did-what number.

---

## 4. The residual gap: verb subcategorization (and part of it is a mis-annotated gold)

The 13 residual misses (`exp_whodidwhat_ideal_structural_v1`) are NOT more chunking and NOT a meaning store:
- **verb SUBCATEGORIZATION frames (~8/13)**: naming/object-complement ("call X a Y"), ditransitive ("gave the man
  godspeed"), clause-boundary ("told that ... pervade the cities").
- **2 are GOLD-ANNOTATION ERRORS** where the chunker picked the PropBank-correct patient: per PropBank/VerbNet
  (call.01 ARG1-PPT = the labelled item, ARG2-**PRD** = the name, a non-patient attribute; give.01 ARG1-PPT = the
  theme, ARG2-**GOL** = the recipient), the deep patient of "call the bungalow a place" is *bungalow*, not *place*.
  So the true structural ceiling is >= 0.9836.

**Glass-box supply (admissible static FOUNDATION, no LLM at inference):** PropBank frame files -- the ARG2-PRD vs
ARG2-GOL tag *is* the object-complement/ditransitive distinction, ~11,600 lemmas, zero runtime inference
(secondary: VerbNet dub-29.3 Theme+Result vs give-13.1 Recipient+Theme). Verb argument-structure projection is
PINNED and early (sec 1). **BUT** on this canonical-DO task the recoverable slice is ~3 items (~0.5%, minus the
gold-errors); its HIGH-value home is the `graded_role_assigner`'s non-canonical / reduced-relative residual, which
its own docstring already flags as "verb-subcat SUPPLY -- suppliable from WordNet frames." So: name it, supply it
there, do NOT build a 7-item patch here.

---

## 5. Signal-loss ledger -- WHERE, exactly, we lose who-did-what signal vs the brain

`exp_whodidwhat_signal_loss_ledger_v1` isolates each pipeline stage by swapping our glass-box component for a
COMPETENT-PARSER ORACLE (spaCy en_core_web_sm -- reference-only, a diagnostic upper bound; never wired into
inference). n=669.

| stage | brain | ours | measured loss |
|---|---|---|---|
| S1 tokenize | continuous segmentation | whitespace split | tiny (punct-attached tokens) |
| S2 POS-tag | near-perfect on archaic | modern UPOS perceptron | **NO recoverable headroom**: a modern tagger (spaCy) is WORSE on 19c (ORACLE_POS 0.9342 < ours 0.9806). ~6/13 residual touch an archaic-form POS disagreement, but no available tagger fixes them net. |
| S3 candidates | every nominal incl. pronouns | content nouns; **pronouns filtered** | **0** who-did-what signal lost on this gold (0 true-dobj pronouns) -- but a structural cap that zeroes case availability |
| S4 head-find | full hierarchical constituents | 2-rule chunk (compound+genitive) | **we are AT/ABOVE the ceiling**: a FULL modern parser (spaCy dobj) scores 0.9297 < ours 0.9806 -- the modern parser is itself degraded on 19c prose (the parent's parser wall, quantified) |
| S5 role-assign | eADM cues + verb-frame projection | order-dominant competition | **~5/13**: verb subcategorization (sec 4) -- the one clean, addressable-but-low-value gap |
| S6 clause | incremental clause segmentation | flat (matrix only) | ~1/13 (embedded-clause object) |
| metric | graded proto-role (Dowty) | exact-match single patient | 2 gold-frame-errors + graded competence unmeasured |

**The headline:** on canonical-active 19c direct objects we are essentially at the ceiling any AVAILABLE system
reaches -- above a full modern parser (which archaic prose degrades), with chunking exhausted, POS not improvable by
a modern tagger, and meaning refuted at power. The residual is bounded (~1.6%) and mostly not cleanly recoverable
on this task. **The real room for improvement is in a regime this gold cannot test** -- the NON-CANONICAL regime
(passive/fronting/wh) where our order-only pipeline would COLLAPSE and the brain's real advantages (case [built,
dormant here], verb-frame projection, full incremental parsing) become decisive -- and in the MEASUREMENT (graded
metric, gold cleanup). Both are named as follow-ons; neither is this task.
