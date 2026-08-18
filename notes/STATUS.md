# STATUS

AS OF: 2026-08-18 | branch `dataprep/mcguffey-graded-corpus` | HEAD `7003df4c1` | GROWTH PAUSED | origin merge needs USER AUTH
Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). Cap 8704 B, OVER -- see
WHAT IS RUNNING. FOUR literals MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `## TOP ITEM`,
`## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` (**THE PLAN; READ SEC 6.18 FIRST -- it supersedes the
step hunt. 6.16 holds the PRE-COMMITTED decision branches; 6.15 the five gated steps**) ->
HERE -> `COMPACTION_HANDOFF_2026-08-17.md` -> `PLAN_NEXT_24H.md` -> `LONG_TERM_PLAN.md`.

## POSITION
**📐 WHY WE KEEP PRODUCING NEGATIVES -- NOW A NUMBER, NOT A COMPLAINT (Director, inline, 08-18).
THE ANSWER TO THE OWNER'S "why aren't we narrowing in on GOOD results?" IS PARTLY THAT OUR
INSTRUMENTS CANNOT SEE A WIN AT THE SAMPLE SIZES WE RUN.**
**A floor is itself an ESTIMATE with its own error bar, so an arm must clear the floor's UPPER
bound to be credible -- not the floor's point value.** That gives a **CREDIBLE BAR**:

| instrument | n/cell | floor quoted | floor's own half-width | **CREDIBLE BAR** |
|---|---|---|---|---|
| WordNet (DSI) | 242 | 0.5431 | 0.0513 | **0.5944** |
| human (v3/v4) | 65 | 0.5943 | 0.0975 | **0.6918** |
| **arc representation (the BINDING one)** | 242 | **0.6317** | 0.0493 | **0.6810** |

**AND THAT SETTLES TONIGHT'S ARM INDEPENDENTLY OF EVERY OTHER OBJECTION: `U1_TYPED_CONTEXT` 0.6669
vs a credible bar of 0.6810 -- IT DOES NOT CLEAR.** *The retraction did not depend on this, but this
would have caught it on its own.*
**METHOD AND ITS LIMIT, STATED: Hanley-McNeil analytic SE, an APPROXIMATION. It is trustworthy HERE
because it reproduces the cells' own bootstrap half-widths -- 0.0513 vs observed 0.0516, 0.0975 vs
0.0987, 0.0493 vs 0.0481. IT DOES NOT REPLACE THE BOOTSTRAP; it is for required-n and order of
magnitude.**
**WHAT IT WOULD TAKE.** Per-cell n to tighten a floor's half-width: **±0.05 -> ~250-290; ±0.03 ->
~770; ±0.02 -> ~1,550-1,780; ±0.01 -> ~6,300-7,200.** *The human instrument runs at **65**. Getting
its bar to ±0.03 needs roughly **12x** the pairs, and its matching funnel is what caps it -- which is
why "buy n by loosening the matcher" keeps being proposed and must keep being refused: **a bigger
sample of an unlicensed instrument is worse than no sample.***
**THE STRATEGIC READ (hypothesis, not a result): WE HAVE BEEN RUNNING EXPERIMENTS THAT COULD NOT
HAVE RETURNED A CREDIBLE POSITIVE, AND THEN TREATING THE ABSENCE AS EVIDENCE ABOUT THE SUBSTRATE.**
*Discipline 14 says a width is not an effect; this is the same error one level up -- **a width in the
FLOOR is not a GATE.** Before the next arm is built, decide what n its instrument needs.*

**🚨 OVERNIGHT 08-18, AND THIS BLOCK IS MIRRORED TO YOUR BOARD SO READ IT FIRST: I HEADLINED A WIN AND
THEN TOOK IT APART. NO ARM CURRENTLY CLEARS A TRUSTWORTHY BAR.**
- **A TYPED-ROLE ARM READ 0.6669 AND I CALLED IT THE FIRST EVER TO CLEAR THE BAR. RETRACTED.** Its bar
  was computed on a DIFFERENT REPRESENTATION; rebuilt correctly, **a control containing NO WORDS AT
  ALL reads 0.6317** against that 0.6669.
- **BOTH BARS THIS PROGRAMME GATES ON INCLUDE CHANCE AT THEIR OWN n: 0.5431 CI [0.4922, 0.5953] and
  0.5943 CI [0.4937, 0.6911].** *I spent two days correcting people that "the bar is 0.5431, NOT 0.5";
  at these sample sizes THE TWO CANNOT BE TOLD APART.*
- **AN AUDIT (`37181d944`) FOUND 21 ARMS ACROSS 3 CELLS GATED THE SAME WRONG WAY -- ALL SUSPENDED, NOT
  REFUTED.** *A wrong floor makes a verdict unsupported; it does not prove the opposite.* **NOT
  programme-wide: the main write-rule ladder does it correctly.** No false positive was manufactured.
- **A VERIFIED CODE DEFECT: the prediction-error rule was applied to the BAG channel, not the typed
  one, so "prediction error doesn't help" IS RETRACTED AND THAT QUESTION IS FULLY OPEN AGAIN.**
- **THE ONE FINDING I TRUST, REACHED INDEPENDENTLY BY TWO LANES ON TWO POPULATIONS: THE TYPED CHANNEL
  WAS NEVER GIVEN ENOUGH DATA TO BE TESTED.** ~8.6 slotted observations per word spread over 10,121
  dimensions; the dense 58-dimension arm on the SAME data does not collapse. **A density sweep is
  running against branches pre-committed at `0504bfd00`.**
- **🧠 THE REFRAME WORTH KEEPING (biology, PINNED): the brain's "what is this LIKE" system (ATL) and
  its "what goes WITH this in an event" system (pMTG/TPJ) doubly dissociate. OUR INSTRUMENT IS THAT
  DISSOCIATION. WE BUILT THE SECOND ORGAN AND GRADED IT ON THE FIRST ORGAN'S EXAM.** *Grammatical
  frames CONSTRAIN a meaning hypothesis; they do not SUPPLY it -- stage one of two.*
- **UNCHANGED BELOW AND STILL TRUE:** Organ A closed, the corpus exonerated, the missing ingredient is
  a learning signal. **Tonight did not touch that; it was about what came after.**

**ORGAN A (THE WRITE RULE) IS CLOSED. ALL FIVE STEPS GATED. THE ANSWER IS A LEARNING SIGNAL, AND THE
CORPUS IS EXONERATED (`0f8a3254a`).** The substitutability signal **IS PRESENT** in first-order counts
from our own corpus: a supervised diagonal reweighting of a PPMI+SVD space reaches AUC **0.9670**
fitted / **0.9606** held-out and -- after the leakage objection was TESTED rather than waved away
(37.6% of pair-member words appear in >1 pair) -- **0.8629 under GROUP-DISJOINT, word-clean CV**
(`56175e456`, `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`). **AND NOTHING UNSUPERVISED
REACHES IT:** our five steps 0.03-0.42; vanilla PPMI **0.0519**; TUNED counts **0.1144** (shift
selected on a WORD-DISJOINT held-out set, the Levy/Goldberg/Dagan steelman, `120cfefae`); second-order
cosine 0.0510; **from-scratch SGNS 0.4417 -- BELOW its own UNTRAINED random-init control at exactly
0.5000.** *Training a neural predictor on this corpus moves it TOWARD co-occurrence.* **So: the corpus
is NOT the blocker, first-order counts CONTAIN the signal, no unsupervised transform extracts it, and
the missing ingredient is WHAT TO SUPERVISE WITH.**

**THE TRAP THAT GOVERNS EVERYTHING NEXT, and it must be stated before any build: the instrument
defines its positive set by WORDNET SYNONYMY and its known-answer arm IS WordNet (0.9599). ANY
supervision derived from WordNet TRAINS ON THE TEST. The 0.8629 fitted oracle is a CEILING
DIAGNOSTIC, NEVER a candidate build.** Drill in flight: `admissible_supervision_sources_drill`.

**METHOD RESULT WORTH AS MUCH AS THE SCIENCE: FOUR arms produced apparent CI-separated wins that their
own controls destroyed** -- max-pool, prediction-error gating (**+0.2369, a 4.3x "improvement"**, killed
by a RATE-MATCHED random gate reading 0.3007 vs 0.3079), the `C2` denominator, and the learned basis.
**Without rate-matched and identity-matched twins this session would have reported four breakthroughs
and built on all of them.** *Any arm that changes HOW MUCH gets written now REQUIRES a rate-matched
random twin.*

**ELIMINATED, each with its own control:** the basis (learned = random), the denominator (row-norm is
a cosine no-op, PROVEN by an identical wrongpool control), not-collapsing (max-pool **-0.0210 BELOW**
the sum at 55x storage; its random-occurrence control sat AT CHANCE, proving the loss is
content-specific), the filter (**a same-size RANDOM draw reads 0.5041 vs the incumbent's 0.4173 --
our stopword selection is WORSE than random**), superposition (**DOES NOT EXIST** -- each word
reconstructs from its own counts to **1.76e-08** across all 617 words), prediction-error gating, and
corpus capacity.

**SUPERSEDED BELOW BUT KEPT FOR ITS REASONING:** **DRILL 1'S CENTRAL PREDICTION IS REFUTED. `CODE` IS
EXONERATED -- TWICE (`ac629b1e7`,
`exp_writerule_learned_basis_denominator_gate_v1`).** The drill argued our store is `H^T p_a`, a random
rotation of `Sigma_yx`, and that the missing operation is factorisation `Sigma_yx Sigma_xx^-1` living
in the `CODE` slot -- so a LEARNED basis should create substitutability where a random projection
cannot. **IT DOES NOT.** `C1_LEARNED_BASIS` +0.0073 [-0.0005,+0.0150] **NOT_SEPARATED**, and
`C1_CTRL_MATCHED_RANK_RANDOM` **MATCHES IT** (-0.0060). Composition moves for NO arm, while
`C1_CTRL_FREQUENCY_SHUFFLED` moves it **+0.0858 [+0.0486,+0.1229] ABOVE (worse)** -- which PROVES the
composition instrument can see change, so the flat readings are real nulls. **"Cortex expands where we
compress" also fails:** accuracy fell MONOTONICALLY across the k sweep, 0.0553 (k=64) -> 0.0393
(k=2048). And `C2`'s one CI-separated accuracy gain is **NOT a denominator effect** -- its winning
`pool='row'` divides each row by a scalar and **cosine is provably invariant to that** (the identical
`WRONGPOOL` control is the PROOF, not a control failure); the genuine denominators (`col`,
`both`=PPMI) scored BELOW A0. **AN ELEGANT DERIVATION IS A HYPOTHESIS. This one made a specific
prediction and its own controls killed it.**

