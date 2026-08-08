# TONIGHT PLAN: three different ways over the grounding/extraction wall + the decision tree

**Filed:** 2026-08-08 by Director (full-auto overnight). USER asked before sleep: "do a few drills on
different ways to overcome the wall we face" + "share a detailed plan for tonight based on what results
you get." USER's strategic read: "I think we're converging on how the brain actually does it. since the
brain can do it, we can do it too." This doc is that plan: the three in-flight attacks, the can-fail
bands, and the decision tree that turns each outcome-combination into the next build.

## THE WALL (one sentence, measured)
Narrative/relational comprehension bottoms out on GENERALIZABLE WORD-GROUNDING: on modern narrative the
achievement-comparison plateaus ~0.60 with surface cues, and the hand-lexicon relation channels
(class_relation / verb_sim / referent_sim) fire ~0/30 because the closed lexicons don't cover modern
vocab. Two framings that may be the same wall or two walls: (i) grounding-COVERAGE (lexicon too small),
(ii) context-EXTRACTION (verb-ID/lemmatizer feeds noise so the earn loop never gets clean inputs).

## THE THREE ATTACKS (in flight tonight)
- **D1 CROSS-POS COMPOSITION (committing agent ad82e872):** extend definition-composition scalar->
  FEATURE-BUNDLE + cross-POS ADJ_SEED; substitute for the closed hand-lexicon in the relation channels;
  re-test on modern narrative. GATE: fire >=50% of OOV, acc-when-fired >=0.70, scramble-collapse >=0.30;
  downstream relation-channel fire 0/30 -> >=10/30, acc >=0.65 (beat 0.60). MUST-FAIL floors: random-gloss
  + scrambled-feature. = the grounding-COVERAGE escape.
- **D2 ORACLE-DECOUPLE (report-only agent a0ae7dc3):** feed the earn-from-exposure loop GOLD context
  extraction (spaCy/hand oracle) on modern prose; compare scramble-vs-real collapse gap under
  real-extract vs gold-extract vs gold-scramble. = ARBITRATES framing (i) vs (ii): if gold-extract makes
  the collapse gap appear, the wall is EXTRACTION; if not, it's the MECHANISM.
- **D3 LEARNED-RELATION (report-only agent ac655dd4):** MDL learner (hdlab/learner, the route that gave
  part-1 goal-recognition recall 0.871) learns the goal->outcome achievement relation from the small
  supervised signal, bypassing grounding coverage. GATE: mdl_select picks NON-episodic (compression>1.0)
  AND held-out > 0.60 plateau AND > majority AND scramble-collapses. = the LEARNING escape.

## THE DECISION TREE (what each outcome-combination means -> next build)
Read D2 FIRST (it arbitrates which wall is binding), then D1 vs D3 as the two escapes.

- **D2 = EXTRACTION-wall (gold context unblocks collapse):** the binding wall is verb-ID/lemmatizer, not
  grounding depth. NEXT = FIX the verb-ID/lemmatizer (brain-faithful: reuse an owned POS/dependency-ish
  signal or the frame_induction syntactic-bootstrapping organ; glass-box) -> clean the credit-assignment
  inputs -> re-run earn-from-exposure. This is the banner's named next action, now evidence-backed.
- **D2 = MECHANISM-wall (gold context does NOT unblock):** extraction isn't the lever; the escape is a
  better grounding/relation mechanism -> weight toward whichever of D1/D3 passed.
