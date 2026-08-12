# PRE-REGISTRATION -- exp_context_conditioned_sense_selection_v1

Filed 2026-08-12 BEFORE any accuracy number exists. Basis:
`notes/wire_reader_to_meaning_organs_2026-08-12.md`,
`notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md`,
`notes/context_conditioned_sense_selection_2026-08-12.md` (step 0-2, commit c8e0bf02d).

## THE QUESTION
Given a CONTEXT, can the substrate select the RIGHT sense of a word that has several?
This is a capability a flat single-pair store cannot have AT ALL (not "has badly"): a flat
store has no context input, so its best possible strategy is a fixed choice per word.

## EVAL SET (fixed before running)
The 288 multi-sense subjects in
`data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl`
(MEASURED: 1751 facts, 1316 distinct subjects, 288 with >1 distinct object, 723 facts
involved, mean k 2.5104, k-dist {2:187,3:77,4:12,5:7,6:3,7:1,10:1}).
One TRIAL = (subject W, true object O_i, one source sentence H of that fact).
EXCLUDED before scoring, counted and reported: trials whose sentence H is a source sentence
of >1 sense of the same W (label-ambiguous; affects 4 words).

## PRIMARY METRIC AND ITS FLOOR
SUBJECT-WEIGHTED accuracy: accuracy computed per word over that word's trials, then averaged
over the 288 words. Chosen so the random-pick floor is EXACTLY the pre-registered
**mean(1/k) = 0.4316** (independently recomputed, matches 035a3acc5).
Secondary, reported with its own different floor: per-trial MICRO accuracy, whose random
floor is 288/723 = 0.3983 (high-k words carry more trials). The two floors are NOT
interchangeable and each number is reported against its own.
The analytic floor is additionally CHECKED by an empirical random-pick simulation
(1000 seeds); a mismatch is a harness bug and blocks the run.

## SELECTORS (both already-owned; no promotion required)
Both receive ONLY (masked context tokens, candidate object strings). Both are bag-of-words
aggregates; argmax over candidates; ties broken deterministically by sorted order.
- **S1 DIST**: `hdlab/random_indexing.RandomIndexingEncoder(N=8192, sparsity=10, window=5,
  min_count=3, seed=0)` fit on the v3 corpus MINUS every eval sentence.
  score(O_i | H) = mean over covered context tokens c of cos(enc(c), enc(O_i)).
  min_count=3 declared here, chosen on COVERAGE (not on outcome) before any accuracy was seen.
- **S2 PERC**: raw uncapped 12-dim Lancaster+Brysbaert profile cosine
  (`hdlab/grounded_similarity` table), same aggregation. RANKING ONLY -- no link/same-idea
  decision is ever emitted, which is the sole thing `GROUNDED_CAP=0.45` exists to prevent.
- **S3 COMBO** (secondary): mean of S1 and S2 per-candidate ranks.
A trial is UNSCORABLE for a selector if that selector covers <2 of the word's candidates or
0 context tokens. Unscorable trials are reported separately and NOT counted as correct.

## LEAKAGE PREVENTION -- exactly how it is enforced
This is the failure that invalidated the earlier foundation-validation harness (target
selected by same-sentence cosine, then tested for co-occurrence in that same sentence).
Three mechanisms, each machine-asserted in the cell; a failed assert aborts the run.
- **L1 -- the sense side never sees H.** The RI encoder is fit on `load_corpus()` with the
  exact string of EVERY eval sentence removed from the token stream. So no eval sentence
  contributes a single co-occurrence count to any word vector. ASSERT: intersection of
  {eval sentences} with {fit sentences} is empty; the removed count is reported.
  For S2 the property is structural: the Lancaster/Brysbaert asset is a static
  word->rating table containing no sentence from this corpus at all.
- **L2 -- the answer is not lexically present in the query.** From H, every token of EVERY
  candidate object of W, every candidate's `definiens_surface`, the subject W, and
  `definiendum_surface` are removed (case-insensitive, token-level). Masking is applied to
  ALL k candidates symmetrically, so the masking pattern itself cannot reveal which is
  correct. ASSERT: no candidate object string survives in the masked token list.
- **L3 -- no extractor metadata reaches the selector.** `pmi`, `pattern`, `patterns_seen`,
  `n_attestations`, `segment`, `fid` are never passed to the scoring function; the scorer's
  signature takes only (tokens, candidates).

