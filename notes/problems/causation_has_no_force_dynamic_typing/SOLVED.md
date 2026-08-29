---
problem: causation_has_no_force_dynamic_typing
status: SOLVED
bar: "CI-separated 3-way accuracy over BOTH the placeholder AND precedence-only (gated on the placeholder's upper CI, on the gold's own population) across: Set A -- CAUSE/ENABLE/PREVENT connective-neutral minimal pairs; Set B -- causal vs merely-sequential; Set C -- the PREVENT KILLER (the endstate never happens ... requires a small NEGATION/polarity detector IN SCOPE). The info-free twin (shuffled verb force-classes) LOSES CI-separated; report CI half-width + shuffle-null p95; no number crosses populations."
result: "force-dynamic 3-way+sequential typing accuracy 0.929 [0.833,1.000] (bootstrap, half-width 0.083; exact CAUSE/ENABLE/PREVENT/SEQUENTIAL match; n=42 pooled = Set A 24 + Set C 10 + Set B 8; connective-neutral constructed minimal pairs, extraction GIVEN). Set A 0.958, Set C (PREVENT killer) 0.900 vs placeholder 0.000, CAUSE-vs-ENABLE verb isolation 1.000."
floor: "the connective/adjacency PLACEHOLDER 0.190 [0.071,0.310] AND precedence-only 0.190 [0.071,0.310] (both type-blind -> majority), recomputed on this population; frequency-matched random-label 0.293. FD lower CI 0.833 > every floor upper CI. Robustness floor: pure-FrameNet-only lexicon (backoff dropped) 0.738 [0.595,0.857] STILL beats the placeholder CI-separated."
controls: "(1) force-class-SHUFFLE info-free twin: mean 0.383, p95 0.500, LOSES (FD lo 0.833 > p95) -> excludes riding connective/order leakage. (2) CAUSE-vs-ENABLE verb ISOLATION (endstate held constant, both reached): FD 1.000 vs verb-shuffle twin p95 0.500 -> excludes the endstate-polarity confound, isolates the verb-force contribution. (3) PRECEDENCE-ONLY (TIME organ alone -> direction not type -> majority): beaten CI-sep -> force dynamics adds the entire type signal. (4) frequency-matched RANDOM-label 0.293: beaten. (5) pure-FrameNet robustness (drop the narrative backoff): win survives -> not a backoff artifact."
files_changed: "experiments/_force_dynamics_lexicon.py, experiments/exp_causal_force_dynamic_typer_v1.py, experiments/exp_causal_force_lexicon_coverage_v1.py, verification/test_causal_force_dynamic_typing.py, notes/problems/causation_has_no_force_dynamic_typing/research_force_dynamics_brain_mechanism_2026-08-29.md, data/force_dynamics_lexicon_v1/lexicon.json (cache)"
reverify: ".venv/Scripts/python.exe verification/test_causal_force_dynamic_typing.py   # scaffold-free, 12/12 PASS, recomputes every headline from source"
---

# SOLVED — a force-dynamic CAUSE/ENABLE/PREVENT causal typer, with the brain-faithful bound measured

## What I built (brain mechanism first)
The opening move was the brain's: Talmy (1988) / Wolff (2007) **force dynamics** — CAUSE / ENABLE /
PREVENT fall out of a small DISCRETE truth-table over three dimensions: (1) does the PATIENT tend toward
the endstate on its own, (2) do affector & patient forces CONCUR or OPPOSE, (3) is the endstate REACHED?
`CAUSE = (no, oppose, yes); ENABLE = (yes, concur, yes); PREVENT = (yes, oppose, NO endstate)`. I copied
that COMPUTATION exactly and swept the PARAMETERS (lexicon coverage, frame inclusion) the brief names.

Three glass-box components (no LLM at inference), mirroring the substrate's `_causal_network` /
`_temporal_ordering` module style:
1. **An EXTERNAL force lexicon** (`experiments/_force_dynamics_lexicon.py`, 415 verbs) derived by
   **FrameNet Causation-family frame membership** — Causation + the Cause_* family -> CAUSE; the letting
   lexical units {allow, enable, let, permit} -> ENABLE; Preventing_or_letting(prevent-sense) + Thwarting
   + Hindering + Halt -> PREVENT. The ONE principled hand-split is the ENABLE-vs-PREVENT lexical units of
   the frame FrameNet conflates. **This is the point: the class assignment PREDATES the test gold, so a
   high score is generalisation of the frame->class map, not memorisation** — the trap the de-risk probe
   (verbs == lexicon) could not escape. A tiny principled backoff fills prototypical narrative force verbs
   FrameNet genuinely lacks (shatter/topple/ignite/shield/release; deter/curb/stall).
