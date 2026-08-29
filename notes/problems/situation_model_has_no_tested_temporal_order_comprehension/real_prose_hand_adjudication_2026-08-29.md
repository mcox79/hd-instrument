# Real-prose reorder hand-adjudication (2026-08-29)

Sample of 22 DIRECT-cue reorderings (a direct tense/connective edge, mechanism reverses narration
order) drawn from 25 LitBank novels, with the brain-faithful clause-pluperfect fix ON. For each, the
mechanism claims pair (a,b)-in-text-order is actually b-before-a. Adjudicated by reading full context.

## Verdicts
- **CLEAN narrative pluperfect flashback -> mechanism CORRECT (5):**
  - [12] "the clergyman explained that ... it had quite died out of knowledge" -> dying BEFORE explaining. CORRECT.
  - [15] "I took no notice ... thinking ... we had once kept two horses" -> keeping BEFORE taking-notice. CORRECT.
  - [16] "durbeyfield ... sat down ... the direction which had been pursued by durbeyfield" -> pursuing BEFORE sitting. CORRECT.
  - [21] "'Some one has died,' answered the boy officer. 'You did not say it had broken out ...'" -> breaking-out BEFORE answering. CORRECT.
  - [10] "it happened ... individuals who had found leisure to become aware" -> finding-leisure BEFORE the happening. CORRECT.
- **LEAN CORRECT (stative/simile pp, anteriority still right) (~3):** [11] "had gone so far", [18] "as if cannel coal had been heaped", [20] "an officer who had just come from England".
- **ILL-POSED / can't-verify (stative "had been" backstory, generic present, quoted registry text,
  truncated context, or an extraction mis-tag) (~14):** [0]-[9], [13], [14], [17], [19] -- Austen's dense
  expository character backstory ("lady elliot had been an excellent woman whose judgement and conduct ...")
  where the pp verbs sit in stative/relative/generic clauses and a narrative "before/after" is not well
  defined; [6] "scarcely any charm is lost" is present-tense (extraction over-reach); [17] "rash" is a
  tagger mis-tag as a verb.
- **CONFIDENT ERRORS: 0.** The one prior confident error (Persuasion "the paragraph had originally STOOD
  ... but sir walter had IMPROVED it", mechanism said improved-before-stood) is ELIMINATED by the
  clause-pluperfect fix -- it now ABSTAINS (both correctly typed anterior, no connective ordering them).

## Takeaways (for SOLVED.md)
1. Where the reordering is a DECIDABLE narrative event pair, the mechanism is correct (0/22 confident
   errors after the fix). The ORDERING LOGIC is sound on real prose given correct extraction -- consistent
   with the construction-gold 1.000.
2. The 8.7% real-prose reorder base rate OVER-COUNTS true flashbacks: a majority of fired reorderings are
   STATIVE / GENERIC / REPORTED past-perfect (backstory anteriority -- "had been", "had once kept"), which
   the pluperfect correctly marks as anterior but which are not narrative flashbacks. So "narration order is
   wrong on ~1 in 11 event pairs" is an UPPER bound on flashback incidence; the true narrative-flashback
   rate is lower (a chunk of the 8.7% is correct-but-not-a-flashback anteriority).
3. The real-prose PRECISION wall is TENSE EXTRACTION, not ordering logic: the fixed 3-token had-window
   mistags inverted/long-subject pluperfects; the brain-faithful clause-level aux->participle binder
   (promote_clause_pluperfect) recovers +31 pluperfests across 25 novels and converts the known
   confident-wrong to an abstain, with no construction-gold regression and no reorder-count blow-up
   (131->131, so not over-firing). Residual: a possession-"had" + coordination edge case
   ("had a book and read it") a full dependency parse would resolve -- a mapped follow-on.