**WHAT IS ESTABLISHED INSTEAD, on TWO independent instruments.** (1) `ACCUMULATE` is the measured
INTERFERENCE source (`b6cad69ca`): the CORRECT score is STATIONARY with depth (POP_128 +0.0013
[-0.0006,+0.0034]) while the competing FIELD's mean AND p95 rise CI-separated; mean pairwise anchor
cosine 0.0127 -> 0.272; **common-mode removal does NOT help (DO-NOT-REDO 27 stays closed)** and the
interference is DIFFUSE, not top-200 words. (2) **THE DISSOCIATION INSTRUMENT IS LICENSED**
(`0eb44eb1d`) -- **the first instrument this programme owns whose FOUR FLOORS SIT AT CHANCE and are
VERIFIED there** (0.5000 / 0.4901 / 0.4664 / 0.5431, every CI including 0.5; known-answer 0.9599 vs a
0.95 gate; random store 0.4862). On it, above 0.5 = substitutability, below = co-occurrence:
`RAW_COUNT_SINGLE_OCC` **0.4173** > `PARADIGMATIC_PROFILE_WRITE` **0.2165** > `INCUMBENT` **0.0710** >
`RAW_COUNT_FULL_ACCUM` **0.0510** > `PRESENCE_ABSENCE_BINARIZED` **0.0294**; the ranking is RESOLVABLE
(max_lo 0.3835 > min_hi 0.0470). **STOP-IF (iii) fired: the incumbent is CI-separated BELOW 0.5.**

**THE ANSWER IS THE LEARNING SIGNAL, AND IT IS MEASURED (`exp_corpus_capacity_ppmi_svd_ceiling_v1`,
plan sec 6.18).** Instrument licensed by EXACT reproduction -- all 8 regression checks at **delta
0.0000**; population loaded BYTE-IDENTICAL from the instrument's own checkpoint; matrix 5,491 x 21,576,
density 0.91%, 1.82M tokens, **coverage PERFECT 242/242 in both cells**.
- **PPMI+SVD FAILS ON OUR CORPUS AT EVERY RANK -- but QUALIFIED 2026-08-18 (`96caca8de`): we ran the
  VANILLA construction (no context-distribution smoothing, no shift, no subsampling). Levy & Goldberg
  proved SGNS implicitly factorises SHIFTED PMI, and a TUNED count method MATCHES SGNS. So the honest
  claim is "UNTUNED PPMI+SVD fails", and A TUNED-COUNT ARM IS NOW MANDATORY AND MUST BE REPORTED
  BEFORE ANY SUPERVISED ARM -- if it clears 0.5 unsupervised, the supervision conclusion below is
  WRONG and the missing thing was hyperparameters.** Numbers as run: k=50/100/300/500 -> **0.0519 / 0.0285 / 0.0230 / 0.0278**, all BELOW 0.5,
  and its BEST is WORSE than our incumbent 0.0710. No k dropped for cost. **We are NOT being beaten by
  truncated SVD.**
- **A SUPERVISED LOW-RANK REWEIGHTING OF THE SAME COUNTS READS 0.8629 UNDER THE STRICTEST TEST.**
  CORRECTED, and the agent caught it before reporting clean: the landed pair-level held-out figure is
  0.9606, but **37.6% of the 617 pair-member words appear in >1 pair**, so pair-level CV leaks word
  identity across folds. Group-disjoint GroupKFold (union-find -> 148 word-disjoint components,
  `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`) gives **0.8629**. **QUOTE 0.8629, NOT 0.9606**
  -- the finding SURVIVES, clearing 0.5 by a wide margin on pairs never jointly seen in fitting.
- **SAME counts, SAME 242 pairs, SAME scorer. SUPERVISION IS THE ONLY VARIABLE, AND IT MOVES AUC FROM
  0.03-0.07 TO 0.96.** So the missing thing is **NOT information, NOT representation capacity, NOT the
  write steps** -- **IT IS THE LEARNING SIGNAL.** Every arm we have ever built is unsupervised and
  chooses what to write with no error signal about which directions matter. **Routes to the project's
  own named flavour MISSING-LEARNING -> REUSE/EXPAND the learner, never a parallel build.**
- **NEVER QUOTE 0.9606 AS A CAPABILITY.** The oracle is FITTED ON THE EVALUATION CONSTRUCT. It proves
  the counts CONTAIN the signal; it does NOT show an unsupervised or brain-plausible learner finds it.
  The live question is what supervision a BRAIN has that we do not -- not a labelled synonym list, but
  prediction error, cross-modal correspondence, consequences of use. **DRILL, NOT BUILD.**

**ORGAN A IS NOW FULLY GATED -- ALL FIVE STEPS (`f311d0ac2`, `34d3fdbab`, plan sec 6.15).** FILTER:
**REAL BUT NEGATIVE-VALUE** -- a same-size RANDOM token draw reads **0.5041, CI-separated ABOVE** the
incumbent's 0.4173. CODE: exonerated x2. ACCUMULATE: interference source. NORMALISE: not in the live
path. SUPERPOSE: **DOES NOT EXIST** -- rebuilding each word from its OWN counts alone reproduces the
incumbent to **1.76e-08 across all 617 words**; proven by reconstruction, not argued.

**RETRACTED 2026-08-18: "the operative defect is COLLAPSING OCCURRENCES INTO ONE VECTOR."** Tested
directly and **FALSE**: `M1_MAXPOOL` (every occurrence kept, scored by best match) reads **0.0299,
-0.0210 [-0.0393,-0.0020] CI-separated BELOW** the sum, at **55x the storage**. Its control decides the
reading: `N1_MAXPOOL_RANDOM_OCC` sits **AT CHANCE (0.4545)**, NOT depressed -- so the depression needs
the word's OWN occurrence content and is not an artifact of the max operator. Not-collapsing is not
the fix.