## CONTROLS -- each must be able to fail
- **C1 CROSS-ITEM CONTEXT SWAP** (the scramble that can actually fail): replace H with a
  source sentence belonging to a DIFFERENT subject, keeping the true label. Preserves
  sentence-level surface statistics (real sentence, real length, real vocabulary) and
  destroys only the context-to-sense relation. FAILS THE CELL if accuracy does not drop:
  that would mean the lift is not coming from the context.
- **C2 CONTEXT LESION**: empty context token list, same code path, same argmax, same
  deterministic tie-break -- NOT a hard-coded random return. It therefore measures any
  CANDIDATE-SIDE bias (sorted-order preference, profile-magnitude preference, a systematic
  correlation between "first-listed object" and "correct"). It CAN come out above floor, and
  if it does, that bias inflates the primary and the primary is discounted by it.
- **C3 SAME-SENSE-DIFFERENT-SENTENCE POSITIVE CONTROL** (strict leave-one-sentence-out):
  restricted to the 102 facts with >=2 source sentences. The sense-side representation is
  built from that sense's OTHER sentences only, and tested on the held-out one. This is the
  one arm whose sense representation is genuinely CONTEXT-derived, and it is leakage-proof by
  construction. Underpowered (102 facts / ~83 words) and reported as such.

### CONTROL REMOVED BECAUSE IT CANNOT FAIL BY CONSTRUCTION -- named as required
**WORD-ORDER SCRAMBLE of H is REMOVED.** Both selectors are bag-of-words aggregates over the
context tokens, so permuting token order leaves every score bit-identical. It would print a
number equal to the primary to the last decimal and prove nothing. C1 (cross-item swap)
replaces it and destroys the same relationship for real.
Also NOT counted as a control: the random-pick floor (0.4316) -- it is an analytic baseline,
not a manipulation of the system.

## PRE-REGISTERED BANDS (primary = subject-weighted acc of the BEST selector)
Floor F = 0.4316.
- **HARD_FAIL / "context-conditioned sense selection does NOT work"** if ANY of:
  (i) acc <= F + 0.03 = 0.4616 for BOTH S1 and S2; OR
  (ii) the best selector's C1 cross-item-swap accuracy is not at least 0.05 BELOW its
       primary (lift is not context-borne); OR
  (iii) C2 lesion >= primary - 0.03 (a candidate-side bias, not context, explains it).
- **MIDDLE_BAND**: 0.4616 < acc <= 0.5500 with C1 drop >= 0.05.
- **PASS**: acc > 0.5500 AND C1 drop >= 0.08 AND C2 <= 0.4616.
- **HARD_PASS**: acc >= 0.6500 AND all controls clean AND C3 >= 0.70.

## WHAT RESULT MEANS IT DOES NOT WORK -- stated plainly, before running
If the best selector's subject-weighted accuracy sits at or within 0.03 of 0.4316, then given
a real context the substrate picks among a word's stored senses no better than tossing a coin
weighted by k. Equally, if accuracy is above floor but C1 (cross-item swap) does not drop, the
above-floor number is NOT context-conditioned selection -- it is a candidate-side prior (e.g.
one sense is simply more common) that a flat store already has. Either outcome is a real,
useful, reportable finding and is to be reported plainly as a null, not softened. The
architecture in PLAN_B has already met real prose once and failed there
(PLAN_B STATUS: "on REAL prose the teaching signal DOESN'T CARRY"), so a null here is the
prior-consistent outcome, not a surprise to be explained away.

## HONEST SCOPE CAPS (declared up front)
- Fit corpus is ~623K tokens (32,955 sentences). Small for distributional semantics
  (text8 = 17M). A null from S1 is a null about THIS corpus at THIS size.
- The "true sense" label is the v3 EXTRACTOR's output, which is itself noisy (the prior
  50-pair audit put ~35% meaningful / 25% related / 40% noise). Where the label is noise, no
  selector can be right, and this caps achievable accuracy by an unknown amount. The
  inseparable-tail analysis is where that cap is characterized, not explained away.
- Only 7 words support the strict LOO arm on every sense; C3 is a 102-fact check.

## RUNTIME
Local, single process, CPU. Expected < 15 min (RI fit over 623K tokens dominates).
Not a queue cell.