2. **The Wolff truth-table typer** (`force_dynamic_type`): (verb-class, endstate) -> type.
3. **An endstate/negation polarity detector** (`detect_endstate_reached`) — the component the brief puts
   in scope. Endstate is read from the narrative OUTCOME clause (default reached; flipped by a
   negation/failure cue), **NOT from the verb**, so endstate stays an INDEPENDENT text signal. This is
   what makes the CAUSE-vs-ENABLE isolation (both reached) a clean discriminator instead of the
   endstate-riding confound the probe flagged.

## What I measured
**The typer clears the bar** (`exp_causal_force_dynamic_typer_v1.py`, witness 12/12): pooled 3-way+seq
accuracy **0.929 [0.833,1.000]** vs the connective/adjacency PLACEHOLDER **0.190** and PRECEDENCE-ONLY
**0.190** (both beaten CI-separated on the floor's upper CI), force-class-shuffle info-free twin 0.383
(p95 0.500, LOSES), frequency-matched random 0.293. The two sharpest controls:
- **PREVENT KILLER (Set C, outcome never happens): FD 0.900 vs placeholder 0.000.** The placeholder LINKS
  cause->outcome; a prevented outcome has no node to link, so it asserts a wrong positive causal link.
  Only force dynamics represents a prevented (counterfactual) endstate — brain-faithful (Wolff, Barbey &
  Hausknecht 2010 "For want of a nail": comprehenders represent never-realised virtual forces; Kaup et
  al. negation-as-simulation).
- **CAUSE-vs-ENABLE verb ISOLATION (endstate constant): FD 1.000 vs verb-shuffle twin p95 0.500.** With
  the endstate held equal, only the verb's force class separates CAUSE from ENABLE; the twin collapses to
  chance, so the lift is genuinely the force-dynamic verb semantics, not endstate polarity riding along.
- **Robustness:** drop the backoff entirely (pure FrameNet) and the win SURVIVES CI-separated (0.738 vs
  0.190) — it is not a hand-added-verb artifact; the backoff adds ~0.19 by covering force verbs FrameNet
  lacks.

**The measured brain-faithful BOUND** (`exp_causal_force_lexicon_coverage_v1.py`) — this is the real
research content, and it answers the owner's "if you hit a wall, understand WHY":
- **The CAUSE-vs-ENABLE TENDENCY-AMBIGUITY WALL.** Wolff's CAUSE-vs-ENABLE turns on whether the PATIENT
  tends toward the endstate — which for many verbs is NOT lexicalised: "the key **opened** the gate"
  (tends -> ENABLE) vs "the wind **opened** the gate" (does not tend -> CAUSE), same verb. On 16
  minimal pairs of covered tendency-ambiguous verbs (move/turn/roll/slide/drop/raise/lift/drive, all
  fixed CAUSE) where only patient disposition flips the type, the verb-lexicon typer is capped at
  **0.500** vs a tendency-oracle **1.000** (gap 0.500). **This is not an implementation bug — it is a
  world-knowledge input the verb does not carry.** The brain reads patient tendency from
  perception/knowledge (Wolff & Song 2003), and the distinction is partly linguistically CONSTRUCTED, not
  a stable lexical representation (Kuhnmuench & Beller 2005). Converging disk evidence: ENABLE is barely
  lexicalised (of 391 non-gold lexicon verbs, exactly **1** is ENABLE). The FIX is a
  patient-disposition/world-knowledge input (adjacent follow-on), not a bigger lexicon.
- **Real-narrative coverage (208 McGuffey causal relations).** A frame-covered verb appears in 67% of
  relations, but that is POLYSEMY-INFLATED by light verbs (do/give/take/see/make in a Cause_* frame in
  some sense); honest distinct-verb coverage is **14.5%**, and most narrative causation is a CONNECTIVE
  linking two event clauses (the Trabasso NETWORK level), not a single transitive force verb. So the verb
  lexicon TYPES the single-force-verb clause relations (a bounded subset) and LABELS network edges; it
  needs verb-sense disambiguation for precision on real text.

## What I did NOT establish (and would withdraw first if wrong)
- **Real-text end-to-end 3-way ACCURACY.** The typer score is on CONSTRUCTED connective-neutral minimal
  pairs with extraction GIVEN (as the SPACE/TIME construction golds isolate their mechanism). The near-0.9
  reflects idealised (agent, verb, patient) extraction on verbs the lexicon covers. The controls rule out
  a hollow construction proof (twin loses, precedence loses, PREVENT killer, pure-FrameNet survives), but
  they do NOT substitute for a hand-labelled real-prose accuracy — **the #1 follow-on** (same honest gap
  the parent discourse-fact problem left). The coverage cell is the realistic bound on where it applies.
