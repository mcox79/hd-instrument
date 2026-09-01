# DEFINITIVE dissection of the MCScript2 before/after ~0.59 wall (2026-09-01)

Owner asked: research + dissect the wall to definitively find WHERE it is, so we can overcome it
brain-foundationally. This is the answer, from a brain literature drill + a decisive stratified re-scoring.

## The brain mechanism (literature drill, `research` 2026-09-01)
The brain answers "did X happen before or after Y?" for a JUST-READ narrative from the **online situation
model** -- iconicity-default (narrated order = chronological unless a cue says otherwise; Zwaan 1996) with a
script/schema fallback (Schank & Abelson) -- and this is **GATED BY EVENT-MENTION ALIGNMENT** (you must first
map the question's re-worded event onto the encoded event). It is NOT long-delay episodic retrieval, NOT
causal reasoning (already shown idle), NOT narrated-order reconstruction as the primary cost. Ranked wall
prediction: **alignment (P=0.40) > script/schema (P=0.30)**. (The note did not persist to disk -- the known
research-drill persistence gap -- but the headline is recorded here and in the task log.)

## The decisive experiment (`experiments/exp_order_wall_dissection_v1.py`, n=301 held-out dev+test)
Partition each questioned pair by whether the reader can LOCATE its two events in the passage, then (on the
locatable slice) whether NARRATED order equals the GOLD order. Score the situation-model+iconicity reader
(align both events by identity, answer by story position) per stratum.

| stratum | fraction | reader acc | reading |
|---|---|---|---|
| ALIGNED_EXPLICIT (both events matched by VERB-LEMMA identity) | **0.213** | **0.609** | reader can pinpoint both events |
| PARAPHRASED (content-overlap only, NO verb-lemma match) | **0.475** | 0.518 | ~chance -- cannot pinpoint the event |
| IMPLICIT (neither content nor lemma match -- not surface-present) | **0.312** | 0.521 | ~chance -- event not narrated |
| SIM floor | -- | 0.525 | |
| situation-model+iconicity reader E2E | -- | 0.538 | |
| MAX-ACHIEVABLE (perfect align + narrated position, guess on implicit) | -- | **0.532** | |

On the ALIGNED_EXPLICIT slice, **iconic 0.609 / non-iconic 0.391**: even when both events ARE locatable,
narrated position gives the gold answer only ~61% of the time.

## WHERE THE WALL IS (definitive)
**A. EVENT-MENTION ALIGNMENT is the DOMINANT wall = 79% of pairs.** 47.5% PARAPHRASED + 31.2% IMPLICIT: the
reader cannot even resolve WHICH two passage events the question is about, so on ~4 of 5 questions it is at
chance (0.52). Every ordering signal -- co-occurrence, narrated position, causal enablement, the operator DAG,
and the possession register -- sits DOWNSTREAM of this and is STARVED: you cannot order two events you cannot
locate. This is exactly why co-occurrence 0.591, enablement 0.568, the operator DAG, and possession ALL cap at
~0.59: they are all fed the same near-random alignment. The paraphrases are real and conceptual, not lexical
("ask for IDENTIFICATION" == "check his age/licence"; nominalizations "the ORDER" <-> "ORDERED"; cross-POS).

**B. NON-ICONICITY is the SECONDARY residual = ~8% of all pairs (39% of the aligned 21%).** Where the reader
CAN locate both events, narrated order still disagrees with gold 39% of the time -> these need order CUES
("then/after/before/earlier") or CHRONOLOGY / conventional-SCRIPT order, not alignment. This is the aligner's
already-filed order/schema problem, and it is why even PERFECT alignment tops out ~0.6 (0.61 measured on the
clean slice), not 1.0.

**C. CLEAN (aligned + iconic) = 13%** -- the situation-model reader gets these for free.

## The brain-foundational fix (in priority order, matching the drill)
1. **THE MEANING CHANNEL FOR EVENT IDENTITY (primary, the 79% gate).** Resolve a paraphrased question-event to
   its passage event by CONCEPTUAL similarity over the role-filler conjunction (verb + patient + path), the
   ATL hub-and-spoke: taxonomic/derivational for the verb (the aligner's prototype: WordNet-wup + derivational
   beats the grounded/sensorimotor kernel for event IDENTITY; grounded is for perceptual similarity, wrong
   spoke here), grounded as OOV fallback. This is the SAME "DECIDE WHAT WORDS MEAN" channel the substrate map
   flags BROKEN/unwired, and the north-star grounded-semantic-graph organ (per-context sense selection by
   spreading activation) is exactly the mechanism -- pointed at EVENT alignment, not word-sense. Biggest lever;
   the brain leads here.
2. **ORDER CUES + CONVENTIONAL-SCRIPT SCHEMA (secondary, the non-iconic 8% + the implicit slice).** Explicit
   order connectives (then/after/before/earlier) to undo non-iconic narration, and a conventional-script
   order source for events that are IMPLICIT (not narrated). This is the aligner's filed
   `learn_canonical_script_order_from_a_causal_enablement_foundation`.

## What this rules OUT (so we do not chase the wrong fix)
- NOT the ordering statistic (co-occurrence's symmetry is real but only bites the 13% clean slice).
- NOT causal enablement / world-state / possession (idle: ~99% causally independent; measured twice).
- NOT the transitive_ordering readout (it is fine on the clean slice).
The wall is UPSTREAM of every ordering mechanism: event-mention alignment (meaning), then the non-iconic/
implicit residual (cues + script schema). Fix the meaning channel for event identity FIRST.

## Reproduce
`.venv/Scripts/python.exe experiments/exp_order_wall_dissection_v1.py --mode full`
  -> strata fractions, per-stratum accuracy, iconicity on the aligned slice, and the WALL_DECOMPOSITION.
