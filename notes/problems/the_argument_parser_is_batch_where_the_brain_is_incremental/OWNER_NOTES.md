---
owner_verdict: DONE
---

---
problem: the_argument_parser_is_batch_where_the_brain_is_incremental
status: SOLVED
bar: "The incremental builder must beat the BATCH UD parser (candidate_generator) at candidate-argument identification / downstream role assignment, CI-separated over its UPPER bound, with an info-free twin (shuffled attachment / random revision) LOSING CI-separated. Report CI half-width + null p95. Attribute the gain to INCREMENTALITY (ablate the revision / prediction). Test where it should matter (garden-path, reversible relatives) AND on a general slice."
result: "MET on candidate-argument identification. A brain-faithful INCREMENTAL LEFT-CORNER argument-structure builder (left-to-right, eager verb-slot projection, bounded Now-or-Never buffer, NO arc graph) beats the BATCH UD parser (candidate_generator over arc_parser) at candidate-argument identification on modern QA-SRL prose. Scorer = per-predicate F1 of the candidate (verb,arg-head) set against the COMPLETE QA-SRL gold argument set (all answered questions' spans; mean 1.935 gold args/predicate). Population = QA-SRL dev+test, every predicate with >=1 gold arg (n=28,149), front-end tokenization-aligned. INCREMENTAL F1 0.6201 vs BATCH F1 0.5849, paired margin +0.0352 [+0.0314, +0.0389] ABOVE (half-width 0.0038), via a large PRECISION gain +0.0998 [+0.0960, +0.1036] (0.619 vs 0.519) at a smaller recall cost -0.0928 [-0.0974, -0.0883] (0.692 vs 0.785): the batch parser OVER-GENERATES by +1.034 [+1.016, +1.052] args/predicate (3.24 vs 2.20 candidates). The builder is genuinely INCREMENTAL: prefix-consistency 0.985 vs the batch parser's 0.941 (truncating the sentence leaves an already-closed verb's arg set unchanged 98.5% of the time vs 94.1% for the batch parse). NO hdlab file changed."
floor: "Strongest floor recomputed on the population = the crude POSITIONAL2 generator (nearest pre-verbal + nearest post-verbal nominal), F1 0.5937 (a HIGHER floor than the batch parser's 0.5849). INCREMENTAL beats POSITIONAL2 CI-separated: paired +0.0264 [+0.0237, +0.0292] ABOVE (its recall 0.692 vs positional 0.620 -- the structured left-corner attachment recovers arguments positional misses, at EQUAL-OR-HIGHER precision 0.619 vs 0.609, so the win is not merely 'emit fewer candidates'). It also beats the bar's named baseline, the BATCH parser (0.5849), by +0.0352. Info-free null (TWIN, random/shuffled attachment matched to INCREMENTAL's set size, 3 seeds) F1 0.4081; TWIN vs BATCH -0.1768 [-0.1804, -0.1734] BELOW (null p95 well under the batch floor); INCREMENTAL vs TWIN +0.2120 [+0.2080, +0.2158] ABOVE. ALL-NOMINALS (max-recall floor) F1 0.5393."
controls: "(1) INFO-FREE TWIN (random attachment, set-size matched, 3 seeds): F1 0.408, LOSES to batch -0.1768 CI-separated -> EXCLUDES 'the win is the smaller set size / any 2-3 candidates'. (2) POSITIONAL2 floor (nearest pre+post nominal, a NON-incremental bounded heuristic): F1 0.594; INCREMENTAL beats it +0.0264 CI-sep AT HIGHER PRECISION -> EXCLUDES 'the win is just bounding to ~2 args' (crude bounding LOSES 0.026). (3) ABLATE PREDICTION (INCREMENTAL vs INCR_noPredict): +0.0007 [-0.0005, +0.0018] NOT_SEPARATED -> the predictive-reader competitor-selection adds ~0 to identification F1 on canonical prose (honest: prediction's value is the predictive interface, not accuracy). (4) ABLATE REVISION (INCREMENTAL vs INCR_noRevise): -0.0101 [-0.0113, -0.0090] BELOW -- revision as gated is slightly NET-NEGATIVE on modern prose -> the F1 win is the EAGER BOUNDED LEFT-CORNER attachment (Now-or-Never), NOT prediction/revision. This is the brain's 'good-enough / don't reanalyse unless forced' principle (Ferreira; Frazier & Clifton) confirmed: on unambiguous edited prose eager commitment should be KEPT. (5) REVISION MECHANISM POSITIVE CONTROL (exp_incremental_garden_path_revision_v1): on genuine NP/S garden paths ('The man knew the dog left'), revision RE-ATTACHES correctly and beats no-revision +0.0852 [+0.0809, +0.0892] CI-sep (F1 0.919 vs 0.833), with ZERO false-fire on canonical items (diff 0.0) and an exact self-test re-attachment -> the revision mechanism IS the brain's operation; it is a no-op-to-harmful on QA-SRL because edited prose carries few garden paths, not because it is broken. (6) GLASS-BOX INCREMENTALITY: incremental_build takes NO dependency-`heads` argument (cannot launder the batch parse) and is prefix-consistent 0.985 vs the batch parser 0.941 -> the builder is genuinely left-to-right, not a re-labelled batch parse. (7) DOWNSTREAM role assignment (honest, decisive-either-way): feeding each generator's candidate set to the SEPARATE converged word-order+voice assigner, INCREMENTAL does NOT beat BATCH for patient-ID on the general slice (-0.0125 [-0.0182,-0.0065]) and even ALL-NOMINALS beats BATCH (+0.0292) -> the batch dependency parse does not earn its place for word-order role assignment; BUT on the non-canonical PASSIVE slice INCREMENTAL beats BATCH +0.0344 [+0.0264,+0.0424] CI-sep (where structure helps)."
files_changed: "experiments/exp_incremental_argstruct_builder_v1.py, experiments/exp_incremental_garden_path_revision_v1.py, experiments/exp_incremental_valency_fidelity_v2.py, experiments/exp_incremental_valency_wall_diagnostic_v2.py, verification/verify_incremental_argstruct_builder.py, notes/problems/the_argument_parser_is_batch_where_the_brain_is_incremental/RESEARCH_incremental_parsing_brain_mechanism.md, notes/problems/the_argument_parser_is_batch_where_the_brain_is_incremental/RESEARCH_deeper_fidelity_discrete_to_graded.md, notes/problems/the_argument_parser_is_batch_where_the_brain_is_incremental/SOLVED.md, data/incremental_argstruct_builder_v1/, data/incremental_garden_path_revision_v1/, data/incremental_valency_fidelity_v2/, data/incremental_valency_wall_diagnostic_v2/. NO hdlab/ file changed (proposed wiring below, Q111)."
reverify: ".venv/Scripts/python.exe verification/verify_incremental_argstruct_builder.py"
---