- **The tendency-ambiguous CAUSE-vs-ENABLE cases** — I claim the typer ONLY where tendency is lexically
  fixed (PREVENT/Thwarting/Hindering always oppose; prototypical CAUSE verbs where the patient does not
  tend). I do NOT claim CAUSE-vs-ENABLE for open/move/turn — that is the measured 0.50 wall.
- The endstate detector is a keyword negation/failure detector; it misses positive-surface prevention
  descriptions ("the dog stayed in" for a would-be escape) — the one Set C miss — which needs the same
  patient-tendency world-knowledge as the wall (a unifying limitation).

## KEY REALIZATIONS (the enabling moves)
1. **Derive the lexicon from an EXTERNAL resource (FrameNet), then choose the gold verbs.** The probe
   scored 1.000 because its gold verbs WERE its lexicon (a construction proof). Building the frame->class
   map first, and only then writing gold, converts "1.0 by construction" into a real generalisation claim
   — and the pure-FrameNet robustness row proves the win isn't the hand-added verbs.
2. **Read the endstate from the OUTCOME clause, not the verb.** This is what makes the CAUSE-vs-ENABLE
   isolation honest: with endstate independent, the verb-shuffle twin must drop to chance (0.500), which
   it does. The probe's own caveat (twin 0.81 on full 3-way because endstate alone identifies PREVENT) is
   exactly the confound this design removes.
3. **The shared wall across CAUSE-vs-ENABLE and the "stayed in" negation miss is ONE thing: patient
   tendency is world-knowledge.** Following the owner's "a shared wall is a signal to go deeper," the two
   apparently separate failures are the same fidelity gap — the brain's force vectors come from
   perception/knowledge (Wolff & Song), and a verb lexicon structurally cannot supply that. Naming it
   once turns two "misses" into one measured, brain-explained bound with a concrete fix.
4. **PREVENT is the sharpest win precisely because it needs a never-happened node.** The placeholder's
   own docstring ("links cause->outcome") is why it scores 0.000 on Set C: there is no outcome to link.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **NEW situation-model CAUSATION organ (force-dynamic typer).** Was: connective + most-recent-adjacency
  PLACEHOLDER (order-agnostic, cannot type, cannot represent a prevented endstate — its own VET caveat).
  Now: a glass-box Wolff/Talmy CAUSE/ENABLE/PREVENT typer over a FrameNet-derived force lexicon + an
  endstate/negation detector, CI-separated over the placeholder AND precedence-only, twin loses. The
  **computation is PINNED** (Wolff force-dynamic truth-table); the **verb LEXICON and the CAUSE-vs-ENABLE
  patient-tendency input are OUR-INVENTION-UNDER-TEST / a measured bound** (verb-lexicon-only is a
  principled wall for tendency-ambiguous verbs).
- **CITATION CORRECTION (propagate to PROBLEM.md §3, the scoping doc, and the probe):** "Kang et al.
  2021" is a **misattribution**. The real meta-analysis is **Feng, Wang, Liu, Wang, Tian & Fan (2021),
  Front. Hum. Neurosci. 15:666179** (L-IFG + L-MTG + bilateral mPFC) — and it localises DISCOURSE causal
  inference generally; it does **not** dissociate CAUSE/ENABLE/PREVENT. Soften any claim that a
  meta-analysis localises the force-dynamic typer. (Full basis in the research note.)