- **D1 PASS (grounding coverage un-starves channels, beats 0.60):** promote the cross-POS composition to
  hdlab + wire it into the relation channels (wire-don't-island) -> re-run the narrative met/unmet
  pipeline end-to-end -> this becomes the generalizable-grounding core the B-program needed.
- **D1 FAIL-COVERAGE (fire ~0):** modern gloss content-words also aren't groundable from the seed ->
  the seed is too small; NEXT = grow the seed via WordNet propagation depth / a second seed-POS pass
  (bounded, still earn-not-supply) before re-testing. NOT a ceiling.
- **D1 FAIL-CORRECTNESS (fire rises, acc collapses):** composition adds coverage without truth for the
  RELATION -> gloss-composition is a scalar-polarity tool, not a relational one -> lean on D3 (learned
  relation) for the relational half.
- **D3 PASS (learned route beats 0.60 without grounding):** the achievement-comparison is LEARNABLE from
  supervision -> promote via hdlab/learner, author more modern met/unmet data to strengthen n, wire as
  the relational typer. Cheapest viable escape if it holds.
- **D3 FAIL-PLATEAU (generalizes but ~0.60):** surface features carry no relational signal -> CONFIRMS
  the relation genuinely needs grounding/deeper semantics -> D1 (or a deeper grounded judgement) is the
  necessary path, not optional. A useful negative.
- **D3 FAIL-EPISODIC (stays episodic):** data-density problem -> author more modern data, re-test; do NOT
  conclude ceiling (flat-learning-result discipline).

## BEST-CASE / WORST-CASE (so the morning read is fast)
- BEST: D2=extraction-wall AND (D1 or D3) passes -> we have BOTH the binding-wall fix (verb-ID) AND a
  working relational escape -> converging on the brain's route, as USER intuited; scale it.
- MIXED: D2=mechanism-wall, exactly one of D1/D3 passes -> clear single next build (the passer).
- WORST: all three flat -> run the anti-premature-HARD_FAIL triage on each (foundation? signal reached?
  genuinely-new? fair regime? n?) BEFORE any ceiling claim; brain=existence-proof -> deepest-culprit
  audit, not a stop. Most likely culprit if all flat = n too small on modern narrative -> author data.

## OPS TONIGHT (invariants in force)
Only D1 commits (one committing agent at a time -- git-race guard). D2/D3 are scratchpad-only; I bank
their findings myself. VET every result per-axis as hard as a negative; read-the-code not the label;
carry the honest caveat that D1's base ARM-A was narrow on arbitrary vocab. Modern data only (McGuffey
demoted). Glass-box + earn-not-supply + no-borrow throughout. Heartbeat every turn. I stay awake while
these run; each return -> VET -> bank -> advance the tree.

## RESULTS (2026-08-08, all three ran to completion; Director-VET'd on disk, per-axis)
Ops note: all three agents auto-backgrounded their scripts + stalled (the recurring detach stall); the
scripts were fully authored, so the Director ran each blocking + read stdout directly + VET'd.

- **D1 CROSS-POS COMPOSITION = PARTIAL (coverage YES, relational-accuracy NO).** Cell
  exp_definition_composition_grounding_featurebundle_crosspos_v1.py, metrics.json disk-verified.
  COVERAGE HALF PASSES: fresh OOV noun/adj fire 13/24=0.542 at acc-when-fires **1.0**; downstream the
  starved channels un-starve **class_relation 1->15/30, verb_sim 0->14/30** (referent_sim stays 0),
  grounded_fire_rate 0.233->0.533. CORRECTNESS HALF FAILS at the RELATION: grounded_acc flat 0.500->
  0.533, acc_when_fired DROPS 0.714->0.625. Floors: scrambled_feature clean 0.5; scramble-delta 0.29
  (at the 0.30 bar); random_gloss 0.6 (slightly high, noted). => grounding-COVERAGE for modern vocab is
  tractable, but word-grounding coverage alone does NOT supply the goal<->outcome RELATION.