**THE ORGAN-LEVEL FINDING, AND IT IS THE REAL RESULT: NOT ONE ARM THIS PROGRAMME HAS EVER MEASURED IS
CI-SEPARATED ABOVE 0.5 ON THE LICENSED INSTRUMENT.** Everything tops out AT chance and never above it
(`N2_SHUFFLED` 0.5296 NOT_SEP, `N1_RANDOM_FILTER` 0.5041 NOT_SEP, `S1_SINGLE_OCC` 0.4173), and
everything carrying MORE accumulated corpus content sits FURTHER BELOW (incumbent 0.0710, full accum
0.0510, max-pool 0.0299, binarised 0.0294). **Interventions that DESTROY information move us TOWARD
chance; interventions that ADD accumulated content move us AWAY from substitutability.** So the
ceiling is not a step we have yet to fix -- **first-order co-occurrence counts from this corpus appear
to carry a co-occurrence signal and NO substitutability signal for these five steps to expose.** The
best any configuration achieves is encoding NOTHING.
**CAVEAT, do not collapse these into one claim:** across `ACCUMULATE` the winner no-relation rate
FALLS 0.8400 -> 0.7971 (-0.043 CI-separated) -- **adjacency was present from sentence one; a bag of
neighbours IS an adjacency record.** Summing does not CREATE adjacency; it raises INTERFERENCE and
degrades retrieval. **REPORT WINNER SHARE, GOLD SHARE AND RATIO TOGETHER, ALWAYS** (the Director once
quoted 66.0->94.4 while dropping the gold's 23.9->60.3 and the ratio, which FELL 3.967->3.822).
**LIMIT: the dissociation instrument is n=242 matched pairs, ALL NOUNS** -- verb/adj/adv strata did not
survive its frequency caliper.
**RETRACTED (VET COMPLETE, off `exp_writerule_step_ladder_v1` `COMPOSITION_DELTA_TABLE`): "summing is
what converts our store from could-replace to appears-near."** FALSE, and backwards: across
`ACCUMULATE` the no-close-relation rate FALLS 0.8400 -> 0.7971, **-0.043 [-0.0800,-0.0086]
CI-SEPARATED**. Adjacency was there from sentence one -- a bag of neighbours IS an adjacency record.
The Director quoted the winner's co-occur share (66.0->94.4) and dropped the gold's (23.9->60.3) and
the RATIO, which FELL 3.967->3.822. **REPORT WINNER SHARE, GOLD SHARE AND RATIO TOGETHER, ALWAYS.**

ONE ORGAN AT A TIME, AND THE ORGAN IS THE WRITE RULE (owner ruling 2026-08-18, `PLAN_ORGAN_STEP_LADDERS`
sec 6.7). The cue side is finished and did not fix the reading; four cells changed the QUESTION we hand
the store and every one improved FINDING THE DRAWER while none improved READING WHAT IS IN IT
(binarising takes addressing 0.0711 -> 0.1094 while hit@1 moves 0.0223 -> 0.0249, +0.0026
[-0.0026,+0.0078] NOT_SEPARATED -- ADDRESSING AND READ-OUT ARE SEPARATELY CAPPED).
**THE DECISIVE WRITE-RULE MEASUREMENT, and it is why this organ is the one:** varying ONLY the target's
own stored row, `SUM_ALL` reads **0.0100**, ONE occurrence picked at RANDOM reads **0.0367**, and
`BEST_SINGLE_ORACLE` reads **0.3033** against the **0.1390** floor we have never cleared. *Summing is
worse than not summing, and individual sentences already carry enough to clear the floor.* The oracle
is a CEILING DIAGNOSTIC, never a capability. **DEPTH IS RETRACTED (sec 6.6): "+0.0503 still climbing"
was an ORACLE-CUE number; on the REAL partial cue POP_72 32->72 is BELOW and POP_128 is NOT_SEPARATED,
with winner composition FLAT at every depth.** Eleven cells across six organs on 08-17 returned ~+0.01
each; the two LADDERS redirected the programme. Method is not in question -- organ selection was.

## TOP ITEM -- FIND AN ADMISSIBLE SUPERVISION SIGNAL THAT IS NOT THE EVALUATION GOLD
Organ A is closed and its answer is that we need a LEARNING SIGNAL. **The whole question is now WHICH
ONE, and the binding constraint is CIRCULARITY, not performance.**
**VERIFIED OFF DISK 2026-08-18, not asserted** (`exp_dissociation_score_instrument_v1.py`):
`SET_P` is built by `build_wordnet_synonym_candidates()` (line 304) from `wn.synsets()` (line 312);
the known-answer arm is WordNet path similarity (0.9599); and `SET_S` **explicitly EXCLUDES any
WordNet pair even at high co-occurrence** (evidence key
`set_S_excludes_wordnet_pair_even_at_high_cooccurrence`, line 674). **So WordNet does not merely
influence the labels -- it DEFINES both sides of them.** Therefore **any signal derived from WordNet --
synonyms, hypernyms, glosses, or anything computed from them -- trains on the test and is UNUSABLE AS
SUPERVISION however well it scores.** Second constraint, the
owner's invariant: **NO LLM in the operational path**, and a pretrained table is disqualified as a
MEANING SOURCE (ceiling reference only) -- **but a STATIC OFFLINE-BUILT ASSET IS ADMISSIBLE** (owner
Q3: *"we can build that foundation however we want, as long as it is a strong foundation, and the
operation is not llm"*). Do not hold us to a stricter standard than the brain meets.
**IN FLIGHT:** `admissible_supervision_sources_drill` -- biology first (what supervises cortical
semantics, and what the prediction-error NULL does and does NOT rule out: it tested error against the
word's OWN accumulator, which is not error against ANOTHER MODALITY or a DOWNSTREAM CONSEQUENCE);
then an **on-disk enumeration by `os.walk`, never registry-first** (a 1.21M-edge CSKG read by nobody
live -- **check whether it CONTAINS WordNet before trusting it**; OpenStax 117,642 sentences;
Brysbaert concreteness; Warriner VAD; Binder; UD parses); then a ranking on brain fidelity /
independence-from-gold / coverage on the 617 matched-pair words / no-LLM survival; then ONE build
with a mandatory rate-matched control.

## SUPERSEDED TOP ITEM -- THE WRITE RULE WAS THE FIRST THING TO MOVE READ-OUT (LESSONS: WRITE RULE)
`exp_readout_writerule_paradigmatic_v1` (full, `a8fdc968f` / `24ca42661`) rebuilt the STORE so a
word's code sums its neighbours' own context PROFILES instead of their arbitrary identity tags, and
left the comparator untouched. `W1_PARADIGMATIC` **0.0298** vs `W0_SYNTAGMATIC` **0.0223**: **+0.0075
[+0.0023,+0.0128]**, half-width 0.00525, analytic null half-width 0.00458, **ABOVE** (~34% relative).
A frequency-matched profile control reads 0.0225 and does NOT beat W0 (+0.0002 NOT_SEPARATED); a
random-profile null reads 0.0188 and does not either (-0.0035 NOT_SEPARATED -- lower, not separated);
three hybrid alphas all land +0.0065..+0.0070 ABOVE; K1 addressing 1.0000 on all seven arms;
orthographic leakage flat at W0's own value. **NO STOP-IF FIRED CLEANLY** and the cell wrote the
honest fourth reading itself: *the write rule was PART of the defect but is not sufficient* -- W1 is
still **-0.0575 [-0.0673,-0.0478] BELOW** its own binding floor (orthographic 0.08731), 2.9x short.
**THE CONTRAST IS THE FINDING: the read-out scoreboard's ~39 prior arms ALL changed the COMPARATOR
and none beat the incumbent CI-separated; this one changed the WRITE RULE and did.** `wire_status` is
`VET_PENDING` -- WIRE-or-SHELVE not decided.

## CUE SIDE -- CLOSED IN FOUR CELLS (LESSONS: CUE SIDE CLOSED; DO-NOT-REDO 44, 45, 46)
(1) PLAN ITEM 3 landed a CLEAN NULL (`2e5a467ae`): `A0_FLAT` reproduces item 1's 0.0849 target
exactly (regression gate PASS), `T1` key-sparsified 0.0704 = **-0.0145 [-0.0203,-0.0088] BELOW**,
`T2` cue-sparsified 0.0886 is the grid's raw MAXIMUM yet **+0.0037 [-0.0013,+0.0088] NOT_SEPARATED**,
T2 vs T1 +0.0182 ABOVE, oracle 1.0000 and random 0.0000 both passing. **Stop-if (i) fired. The cell's
own verdict: "Neither, cleanly" -- no arm beat the flat store and the sparsified arms LOST accuracy
rather than matching it more cheaply.** `C1` vs `T1` is bit-identical 0.0 [0,0] BUT CARRIES A
CONSTRUCTION CAVEAT: K=32 exceeds the cue's own median nnz of 12.0, so that truncation is a no-op for
most items and the tie is partly an artifact. (2) COMPRESSION DIAGNOSED (`201776cc9`): what matters
is PRESENCE, not counts -- the losing property is MAGNITUDE, not sparsity and not non-negativity.
`B1_BINARIZED_RAW` (presence only, uncompressed) +0.0383 [+0.0293,+0.0476]
above the incumbent and +0.0248 [+0.0160,+0.0338] above raw counts; S1 -0.0100 BELOW, N1 -0.0003
NOT_SEPARATED. Loss is CONCENTRATED: the 93 lost items have shorter cues (10.80 vs 12.48) and much
sparser store profiles (106.4 vs 210.8), both CI-separated. (3) IT DOES NOT TRANSFER (`1e085d761`) --
see POSITION; R2 (binarised THEN projected) gives back two thirds of the addressing gain, so **the
two defects are not independent**. (4) THE BASIN THEORY IS REFUTED -- see CLEANUP.

## PHASE DIAGRAM -- THERE ISN'T ONE (LESSONS: PHASE DIAGRAM)
`substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md` (`32cc8ce71`), enumerated
from the filesystem: 7,804 `metrics.json` (re-walked 7,807, delta = this session's own files, nothing
missing); ~59 vary dimensionality, ~21 sparsity, 2 expansion; **23 of 42 parameter-by-operation
squares NEVER MEASURED**, 13 usable, six diagrams on six scorers that may NOT be merged. The "55-65%
coverage" recollection traces to `director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`, whose own line
items say ~10% and <5%. Q13's sparsity sweep has NO cell under `data/` -- it is in gitignored
`scratch/sparsify_right_object/`; promote before the next clear. **Its d-sweep row is corrected by
C36.**

## BRIDGING -- TWO MEASURED NULLS (LESSONS: DO-NOT-REDO 38, 43)
Phase 2 FULL: B1 rho 0.0270 n=394 vs floors 0.0412/0.0317/0.0905, NOT_SEPARATED, perm p 0.30, both
known-answer arms ABOVE (K1 0.3301, K2_ORACLE 0.2893); bridged codes KEEP IDENTITY (96.12% distinct)
and LOSE MEANING (retention 0.0819); the curated CSKG arm fails too. SELECTIONAL-CONSTRAINT
BRIDGING, the owner's own mechanism, is the SECOND and worse null: -0.1049 [-0.2041,-0.0057] BELOW
the incumbent, -0.0015 NOT_SEPARATED from a random target, instrument alive (K1 0.3311). KILL
STATUS: withdrawn for thematic, re-worded for selectional, per HANDOFF 8b(B) -- whose numbers remain
NOT re-verified by any pass.

## STORAGE -- THE WRITE/READ ASYMMETRY IS REAL AND DID NOT SURVIVE AS A WIN (LESSONS: WRITE/READ ASYMMETRY)
`exp_sparse_address_dense_value_v1` (n=3994, own floors): best partial-cue addressing anywhere is
0.0719 at a DENSE address; a 1%-occupancy address (82 of 8192 units) read with a DENSE cue matches
it at 0.0699, CIs overlapping; read SYMMETRICALLY it is 0.0483, 1.45x worse; the dense read wins 18
of 24 matched pairs, max 6.27x. **RE-TESTED 08-17 on the UNCOMPRESSED base, where it is a DIRECTION
AND NOT A WIN: T2 (cue sparsified) beats T1 (key sparsified) +0.0182 CI-separated, but T2 does not
beat the flat store (+0.0037 NOT_SEPARATED).** C36: the d-sweep line "0.0711 -> 0.0716 at 8192" mixes
read regimes; matched at `a_read=1.0` it is 0.0711 / 0.0714 / **0.0709** -- 32x the memory buys less
than nothing, so the conclusion strengthens.

## CLEANUP / SURPRISE / TARGET SPACE (LESSONS: CLEANUP MEMORY, SURPRISE, TARGET SPACE)
**AND THE BASIN EXPLANATION FOR THE CLEANUP NULLS IS REFUTED (`exp_cleanup_basin_conditional_v1`,
landed 08-16 22:41, UNREAD BY ANYONE FOR ~14 HOURS).** Six tau strata summing to 3994, known-answer
arm 1.0000 in every one: lift is CI-separated ABOVE **only in the LOWEST-tau stratum** (+0.0036
[+0.0009,+0.0072]) and NOT_SEPARATED in every higher one **including the highest** (+0.0154
[-0.0039,+0.0347]) -- the OPPOSITE of what basin theory predicts and of what the cell pre-registered
as confirming. It licensed skipping an elaborate settle mechanism, and the one cheap settle arm run
anyway is null (-0.0010 [-0.0025,+0.0003]). **AN UNREAD RUN IS A RUN THAT DID NOT HAPPEN -- second
instance in two days.**
CLEANUP MEMORY IS REAL, NOT INERT (fixed points 1.0000, idempotent, capacity on VSA's own d/log d
scale): first measured lift, +0.0033 and +0.0078 CI-separated in 2 of 3 pools, every arm still
-0.1135 BELOW the binding constant floor -- which makes the FIVE BANKED CLEANUP NULLS STRONGER, the
load-bearing half was NOT missing. SURPRISE-WEIGHTING: clean null, named cause -- signal DEGENERATE
(median 0.875 where 1.0 is orthogonal), selection beats a token-matched random subset in 4 of 18
comparisons, residual rule a near-no-op (cos 0.9771 to uniform) = the PRE-REGISTERED bootstrapping
problem. TARGET SPACE: affect +0.1013 is a CEILING DIAGNOSTIC, no floors, no null, clears nothing;
its verb half is now MEASURED, not suspended (C33).

## TOOLING STATE (LESSONS: VERDICT BAR, SKIPPED FULLS, C31, C32)
Corrected base rate: 7,789 enumerated, MEETS_BAR **1** (`exp_cue_to_store_translation_v1`), FAILS
7,770, NO_EVIDENCE 18; 238 flagged cells ARE cited by an index -- OPEN OPERATOR DECISION, NOT TAKEN.
The one pass is rejected on four grounds (pool admits a fitted constant 0.7354 vs chance 0.0625;
exact-key is not the operating point; the cell declines a verdict; margin overstated 4.20x).
`verdict_bar_check.py` HAS FALSE-PASSED FOUR TIMES -- run it, NEVER rely on its verdict, state
arm-by-arm margins; it also returns NO_EVIDENCE on any cell whose arms are nested per-stratum
(ITEM 2's). Only 12 of 7,789 cells ever recorded a constant floor, so every historical bar decision
used a THREE-floor max. `matched_candidate_sets` WAS VOID and is rebuilt; `eligB` still suspect.
FOUNDATION v4 ~49% (`d62acfe58`); TRIAGE -> `RECOVERY_PROGRAM.md`.

## DO NOT REDO -- NEVER-TRIM -- stubs; detail in LESSONS
All CLOSED. `*` = revival criterion. 1 intersection-over-argmax; 2 the "40% ceiling"; 3 syntactic
bootstrapping*; 4 F2 freq-corrected pool*; 5 same-sentence cosine/PMI; 6 FHRR superposition; 7 PBV;
8 read-out vs v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 norms as FILTER*; 12 sense
selection v2; 13 minimum-grounded-basis; 14 `genuine_cross_source_corroboration_v1`*; 15 combined
dictionary v1; 16 "context vector is noise"; 17 co-occurrence as the explanation; 18 role-bound
structure alone -- STRUCTURE_HURTS*; 19 frontmatter `isolation:`/`background:`; 20 the voting
mechanism*; 21 hand-scored delta at 1-3%; 22 the 2-hop bridges; 23 extraction as DIRECT-BANK*;
24 distinctiveness as log-IDF*; 25 differentia/genus + supply; 26 `sign()` vs forgetting kernel;
27 rank-1 common-mode removal*; 28 FORAGE_REFUSAL; 29 five-stage read-out chain; 30 near-duplicate
anchors; 31 supply as an ADDITIVE CHANNEL -- NARROWED*; 32 DG/pattern-separation for grounding;
33 crowding as a gate criterion; 34 the GRADED SWITCH*; 35 +0.0602 as a C3 number; 36 `k_eff~=50` as
a MEASURED limit*; 37 "right neighbourhood, wrong member"*; 38 bridging WITH the THEMATIC hub --
MEASURED NULL*; 39 sparsifying the READING anchor -- dies on the real task*; 40 quoting +0.2285 as
the bridging margin; 41 quoting a "0.073 lift gap"; 42 `grounded_similarity()` AS A SCORER --
76.18% of SimLex on two values, NO revival; 43 SELECTIONAL-CONSTRAINT bridging -- CI-separated
BELOW the neighbour-copy incumbent and NOT_SEPARATED from a random target*; **44 SPARSIFYING THE
STORED KEY under a partial cue -- -0.0145 [-0.0203,-0.0088] BELOW the flat store with oracle 1.0000*;
45 THE BASIN EXPLANATION for the cleanup nulls -- lift separates ONLY in the LOWEST-tau stratum,
opposite to prediction; do NOT build a settle mechanism*; 46 CUE-SIDE ENGINEERING AS A READ-OUT FIX
-- the biggest addressing gain we have (+0.0383) transfers to hit@1 at +0.0026 NOT_SEPARATED*.**
CAVEATS: D1 near-vs-far; D2 encoder-swap; D3/D4 foraging reversals; D5 sharpening SMOKE-only;
CT1 consistent!=good; CT2 run_mode is an ingestion constant.
CORRECTIONS: C1 availability-binds-first; C2 CLIP-at-INGEST; C3 the 94% has NO floor;
C4 DGProj=interference; C5 an encoder EXISTS; C6 wrong checkpoint; C7 opp-map #5/#6; C8 comparator
was a LOOKUP TABLE; C9 results ARE searchable; C10 tautology=eligibility bug; C11 "58% common mode";
C12 doc date; C13 the FULL DID report; C14 whiten+pinv IS tested; C15 chain self-contradiction;
C16+C22 `A5_STRINGCTRL` not zero-meaning; C17 scramble is DONOR-RULE dependent; C18 conjunctive lean
QUALIFIED; C19 k_eff correction-of-a-correction; C20 "0.90 precision" UNSOURCED; C21 "0.95"=parse
coverage; C23 121.1M-token encoder/237.7M corpus; C24 norms stale BOTH ways; C25 shortlist-hit out
of scope; C26 FHRR 0.956 bare threshold; C27 VET residue; C28 +0.2285 was a NEIGHBOUR-CHOICE
diagnostic; C29 the "0.073 lift loss" is 0.0034, populations mixed; C30 "retrieval fine / we tie
spelling" is EXACT-KEY + OPTIMISTIC-TIE ONLY; C31 the checker's false pass was THREE defects;
C32 "0 of 7,769 meet the bar" -> 1 of 7,789, and that survivor is itself rejected; **C33 "our
instrument cannot resolve verbs even when handed the answer" -- SUSPENDED at n=86, now MEASURED at
n=222: rho 0.2607 [0.1282,0.3841], strongest floor (scramble p95) 0.1152 against a 0.1107 null-width
orientation, margin +0.1452 [-0.0496,+0.3379] NOT_SEPARATED, permutation p 0.001. The null genuinely
tightened, so this is a real negative and not the n=86 artifact. A verb-channel build is licensed
CITING THIS AND NEVER THE RETIRED n=86 NUMBER;** C34 "the constant floor is the binding one" FALSE
in general -- it is -0.1959 on the bridging stratum and -0.2253 on the selectional one, the WEAKEST
member of the four; **C35 "the binding-operator choice is EMPIRICALLY NULL across two cells and six
operators" (HANDOFF 8b(D)) is PART-WRONG THREE WAYS -- a 3-BIN instrument is not a null (and FHRR
reads 0.8000 vs Hadamard 0.2889 inside the very bin that produced "invariant"); the 500/500/500 half
names the wrong cell and is SUPERSEDED, not absent; and two of the six operators COLLAPSE (0.0720
and 0.0000 against ~0.81). The operator has never been varied on any job this programme runs on.**
**C36 "d 256->8192 moves partial-cue addressing 0.0711->0.0716" MIXES READ REGIMES -- 0.0716 is the
`a_read=0.2` cell at D=8192; matched at `a_read=1.0` the sweep is 0.0711/0.0714/0.0709, so the
conclusion (dimensionality does nothing for addressing) STRENGTHENS. The correction already filed
against it is ALSO wrong: 0.0716 does NOT trace to a D=2048 draw, it is a genuine D=8192 reading
(`BEST_ASYMMETRIC_REGIME_SWITCH_CONFIG`). Both notes fixed in place. Second correction-of-a-
correction in one day.**

## STANDING DISCIPLINES -- NEVER-TRIM -- LESSONS
1 NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% -- cost TWO experiments, the
2nd claiming to have FIXED the 1st; gate on KNOWN-ANSWER RECALL. 2 SERIALIZE MEASUREMENT vs CODE
CHANGE (2x). 3 A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night; C31 = 5th).
4 ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM (6x); AN ABSENCE CLAIM REQUIRES
AN ENUMERATION, NOT A SEARCH -- state HOW. 5 BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS
THE OPERATION IT SCORES. 6 RUN A POSITIVE / KNOWN-ANSWER ARM (2x): a FLOOR says whether the EFFECT
is real, a KNOWN-ANSWER arm whether the INSTRUMENT is -- run both. 7 NO DEMOTION WITHOUT A FRESH
ON-DISK RE-CHECK -- ~11 wrongly demoted, 17 corrections-of-a-correction in 48h; keep
EXISTS/IS-REACHED/IS-GOOD separate. **C35 is the 18th: a correction said a claim "does not
reproduce" when the cell it reproduces in was never opened.** 8 A GATE IS A CI-SEPARATED MARGIN
ABOVE max(ORTHOGRAPHIC, FREQUENCY, SCRAMBLE, CONSTANT) on the IDENTICAL scorer/n/pool/gold -- never
a bare number, baseline STANDALONE, every floor recomputed on the item's OWN population **AND ITS OWN
REPRESENTATION (widened 08-18 -- see 16; "population" alone did NOT catch the 0.5431 import).**
9 DETECTORS FIRE ON HONESTY (49/49 flagged were false positives). 10 SILENT JOINS FABRICATE GREEN
AND RED -- ASSERT+COUNT joined rows. 11 A NUMBER MAY NOT BE CARRIED BETWEEN SCORERS OR POPULATIONS
-- cost 3x in one night (C28/C29/C30); name the scorer, n, pool and gold for BOTH sides or you have
no comparison. 12 A CLAIM MEASURED AT THE EXACT-KEY OPERATING POINT DOES NOT TRANSFER TO THE
PARTIAL-CUE REGIME, WHICH IS THE REAL ONE -- top-50 0.5566 exact vs 0.3758 partial; state the cue
regime beside every retrieval number. 13 REPORT TIE CONVENTIONS BOTH WAYS, NEVER SILENTLY PICK THE
FLATTERING ONE -- +0.0105 NOT_SEP flips to +0.0641 ABOVE on tie mass alone. 14 REPORT THE CI
HALF-WIDTH AND THE NULL p95 AT THAT n BESIDE EVERY MARGIN -- A WIDTH IS NOT AN EFFECT. Cost 3x in
one night (C32/C33/C34), each an UNDERPOWERED NULL read as a CAPABILITY STATEMENT; at n=86 the
"floor" WAS the null distribution's own spread. **15 A GRID'S RESOLUTION IS PART OF ITS VERDICT: an
equality reported on a 3-value grid is a BIN, not a measurement (C35). State the swept values and
the number of queries per point beside every "no difference".**
**17 EVERY NEGATIVE GETS A BRAIN-FIDELITY DRILL, EVERY TIME -- OWNER INSTRUCTION 2026-08-18
(COMMENTARY): *"All negative results you should drill (safely -- we shouldn't be giving away any of
our substrate specifics here) for brain fidelity and what we should do to get closer to that -- every
time."*** A negative is not filed until it has been asked: **WHICH BRAIN STRUCTURE performs this
operation, are we REPLICATING it or SUBSTITUTING something convenient, and WHAT WOULD CLOSE THE
GAP?** *This is not new doctrine -- it is the standing rule made non-optional and applied at the
moment of the negative rather than in a later drill that may never happen.* **🔒 SAFETY CLAUSE, OWNER
EXPLICIT: NEVER PUT OUR SUBSTRATE SPECIFICS INTO AN EXTERNAL QUERY.** Research drills ask about the
BIOLOGY in general terms -- *"how does cortex represent grammatical role"* -- **never about our
architecture, our organs, our operators, our dimensionalities or our results.** *Web search is a
one-way door; a query naming our design is disclosure that cannot be recalled.*
**AND THE FIRST QUESTION OF ANY SUCH DRILL IS WHETHER THE NEGATIVE IS EVEN REAL: on 2026-08-18, FOUR
of the night's "negatives" were MEASUREMENT DEFECTS, not results** -- a bar computed on the wrong
representation, an error rule applied to the wrong channel, an instrument with 10.9% coverage of the
arm it was testing, and a corruption control that was near rank-preserving and so **incapable of
failing.** *Drilling a defect for brain fidelity would have produced a confident, wrong story about
the brain. **ESTABLISH THAT THE EXPERIMENT COULD HAVE SUCCEEDED BEFORE ASKING WHY THE BRAIN
SUCCEEDS WHERE WE DID NOT.***
**16 A FLOOR IS SPECIFIC TO THE REPRESENTATION IT WAS COMPUTED ON, NOT ONLY TO THE POPULATION --
AND THIS RULE EXISTS BECAUSE RULE 8 AS WRITTEN COULD NOT CATCH THE VIOLATION.** 0.5431 was computed
on the BAG-of-words representation and quoted as "THE bar" across `STATUS.md` and the plan for two
days -- **including in the banner that corrected everyone for saying 0.5** -- then applied to arms
built on grammatical ARCS. Rebuilt on the arc representation, a **no-words attestation floor read
0.6317 [0.5820, 0.6781]** against a 0.6669 headline: **the gate was meaningless and the coverage
control could not catch it (`COVERAGE_MIN=3` dropped 0 of 242 pairs).** *Same population, same
scorer, same gold -- so rules 8 and 11 both PASSED while the comparison was already void.* **STATE
THE REPRESENTATION BESIDE EVERY FLOOR, AND REBUILD THE FLOOR WHENEVER THE REPRESENTATION CHANGES,
EVEN IF NOTHING ELSE DID.** *Corollary, earned the same night: a control with a threshold that
excludes nothing is not a control -- report how many items each control actually removed.*

## WHAT IS RUNNING / BLOCKED

- **📋 BOARD TRIAGE -- 12 OPEN, BUT ONLY 5 NEED YOU. SEVEN ARE ONE FAULT AUTO-FILED SEVEN TIMES.**
  **Q47, Q48, Q53, Q54, Q55, Q57, Q58 are all the SAME `rm`-bundling denial** -- the loop files a
  board question per denial, so a recurring fault floods the board. **I verified two of them touched
  no result** (the deleted paths were a smoke directory and a log truncated by `>` anyway) and the
  rest are the same shape. **Q49 asks the one policy question they all reduce to; answering Q49
  disposes of all seven.** *Read them as one item, not seven.*
  **THE FIVE THAT ARE REAL, in the order I would take them:**
  1. **Q52 -- 844 uncommitted insertions across 10 experiment files that are NOT mine**, last
     modified 2026-08-17, existing only in the working tree. **Any reset/checkout/worktree op
     destroys them.** I did not touch them: committing a concurrent session's in-progress state
     under my name would be wrong either way. *Highest consequence on the list.*
  2. **Q51 + Q56 (one issue, evidence added) -- 3,894 watchdog files, 31% of `notes/`, still
     arriving every 10 min from the DEAD four-session fleet.** **Now MEASURED, not hypothesised: a
     plain `find` over `notes/` TIMED OUT at 300 s tonight**, and the same cost hit the supervision
     drill and two agents. Cheapest performance fix in the repo. *Disable the task first, then
     clear; otherwise it refills at 6/hour.*
  3. **Q50 -- `CLAUDE.md` tells every session to open by running a tool that returns ZERO BYTES and
     exits 0.** I flagged it in this file but did NOT edit the conventions file unprompted.
  4. **Q49 -- keep halting the loop on the `rm` fault, or log-and-continue?** *My recommendation is
     KEEP HALTING and fix the cause; it is the only thing that reliably catches dropped
     preconditions, and it caught them tonight.*
  5. **Q16 / Q17 (older) -- build a word-onset channel? is that blocked file path deliberate?**
  **Nothing on this list blocks the science.** All four research lanes ran to completion or are
  still running.
- **⚠️ THE BAR IS `max(four floors)` = 0.5431 ON THE LICENSED INSTRUMENT, **NOT 0.5**. CHANCE is 0.5;
  the BAR is 0.5431 (the constant/prototype floor). Sections of this file below still say "above 0.5
  = substitutability" -- **that describes CHANCE, not the GATE.** No conclusion flips (every arm sat
  0.03-0.44, far below both), but **any future arm must clear 0.5431**, and the Director spent a night
  describing 0.5 as the target. Corrected in `PLAN_ORGAN_STEP_LADDERS` 6.29.
