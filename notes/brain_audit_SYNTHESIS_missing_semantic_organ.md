# Brain-foundational audit — SYNTHESIS: the missing semantic organ

Date: 2026-08-05. Director synthesis of two VET'd tracks:
- Brain mechanism (literature): `notes/brain_audit_affective_comprehension_mechanism.md`
- Our components (code-read, disk-verified): `notes/brain_audit_our_components_status.md`

## Headline (both tracks independently converge)
The goal-owner / grounded-comprehension frontier is blocked by a **whole missing organ**, of which the
"affect/valence reader" is only the visible symptom. The brain reads affect via a *default concept
activation* (ATL semantic hub + valuation spokes) that is **actively overridden toward the
context-licensed sense** by a separate **semantic-control network (IFG + pMTG)**, gated by the running
situation model. We have NEITHER piece over text: no learned lexical-semantic hub, and no
context-driven word-sense selection. Every lexical signal into our affect/goal pipeline is a fixed
hand table or a hash-seeded random-projection bag-of-words (two senses of "hard" -> identical vector).
A better lexicon or more surface-cue patches CANNOT close this (disk evidence: arm_c cue-patch REGRESSES
causal -0.308; blind valence is INERT on the confused-4 hard subset -- scrambling the HARM/HELP tables
wholesale leaves accuracy unchanged at 0.75, so valence contributes nothing there).

## Brain <-> substrate per-component map (VET'd)
| Brain subsystem (Track 1) | Our analog (Track 2, code-read) | Foundational (shape/pos/metric) | Performance on disk | Wired |
|---|---|---|---|---|
| ATL semantic hub (learned amodal concept) | NONE (word_vector = hash-random; 3 fixed tables) | ABSENT | n/a | MISSING |
| IFG+pMTG semantic control / word-sense selection | NONE | ABSENT | n/a | MISSING |
| OFC/vmPFC + amygdala/insula valuation (grounded affect) | resolve_valence_blind (22/20-word bag) + grounded_appraisal sim | reader: WRONG shape (keyword vote, no sense); sim: OK shape | reader INERT on confused-4 (scrambled==oracle 0.75); arm_c causal -0.308; sim MECHANISM_EARNS FULL=1.000 (synthetic) | Island |
| DMN + WM situation model (Zwaan event-indexing) | hdlab/situation_reader SituationModel | faithful ent/time; causation reducible; **NO affect dim** | self-tests pass | WIRED |
| Hippocampal relational binding / Centering coref | hdlab/coreference_resolver (Cb + Principle B) | FAITHFUL | HARD_PASS (29613/14/18), +0.035/+0.08 | WIRED (strongest) |
| Situation-model intentionality dim + frame roles | Component-3 frame_primary_role + thematic_role_labeler | frame-primary faithful; **production = hand table + positional OOV fallback** | MIDDLE_BAND; known 1.0 by-constr; OOV ~0.767 offline | table wired; OOV offline |
| Mentalizing TPJ/dmPFC (ToM, irony reattribution) | ToM sally_anne nested-HRR | plausible shape | HARD_PASS Q2=0.806 gap=0.668 | ISLAND |
| Predictive coding (valence prediction, N400) | NONE (no forward valence expectation) | ABSENT | n/a | MISSING |
| ACC conflict/incongruity detector | NONE (implicit only) | ABSENT | n/a | MISSING |
| Plasticity (learn features/senses) | hdlab/learner (MDL over SUPPLIED atoms) | right for RULES; cannot induce a semantic space | refuses non-compressing fits | Library |

## Three-tier bottom line
- **MISSING ENTIRELY (brain-necessary, we have nothing):** (1) the ATL learned lexical-semantic HUB;
  (2) IFG/pMTG semantic CONTROL / word-sense disambiguation; (3) predictive valence expectation; (4) an
  explicit incongruity detector. #1+#2 are the load-bearing root of every affect-reader failure.
- **PRESENT BUT NOT FAITHFUL / not-in-production:** valence reader (wrong shape, INERT on hard items,
  "learned" label over-reads a hand-cue table); Component-3 production path (hand table + positional OOV
  fallback -- situation_reader self-test even asserts OOV `cherished->AGENT`, the wrong-but-honest
  default); situation model (faithful skeleton but NO affect dimension -- the natural home that's empty).
- **FAITHFUL + PERFORMANT:** coreference (WIRED, HARD_PASS, brain-faithful -- the one solid organ).
  Appraisal sim (MECHANISM_EARNS) and ToM (HARD_PASS) are real but ISLANDED, and the sim's 1.000 is a
  synthetic mechanism-proof, NOT a text-capability number.

## The brain-foundational fix (what to build)
NOT a bigger affect table. The biology prescribes a **two-stage valence/meaning process**:
1. **Default concept activation** (a learned, glass-box lexical-semantic representation over text = the
   ATL-hub analog). MUST be earned, NOT a borrowed embedding (standing invariant: no GloVe/BERT as the
   meaning organ). Random indexing is not enough -- it needs graded similarity + groundable structure.
2. **Situation-model-gated override** (the IFG/pMTG control analog): select the context-licensed sense by
   biased competition constrained by the running situation model, then let valence ride the
   *sense-resolved concept*, not the raw surface token. This is where "studied hard" != harm is fixed.
Then: (a) implicit affect = integrate-then-PREDICT over the situation model (Bayesian cue integration +
forward projection), NOT a per-token detector; (b) irony falls out for free as predicted-vs-surface
mismatch + mentalizing reattribution IF stage 2 is genuinely predictive -- do not build a separate irony
classifier; (c) goal-owner is a binding/indexing problem (intentionality dim bound to protagonist-index,
persisted via coref/hippocampal store) -- already the Component-3->5 direction, and the literature
independently validates frame-conditioned + persistent binding.

## Falsifiable test the brain doc handed us (Section 6 of the mechanism doc)
Baseline (table valence + positional roles) vs situation-model-gated. HARD-PASS = >=15pts absolute gain
on the implicit-affect and goal-owner subsets (the two that provably cannot be solved without the
situation-model layer); HARD-FAIL = <5pts on those. P_deflated(gating closes most of gap)=0.45.

## Strategic read (Director, hypothesis-pending)
The "one bottleneck = valence reader" framing was correct but understated. The real work is building the
missing ATL-hub + IFG-control organ (glass-box, earned) and giving the situation model an affect
dimension + a predictive step. Coref (faithful) and the appraisal sim (earned valuation) are assets to
build ON. Recommended sequencing: build the smallest honest version of the learned sense-resolving
concept layer first (the missing organ), prove it clears the word-sense collisions + INERT-valence
failures on the exact items we have, THEN wire valence/affect onto sense-resolved concepts and give the
SituationModel its affect dimension. This is squarely inside the USER-authorized grounded pivot.