- **D2 ORACLE-DECOUPLE = EXTRACTION-WALL (agent labeled MIXED/UNDERPOWERED; Director read = extraction
  on the primary-accuracy axis).** spaCy gold oracle, 24 episodes / 6 lemmas. PRIMARY ACCURACY:
  REAL_EXTRACT **0.5** -> GOLD_EXTRACT **1.0** (same loop, only the extractor swapped). Concrete culprit
  = LEMMATIZER MIS-STEMMING: revive->reviv, dwindle->dwindl, corrode->corrod truncate past the
  dictionary lemma so valence never attaches (revive/dwindle/corrode register null in REAL, all correct
  in GOLD). Extraction precision 12/24 verbatim-lemma; garbage-canary 4/15 wrongly flagged verb-like.
  Scramble-collapse present in BOTH arms => the earn MECHANISM is intact; the binding wall is extraction.
  (agent's MIXED label = keyed on scramble-gap-only-with-gold, which didn't fire cleanly; the primary-
  acc 0.5->1.0 signal did. n=24 small -> directional, but matches the banner's named culprit.)
- **D3 LEARNED-RELATION = FAIL-PLATEAU / AMBIGUOUS (generalizes but re-finds the surface plateau; no
  genuine relation).** hdlab/learner mdl_select chose **gam** (non-episodic, compression 1.295 > 1.0) =>
  learner works, "missing-learning" is NOT the issue. Held-out **0.625** (n_test=16, SE~0.12) is
  statistically indistinguishable from the 0.60 plateau. LOAD-BEARING NEGATIVE: **pairscramble does NOT
  collapse** (0.625->0.562, delta +0.062) => the learned model reads OUTCOME-ONLY surface cues
  (achieve_verb/fail_verb/affect/negation carry all the weight; referent-overlap ~0), NOT a goal<->
  outcome relation. The learned route escapes nothing; it re-finds the plateau by another path.

## THE CONVERGENCE (the payoff -- the wall DECOMPOSES into two sub-problems that were conflated)
- **(a) WORD-LEVEL grounding/valence attachment = TRACTABLE.** D2: fix the lemmatizer mis-stemming
  (REAL 0.5->GOLD 1.0). D1: coverage extends to modern vocab (fresh OOV acc-when-fires 1.0). So words
  CAN get grounded on modern text once extraction is clean + coverage is extended.
- **(b) The goal<->outcome RELATION (does the outcome ACHIEVE the goal) = THE TRUE RESIDUAL.** NEITHER
  grounding-coverage (D1 acc flat) NOR learning-over-surface (D3 pairscramble no-collapse) captures it,
  because neither does a STRUCTURAL goal-state<->outcome-state comparison -- both read words/outcomes in
  isolation. This is the brain's ACC expectancy-violation function (part-2 formalize sec 1), which
  COMPOSES with vATL word-grounding rather than replacing it. USER intuition supported: the brain does
  BOTH and composes them; our escapes each failed by doing only one half.
- **New sharp can-fail tool (from D3):** any genuine relational model MUST make PAIRSCRAMBLE COLLAPSE
  (scrambling goal<->outcome pairing must drop accuracy). D3's +0.062 non-collapse is the number to beat.

## DECIDED NEXT BUILD (synthesized; test-first; brain-faithful; the tree resolved here)
Compose, don't run-separately. Sequence:
1. **FIX the lemmatizer mis-stemming** (D2's concrete culprit; cheap; unblocks word-grounding
   attachment). Brain-faithful = temporal-lobe lexical access / affix-strip TO a real lemma entry, not
   past it. Can-fail: REAL_EXTRACT primary-acc rises toward GOLD's 1.0 on the D2 probe.
2. **WIRE the extended grounding (D1) INTO a STRUCTURAL goal-state<->outcome-state comparison** (reuse
   the part-2 formalize's ACC-analog: GoalOutcomeRegister bind(goal-state)+bind(outcome-state) ->
   _class_relation/did-it-happen over GROUNDED word features, NOT a flat outcome classifier). Can-fail:
   met/unmet on modern narrative beats 0.60 AND **pairscramble collapses >= ~0.15** (the D3 diagnostic)
   AND non-episodic. This is the composition the three drills prove is necessary.
HARD-FAIL triage stays: n is small across all three (16-30) -> author more modern goal-achievement data
before any ceiling claim; brain=existence-proof (ACC does goal-achievement monitoring -> achievable).
