---
problem: no_glass_box_verb_sense_disambiguation
status: PARTIAL
bar: "PASSES only with ALL of: 1. A glass-box sense/frame disambiguator over the dependency parse for AT LEAST the two dominant confusions (motion-vs-transitive-deposit; perception-vs-speech). 2. Beats a most-frequent-sense floor CI-separated on a real WSD gold (recompute the floor on the same population); an info-free twin LOSES CI-separated; report CI half-width + null p95; a positive control the metric can move (a context-flipped minimal pair the disambiguator gets and MFS cannot). 3. Lifts a downstream front-end CI-separated vs the un-disambiguated path. 4. One-screen summary. A rigorous NEGATIVE is a full pass (the downstream lift alone passes)."
result: "BUILT the glass-box event-frame disambiguator (bar 1, met; witness 9/9; minimal-pair positive control 6/6) AND its 3 brain-foundational optimizations. WINNER = both foundations ON (stored-unit IDIOM lexicon + sense-keyed selectional-preference FIT cue). Bar 2 STILL NOT met: on every real WSD gold the winner TIES or LOSES per-lemma MFS -- SemCor coarse event-frame DISAMBIG 0.812 [0.801,0.823] vs MFS 0.811 [0.800,0.822] (n=4544, a tie; but the BLIND diagnostic subpop now BEATS MFS 0.548 vs 0.529, up from a pre-foundation 0.35 taxonomy-mismatch LOSS); binary motion confusion 0.691 vs per-lemma MFS 0.707 (n=191, curated); binary perception/speech 0.809 vs 0.846 (n=162). On the curated confusion verbs the winner BEATS the info-free twin (0.691 vs 0.628; 0.809 vs 0.747) and the un-disambiguated front-end (0.607/0.685). Bar 3: the ToM-ledger motion gate is correct + never-harmful and PROVEN on a polysemy positive control (BASELINE 0.500 -> GATED 1.000, McNemar p=0.0005, 12/12 false departures suppressed) but is NOT exercised by the shipped ToM golds (motion-sense polysemy present in only 2/49 intact, 0/76 corpus clauses)."
floor: "STRONGEST floor = per-lemma most-frequent-sense, recomputed per population: coarse-frame 0.811 [0.800,0.822]; binary motion 0.707 [0.644,0.770]; binary perception/speech 0.846 [0.784,0.895]. Un-disambiguated FRONT-END floor: ledger-always-motion 0.586-0.607; raw-ccomp cue 0.685. The winner beats the front-end + the info-free twin (paired) but NOT the per-lemma MFS floor on any full population."
controls: "3-ROUTE BAKEOFF (exp_frame_sense_bakeoff_v1): BASE < +IDIOM ~ +FIT < +BOTH on all four confusion populations (each foundation adds a real increment; +BOTH is the winner). INFO-FREE TWIN (shuffled construction->frame map, same gate): loses to +BOTH on the CURATED confusion verbs (mapping load-bearing) but ties/beats it on the AUTO over-inclusive pops (taxonomy mismatch on non-confusion verbs). ToM POLYSEMY POSITIVE CONTROL: injected non-motion departure verbs -> BASELINE 0.500, GATED 1.000 (proves the downstream gate works + keeps genuine motion). JOINT-vs-TYPED ablation: no material difference. CONSERVATIVE-DEFER: bare 'He left.' -> MFS. CCOMP-complementizer: 'made him go' is NOT a propositional complement."
files_changed: "experiments/frame_sense_disambiguator.py; experiments/idiom_gate.py; experiments/sense_selprefs.py; experiments/exp_frame_sense_semcor_v1.py; experiments/exp_frame_sense_wic_v1.py; experiments/exp_frame_sense_serves_motion_cue_v1.py; experiments/exp_frame_sense_confusion_pairs_v1.py; experiments/exp_frame_sense_serves_tom_ledger_v1.py; experiments/exp_frame_sense_bakeoff_v1.py; verification/test_frame_sense_disambiguator.py; data/idiom_foundation_v1/idioms.json; data/sense_selprefs_v1/table.json; notes/problems/no_glass_box_verb_sense_disambiguation/{BRAIN_MECHANISM_SPEC.md,SOLVED.md,research_brain_foundational_verb_sense_2026-08-28.md}. NO hdlab/ writes (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_frame_sense_disambiguator.py  (-> 9/9); then experiments/exp_frame_sense_bakeoff_v1.py (-> +BOTH is the best DISAMBIG on all 4 pops, still < per-lemma MFS); experiments/exp_frame_sense_serves_tom_ledger_v1.py (-> gate correct + proven on the polysemy control, null on the shipped ToM golds)."
---

# PARTIAL: a brain-faithful disambiguator + 3 foundations that help but cannot beat most-frequent-sense

## What I built (bar 1, met)