## Adjacent components — brain-fidelity + optimization potential (seeds for next problems)
1. **Patient-disposition / world-knowledge input for CAUSE-vs-ENABLE (HIGH leverage, PINNED gap).** The
   0.50 wall's fix. Brain-faithful mechanism: force vectors from perception/knowledge set patient
   tendency. The substrate has candidate seeds — the `verbnet_affectedness_lexicon_v1` (Dowty/Beavers
   proto-patient affectedness, a change-of-state prior) and the grounding assets. A "does the patient tend
   toward this endstate?" typed input would lift CAUSE-vs-ENABLE off its lexical cap. Currently ABSENT.
2. **Glass-box VERB-SENSE DISAMBIGUATION (already a filed problem: `no_glass_box_verb_sense_disambiguation`).**
   The measured precision bound: broad Cause_* frames over-admit light verbs (do/give/take/see), so
   distinct-verb coverage is high-recall/low-precision (14.5% honest vs 67% inflated). A sense gate on
   the lexicon is exactly what real-text precision needs — this problem gives it a concrete consumer.
3. **CLAUSE-level force dynamics vs DISCOURSE-level causal NETWORK (Trabasso).** Most narrative causation
   is connective-linked clause pairs, not single force verbs. Force dynamics LABELS network edges; the
   live `_causal_network` builds the (untyped) network. Composing the two — force-dynamic TYPES on the
   Trabasso network edges — is the natural next integration (the PROBLEM.md §3 "OUR-SYNTHESIS" is
   unbuilt). PINNED at each level, the composition is our synthesis.

## What strategy would change in hdlab/ (Q111 — I propose, do not land)
Promote `_force_dynamics_lexicon.py` (lexicon + typer + endstate detector) into hdlab as the CAUSATION
dimension's typer, and replace `situation_reader._read_causation`'s "link + method tag" with a TYPED
`CausalLink(cause, outcome, force_type in {CAUSE,ENABLE,PREVENT}, endstate_reached)`. Gate CAUSE-vs-ENABLE
emission by tendency-confidence (emit ENABLE only for lexically-fixed letting verbs; abstain-to-CAUSE for
tendency-ambiguous verbs until the patient-disposition input (adjacent #1) exists). Keep precedence as the
DIRECTION gate (reuse the TIME register), force dynamics as the TYPER, plausibility as validation. Do NOT
land it as a coverage-complete real-text organ — land the mechanism + the measured bounds, wired for the
downstream consumers (why-questions, ToM/blame, event segmentation), and file adjacent #1 as the lift.

## TLDR
Our reader could not tell apart three kinds of causation — the rain that CAUSED a flood, the open gate
that merely LET it happen, and the sandbags that PREVENTED it (where the flood never happened at all). I
built the brain's way of doing this: force dynamics (a tiny fixed rule over "did the thing tend to happen
on its own, did the forces push together or against, did it actually happen"), reading each verb's force
from an external dictionary (FrameNet) and reading whether the outcome happened from the sentence. It
tells the three apart 93% of the time on clean test cases versus 19% for the current placeholder, and it
correctly represents a prevented, never-happened outcome that the placeholder cannot represent at all
(90% vs 0%). Every fairness check passes (a shuffled-meaning twin drops to chance). The honest limit I
measured and understand: the CAUSE-vs-ENABLE difference sometimes lives not in the verb but in whether
the THING tends to happen on its own ("the key opened the gate" vs "the wind opened the gate"), which is
world-knowledge the dictionary can't carry — the brain reads it from the situation, and building that
input is the clear next step.

## QUESTIONS
None. (The mechanism is built and clears the bar; the tendency-ambiguity wall is a measured
brain-faithful bound with a named fix, not an open question.)

## NEXT STEPS
1. **Real-prose accuracy serve** — hand-adjudicate ~20 real narrative force-verb sentences and run the
   full pipeline (extraction + endstate detection + typing); the #1 unestablished number.
2. **File the patient-disposition/world-knowledge input** as the follow-on that lifts the CAUSE-vs-ENABLE
   0.50 wall (adjacent #1; seed from the affectedness lexicon / grounding).
3. **Compose force-dynamic types onto the Trabasso causal-network edges** (adjacent #3) so the typer
   labels the discourse-level network, not just single clauses.
4. Strategy: land the typer in hdlab (proposal above), reusing the TIME precedence gate; propagate the
   Feng-et-al. citation correction into PROBLEM.md/the scoping doc/the probe.