- **✅ THE HUMAN INSTRUMENT IS LICENSED (`f792c3ab8`, v3, THIRD attempt). n=7 -> 65 per cell.**
  Frequency-STRATIFIED matching -- bin each POS stratum's frequency into 3 quantile bins, then run
  the UNCHANGED matcher inside each (POS, bin) cell. **All four floors CI-include 0.5;
  `max(four floors)=0.5943`** (higher than the WordNet instrument's 0.5431). Known-answer is the
  **published human rating**, NOT WordNet -- its AUC 1.0 is **tautological plumbing, not a result**.
  **All seven arms scored AT OR BELOW CHANCE on human judgements** (INCUMBENT 0.2265, SINGLE_OCC
  0.4644, PARADIGMATIC 0.2788) -- the same qualitative picture WordNet gave.
  **THE DECIDING NUMBER IS INCONCLUSIVE, on the PRE-COMMITTED branch: rho = 0.7857 between the two
  instruments' arm orderings, permutation p = 0.048, BUT bootstrap-of-arms 95% CI = [-0.0439, 1.0],
  WHICH INCLUDES ZERO. The 6.24 WordNet caveat REMAINS OPEN.** *rho 0.79 is NOT agreement; the wide
  CI is NOT disagreement.*
  **THE POWER LIMIT MOVED TO THE ARM COUNT.** The bootstrap resamples **ARMS, not pairs** -- 7 items
  cannot give a tight CI however good each AUC is. **Fix = MORE ARMS, not more pairs.** *In flight:
  `arm-expansion`, harvesting the 20+ store variants already built tonight and scoring them on both
  instruments.*
  **CAVEAT THAT TRAVELS WITH EVERY v3 NUMBER:** post-match balance is materially WORSE than its
  sibling's (`mean_log_freq` -0.4382 vs -0.0416; `mean_length` 0.3988 vs -0.0121). **Floors pass,
  which is the gate -- but this instrument is LOOSER.** And absolute AUCs are **NOT comparable across
  the two instruments; only the ORDERING is.**
- **SUPERSEDED: HUMAN INSTRUMENT v1/v2, BOTH `POWER_INSUFFICIENT` AT n=7 (`6976f08ca`).**
  v2 used the FULL 5,491-anchor set and got the SAME n=7 as v1 -- **which disproves the Director's
  own diagnosis.** *I claimed v1 collapsed because I restricted it to the WordNet instrument's 617
  words; v1's checkpoint diagnostics show that restriction NEVER EXISTED. Plan 6.30 is RETRACTED by
  6.33(B).* **The real cause: a structural frequency gap between the human-labelled sets (pre-match
  SMD on `mean_log_freq` = -1.8396) colliding with the WordNet-tuned caliper (0.02), which drops
  429 of 436 candidates. Adjective and noun strata yield ZERO matches; the 7 survivors are VERBS.**
  **So the blocker is the MATCHER, not the population** -- and loosening the caliper stays forbidden
  because it would unlicense the instrument. **The 6.24 WordNet caveat REMAINS OPEN.**
- **0.8629 IS VERIFIED AND NOW HAS AN ARTIFACT (`dfc84429a`).** Spot-checking found the night's most
  load-bearing number lived ONLY in prose -- zero hits in the capacity cell's `metrics.json`. Its
  script was committed, so reproducible not fabricated. **Re-ran: group-disjoint 5-fold CV AUC
  0.8629, pair-level 0.9587, both exact.** Log at `notes/groupdisjoint_verification_log_2026-08-18.txt`.
- **🚨🚨🚨 AUDIT LANDED 06:52 (`37181d944`) -- BRANCH (i): 3 CELLS, 21 ARMS MIS-GATED, TWO OF THEM NEW.
  AND IT SURFACED SOMETHING LARGER THAN THE IMPORT: THE BAR ITSELF WAS NEVER SEPARATED FROM CHANCE.**
  **`F_CONSTANT_PROTOTYPE` = 0.5431 CARRIES CI [0.4922, 0.5953] -- IT INCLUDES 0.5.** I checked the
  human instrument's bar too: **`F_SCRAMBLE` = 0.5943, CI [0.4937, 0.6911] -- ALSO INCLUDES 0.5.**
  **BOTH BARS THIS PROGRAMME GATES ON ARE STATISTICALLY INDISTINGUISHABLE FROM CHANCE AT THEIR OWN n.**
  *I spent two days correcting people that "the bar is 0.5431, NOT 0.5" -- and the honest statement is
  that at these sample sizes THE TWO CANNOT BE TOLD APART. That correction was itself a width read as
  an effect: discipline 14, committed by the person who wrote it.*
  **MECHANISM (DSI L99-108): `F_SCRAMBLE` and `F_CONSTANT_PROTOTYPE` are computed FROM THE STORE
  MATRIX; the other two are not. The bar is always owned by one of those two -- SO THE BAR IS
  INHERENTLY THE REPRESENTATION-BOUND QUANTITY.** *That is why importing it across representations
  was guaranteed to be wrong, not merely unlucky.*
  **THE THREE, ALL `SUSPENDED, NOT REFUTED` -- a wrong floor makes a verdict UNSUPPORTED, it does NOT
  establish the opposite:** (A) the typed-role arc cell, already retracted; (B) **NEW --
  `exp_typed_role_selectional_asset_writerule_v1` (`c1d2bc80e`, 7 arms)**, corroborated off its own
  data: **its must-fail controls `N1` 0.5516 and `N3` 0.5630 sit ABOVE the 0.5431 bar**, so its native
  floor is ~0.55-0.56 and the imported bar was too low, *same direction as the arc rebuild*; (C)
  **NEW -- tonight's human-instrument cell (`16475c9c5`, 4 arms)**, which re-derived its bar sincerely
  but along the wrong axis -- right population, from v3 arrays built on the **bag** store.
  **✅ WHAT SURVIVES UNTOUCHED, and this matters: (B)'s `WORD_SELECTION_NOT_TYPE` verdict is
  WITHIN-CELL and same-representation, so it STANDS; no false positive was manufactured anywhere
  (B's `T1` never cleared the bar even at its CI lower bound 0.5296); and BRANCH (B) FROM 6.39 STANDS
  *A FORTIORI* -- `U1` 0.4125 failed a bar we now know was TOO LOW.**
  **NOT A PROGRAMME-WIDE CRISIS, and I was primed to call it one.** The write-rule ladder already does
  this correctly **per arm** (`F_CONSTANT_PROTOTYPE__<arm>`); `corpus_capacity`, `tuned_count` and
  `predictive_coding` gate on 0.5 and hold 0.5431 only inside regression gates. **Branch (iii) ALSO
  fired: NO `metrics.json` ANYWHERE records the REPRESENTATION a floor came from** -- every
  determination above needed the source, so this is unauditable from artifacts today.
- **🔴🔴 07:05 -- THE DEGENERACY HYPOTHESIS BELOW IS NOW CONFIRMED FROM THE CELL'S OWN PERSISTED
  DIAGNOSTICS, AND IT MEANS THE HUMAN INSTRUMENT COULD NOT FAIRLY TEST `U1` AT ALL.**
  `report/OCCURRENCE_DATA_STATS`: **`n_occurrences_total` = 10,215, `n_occurrences_with_slot` =
  1,112. ONLY 10.9% OF OCCURRENCES ON THIS POPULATION CARRY THE SLOT INFORMATION THE TYPED ARM IS
  BUILT FROM.** And `report/ARM_DIAGS` gives `U1` **`vocab_size` = 10,121** dimensions. **That is
  ~8.6 SLOTTED OCCURRENCES PER WORD SPREAD OVER A 10,121-DIMENSIONAL SPACE.** *Nearly every pair of
  words shares no dimension at all, so nearly every cosine is zero and the arm collapses onto the
  constant-prototype value -- which is EXACTLY the 0.4125/0.4125 tie the audit spotted.*
  **THE CONTRAST INSIDE THE SAME RUN SETTLES IT: `U3_ROLE_ONLY` uses `vocab_size` = 58 -- DENSE --
  and reads 0.5037, at chance but NOT degenerate. Same corpus, same population, same 28,832 arc
  events; the only thing that changed is how thinly they were spread.**
  **WHAT THIS DOES TO BRANCH (B). THE BRANCH FIRED AS PRE-COMMITTED AND I AM NOT UNFIRING IT -- BUT
  ITS INTERPRETATION IS NOT SUPPORTED. "The 0.6669 was WORDNET-SPECIFIC" REQUIRES THAT THE HUMAN
  INSTRUMENT GAVE THE ARM A FAIR TEST, AND AT 10.9% SLOT COVERAGE IT DID NOT.** *The correct reading
  is much closer to 6.39's branch (C): **this population cannot test this arm.** The agent noted (C)
  "did not fire only because `U1` is not above chance" -- and a starved arm sitting ON its own
  constant floor is precisely how an untestable arm presents.*
  **WHAT IS STILL TRUE AND MUST NOT BE QUIETLY DROPPED: THIS DOES NOT RESCUE THE 0.6669.** That
  number died for an unrelated and still-standing reason -- **its bar was a bag-representation floor,
  and on a rebuilt arc floor a no-words attestation control reads 0.6317.** *Two independent defects,
  one per instrument; fixing this one does not touch that one.*
  **AND IT CONVERGES WITH THE BIOLOGY DRILL, WHICH REACHED THE SAME DIAGNOSIS FROM THE OTHER
  INSTRUMENT: "a median 130 arcs per word cannot populate 21,093 dimensions -- the lexical channel
  was STARVED, NOT FALSIFIED." TWO LANES, TWO POPULATIONS, SAME CAUSE.** *The typed channel has never
  once been given enough data to be tested, on EITHER instrument.*
  **HONEST SCOPE: I measured SLOT COVERAGE, which is the upstream CAUSE. I did NOT measure the
  pairwise-cosine spread, which is the direct SYMPTOM and is still the cleaner confirmation.** *I said
  I would not rewrite branch (B) before measuring, and I am recording a re-interpretation on
  different evidence than the check I named -- stronger evidence, but not the same evidence. The
  cosine-spread check stays open.*
- **🔬 [SUPERSEDED BY THE CONFIRMATION ABOVE] MY OWN FOLLOW-UP, HYPOTHESIS NOT FINDING -- THE ONE ITEM THE AUDIT FLAGGED AND LEFT UNVERIFIED,
  NOW CONFIRMED NUMERICALLY AND IT MAY RE-INTERPRET BRANCH (B).** In the human cell, `U1_TYPED_CONTEXT`
  reads **0.4125 [0.3148, 0.5138]** and `F_CONSTANT_PROTOTYPE` reads **0.4125 [0.3164, 0.5153]** --
  **IDENTICAL TO FOUR DECIMALS, different CIs** (so two genuinely different computations, not one value
  copied). **`F_CONSTANT_PROTOTYPE` IS BY DEFINITION WHAT YOU SCORE WHEN EVERY WORD HAS THE SAME
  VECTOR.** *So the live alternative to "typed context is bad at human similarity" is **"typed context
  produced near-DEGENERATE vectors on this 65-pair population"** -- which would make branch (B) a
  statement about COVERAGE COLLAPSE, not about the channel.* **CHEAP DECISIVE CHECK, NAMED AND NOT RUN:
  the pairwise-cosine spread of `U1`'s vectors on that population -- near-zero spread confirms
  degeneracy.** **DO NOT REWRITE BRANCH (B) UNTIL THAT IS MEASURED; an exact tie at n=65 is suggestive,
  not proof, and I have twice tonight promoted a suggestive number too early.**
- **🚨🚨 RETRACTION, 06:15 -- I HEADLINED "THE FIRST ARM EVER TO CLEAR THE BAR" AND TWO INDEPENDENT
  LANES TOOK IT APART WITHIN THE HOUR. THREE OF THE FOUR SUPPORTS ARE GONE. READ THIS BEFORE THE
  GREEN BLOCK BELOW, WHICH IS SUPERSEDED.**
  1. **THE BAR WAS THE WRONG BAR -- MY OWN RULE, BROKEN BY THE CELL AND MISSED BY ME.**
     `bfc0e941c` rebuilt the arms from the cell's persisted `arc_events`, **reproduced U1 0.6669 /
     U3 0.6466 exactly**, then recomputed the floors **on the arc representation the arms actually
     use.** An **ATTESTATION floor -- `log(min(arc_mass))`, NO WORDS, NO MEANING -- reads 0.6317
     [0.5820, 0.6781]**, effectively at the 0.6669 headline. The 0.5431 bar was a **BAG**-
     representation number imported across representations. *"EVERY FLOOR RECOMPUTED ON THE ITEM'S
     OWN POPULATION, NEVER IMPORT" is discipline (2) in this file, and the run imported one.*
     `U1_COVERAGE_MATCHED` could not catch it -- `COVERAGE_MIN=3` dropped **0 of 242 pairs**, so the
     control never bound.
     **WHAT SURVIVES, AND IT IS NOT NOTHING:** on a **mass-matched subsample (n=189, residual floor
     0.507)** the effect holds -- **U3 0.6369, U1 0.6284** -- and against **frequency-matched random
     noun pairs** U3 reads **0.5958 [0.5458, 0.6458]** vs floors 0.5141 / 0.5053. **A 64-bin role
     histogram with the words thrown away does carry real substitutability. It is a SMALLER, HONEST
     result standing on a REBUILT floor, not the headline I wrote.**
  2. **🔴 "SECOND INDEPENDENT NEGATIVE ON PREDICTION ERROR" IS RETRACTED OUTRIGHT -- I VERIFIED THE
     DEFECT IN SOURCE MYSELF.** `store_from_s1` and `store_from_s1_permuted_magnitude` both iterate
     **`rec["bag_counts"]`** (`experiments/exp_typed_role_context_write_rule_dissociation_v1.py`
     ~590-640, called at 954-957). **The prediction-error rule was applied to the BAG channel -- the
     one already known to be a pure co-occurrence detector at A0 0.0510 -- NOT to the typed channel.**
     That is why S1 0.0695 and N3 0.0591 sit right beside A0. **A null there says essentially nothing
     about whether an error signal helps the typed representation. PREDICTION ERROR ON THE TYPED
     CHANNEL HAS NEVER BEEN TESTED.** *I propagated this claim twice tonight.*
  3. **THE CORRUPTION-TOLERANCE EVIDENCE IS RETIRED.** `N6` replaces corrupted arcs by drawing from
     the marginal, which **adds a shared vector to every word -- near rank-preserving for a rank-sum
     AUC. THE CONTROL AS BUILT IS NEARLY INCAPABLE OF FAILING**, so "survives 50% corruption" was a
     property of the corruption model, not of the representation.
  4. **BRANCH (B) FIRED ON THE HUMAN INSTRUMENT (`16475c9c5`), EXACTLY AS PRE-COMMITTED AT
     `fa5da1d2c`: `U1_TYPED_CONTEXT` = 0.4125 [0.3148, 0.5138] -- BELOW CHANCE.** (`U3` 0.5037,
     `T2` 0.3567; bar 0.5943 **derived here, nothing imported**; both gates PASS.) **6.24 PARTIALLY
     RE-OPENS: the two instruments agree about the poor arms (rho 0.9034) and DISAGREE at the top of
     the range, which is the only region anyone cares about.** **THIS IS THE INFORMATIVE CASE AND IS
     NOT TO BE WRITTEN UP AS "MIXED".**
     **CONFOUND, FLAGGED BY THE AGENT AND NOT RESOLVED: that human population is 83% VERB pairs
     (108v / 18n / 4a) while the WordNet instrument is NOUNS-ONLY. "WORDNET-SPECIFIC" AND
     "NOUN-SPECIFIC" ARE NOT SEPARATED BY THIS RUN.** *A POS-stratified re-read is named, not run.*
  - **WHERE THAT LEAVES THE "WHICH KIND OF SLOT, NOT WHICH WORD" READING -- THE TWO LANES DISAGREE,
    AND THE DISAGREEMENT IS THE POINT.** The OBSERVATION replicates on both sticks (`U1-U3` NOT
    separated: +0.0203 [-0.0185, 0.0591] WordNet, **-0.0911 [-0.2014, 0.0192] human**). But
    `bfc0e941c` argues the tie is **DATA POVERTY, NOT A FINDING: a median 130 arcs per word cannot
    populate 21,093 dimensions, so the lexical channel was STARVED, NOT FALSIFIED** (effective code
    is **~3 relation bins**; top-3 gives 0.6240 of U3's 0.6466). **A starved lexical channel would
    tie on BOTH instruments too, so replication does not discriminate.** *The observation stands;
    my interpretation of it does not follow. I stated it as the finding twice.*
  - **🧠 THE BIOLOGY PUTS THE WHOLE NIGHT IN A DIFFERENT FRAME (PINNED, and the most useful thing
    anyone produced tonight): taxonomic (ATL) and thematic (pMTG/TPJ) systems DOUBLY DISSOCIATE.
    OUR INSTRUMENT *IS* THAT DISSOCIATION MEASURED IN A CORPUS, AND THE WINNING ARM IS THE THEMATIC
    ORGAN DOING THE TAXONOMIC ORGAN'S JOB.** Coarse frames drive **CATEGORY** induction unsupervised
    (Mintz 2003); syntactic bootstrapping shows frames **CONSTRAIN** a meaning hypothesis, they do
    not **SUPPLY** it. **So role profile = STAGE ONE, grounded cross-modal convergence = STAGE TWO --
    WE BUILT STAGE ONE AND SCORED IT ON A STAGE-TWO INSTRUMENT.** *That, not the AUC, is the finding
    worth keeping.* **OPEN (do NOT write as pinned): whether role is coded SEPARATELY from filler --
    F&G's own ROIs reanalyse as non-orthogonal, and Fedorenko 2020 finds NO syntax-selective region.*
- **[SUPERSEDED BY THE RETRACTION ABOVE -- KEPT SO THE OVERCLAIM STAYS VISIBLE] LANDED 05:36
  (2026-08-18) -- `exp_typed_role_context_write_rule_dissociation_v1` (`5170c7751`).**
  Instrument re-licensed IN THIS RUN (all 8 cached DSI checks reproduced at delta 0.0000, floors at
  chance, **n=242 per cell** -- not the n=7 of the human v1 attempt). **Matching is per-POS-stratum,
  so SET_P/SET_S cannot differ in POS by construction.**
  **`U1_TYPED_CONTEXT` 0.6669 [0.6184, 0.7136] vs incumbent bag-of-words `A0` 0.0510** -- and the
  three mandatory controls all held: beats `N1_LABEL_PERMUTED` **+0.1105 [0.0800, 0.1420]**, beats
  `N2_RANDOM_TYPING` **+0.1068 [0.0696, 0.1449]**, and `U1_COVERAGE_MATCHED` is 0.6669, unmoved.
  **READ THE MARGINS FROM THE PAIRED-DIFFERENCE CI, NOT FROM WHETHER THE TWO ARMS' OWN CIs OVERLAP**
  -- I misread overlap as "not separated" while checking this, and the two tests disagree.
  **BUT `STOPIF3` FIRED AND IT DOWNGRADES THE HEADLINE: `U3_ROLE_ONLY` 0.6466 TIES `U1`**
  (+0.0203 [-0.0185, 0.0591], NOT separated), and an independent parse-noise sweep **barely moved the
  score -- 0.667 -> 0.651 with 50% of the parse neighbours CORRUPTED.** *If half the neighbours can be
  wrong and the answer survives, the specific typed neighbours are not what is carrying it.*
  **THE HONEST CLAIM IS THE COARSER ONE: most of the signal is WHICH KIND OF SLOT a word fills, not
  WHICH WORD fills it.** `T2_UNTYPED_SAME_COVERAGE` 0.6128 clears the bar on its own -- selection
  carries the bulk -- with the type label adding a real but small CI-separated increment
  (**+0.0541 [0.0339, 0.0753]**). **DO NOT WRITE "GRAMMAR CARRIES SUBSTITUTABILITY."**
  **SECOND INDEPENDENT NEGATIVE ON PREDICTION ERROR:** `S1_SLOT_COMPETITION` 0.0695 does NOT beat
  `N3_MAGNITUDE_PERMUTED` 0.0591 (+0.0104 [-0.0069, 0.0289]). *That is now twice, on different
  mechanisms.*
  **AND 6.38's PREMISE REPLICATES ACROSS CORPORA:** `T3_COMBINED` (the published Komninos &
  Manandhar window+dependency pattern) **HURT in both corpora** -- 0.3533 here, **-0.3136
  [-0.3476, -0.2812] vs `U1` alone**, and 0.2264 on SimpleWiki. **Concatenating an anti-correlated
  channel is now a two-corpus finding, not a one-off.**
  **CORRECTION TO MY OWN 93d54ba72, MADE 10 MINUTES EARLIER: I claimed this run's stdout log lagged
  its `units.jsonl` because stdout was block-buffered. THAT WAS WRONG.** Re-checked at 05:34: both
  mtimes 2 min ago, in sync. The 11-minute gap I saw was **PRINT CADENCE** -- the occdata stage prints
  every 100 words, and 381 units sat between the 300 and 400 marks. *There is no buffering defect;
  `units.jsonl` mtime is still the better liveness signal, but the log is not lying.*
- **🟢 LANDED 05:44 -- `exp_dissociation_score_instrument_human_v4` (`75e093747`). THE 6.24 WORDNET
  CAVEAT IS DISCHARGED. VERIFIED OFF DISK BY THE DIRECTOR, NOT TAKEN FROM THE AGENT'S PROSE.**
  **rho = 0.9034 at 24 arms, bootstrap-of-arms 95% CI [0.7548, 0.9676] -- EXCLUDES ZERO**, against
  rho 0.7857 / CI **[-0.0435, 1.0]** at 7. **Pre-committed branch (i) fired.** *The arm count really
  was the limit: with 7 arms the CI could not separate from zero at any estimate quality.* Both
  regression gates PASS (DSI 8 checks at tol 0.0005; v3 floors + n=65 bit-for-bit).
  **WHAT THIS BUYS: every Organ A conclusion rested on an instrument built from WordNet, and the fear
  was that we had only ever measured AGREEMENT WITH WORDNET. Two independently-built instruments --
  one from WordNet, one from published HUMAN similarity ratings -- now rank our 24 arms the same way.
  ORGAN A'S CLOSURE IS A FACT ABOUT OUR STORE.**
  **🚨 BUT READ THE HUMAN ARM TABLE BEFORE CELEBRATING: ALL 24 ARMS SIT AT OR BELOW CHANCE ON HUMAN
  JUDGEMENTS.** The two best straddle 0.5 and clear nothing -- `F1_NO_FILTER` [0.4542, 0.6508],
  `T1_TYPED_ROLE` [0.4054, 0.6057] -- and the human bar is **0.5943**. *Agreeing about the ordering of
  24 arms is not the same as any arm being good; the instruments agree that they are all poor.*
- **🎯 THE OBVIOUS NEXT TEST, AND NOBODY HAS RUN IT: `U1_TYPED_CONTEXT` (0.6669, the only arm ever to
  clear the WordNet bar) IS NOT IN THE 24.** It landed at 05:36; the harvest was already built. The
  `T1_TYPED_ROLE` in the table is the **SimpleWiki** arm, a DIFFERENT cell. **So the one arm that
  cleared a bar has never been scored against human judgement.** v4 now has the harvesting machinery,
  so this is cheap. **rho = 0.9034 predicts it should replicate -- WHICH IS EXACTLY WHY IT IS WORTH
  RUNNING: a pre-committed prediction that can FAIL.** *Recorded, deliberately NOT dispatched --
  CLAUDE.md's rule is that an agent report ends my involvement and the owner decides what happens
  next.*
- **🔵 IN FLIGHT NOW (07:20) -- `typed-density-sweep`, THE ONE LANE RUNNING. DO NOT RESPAWN.**
  Sweeps the typed channel's density by coarsening `(neighbour, relation, direction)` binning from
  ~10,121 dimensions toward `U3`'s 58, **recomputing every floor PER CONFIGURATION on that
  configuration's own representation.** **Branches PRE-COMMITTED at `0504bfd00` (plan 6.41) BEFORE
  dispatch -- READ THEM BEFORE READING ITS RESULT:** *(α) some density clears its own rebuilt floor
  -> the channel was starved, and **the occurrences-per-dimension at which it turns on IS the
  finding, not the AUC**; (β) nothing clears anywhere -> it does not carry substitutability at any
  density reachable **on THIS corpus** -- **state the corpus and range, do NOT call it impossible**;
  (γ) it clears only once coarsened onto `U3` -> **role identity is the carrier, typed context adds
  nothing, headline is `U3`** -- pre-committed as **the branch I expect to dislike**, and it must not
  be softened.*
  **IT WAS TOLD TO COPY THE WRITE-RULE LADDER'S PER-ARM FLOOR PATTERN AND EXPLICITLY *NOT* THE CELL
  THAT IMPORTED 0.5431.**
- **📋 BOARD FELL 13 -> 3 WITH NO OWNER INPUT THIS SESSION. NOTED, NOT CHASED.** *Consistent with the
  seven duplicate `rm`-denial questions being auto-closed -- which is what the triage predicted would
  happen once the underlying fault stopped recurring -- but **I have not verified that** and it
  should not be reported as if I had.*
- **[LANDED -- kept for the compaction reader] IN FLIGHT (2 lanes, both dispatched 05:50-05:55). DO NOT RESPAWN EITHER -- a duplicate is the
  more expensive error, and I made exactly that mistake twice tonight.**
  1. **`U1` ON THE HUMAN INSTRUMENT** -- scoring `U1_TYPED_CONTEXT`, `U3_ROLE_ONLY` and
     `T2_UNTYPED_SAME_COVERAGE` against human similarity ratings (n=65, bar **0.5943**). **Its
     branches were PRE-COMMITTED at `fa5da1d2c` BEFORE dispatch -- plan 6.39. READ THEM BEFORE
     READING ITS RESULT.** *(A) clears CI-separated -> holds on two independent instruments;
     (B) at or below chance -> the 0.6669 was WordNet-specific, rho 0.9034 was carried by the poor
     arms, instruments DISAGREE where it matters, 6.24 partially RE-OPENS -- **the informative case,
     NOT "mixed"**; (C) above chance but not separated -> **`POWER_INSUFFICIENT`, NOT a ceiling.***
  2. **BIOLOGY DRILL: role vs filler** -- how cortex represents a word's grammatical role, whether
     role is coded separately from the word filling it, and **whether our coarse corruption-tolerant
     role profile REPLICATES something real or is a symptom of an impoverished encoding.** *That
     second reading is the one that would deflate tonight's result, which is why the drill was told
     to argue both.* Writes a note only; touches no cell.
- **⚠️ WHY (C) IS A LIVE OUTCOME, NOT A HEDGE: the human population is n=65 against the WordNet
  instrument's n=242 -- 3.7x smaller -- and v4's human CI half-widths run ~0.10, WIDE ENOUGH TO
  SWALLOW THE ENTIRE 0.6669-vs-0.5943 MARGIN BEFORE ANY CAPABILITY QUESTION IS ASKED.** *Do not let
  a width be read as an effect in either direction.*
  **This is NOT evidence it is dead.** I misread agent silence as death twice tonight and was wrong
  both times -- once standing down a healthy agent that was authoring a 58 KB cell. **Do not respawn
  it; a duplicate is the more expensive error.**
  **NEITHER MAY BE HEADLINED ALONE.** Pre-commitment 6.35 governs (a): it is one half of a
  cross-corpus PAIR with the landed SimpleWiki arm, and *"one of two independent tests is not a
  result"*. **If the two DISAGREE that is the informative case and must NOT be reported as "mixed".**
- **SUPERSEDED IN-FLIGHT NOTE (2026-08-18 ~04:45):** (a) **typed-role write rule** (re-dispatched tight after the
  first attempt stalled an hour on my own over-broad enumeration instruction); (b) **frequency-
  stratified matcher** -- matches WITHIN frequency bands instead of one global caliper, to fix the
  n=7 cause above. **Its gate is unchanged: if it buys n but ANY floor leaves chance, it is REJECTED
  as a worse matcher.** A bigger sample of an unlicensed instrument is worse than no sample.
- **SUPERSEDED IN-FLIGHT NOTE (2026-08-18 ~04:20):**
  (1) **`typed-role write rule`** -- the FIRST arm in ~15 experiments to use the GRAMMATICAL RELATION
  rather than an unordered bag of words. *Every prior arm varied WHICH words counted or HOW they were
  weighted; none used the role label.* Uses `data/selectional_preferences_v1/` (41,529 verb+ROLE
  slots, 90.0% coverage of the 617 scored words, no WordNet, no LLM). Carries an UNTYPED
  same-coverage twin so a win cannot be credited to TYPE when it is really SELECTION, plus
  label-permuted / magnitude-permuted / coverage-matched controls (SET_P 218 vs SET_S 185 coverage
  asymmetry is the flagged artifact risk).
  (2) **`human instrument v2`** -- rebuilt on ITS OWN population after v1 collapsed to **n=7**. That
  collapse was a DESIGN error, not sampling: the deciding statistic is a RANK CORRELATION OVER ARMS,
  which does not require shared ITEMS, and restricting to the WordNet instrument's 617 words threw
  away ~550 of 573 usable SimLex pairs. **Absolute AUCs will NOT be comparable across the two
  instruments -- ONLY the ordering.** See `PLAN_ORGAN_STEP_LADDERS` 6.30.
- **DISK IS FINE (checked 04:20):** one KB staging dir at ~0 MB (not the documented 10.65 GB
  runaway), 456 GB free. The main director KB is **16.4 GB** and answers every query with nothing.
- **🚨 THE MANDATORY PRIOR-WORK CHECK IS NON-FUNCTIONAL. `CLAUDE.md`'s SESSION STARTUP RITUAL TELLS
  YOU TO RUN IT AS "THE LOAD-BEARING FIRST ACTION". DO NOT TRUST ITS ANSWER.** Measured 2026-08-18,
  both interpreters, twice: `tools/substrate_query.sh` and `tools/director_kb_query.py` **return ZERO
  BYTES and exit 0** after ~38-51 s. Bare `python` resolves fine (3.12.10), so this is NOT the
  venv trap and NOT a hang -- the tool runs, prints nothing, and reports success. **AN EMPTY RESULT
  IS NOT EVIDENCE OF ABSENCE**, and this project has a standing rule that an absence claim requires
  an ENUMERATION. **Every "not a rediscovery" claim made through this tool is unsupported.**
  **DO INSTEAD, and SAY WHICH YOU DID:** `ls notes/ | grep -i <topic>` then READ the hits; `os.walk`
  over `data/` for `metrics.json`, then reconcile to the registry, never the reverse.
  **PROVEN COST:** enumerating by hand on 2026-08-18 found `exp_pc1_predictive_coding_residual_gate_v1`
  (2026-06-22) -- the SAME write-gate mechanism as `e822eeaaf`, uncited in its brief. *It turned out
  to REPLICATE tonight's null on a different substrate and instrument, which is a gain, but it was
  found by hand and not by the tool that exists to find it.* Header of `substrate_query.sh` carries
  the full measurement; a 25 s guard was added there and is marked **UNPROVEN** because its firing
  could not be demonstrated.
- **WRITE-RULE ORGAN, GATE STATE (2026-08-18).** `CODE` **EXONERATED TWICE** (`ac629b1e7` -- a learned
  basis is MATCHED by a same-rank RANDOM basis; nothing moves composition; drill 1's prediction is
  REFUTED). `ACCUMULATE` **GATED = the INTERFERENCE source** (`b6cad69ca`). **The DISSOCIATION
  INSTRUMENT IS LICENSED** (`0eb44eb1d`) -- four floors AT CHANCE and verified there, the first such
  instrument this programme owns; incumbent AUC **0.0710**, single-occurrence **0.4173**, above 0.5
  would mean substitutability. `FILTER` and `SUPERPOSE` are the two steps still UNGATED.
- **ONE AGENT LIVE:** `noncollapse-maxpool` -- the organ's decisive build. Scores MAX-over-occurrences
  vs the incumbent SUM on the licensed dissociation instrument, with `N1_MAXPOOL_RANDOM_OCC` as the
  control that decides whether any gain is the mechanism or merely the max operator. Do NOT edit
  `experiments/` or `hdlab/` while it runs. **It replaces `exp_organ_f_noncollapsing_accumulation_v1`,
  which was KILLED at ~9 h projected runtime (spherical k-means per anchor); that cell is on disk,
  self-tested, and is NOT the current attempt.**
- **THE OVERNIGHT LOOP IS FIXED AND VERIFIED (2026-08-18), after running exactly ONE turn for days.**
  Three defects, all real: the `Stop` hook was registered ONLY in `hd-instrument/.claude/settings.json`
  which is NOT the session's project root, so it never executed (canary silent since 08-13) -- now
  registered in `D:/AI/.claude/settings.json` beside the SessionStart hook that demonstrably fires;
  `_plan_path()` resolved only `PLAN_NEXT_12H.md`/`PLAN.md`, NEITHER OF WHICH EXISTS, so every
  continuation pointed at a missing file; and **GUARD 1 returned on `stop_hook_active`
  unconditionally, so the chain could continue ONCE and the cap of 200 was unreachable by
  construction.** GUARD 1 now continues while ARMED, bounded by the cap AND a 20 s wall-clock floor;
  DISARMED behaviour is unchanged. GUARD 1D narrowed to `permission-rule` + `user-rejected` only
  (owner ruling) -- `cancelled` teardowns are logged, never halt. Self-test OVERALL PASS.
- `.claude/scan-out/` REFUSES FILE CREATION (4x); `notes/ tools/ experiments/ verification/` accept.
  `experiments/exp_propose_reject_retrieval_v1.py` IS A BLOCKED PATH -- OWNER'S CALL, never retry a
  variant.
- NO BACKUP, gitignored: `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB).
  Also gitignored and citation-bearing: `scratch/sparsify_right_object/` (the Q13 sparsity numbers).
- Three `data/cornerstone_results/*/metrics.json` are deleted in the working tree but PRESENT in
  git (`39cc197ff`) -- recoverable, not lost; nobody has decided whether the deletion was intended.
- USER AUTH: `d=256->1024` (rewrites every anchor store; the phase-diagram pass says it is justified
  for the comparison job and NOT for addressing), merge to `origin/main`, any push. Autoloop ARMED
  at 200.
- `hd_director_kb_continuous_ingest` LIVELOCKED (10.65 GB, self-killed at 45 min) while the
  scheduler reports it healthy -- `director_kb_query.py` and `substrate_query.sh` are STALE and
  `substrate_query.sh` currently ERRORS on a locked cache file rather than returning no hits.
- **DATA HAZARD FOUND AND FIXED 2026-08-17 -- THIS ENTRY'S EARLIER WORDING IS SUPERSEDED.** It read
  "`notes/LONG_TERM_PLAN.md` HAS NEVER BEEN COMMITTED", which was true when written. **It is now
  TRACKED, committed unchanged at `0c8d202d7`** (`git log -- notes/LONG_TERM_PLAN.md` returns that
  one commit; the working tree is clean against it at 32,823 B). The hazard is closed; the staleness
  below is not.
- `LONG_TERM_PLAN.md` also stale: sec 2 rows 3/4/6 superseded by STORAGE + C30; sec 4's dual-hub
  `[PINNED]` (line 185) should drop to CONTESTED; its Phase 2 kill banner (line 343) is recorded as
  FIRED without the 8b(B) withdrawal-for-thematic. Director's call, NOT done here (PLAN sec 9).
- OVER CAP AND DELIBERATELY SO, AND THE GAP GREW AGAIN: **19,450 B against the 8,704 cap** (11,571 B
  on 08-16, 15,149 B after the first 08-17 docs pass, this figure after the third). The new growth is
  never-trim class -- five landed results, DO-NOT-REDO 44/45/46 each with a revival criterion, C36 --
  offset only partly by tier trims to PHASE DIAGRAM, BRIDGING and STORAGE. **`STATUS_SPEC.md` sec 7's
  own measurement is now stale by ~7.9 KB and BOTH of its options (raise to 12,288 B; move the stub
  index into an uncapped `STATUS_CLOSED.md`, which was sized to land this file at ~8,580 B) are now
  undersized -- re-measure before enacting either.** Still PROPOSED, NOT ENACTED: DIRECTOR'S CALL.
  Never close the gap by evicting a never-trim entry.