`experiments/frame_sense_disambiguator.py` -- a glass-box verb-sense / **event-FRAME** disambiguator over the
spaCy dependency parse (no LLM at inference), copying the brain's PINNED computation (research-verified,
2026-08-28): frequency **prior** (reordered access; Duffy/Morris/Rayner) + a near-categorical argument-structure
**CONSTRUCTION** cue (Goldberg; Levin 1993) + graded **thematic fit**, combined through the substrate's own
`hdlab.graded_competition`. Witness 9/9; minimal-pair positive control 6/6 (the two confusions MFS cannot flip).
It implements every research recommendation: JOINT (verb,noun)-sense co-selection, a homonym/polysemy grain gate,
the three missing construction rules (light-verb, double-object, resultative), the "that"-complementizer test, a
CONSERVATIVE underspecification default, and pronoun-object deferral (the coref seam).

## The three brain-foundational optimizations I then tried (owner-directed "try it all, pick the winner")

1. **IDIOM stored-unit lexicon** (`experiments/idiom_gate.py` + `data/idiom_foundation_v1/`, 1813 phrasal + 414
   verb+object entries, offline, glass-box). Brain rationale: the mental lexicon stores non-compositional MWEs as
   UNITS and retrieves them holistically before literal composition (Jackendoff's construction lexicon; Cutting &
   Bock 1997). Retrieves "pass away"->die, "pass a law"->social, "make sense"->cognition, "go off"->change,
   suppressing the false LITERAL reading -- the world-knowledge residual that capped the construction cue.
2. **Sense-keyed selectional-preference FIT cue** (`experiments/sense_selprefs.py` + `data/sense_selprefs_v1/`,
   15 frames x 26 supersenses, offline from SemCor). A data-driven thematic-fit cue INDEPENDENT of the
   construction rules -> moves the additive->softmax combination toward a true Bayesian posterior (the calibration
   gap the research flagged). Weight 0.4 (a secondary tie-breaker; the construction stays the categorical cue).
3. **ToM-ledger motion GATE** (`experiments/exp_frame_sense_serves_tom_ledger_v1.py`). Gates the ledger's
   `_motion_signal` with the disambiguator to suppress false departures ("left a note" != "left the room").

## What the bakeoff found (the winner + the wall)

**Winner = both foundations ON (+BOTH).** It is the best DISAMBIG on all four confusion populations
(motion-curated 0.639->**0.691**, motion-auto 0.706->0.728, prop-curated 0.802->0.809, prop-auto 0.807->0.822),
each foundation adding a real increment (idiom helps motion; fit helps perception/speech). It BEATS the info-free
twin and the un-disambiguated front-end on the curated confusion verbs, and it flipped the coarse-frame
**diagnostic subpopulation** from a pre-foundation LOSS (0.35 vs 0.49, taxonomy mismatch) to a WIN over MFS (0.548
vs 0.529) -- i.e. where the mechanism now commits, it is more accurate than the frequency prior.

**But the wall holds:** even the winner **ties or loses to per-lemma most-frequent-sense** on every FULL
population (coarse-frame 0.812 vs 0.811; binary motion 0.691 vs 0.707; binary prop 0.809 vs 0.846), never
CI-separated. Bar 2 is a rigorous NEGATIVE. **Route 3 (the ToM gate) is correct and never-harmful and PROVEN on a
polysemy positive control (0.500->1.000, 12/12 false departures fixed), but the shipped ToM golds contain almost
no motion-sense polysemy at the cue clause (2/49 intact, 0/76 corpus), so it is a harmless, rarely-exercised
safety check, not a measurable lift on those golds** -- a population property, not a ceiling.

## Why -- the finding (brain-grounded, now with all levers pulled)

Three orthogonal reasons, each drilled: (1) **TAXONOMY MISMATCH** -- WordNet lexname is a semantic-field taxonomy
that fights the event-frame ("leave behind"=cognition, "elapsed time"=motion, "put"=contact); this is why the
prior `entity_typing` SemCor test nulled, and the foundations only partly repair it (the diagnostic-subpop flip).
(2) **GRAIN MISMATCH** -- WiC's sense grain is orthogonal to event-frames. (3) **MFS + WORLD-KNOWLEDGE is the wall**
-- per-lemma frequency (0.71-0.91) captures the dominant-sense skew that IS most of verb-sense; the construction
cue is low-coverage, the idiom lexicon closes part of the world-knowledge residual (measured: +0.02-0.05) but not
all of it (open-class idioms + discourse remain), and the no-LLM invariant precludes the full lexical-semantic
knowledge the brain uses. **The reframe stands: a front-end disambiguator should be scored on the downstream task,
not a WSD benchmark; there the mechanism is correct and non-harmful, and the idiom foundation is the highest-value
brain-foundational lever.**

## What I did NOT establish / would withdraw first