# SOLVED: an incremental left-corner argument-structure builder beats the batch UD parser at candidate identification -- and the win is Now-or-Never bounding, not prediction or revision

The brief said the reader's candidate generator is a BATCH dependency parser where the brain is INCREMENTAL,
PREDICTIVE and REVISABLE, and asked whether an incremental builder supplies BETTER arguments to the
(converged) role assigner. It does, at candidate identification -- CI-separated and cleanly attributed. But
the disk SHARPENS the brief in three ways that are the actual result: (a) the win is the EAGER, BOUNDED,
LEFT-CORNER attachment (Now-or-Never), NOT the predictive or revisable components, which add ~0 and slightly
hurt on modern prose; (b) that is not a defect -- it is the brain's own "good-enough / don't reanalyse unless
forced" principle, and the revision MECHANISM is separately validated to work where a garden path genuinely
exists; (c) for DOWNSTREAM role assignment the batch dependency parse does not earn its place at all -- word
order over the raw nominals matches or beats it -- so the honest recommendation is architectural, not an
accuracy headline.

## Headline in plain language

To find who-did-what in a sentence, our reader runs a standard computational-linguistics parser: it reads the
WHOLE sentence, computes a full grammatical tree using words from both directions, then reads the arguments
off it. The brain never sees the whole sentence at once -- it builds structure as it reads, one word at a
time, guessing the verb's arguments on the fly and only occasionally backing up. I built the brain's version:
a left-to-right builder that, when it hits a verb, opens "slots" for that verb's subject and object and fills
them from the nearby words as they arrive, committing immediately and keeping only a short memory of recent
words (because the brain must, its memory for exact words fades in under a second). On ~28,000 held-out modern
sentences, this incremental builder identifies a verb's arguments more accurately than the batch parser
(F1 0.62 vs 0.58, a clean separated margin) -- mainly because the batch parser OVER-GENERATES (it proposes
about 3.2 candidate arguments per verb where the truth is ~1.9, and half are wrong), while the incremental
builder proposes a tighter ~2.2 and gets a much higher fraction right. A scrambled (random-attachment) version
fails badly, and a crude "just grab the nearest noun before and after" version also loses -- so the win is the
structured left-to-right attachment, not merely proposing fewer candidates. Three honest findings sit next to
the win: (1) the "predictive" part (using the verb's expected meaning to pick between candidates) adds nothing
to accuracy on ordinary prose; (2) the "revising" part (backing up on a garden-path) slightly HURTS on
ordinary prose -- because ordinary edited prose almost never garden-paths, so backing up mostly introduces
errors; and yet (3) on genuinely ambiguous garden-path sentences, built specially, the revising part works
exactly as the brain's does. So the brain-faithful default is: build eagerly and left-to-right, and DON'T
revise unless a real conflict forces it -- which is itself a well-known fact about human parsing.

## How the brain does this, and what I built (PINNED vs OUR-INVENTION)

A dedicated research drill (persisted verbatim in `RESEARCH_incremental_parsing_brain_mechanism.md`) pinned the
mechanism before I built, and CHANGED the architecture:

- **PINNED -- LEFT-CORNER, eager, connected (Q1).** Human incremental parsing is best modelled as left-corner
  (recognise the leftmost seen material bottom-up, then top-down-project the rest of the rule), because that
  and only that concentrates memory cost on true center-embedding (Abney & Johnson 1991; Resnik 1992;
  left-corner RNNGs fit reading times + garden-path behaviour better than top-down, arXiv:2109.04939; Schuler
  2024). COPIED the operation. [OUR-INVENTION, swept: the beam width -- I use a single eager path.]
- **PINNED -- verb-slot projection IS the top-down step (Q2).** On reading a verb the brain immediately opens a
  ranked, typed argument frame (Altmann & Kamide 1999 anticipatory eye movements; Demberg/Keller/Koller PLTAG
  formalise it as the same operation). I open subject/object slots on the verb and bind incoming nominals to
  them. `predictive_reader` (the just-integrated selectional-preference centroid) supplies the prediction.
- **PINNED -- revision is BOUNDED/LOCAL, gated by a TWO-ROUTE CONFLICT (Q3).** Fast thematic-fit route vs the
  structural/eager route (Kim & Osterhout semantic-P600; Fodor & Inoue local repair); "leave underspecified"
  is first-class (Frazier & Clifton construal; Ferreira good-enough). I re-attach an eagerly-bound object to a
  following verb's subject ONLY when its thematic-fit to the first verb is low (a genuine NP/S garden path).
  [OUR-INVENTION, swept: the conflict threshold; CONTESTED in the literature -- so not a falsifiability anchor.]
- **PINNED -- Now-or-Never (Q4).** Raw input decays in <1s, so the brain commits eagerly over a lossy, bounded
  buffer (Christiansen & Chater 2016). I keep a bounded buffer of recent nominals and commit immediately.
  [OUR-INVENTION, swept: buffer depth -- the literature explicitly leaves the size unpinned; I sweep it, adopt none.]
- **PINNED, and the decisive architectural constraint -- STRUCTURE-BUILDING and ROLE-BINDING are SEPARATE
  ORGANS (Q5).** Beber et al. 2025 (VLSM double dissociation), Matchin & Hickok 2020, eADM: structure-building
  (frontal/pMTG) is a different computation from thematic role assignment (posterior-temporal / angular gyrus /
  inferior-parietal). So my builder ONLY emits the bounded candidate-argument SET; the SEPARATE converged role
  assigner (word-order + voice, integrated) picks the patient. I do NOT fuse attachment with role assignment.

Data: modern QA-SRL v2 (gold predicate-argument spans; the corpus the batch parser is trained on -- era held
fixed across arms). The identification metric scores each generator's per-verb candidate set against the
COMPLETE gold argument set (all answered questions), so a batch "over-generated" candidate that is in fact a
real other-role argument is NOT counted against it -- the fair test.

## What I measured (all CI'd; reverify = the witness, PASS)

1. **THE HEADLINE -- incremental beats batch at candidate identification, CI-separated.** n=28,149 predicates,
   full gold (mean 1.935 args). INCREMENTAL F1 0.6201 vs BATCH 0.5849: +0.0352 [+0.0314, +0.0389], hw 0.0038.
   Driven by PRECISION +0.0998 [+0.0960, +0.1036] (batch over-generates +1.034 args/predicate) at recall
   -0.0928. **BAR MET.**
2. **THE INFO-FREE TWIN LOSES.** Random/shuffled attachment (set-size matched, 3 seeds) F1 0.4081; vs batch
   -0.1768 [-0.1804, -0.1734] BELOW; INCREMENTAL vs twin +0.2120 [+0.2080, +0.2158].
3. **MORE THAN CRUDE POSITIONAL (strongest floor).** POSITIONAL2 (nearest pre+post nominal) F1 0.5937 -- itself
   ABOVE the batch parser. INCREMENTAL beats it +0.0264 [+0.0237, +0.0292] at HIGHER precision -> the win is
   the structured left-corner attachment (recall 0.692 vs 0.620), not merely a smaller set.
4. **PREDICTION ADDS ~0 (honest).** INCREMENTAL vs INCR_noPredict +0.0007 [-0.0005, +0.0018] NOT_SEPARATED.
   The predictive-reader competitor-selection does not move identification F1 on canonical prose; its value is
   the predictive INTERFACE (a batch parser cannot supply a verb's open slots mid-sentence to a predictive
   reader at all), not accuracy here.
5. **REVISION SLIGHTLY HURTS ON MODERN PROSE (honest) -- and this is the brain's own principle.** INCREMENTAL
   vs INCR_noRevise -0.0101 [-0.0113, -0.0090] BELOW: turning revision OFF gives a HIGHER F1 (0.6302). Edited
   prose is overwhelmingly canonical, so eager commitment is almost always right and re-analysis mostly
   introduces errors -- exactly "good-enough parsing / don't reanalyse unless forced" (Ferreira; Frazier &
   Clifton). The brain-faithful default is revision OFF, fired only on a genuine conflict.
6. **THE REVISION MECHANISM IS VALIDATED where a garden path EXISTS (positive control).**
   `exp_incremental_garden_path_revision_v1`: on synthetic NP/S garden paths ("The man knew the dog left" --
   "the dog" is the subject of "left", not the object of "knew"), revision re-attaches correctly and beats
   no-revision +0.0852 [+0.0809, +0.0892] (F1 0.919 vs 0.833), with ZERO false-fire on canonical items and an
   EXACT self-test re-attachment ({knew,dog}->{man} for knew; dog->left). So the mechanism is the brain's; it
   is simply rarely applicable on modern edited prose. (HONEST LIMITATION: on a PURE-garden set an
   info-free "revise-at-random" twin nearly ties real revision, because when every item is a garden path any
   revision helps; the conflict signal's SELECTIVITY is what earns its place on MIXED/canonical populations,
   evidenced by revision being near-neutral rather than catastrophic on QA-SRL.)
7. **DOWNSTREAM ROLE ASSIGNMENT -- a rigorous negative on the general slice, positive on the tail.** Feeding
   each generator's candidate set to the SEPARATE converged word-order+voice assigner: on the patient-bearing
   slice INCREMENTAL does NOT beat BATCH for patient-ID (-0.0125 [-0.0182, -0.0065]), and ALL-NOMINALS beats
   BATCH (+0.0292) -> the batch dependency parse does not earn its place as a candidate generator for
   word-order role assignment; word order over the raw nominals suffices. BUT on the non-canonical PASSIVE
   slice INCREMENTAL beats BATCH +0.0344 [+0.0264, +0.0424] -- where the tighter candidate set removes
   distractors that fool the voice assigner.
8. **GLASS-BOX INCREMENTALITY.** `incremental_build` takes NO dependency-`heads` argument (it cannot launder
   the batch parse) and is prefix-consistent 0.985 vs the batch parser's 0.941 (the batch parse changes an
   already-closed verb's arg set on 6% of prefixes; the incremental builder on 1.5%). The batch parser's
   candidate rules use bidirectional (future-word) features + whole-graph cycle-breaking -- structurally
   non-incremental; the builder is strictly left-to-right.
9. **ROBUSTNESS (sweep).** The headline holds across every OUR-INVENTION param: buffer_n in {2,3,4,6} x
   conflict_margin in {0.0, 0.15, 0.30} all give INCREMENTAL F1 0.662-0.668 vs BATCH 0.625, margin +0.024 to
   +0.054, ALL CI-separated ABOVE (dev slice). Two honest facts fall out: (a) buffer_n is INVARIANT (2=3=4=6
   identical) -- sentences are short enough that the bounded buffer rarely fills, so buffer depth is not a
   load-bearing tuned knob here; (b) revision is monotonically LESS harmful the LESS it fires (ablate-revise
   -0.006 at margin 0.0 -> -0.012 at 0.30), re-confirming that on canonical prose the good-enough default is
   minimal revision. The win is not a tuned point; buffer_n=3, conflict_margin=0.15 are reported defaults,
   adopted from none.

## Is this brain-faithful? (the deepening drill's verdict)

YES on the operation, with the components honestly separated:

- **The core operation is faithful.** Eager, connected, left-to-right, left-corner verb-slot projection over a
  bounded lossy buffer -- Q1/Q2/Q4 pinned, copied. The builder emits structure at every word (prefix-available),
  which a batch parser structurally cannot; this is what a predictive reader REQUIRES to be fed.
- **Structure-building and role-binding are kept SEPARATE (Q5) -- the biggest architectural fidelity gain.**
  The builder does attachment only; the converged assigner does role-binding. This matches the lesion+TMS+fMRI
  double dissociation (Beber 2025) and is the brief's own split.
- **The components were interrogated, not assumed.** Ablations show the F1 win is the EAGER BOUNDED attachment
  (incrementality's Now-or-Never core), not prediction (~0) or revision (net-negative on canonical). Rather
  than hide this, it is the result: it reproduces the brain's good-enough principle, and the revision mechanism
  is separately validated on genuine garden paths.
- **The honest deviation: the population lacks the ambiguity the predictive/revisable machinery is FOR.** QA-SRL
  is modern edited prose; genuine garden paths and reversible non-canonicals are rare (the relcl SOLVED
  measured its filler-gap circuit firing on 0.75% of QA-SRL). So prediction/revision cannot move an aggregate
  modern-prose number; their value is the tail + the predictive interface. This is named, not hand-waved.

## DEEPER FIDELITY AUDIT (owner-requested 2nd drill, 2026-08-27) -- the one deep gap is DISCRETE vs GRADED

A second literature drill + empirical tests interrogated whether EVERYTHING here is brain-faithful. Verdict:
PARTIALLY -- and the deepest gap unifies most of the others. Full record in
`RESEARCH_deeper_fidelity_discrete_to_graded.md`.

- **The gap: the brain builds structure in GRADED activation, not HARD binds.** Human incremental parsing is
  parallel graded probabilistic competition (MacDonald 1994; Trueswell 1993; Levy 2008), and the discrete rule is
  the noise->0 limit of graded cue-based retrieval (Lewis & Vasishth 2005 -- collapse when the activation GAP is
  large). This is the SAME direction the relcl SOLVED found for role assignment -> "discrete -> graded" is a
  SUBSTRATE-WIDE lever, not this organ's alone.
- **I tested the highest-value instance -- graded VERB VALENCY -- and it does NOT beat the generic builder here**
  (`exp_incremental_valency_fidelity_v2`, full-gold F1). The brain's valency is a graded frame-probability
  distribution, not integer arity (Garnsey 1997; Jurafsky 1996). But conditioning the builder on learned per-verb
  valency loses at every fidelity level (n=28,149 dev+test, full-gold F1): integer arity -0.0322
  [-0.0351,-0.0293], hard intransitivity-gate -0.0023 [-0.0028,-0.0018], GRADED (P_post x fit > tau) -0.0628
  [-0.0656,-0.0600] -- all CI-separated BELOW the generic INCREMENTAL (0.6192), all by UNDER-generating
  (sizes 1.83 / 2.18 / 1.50 vs the generic 2.20 and mean gold 1.94).
- **WHY the faithful fix loses -- VERIFIED, not asserted (`exp_incremental_valency_wall_diagnostic_v2`, per the
  "a weak impl != an intrinsic ceiling; decompose the wall" discipline). The barrier is TWO-part, and my first
  "gated behind p1" note was an OVER-SIMPLIFICATION:**
  1. **SMALL task headroom (the binding limit).** A PERFECT object-inclusion decision (ORACLE_OBJ) beats the
     generic eager builder by only **+0.028 [+0.020, +0.036]** -- the generic "attach the nearest post-verbal
     nominal" is already near-ceiling on canonical English. This is the SAME brain-foundational reason the
     front-end SOLVED found word order dominates: English is a rigid word-order language, so word-order cue
     validity is highest and valency/semantic cues have little to add (Competition Model, Bates & MacWhinney).
     The brain relies on order for English too. So there is not a big win here for ANY valency mechanism.
  2. **WEAK fit signal (a real p1 symptom, but secondary).** cos(noun, verb patient-centroid) separates gold
     objects from non-gold post-verbal nominals at **AUC 0.59** only (frame-probability alone AUC 0.66) -- the
     coarse 12-dim grounded space barely tells patient from non-patient. So even the small headroom cannot be
     captured by the semantic route; every real-signal arm loses (fit-only -0.11, frame-prob-only -0.04).
- **CORRECTED conclusion:** graded valency/attachment is NOT "a big win gated behind p1 on this task." On
  canonical English argument-ID the task itself is near-saturated by eager word-order attachment (oracle ceiling
  +0.028), and the semantic signal is additionally weak (p1). The generic eager Now-or-Never bounding stays the
  right mechanism HERE. The graded direction's real value is the **non-canonical / freer-word-order / ambiguous
  tail** (where eager commitment genuinely errs) -- NOT canonical English argument-ID, and NOT primarily a p1 gate.

> **FOR THE STRATEGY SESSION -- proposed FOLLOW-UP PROBLEM (your call to open; do NOT staple onto this one),
> now with the VERIFIED barrier:** "the parser commits discretely where the brain competes in graded activation."
> The graded direction (graded-attachment via best-vs-second activation-gap collapse, Lewis & Vasishth; targeted
> k=2-3 beam at close-call points, Franzluebbers/Hale 2024; graded frame-probability valency) is real and
> substrate-wide (unify with the graded role-assignment finding, relcl). **BUT the verification corrects WHERE to
> test it: NOT on canonical English argument-ID** -- there the oracle ceiling over the generic eager builder is
> only +0.028 (English word-order dominance saturates the task) and the fit signal is weak (AUC 0.59). **Test
> graded attachment where eager commitment genuinely errs: the non-canonical / ambiguous / passive / object-
> relative tail, and ideally a freer-word-order or case-marked language** (where the Competition Model predicts
> valency/case cues carry real validity). p1 (richer meaning features) would lift the weak fit signal, but on
> canonical English it is the TASK ceiling, not p1, that binds -- so "build graded after p1" is the wrong framing;
> "test graded on populations with real structural ambiguity" is the right one. Do NOT build a hierarchical stack
> parser for argument ID (Frank & Bod 2011; its value is center-embedding/long-range, not argument ID).

## What would change in hdlab (proposed; the strategy session lands it, Q111)

- **Add a new organ `hdlab/incremental_structure_builder.py`** = the left-corner eager builder: left-to-right,
  verb-slot projection, bounded buffer, emits per-verb candidate arg SETS. NO arc graph. Glass-box, numpy +
  pure-python, composes `predictive_reader` for the slot prediction.
- **Wire it BEHIND A FLAG as the candidate source** in the live reader (`situation_reader` /
  `reading_grounding_loop`), replacing `candidate_generator`'s arc-parse candidate generation. Identical
  downstream: the converged role assigner is UNCHANGED (Q5 -- separate organ). Only the argument-source changes.
- **Default config: eager bounded builder, prediction ON (harmless + architecturally required for the
  predictive interface), REVISION OFF by default** (fire only on the high-precision garden-path conflict; the
  brain's good-enough default). buffer_n=3 as a swept default, not adopted.
- **Compose, do not duplicate:** `predictive_reader` supplies the verb-slot anticipation (Altmann-Kamide); the
  relcl filler-gap resolver (integrated) handles the reversible-relative tail -- the builder routes to it on a
  closed-class relativizer (its specialised circuit reaches oracle where the general parse is HARMFUL). The
  N400 monitor consumes the difficulty signal.
- **The batch `arc_parser` is REPLACEABLE as a candidate generator for role assignment.** It over-generates
  (+1 arg/predicate), is non-incremental (cannot feed a predictive reader), and even all-nominals+word-order
  matches it downstream. Keep it only if a full dependency graph is needed elsewhere; for candidate generation
  the incremental builder is preferable on fidelity + precision at equal-or-better identification F1.
- **Expect a FIDELITY + PRECISION win, not a big downstream accuracy jump.** On canonical modern prose word
  order dominates role assignment; the incremental builder's live value is (1) a genuinely incremental,
  prefix-available structure the predictive reader can consume, (2) reduced over-generation (the documented
  harm that made naive wiring 0.385 in the front-end SOLVED), (3) a validated garden-path revision for the tail.
  Measure on the live reader before any capability claim.

## KEY REALIZATIONS (the enabling moves)

- **The FAIR gold flipped a tie into a CI-separated win.** My first metric scored candidates against only the
  {patient, agent} I extracted, and INCREMENTAL merely TIED batch (+0.009, not separated) -- because the batch
  parser's "over-generated" candidates were partly REAL other-role arguments I wasn't crediting. Scoring
  against the COMPLETE QA-SRL gold argument set (all answered questions) is the fair identification metric, and
  it separates cleanly (+0.035). The lesson: an over-generation penalty is only fair if the gold is complete.
- **The batch parser's over-generation is the lever, and the metric has to expose it.** F1 against a complete
  gold penalises the batch parser's +1 extra arg/predicate exactly; precision/recall on the same population
  make the trade legible (precision +0.10, recall -0.09, net +0.035).
- **The ablations refuting my own "predictive/revisable" components are the real finding.** I built prediction
  and revision because the brief and the biology call for them; the disk says they add ~0 and slightly hurt on
  modern prose. Rather than tune them until they helped, the honest reading -- they are FOR ambiguity the
  population lacks, and the brain itself doesn't reanalyse unambiguous prose -- is more brain-faithful than a
  tuned win would have been. The garden-path positive control then proved the revision mechanism is correct,
  so "it doesn't help here" is a population fact, not a broken mechanism.
- **Keeping structure-building and role-binding SEPARATE (Q5) is what made the experiment clean.** Because the
  builder only proposes candidates and the SEPARATE converged assigner picks the role, "does incrementality
  supply better arguments" is a clean question about the candidate set, and the downstream test cleanly shows
  the batch parse doesn't even earn its place there.
- **Prefix-consistency operationalises "incremental" as a testable property.** Truncating the sentence and
  checking an already-closed verb's arg set is unchanged (0.985 for the builder vs 0.941 for the batch parse)
  turns "is it really incremental" from a claim into a number, and is the glass-box guard against a re-labelled
  batch parse.

## What I did NOT establish (and would withdraw first if wrong)

- **This is a held-out candidate-IDENTIFICATION result, not a demonstrated live-reading gain.** The FIRST thing
  I would withdraw is any implication that wiring this moves a live comprehension/QA number; downstream role
  assignment does NOT improve on the general slice (word order dominates). Its value is fidelity + precision +
  the predictive interface, to be measured on the live reader.
- **Prediction and revision do NOT earn their place on this population** (predict ~0, revise net-negative). I do
  NOT claim they help identification on modern prose; I claim the mechanism is correct (garden-path control) and
  applicable to the rare non-canonical tail + the predictive interface. If a reviewer needs prediction/revision
  to carry an aggregate number, this is a PARTIAL, not a SOLVED -- I read the bar as met by the identification
  win, which is squarely "candidate-argument identification."
- **The garden-path validation is SYNTHETIC with oracle POS.** It proves the revision MECHANISM re-attaches
  correctly; it does not measure a garden-path rate on real prose (rare, and the reversible tail is owned by the
  relcl SOLVED). The info-free revise-at-random twin nearly ties on a pure-garden set -- a design limitation of
  that control, disclosed.
- **I did NOT rebuild the role assigner or a full parse.** Per the brief, the assigner is converged and I do not
  reproduce a UD tree. The downstream assigner is the converged word-order+voice rule; a stronger learned
  assigner might use structure differently, untested (the front-end SOLVED found word order dominates it too).
- **The buffer/beam is a single eager path, not the multipath beam the fMRI evidence (Franzluebbers/Hale 2024)
  suggests.** A small competing beam is more faithful and untested here; I swept buffer depth but kept beam=1.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **TIER 1 "Dependency / argument-structure parse (arc_parser)" -- add the CANDIDATE-GENERATOR verdict.** The
   entry records arc_parser as UNSCORABLE and (for filler-gap) HARMFUL. Add: as a CANDIDATE GENERATOR feeding
   role assignment on modern prose, the batch arc parse is MEASURABLY REPLACEABLE -- an incremental left-corner
   builder beats it on candidate-identification F1 (+0.0352 CI-sep, n=28,149) via reduced over-generation
   (+1.03 args/predicate), is genuinely incremental (prefix-consistency 0.985 vs 0.941), and even
   all-nominals+word-order matches/beats it downstream. Recommend the audit record the structural front-end as
   an INCREMENTAL/PREDICTIVE build target, with the batch arc parse marked replaceable for candidate generation.
2. **TIER 3 "Thematic role assignment" -- record the STRUCTURE/ROLE SEPARATION (Beber 2025).** The audit already
   localises reversible role binding to posterior-temporal/inferior-parietal. Add the load-bearing architectural
   fact from the research drill: structure-BUILDING (frontal/pMTG, eADM Phase 1) and role-BINDING (posterior-
   temporal/angular gyrus, eADM Phase 2) are SEPARATE ORGANS with an asymmetric double dissociation (Beber 2025
   VLSM + TMS + fMRI): posterior damage -> selective thematic errors with intact structure; frontal damage ->
   both. Implication for the substrate: keep the candidate/structure builder and the role assigner as separate
   organs (as done here), never fuse attachment with role assignment.
3. **NEW cross-cutting note -- "feed-forward where the brain is predictive" now has its STRUCTURAL instance.**
   The predictive-reader closed it for semantics; this closes it for STRUCTURE: an incremental builder supplies
   prefix-available structure a batch parser cannot, which is the architectural prerequisite for a predictive
   reader. Recommend the audit link the predictive-reader and this builder as the two levels (semantic +
   structural) of one predictive front-end, with revision default-OFF (good-enough parsing) and the relcl
   filler-gap circuit as the specialised tail.
4. **NEW substrate-wide deviation -- DISCRETE where the brain is GRADED (owner-requested 2nd drill).** The
   incremental builder makes HARD binds; human parsing is graded probabilistic competition, discrete = the
   noise->0 limit of graded cue-based retrieval (Lewis & Vasishth 2005) -- the SAME mechanism the audit's TIER 3
   role-assignment entry already names for reversible role binding. Recommend the audit record a CROSS-ORGAN
   "discrete -> graded" deviation spanning parsing AND role assignment, with the shared collapse rule
   (activation-gap threshold), and MEASURED evidence that a graded VALENCY fix under-generates on QA-SRL
   (`exp_incremental_valency_fidelity_v2`, n=28,149: integer -0.0322, gate -0.0023, graded -0.0628 vs the generic
   builder, all CI-separated BELOW). **VERIFIED barrier (`exp_incremental_valency_wall_diagnostic_v2`, per the
   "decompose the wall, don't assert a ceiling" discipline): the block is TWO-part -- (1) SMALL task headroom on
   canonical English (oracle-perfect object decision beats the generic eager builder by only +0.028; word order
   already saturates argument-ID -- Competition Model, the same reason the front-end found word order dominates),
   and (2) a WEAK fit signal (patient-centroid cosine AUC 0.59; a p1 symptom, but secondary).** So the audit should
   record this as a CANONICAL-ENGLISH TASK ceiling + a p1 signal-quality symptom -- NOT a clean "p1 gates a big
   graded win." Implication: open graded attachment as its own substrate-wide problem, and TEST IT ON NON-
   CANONICAL / FREER-WORD-ORDER / AMBIGUOUS populations, where eager commitment genuinely errs -- not on canonical
   English argument-ID.

---

## TLDR
The reader used a whole-sentence grammar parser to find each verb's arguments; the brain does it left-to-right,
one word at a time, guessing as it goes. I built the brain's version -- a left-to-right builder that opens a
verb's argument slots the moment it reads the verb and fills them from nearby words, committing immediately and
keeping only a short memory. On ~28,000 modern held-out sentences it identifies a verb's arguments more
accurately than the batch parser (0.62 vs 0.58, a clean margin), mainly because the batch parser proposes too
many candidates (3.2 per verb vs the true ~1.9) while the incremental one proposes a tighter, cleaner ~2.2. A
random-attachment version fails badly and a crude nearest-noun version also loses, so the win is the structured
left-to-right building, not just proposing fewer. Three honest results sit beside it: the "predict the next
argument" part adds nothing to accuracy on ordinary prose; the "back up and revise" part slightly HURTS on
ordinary prose (because ordinary prose rarely tricks you, so backing up mostly adds mistakes) -- yet on
sentences specifically built to trick you, the revising part works exactly right. And for the final who-did-what
decision, the grammar parse turns out not to earn its keep at all -- plain word order over the raw nouns does
just as well. So the recommendation is architectural: make the structure-builder incremental (it's more
faithful, proposes cleaner candidates, and is the only kind of builder a word-by-word predictive reader can
actually use), keep revision off by default the way the brain does, and stop relying on the batch parse.

## QUESTIONS
None. One judgement call for the owner at integration: I read the bar as MET by the candidate-IDENTIFICATION
win (CI-separated, twin loses, floors cleared). If the bar is read as requiring a DOWNSTREAM role-assignment
win on the general slice, this is a rigorous PARTIAL -- downstream ties on canonical (word order dominates) and
only wins on the non-canonical passive tail. The identification win + the "batch parse is replaceable" finding
are the durable results either way.

## NEXT STEPS
1. Land the incremental left-corner builder as a new `hdlab` organ and wire it BEHIND A FLAG as the candidate
   source in the live reader, replacing `candidate_generator`'s arc-parse candidate generation; the converged
   role assigner is unchanged (separate organ). Measure on the LIVE reader, not in isolation.
2. Default: eager bounded builder, prediction ON (predictive interface), REVISION OFF (good-enough); fire
   revision only on the high-precision garden-path conflict. Route to the relcl filler-gap resolver on
   relativizers.
3. Test the one place structure helps role assignment on real text -- the non-canonical/passive tail
   (INCREMENTAL beat BATCH downstream +0.034 there) -- on a live passive-bearing population.
4. Add a small competing beam (Franzluebbers/Hale 2024 multipath) and re-test -- the single eager path is a
   simplification; a 2-4-way beam is more faithful and may recover recall lost to eager commitment.
5. Feed the builder's per-word difficulty/conflict signal to the N400 monitor + write-gating as the incremental
   revision signal a batch parser cannot produce.
6. **(STRATEGY, not this problem)** Open the substrate-wide "discrete -> graded" follow-up (see the DEEPER
   FIDELITY AUDIT + AUDIT UPDATE #4), unified with the graded role-assignment finding. VERIFIED here: on canonical
   English the oracle ceiling over the generic eager builder is only +0.028 and the fit signal is weak (AUC 0.59),
   so graded attachment is NOT a big canonical-English win -- TEST IT on non-canonical / freer-word-order /
   ambiguous populations where eager commitment genuinely errs (a richer p1 representation lifts the fit signal
   but is not the binding limit on canonical English).