- Bar 2 (beat MFS CI-separated) is unmet even after all three optimizations -- the robust negative. Withdraw first
  if wrong: the diagnostic-subpop win over MFS (0.548 vs 0.529) is directional, not CI-separated (n=157).
- Bar 3's lift is proven only on an INJECTED polysemy control, not on a natural gold with attested motion-verb
  polysemy at the cue clause (the shipped ToM golds lack it). I refuse to claim a natural-gold ToM lift.

## KEY REALIZATIONS (the enabling moves)

1. **The gold's taxonomy was fighting the mechanism** -- reading WordNet lexnames for the target verbs proved
   SemCor-lexname is the wrong instrument and explained a prior landed null.
2. **A general construction cue applied to every verb HURTS** (-0.03); VERB-SENSITIVITY + a CONSERVATIVE default
   turned "worse than MFS" into "ties MFS".
3. **The idiom foundation is a stored-unit RETRIEVAL, not a rule** -- holistic MWE access (brain-faithful) is what
   flipped the diagnostic subpop from a taxonomy-mismatch loss to a win, and it fixes false departures downstream.
4. **A pronoun object is the coreference seam** -- not typing "it/him" removed a measured real-prose error class.
5. **MFS is the finding, not an embarrassment** -- the brain's edge here is world knowledge the invariant forbids;
   I pulled every brain-foundational lever (construction + stored idioms + independent selectional fit) and MFS
   still wins on the full population, which is the precise, defensible reason this is a PARTIAL not a PASS.

## AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md)

The **verb-polysemy** wall now has a measured verdict + two new offline foundations. PINNED: reordered-access +
construction + thematic-fit + graded-competition is the mainstream account (research-verified). New deviation:
the additive->softmax combination is "structurally isomorphic to, not proven equal to" a Bayesian posterior
(McClelland 2013 needs calibrated log-likelihoods + conditional independence); the sense-keyed FIT cue is a step
toward independence. Recommendation: do NOT wire a WSD organ; the measured value is (a) the IDIOM stored-unit
lexicon (a reusable glass-box FOUNDATION -- flags non-compositional MWEs for ANY front-end) and (b) a
CONSERVATIVE ledger gate that removes false departures (proven on a control, harmless on real golds).

## Proposed hdlab change (strategy lands; I did not write hdlab/)

Do NOT promote a WSD organ. Two optional, default-OFF, brain-foundational pieces worth landing: (i) the IDIOM
stored-unit lexicon (`experiments/idiom_gate.py` + asset) as a shared MWE-flagging FOUNDATION; (ii) the
`strong_construction` + `disambiguate_token(conservative=True)` gate consulted by
`perceptual_access_ledger._motion_signal` to suppress non-motion departures. Both are precision-oriented and
proven non-harmful; neither is a capability win; measure on the live reader before any claim. Keep the no-LLM invariant.

## Adjacent bottlenecks (mapped follow-ons)

- **Coreference (~0.65)** -- typing pronoun/anaphoric objects + the caused-motion "to X" head. Owned by the coref brief.
- **An open-class idiom / world-knowledge FOUNDATION** -- the idiom lexicon closes phrasal + institutional MWEs;
  the open tail (novel metaphor, discourse-dependent readings) is the residual true ceiling. Candidate new problem:
  a larger glass-box collocation/idiom asset mined at scale (still offline, invariant-compatible).
- **A construction-labeled + attested-polysemy gold** -- to score bar 2/3 on the mechanism's own taxonomy/domain.

## TLDR / QUESTIONS / NEXT STEPS

**TLDR (plain language):** "Left the room" (walked out) vs "left a note" (put it down) -- I built a glass-box reader
that tells these apart from grammar, and then, on your instruction, added two brain-inspired upgrades and tested a
third: a small dictionary of stored idioms ("pass a law" = governing, not moving), a data-learned "does this object
fit this meaning" table, and a hook into the mind-reading module. All three help a little and the combination is the
best version -- and it now beats a shuffled-information control and the old un-checked front-end. But it still cannot
beat the dumb rule "always guess the word's commonest meaning," because that rule is already right most of the time
and the exceptions mostly need real-world knowledge our no-outside-AI rule forbids. The idiom dictionary is the most
valuable piece and is worth keeping. Honest verdict: a faithful, improved mechanism; a real but small win; and a
precise reason it can't clear the top bar.

**QUESTIONS:** one judgement call: land the idiom foundation + the harmless ledger gate now (recommended), and open
the open-class world-knowledge asset as a separate brief?

**NEXT STEPS:** (1) land the two optional default-off pieces (idiom lexicon; ledger gate) and measure on the live
reader; (2) open the open-class idiom/world-knowledge FOUNDATION brief -- that, not a cleverer grammar cue, is the
only route left to beat MFS; (3) route pronoun/anaphoric objects to coreference; (4) build a construction-labeled +
attested-polysemy gold to score the mechanism on its own taxonomy/domain.
