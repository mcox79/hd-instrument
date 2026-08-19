# STATUS

AS OF: 2026-08-18 END OF SESSION | branch `dataprep/mcguffey-graded-corpus` | HEAD `a8b8a5d58` | GROWTH PAUSED | origin push needs USER AUTH | READ THE COMPACTION HANDOFF AT THE TOP OF ## POSITION AND STOP THERE
Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). Cap 8704 B, OVER -- see
WHAT IS RUNNING. FOUR literals MACHINE-PARSED, never reword: `AS OF:`, `## POSITION`, `## TOP ITEM`,
`## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` (**THE PLAN; READ SEC 6.18 FIRST -- it supersedes the
step hunt. 6.16 holds the PRE-COMMITTED decision branches; 6.15 the five gated steps**) ->
HERE -> `COMPACTION_HANDOFF_2026-08-17.md` -> `PLAN_NEXT_24H.md` -> `LONG_TERM_PLAN.md`.

## POSITION

# ⏱️ COMPACTION HANDOFF -- 2026-08-18 END OF SESSION. READ THIS BLOCK, THEN STOP AND ACT.
**Everything below this block is the session's working record and is 112 KB. DO NOT read it top to
bottom on recovery. This block is the entry point; the four artifacts it names are authoritative.**

## WHERE WE ARE, IN TWO SENTENCES
**The CLAIMS layer is mostly unverified: 30 vetted, 1 upheld, and 99.5% of the archive's 2,678
HARD_PASS carry neither a CI nor a null, so they cannot be checked from their own files.**
**The ORGAN layer is in genuinely good shape: 163/163 import, 83/87 self-tests pass, 0 constants
among the 13 largest -- and 67 organs are BUILT, SELF-TEST-PASSING, AND UNWIRED.**

## THE FOUR ARTIFACTS -- USE THESE, DO NOT RE-DERIVE THEM
| artifact | answers |
|---|---|
| `tools/experiment_index.py` | what exists in 8,834 cells. **Prints rows scanned BEFORE results**, so silence can never again read as absence. **REPLACES `substrate_query.sh`, WHICH RETURNS ZERO BYTES AND EXITS 0.** |
| `tools/verdict_evidence_gate.py --census` | which claims carry a CI + null (13 of 2,678) |
| `notes/VETTING_LEDGER.md` + `tools/vetting_ledger.py --cite NAME` | may I cite this, and with what narrowing attached? 1 WIRE / 12 WIRE_NARROWED / 4 RERUN_NAMED / 13 SHELVED_REFUTED |
| `notes/ORGAN_ACCOUNTING_2026-08-18.md` | what machinery works, what is unwired, what would be false coverage |

**PLAN = `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`, SECTION 7 (prepended; read it BEFORE sec 6).**

# ➡️ THE PLAN TO EXECUTE IS `notes/BUILD_PLAN_post_audit_2026-08-19.md`. OPEN IT AND START AT PHASE 0.
**It is self-contained, owner-approved, and written for exactly this handoff.** Phase 0 is one hour
(fix `situation_reader`'s import-time training; remove a scratch file from `hdlab/`; make the
dashboard show `UNVETTED` instead of a blank). Phase 1 wires Tier 0+1 (~75 s import). **PHASE 2 IS
THE ONE THAT MATTERS: an end-to-end can-fail test with a real floor and a scramble twin, because
every organ was validated ALONE and wiring ten together is exactly how the 0-for-30 claims layer
happened.** Phase 3 builds the empty slots. The ranked list below is the same plan in summary.

## NEXT STEPS, RANKED -- START AT 1
1. **WIRE THE SIX ORGANS BOTH AUDITS AGREE ON:** `hippocampal_encoder`, `cortex`,
   `information_foraging`, `coref`, `goal_owner_select`, `definitional_extraction`. **Recovering
   built machinery beats building new machinery.** Re-run `situation_reader`'s self-test with a
   >240 s budget first (it needs 204 s just to import) and add it if clean.
   **⛔ A PASSING SELF-TEST IS NOT SUFFICIENT: `atom_consultation` passes AND has `applied`
   hard-coded `False`; `definitional_predicate_v61` passes AND fires on 0.27% of its intended
   population. BOTH SIT INSIDE THE 67. WIRE ONLY THE INTERSECTION of self-test-passing AND
   probe-FUNCTIONAL.**
2. **MINE MIDDLE_BAND, NOT HARD_PASS.** 117 meaning-relevant, never read. **Building the queue from
   HARD_PASS SELECTED FOR OVER-CLAIMING** -- two cells found this session had MIDDLE_BAND as their
   honest tier while an over-claimed sibling took HARD_PASS. **Highest expected yield in the archive.**
3. **Fix `goal_achievement`** -- the one genuine self-test failure (`AssertionError: channel
   'relation:recur' != 'majority'`), and the SAME organ the constant-probe independently flagged.
   Two methods converged; that is the strongest signal in the organ layer.
4. **Remove `_scratch_orig_goal_owner_select`** from `hdlab/` and from the registry. It is a scratch
   file counted as recoverable capability.
5. **Re-rank the remaining claim queue by ITEM-PRIORITY** (below), not by evidence-carrying.
6. **No new verdict without** a CI, a null, a declared STRONGEST floor, and a statement of whether
   the items predate the mechanism.

## THE STRONGEST PREDICTOR, AND IT IS FREE
**DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID?** Every vetting survivor was scored on items
built independently of the rule; every pass-5 refutation had detectors authored against the items
they were scored on. **It beat every statistical signal tried. Ask it first.**

## MY FOUR ERRORS THIS SESSION -- ALL ONE FAULT, DO NOT REPEAT IT
1. "No prior work found" x3 -- from a tool that returns zero bytes and exits 0.
2. "25 results landed 08-17" -- my index dated cells by **file mtime**; 60 share one bulk-touch
   minute. True count 3. Now reads `ts_iso`.
3. "1,042 never run" -- a LOCAL-DISK claim. **At least 142 had run; 15 recovered from the remote.**
4. "31 organs self-test" -> ~82 -> **87 measured.** A too-narrow regex, corrected upward twice.
**EVERY ONE WAS AN ABSENCE CLAIM MADE FROM A SEARCH INSTEAD OF AN ENUMERATION.**
*Also: I twice framed the owner's WORKING process as a defect (the remote's intentional idleness,
the deliberate SSH-back of results). **Ask what the operator intended before naming something broken.***

## STANDING CONTEXT
Remote `marsh@home` idle **BY INTENT**; results deliberately SSH'd back to this laptop. Growth
paused. Origin push needs USER AUTH. `data/foundation/` READ-ONLY, one disk, NO BACKUP. Never bundle
a deletion with real work. Never `git add -A`.

---

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
**❌ MY STRATEGIC READ WAS "we have been running experiments that could not have returned a credible
positive, then treating the absence as evidence about the substrate." I TESTED IT IMMEDIATELY AND ON
THE HUMAN SIDE IT IS FALSE. RETRACTED, SAME SESSION, BEFORE IT COULD BE QUOTED.**
Classified all 24 human-side arms by whether their CI **upper** bound could even reach the credible
bar 0.6918: **24 of 24 CANNOT. ZERO are undetectable. EVERY ONE IS A REAL NEGATIVE.** The best arm
`F1_NO_FILTER` tops out at **0.6508** and the runner-up `T1_TYPED_ROLE` at **0.6057** -- both short
of 0.6918 *even in the most favourable corner of their own error bars.*
**SO BOTH THINGS ARE TRUE AND THE SECOND DOMINATES: the human instrument IS underpowered (it demands
>=0.69), AND our arms are so far below that the power problem does not rescue a single one.** *I
reached for an instrument-level excuse for a substrate-level result; the excuse does not survive
contact with the arm table.*
**WHERE THE POWER ISSUE GENUINELY BITES IS NARROW: arms sitting NEAR a floor -- which tonight means
exactly ONE, `U1_TYPED_CONTEXT` at 0.6669 against a 0.6810 credible bar.** *Discipline 18 is still
right and still binding; its SCOPE is "arms near the bar", NOT "our negative record generally".*
**AND THE OWNER'S QUESTION KEEPS ITS HONEST ANSWER: the negatives are mostly REAL. The instrument is
not what is holding us back -- what we are BUILDING is.**

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
**18 GATE ON THE FLOOR'S UPPER BOUND, NOT ITS POINT VALUE -- AND IF NO ACHIEVABLE SCORE COULD CLEAR
IT, THE POINT IS UNTESTABLE, NOT NEGATIVE.** A floor is an ESTIMATE and carries its own error bar, so
**CREDIBLE BAR = floor + its own 95% half-width.** Measured 08-18: WordNet 0.5431 -> **0.5944**;
human 0.5943 -> **0.6918**; the binding arc floor 0.6317 -> **0.6810**. *`U1_TYPED_CONTEXT` 0.6669
clears the floor and FAILS the credible bar -- this alone would have caught the night's retraction.*
**AND THE SECOND HALF IS THE ONE THAT CHANGES BEHAVIOUR: WHEN A FLOOR'S HALF-WIDTH IS SO WIDE THAT NO
ACHIEVABLE AUC COULD CLEAR ITS CREDIBLE BAR, THAT CONFIGURATION IS UNTESTABLE AND MUST NOT BE FILED
AS A FAILURE OF THE THING BEING TESTED.** *This is discipline 14 one level up: **a width in the FLOOR
is not a GATE.** Required per-cell n to tighten a floor: +-0.05 ~250-290, +-0.03 ~770, +-0.02
~1,550-1,780, +-0.01 ~6,300-7,200 -- **the human instrument runs at 65.*** **BEFORE BUILDING AN ARM,
DECIDE WHAT n ITS INSTRUMENT NEEDS; IF THAT n IS UNREACHABLE, THE ARM IS NOT YET WORTH BUILDING.**
*Never buy n by loosening the matcher -- a bigger sample of an unlicensed instrument is worse than no
sample.*
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
- **🚨🚨🚨 THIS DOCUMENT HAS BEEN DESCRIBING A TINY, ACCIDENTAL SLICE OF THE PROJECT. THE OWNER SAID
  SO AND THE INDEX PROVES IT. TREAT EVERY "WE HAVE NEVER" AND "NOTHING REACHES" CLAIM BELOW AS
  UNVERIFIED UNTIL RE-CHECKED AGAINST `tools/experiment_index.py`.**
  Measured 2026-08-18 off the newly built index (8,834 cells, 7,570 with verdicts):
  **2,678 HARD_PASS** (June 323 / July 2,193 / August 162), 1,369 HARD_FAIL, 1,068 MIDDLE_BAND.
  Excluding substrate-physics cells (capacity, scaling laws, binding, Hopfield), **236 HARD_PASS are
  MEANING-RELEVANT** -- June 14 / July 182 / August 40.
  **🔴 RETRACTED WITHIN THE HOUR BY THE VET (`a2e65896`): "25 HARD_PASS LANDED 2026-08-17" IS FALSE.
  THE TRUE COUNT IS 3, AND THE ERROR WAS MY OWN TOOL.** `experiment_index.py` dated cells by the
  metrics.json **FILE MTIME**. **Exactly 60 metrics.json share the minute 2026-08-17 17:44 and 3,850
  share 2026-07-03 14:28 -- BULK TOUCHES, NOT RUNS.** Their internal `ts_iso` says the six I vetted
  actually ran **2026-07-17 to 07-23**, and ZERO ran on 08-17. *A file's mtime is when it was last
  WRITTEN, not when the science happened; any copy, checkout or sync rewrites it.* **FIXED: the index
  now reads `ts_iso` first and records `date_source` per row.** *I told the owner we had ignored 25
  results the day after they landed. We had not. The July work was resurfaced by a touch.*
  **⚠️ AND THE FIX IS ONLY PARTIAL, SO DO NOT TRUST RANKING BY DATE YET: of 7,794 landed rows only
  **2,538 carry a `ts_iso`**; **5,256 STILL FALL BACK TO MTIME**. Two-thirds of the archive has no
  trustworthy run-date at all.**
  **[SUPERSEDED CLAIM, KEPT VISIBLE] "25 HARD_PASS landed 2026-08-17 and this document mentions none
  of them."** Among the cells named:
  `exp_read_grow_openvocab_fastmap_v1` (**learn NEW words WHILE reading instead of abstaining**),
  `exp_read_grow_oov_verb_extension_v1`, `exp_read_grow_foundation_realprose_glassbox_ie_v1`
  (*"THE SUBSTANTIVE READING STEP"*), `exp_online_knowledge_condenser_selectional_v1`
  (**condenses generalizable knowledge as it reads**), `exp_role_filler_factorization_compgen_v1`
  (brain-faithful structure-content factorization), `exp_three_factor_eligibility_distal_credit_v1`
  (**a three-factor eligibility trace solving DISTAL CREDIT ASSIGNMENT**),
  `exp_reward_contingency_credit_assignment_v1`, and
  `exp_relational_vs_similarity_conflict_viability_probe_v1` (**GREEN_LIGHT_PENDING_VET -- the
  taxonomic-vs-thematic conflict**).
  **THE MOST EMBARRASSING SPECIFIC: I SPENT 2026-08-18 CONCLUDING "THE MISSING INGREDIENT IS A
  LEARNING SIGNAL" AND "WE HAVE NEVER BUILT THE TAXONOMIC ORGAN". A THREE-FACTOR LEARNING RULE AND
  A RELATIONAL-VS-SIMILARITY PROBE BOTH HARD_PASSED THE PREVIOUS DAY, AND
  `hdlab/random_indexing.py` -- AN EARNED DISTRIBUTIONAL ORGAN -- HAS EXISTED SINCE 2026-08-06.**
  **⚠️ THE DEFLATION, AND IT IS NOT OPTIONAL: A HARD_PASS IN THIS PROJECT IS A CLAIM, NOT A
  CAPABILITY.** Five apparently clean wins died to their own controls in ONE session on 08-18, one
  of these 25 is explicitly `PENDING_VET`, and this file already records 21 arms suspended for a
  mis-imported bar. **THE CORRECT STATEMENT IS: A LARGE BODY OF CLAIMED POSITIVE RESULTS EXISTS THAT
  OUR POSITION DOCUMENT IGNORES, AND IT NEEDS VETTING -- NOT THAT WE HAVE 2,678 WINS.**
- **🟢🟢 VETTING PASS 5 (`ae41755a`) -- *** THE FIRST UPHELD RESULT IN 30 VETTED CELLS. ***
  1 UPHELD, 2 QUALIFIED, 1 SUSPENDED, 2 REFUTED.**
  **✅ UPHELD -- `exp_agreement_depth_productivity_generalization_v1`. IT GENERALISES, AND THE SPLIT
  IS ASSERTED IN CODE.** A learned function-word accumulator **supervised ONLY on depth<=1**, tested
  on **2,597 HELD-OUT depth>1 Linzen items: 0.7324 [0.7154, 0.7494]** against the strongest floor
  ACTUALLY RUN (majority 0.5741, upper bound 0.5931) -- **margin +0.1223 READ FROM THE CI LOWER
  BOUND.** Still holds out-of-distribution at **depth 4+: 0.6810 [0.6462, 0.7111]** vs majority
  upper 0.5751. Real seed spread (not one measurement printed n times); scramble drops 0.2947 and
  changes 86.5% of decisions; five filters removed 350 / 289 / 518 / 9,887 / 7,122 items, so the
  controls BIND. No LLM on the path.
  **⚠️ ITS HONEST CEILING, STATED BY THE AUDITOR AND NOT TO BE DROPPED: IT *TIES* THE HAND-WRITTEN
  RECURSIVE RULE (0.7312). IT DOES NOT BEAT IT.** *So: a learned mechanism reaches parity with the
  symbolic rule it was meant to replace, generalising to depths it never saw. That is a real result
  and a bounded one.*
  - **QUALIFIED -- `exp_graded_divisive_comparator_v1`:** real +0.0602 [0.0440, 0.0762] with a
    scramble twin at 0.5065, **but the CI lower bound does NOT clear its own pre-registered
    `d >= 0.05`, and the "divisive normalisation" half of the title contributes +0.00175.**
  - **QUALIFIED -- `exp_read_xsent_coref_scene_protagonist_v1`:** the gain is real (0.2462 -> 0.4003,
    McNemar CI lower +0.1039) **but the mechanism is a 5-sentence window, not "scenes" -- the cell
    says so itself.**
  - **SUSPENDED -- `exp_multi_turn_loop_realtext_nphead_gate_v1`:** "true zero confident-wrong" is
    **0 wrong of 18 kept** (rule-of-three upper bound 0.167) against a declared band of 0.01, and its
    one new variable fired on **two items that are the same passage, same answer, same gold** -- n=1.
  - **REFUTED -- `exp_social_relational_grounding_axis_v1`: THE SUBSTRATE CANNOT CHANGE ANY
    PREDICTION.** `valence` takes exactly **three distinct values across all 12 items**, and
    `acc_real` equals the WordNet `dictionary_lookup` accuracy **EXACTLY** (10/12). It is a 3-entry
    lookup table wearing a substrate.
  - **REFUTED -- `exp_desiderative_negation_channel_v1`: 8 OF 8 RECOVERIES LIE INSIDE THE 10-ITEM SET
    THE TAXONOMY WAS DESIGNED FROM, AND 0 OF 27 NON-DESIGN ITEMS RECOVERED.** The channel is
    **bit-identical ON vs OFF on both full benches** (n=80: 0.6992/0.6992; n=160: 0.6623/0.6623).
- **🚨 A BUG IN MY OWN GATE, CAUGHT BY THE AUDITOR, AND I HAD ALREADY QUOTED ITS NUMBER TO THE OWNER.**
  `CI_PAT` contained a bare `confidence`, which matched `lookup_confidence` and
  `high_confidence_idxs` -- model confidences, not intervals -- so two cells computing NO interval
  entered the "best evidenced" shortlist. **CORRECTED FIGURES: 28 carry a CI (not 52), 13 carry BOTH
  a CI and a null (NOT 26), and EVIDENCE_INSUFFICIENT is 2,665 = 99.5% (not 99.0%).** *The direction
  was right and the shortlist was half the size I said.*
- **🎯 THE BEST PREDICTOR IS NOT EVIDENCE-CARRYING, AND THIS IS THE MOST USEFUL THING FIVE PASSES
  PRODUCED: WHAT SEPARATES THE SURVIVORS FROM THE FAILURES IS *** WHETHER THE TEST ITEMS EXISTED
  BEFORE THE MECHANISM DID. ***** The three that survived this batch were scored on items built
  independently of the rule; the three that failed had detectors authored against the very items
  they were scored on -- one docstring even names the specific token pair its rule was written for.
  **CARRYING A CI IS NECESSARY AND WEAK; ITEM-PRIORITY IS THE STRONG TEST, AND IT SHOULD BE THE
  FIRST QUESTION ASKED OF EVERY REMAINING CLAIM.**
- **🔬🔬🔬 VETTING PASS 4 (`a6e60cfa`): 3 REFUTED, 1 SUSPENDED, 2 QUALIFIED, 0 UPHELD.
  RUNNING TOTAL OVER 24 CELLS: 11 REFUTED, 4 SUSPENDED, 9 QUALIFIED, *** ZERO UPHELD ***.**
  - **🚨 THE CAUSAL-LINK RESULT IS PROVEN CONTENT-FREE, NOT MERELY SUSPECT. The auditor RE-RAN the
    organ WITH THE GOLD LINKS REPLACED BY ARBITRARY RANDOM PAIRS AND GOT `organ_integration =
    0.9722` -- BIT-IDENTICAL TO THE HEADLINE.** The cell writes `add_causal_link(cause, effect)` for
    every gold item and queries the same indices back; no text is read (its own label is
    "GOLD-ISOLATION"). **It measures FHRR write/read fidelity at bundle-load 2 and nothing else.**
    **⛔ AND THE BASELINE WAS TUNED UNTIL IT FAILED.** The cell's own comment records sweeping
    distractor density from 200/20 to 15/10 to find *"the smallest min_dist that keeps mr_control >=
    the 0.50 can-fail floor WHILE DRIVING mr_integration TO 0.0000"*. **That is a gate adjusted
    until it passed. All three siblings die together: `pilot_v1`, `fuller_v2`, `fuller_v3_cleaned`.**
  - **REFUTED -- `exp_unified_self_learning_loop_v3`: ITS OWN SCRAMBLE CONTROL BEAT IT.** MAIN LOW
    gain **0.0243** vs SCRAMBLED **0.0288** -- scrambled text learns MORE. Every separation gate is
    `HP_CONTROL_SEP = 0.0` and `CONTRAST_EPS = 0.0`: **a margin of literally zero.** Its own
    label-shuffle null on the same slice wobbles **0.0258** cycle-to-cycle, larger than the entire
    claimed gain. Two arms are one measurement (`NO_READ` and `READ_NO_SLEEP` share the store digest
    `c23b44bc…`). **AND `..._loop_v4`, LANDED FIVE HOURS LATER THE SAME DAY, RECORDS
    `teaches_new=False` AND CARRIES v3's OWN NUMBER AS A CONTROL THAT FAILS. v3 WAS ALREADY DEAD AND
    WAS STILL SITTING ON THE QUEUE AS HARD_PASS.**
  - **QUALIFIED -- `exp_pivot_selectional_knowledge_richness_2afc_v1`: THE TABLE IS THE ANSWER KEY.**
    Its 117 rated pairs and its 59 items x 2 fillers = 117 evaluation pairs are a **PERFECT
    BIJECTION** (eval-not-rated 0, rated-not-in-eval 0): an LLM rated EXACTLY THE TEST. *Offline
    LLM-built foundations are admissible under the owner's ruling, but a table whose vocabulary IS
    the eval is an ORACLE, not a foundation.*
    **✅ THE PART THAT SURVIVES AND MATTERS: the dumb twins DO NOT reproduce it** -- verb-noun
    `Counter` 0.5508, noun frequency 0.5339, length 0.4915. **So the knowledge is REAL and ABSENT
    FROM OUR CORPUS. Honest claim: a cheating oracle reaches 0.78-0.85 on these 59 items and THE
    SUBSTRATE DID NONE OF IT.** *Convention was never declared: tie->0.5 gives 0.8136, tie->loss
    0.7797, tie->win 0.8475.*
  - **SUSPENDED -- `exp_outcome_valence_goal_congruence_v1`: THE DUMBEST RULE SITS EXACTLY ON THE
    BAR.** "Predict MET iff the goal's infinitival verb lemma equals the outcome verb's lemma" --
    no referent, no NP head, no registry -- scores **7/8 = 0.875, precisely the pre-registered
    HARD-PASS floor.** Mechanism 8/8 beats it by ONE item; CIs overlap; P(8/8 | p=0.875) = 0.34.
    *Its v2 reaches 1.0 at N=22 and self-tiered MIDDLE_BAND -- the honest tier v1 should have had.*
  - **QUALIFIED -- `exp_learned_argstruct_parser_lccp_independent_gold_v1`: THE WRONG COMPONENT IS
    CREDITED.** Arm B (cue-competition, **no LCCP**) already clears EVERY gate; adding the LCCP
    prior moves F1 0.3934 -> 0.4048, two items. **Its "generalization" gate is ONE-SIDED and fired
    because held-out precision (0.632) EXCEEDS seen (0.449) -- an EASIER held-out subset, not
    generalization.** *"Independent gold" means independent of reader output; the annotator was the
    authoring agent, same day, single pass. Absolute performance: P=0.50, R=0.34.*
  - **🚨🚨 THE CROSS-CUTTING FINDING, AND IT IS THE ONE THAT EXPLAINS THE 0-FOR-24: NOT ONE OF THESE
    SIX CELLS COMPUTED A SINGLE CONFIDENCE INTERVAL, NULL DISTRIBUTION OR p-VALUE.** Grepped for
    `confidence|ci_low|bootstrap|p_value|binomtest|permutation|half_width`: two hits, both unrelated
    words. **EVERY HARD_PASS IN THIS BATCH IS A POINT ESTIMATE COMPARED TO A POINT ESTIMATE, SEVERAL
    AT GATE MARGINS OF EXACTLY 0.0.** *That is not a scoring accident; it is the archive's method.*
- **🔬🔬 VETTING PASS 3 (`a04ef6b9`): 4 REFUTED, 2 QUALIFIED, 0 UPHELD. RUNNING TOTAL OVER 18 CELLS:
  8 REFUTED, 3 SUSPENDED, 7 QUALIFIED, *** STILL ZERO UPHELD AS CLAIMED ***.**
  **AT 0-FOR-18 THE PRIOR HAS MOVED: A HARD_PASS IN THIS ARCHIVE SHOULD BE READ AS "UNVERIFIED
  CLAIM", NOT AS EVIDENCE. THAT IS NOW A MEASURED BASE RATE, NOT A CAUTION.**
  - **REFUTED -- `exp_gap_driven_reader_controlled_v1`: A 12-LINE `Counter` WITH NO SUBSTRATE
    REPRODUCES THE HEADLINE 8/8 EXACTLY.** Ranking co-occurring unknown words by raw count scores
    1.0000, identical to the treatment. *The templates write the target into 2 of 2 intro sentences
    and the distractor into 1 of 2 -- **the margin is AUTHORED**. Its "ablated=0.0000" arm replaces
    the novelty filter with noise, removing the candidate SET rather than changing the RANKING: an
    extreme lesion, not a matched control.*
  - **🚨 REFUTED -- `exp_reading_grounding_loop_cycle2_v1`: THIS PROJECT ALREADY REFUTED IT ON DISK
    AND THIS DOCUMENT NEVER CAUGHT UP.** `exp_reading_grounding_loop_cycle3_groundingfix_v1` records
    `B1_taut 0.656885 -> 0.0` and `B4_grounded 3544 -> 634`. Independently recomputed from
    `data/foundation/reading_grounding_v1/store/store_facts.json`: **2,328 of 3,544
    GROUNDED_MEANING facts are SELF-ANCHORED -- 67% of "grounded concepts" have THEMSELVES as their
    meaning.** Of the 1,216 real links the top anchors are `also` (31), `say` (15), `people` (10),
    with samples like `web -> polar` and `stargaz -> million`; 121 stem/full-form pairs
    (`cigarett`/`cigarette`) are counted as separate concepts.
    **⛔ RETIRE THE FIGURE "3,544 CONCEPTS / 9.87x THE HAND LEXICON" WHEREVER IT APPEARS.**
  - **REFUTED -- `exp_verb_class_openvocab_similarity_v1`: THE "HELD-OUT" SET IS FOUR VECTORS.**
    In `hdlab/verb_lexical_similarity.py` every desiderative word -- 10 seeds AND all 16 held-out --
    carries the SAME four hand-written tags. **Held-out similarity to its own class is EXACTLY
    1.0000, cross-class 0.0104. The 64 "held-out" decisions are 4 distinct vectors; accuracy 1.0 is
    AN IDENTITY, NOT GENERALIZATION.**
    **AND ITS CITED BASELINE DOES NOT EXIST AS QUOTED:** it claims owner-acc 0.30 from
    `exp_real_text_goal_owner_generalization_diagnostic_v1`, whose single copy on disk reads
    **0.6000** and was written AFTER this cell ran. **The claimed +0.20 is unreproducible.** *In its
    own landed numbers the organ scores 0.5 owner vs recency 0.7 and ties its own lexicon baseline
    on polarity -- it LOSES to one dumb baseline and TIES the other, inside a HARD_PASS.*
  - **REFUTED -- `exp_c5_multigoal_content_coherence_tiebreak_v1`: GOLD IS DEFINED BY THE RULE THE
    MECHANISM APPLIES.** Plain bag-of-words overlap scores **12/12 = 1.0000 under all three tie
    conventions with zero ties**; margin over the strongest floor is **0.0000**. The cell's own
    docstring says gold IS the unique theme-overlapper.
  - **QUALIFIED -- `exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1`: LEAK-CLEAN AND
    REAL, BUT NOT CI-SEPARATED.** It explicitly fixed a predecessor's gold leak and proves it with
    seven self-tests. **But its four floors are ALL POSITIONAL and read 0.0000 BY CONSTRUCTION**,
    while a lexical-overlap floor scores 0.80 / 0.675 depending on tie convention. System 20/20,
    Wilson lower 0.8389 vs the floor's upper 0.9193 -- **overlapping**; paired exact test on the one
    discordant item, p=1.0. *The auditor MEASURED THIS FLOOR AT 0.9839 FIRST AND CORRECTED ITSELF --
    that convention used roster-key order, which favours the owner. Both are reported.*
  - **QUALIFIED -- `exp_reading_grounding_loop_cycle1_v1`:** its context-scramble control BINDS
    (removed 132 of 185), but the same 67% self-anchoring applies, and its curriculum-order arm
    moved link-rate 0.3297 -> 0.3047 -- **a null shipped inside a pass**.
  - **✅ CLEAN ON TWO DIMENSIONS, AND WORTH SAYING: NO LLM in any operational path across six cells
    and four organs (grepped), and every cited path in this batch exists.** *But **NO CELL IN THIS
    BATCH REPORTS A p-VALUE OR A CI AT ALL**, and all three "3-seed" cells return bit-identical
    per-seed numbers BY DESIGN -- one measurement, printed three times.*
- **🔬 VETTING PASS 2 (`afb293f4`): 3 REFUTED, 3 QUALIFIED, 0 UPHELD. RUNNING TOTAL OVER 12 CELLS:
  4 REFUTED, 3 SUSPENDED, 5 QUALIFIED, *** ZERO UPHELD AS CLAIMED ***.**
  - **REFUTED -- `exp_causal_link_comprehension_fuller_v2`: THE ANSWER IS WRITTEN IN.** The cell
    calls `reg.add_causal_link(cause_idx, effect_idx)` for every item and then queries
    `query_effect_of(c_idx)` against `e_idx`. **That is write-then-read from a register at bundle
    load 2, and the two "baselines" NEVER RECEIVED THE WRITE**, so `most_recent=0.0000` and
    `random=0.0000` are STRUCTURAL, not measured. **NO COMPREHENSION WAS TESTED.** *What is
    actually there is 91.7% exact-key retrieval at 697 slots [0.782, 0.971] -- an 8% error rate at
    load 2, which reads as a MILD NEGATIVE ABOUT THE STORE.*
  - **REFUTED -- `exp_pivot_scaled_seed_knowledge_table_v1`: A ZERO-KNOWLEDGE FLOOR COMPUTABLE FROM
    THE CELL'S OWN CACHE SCORES 1.0000 (108/108) AGAINST THE LLM TABLE'S 0.6898.** Its gold is the
    verb's most-frequent attested patient and its distractor a never-attested noun, so plain corpus
    attestation is perfect by construction. **AND SCALING CHANGED NOTHING: the scaled and tiny
    digests are IDENTICAL (`5df85d80df03d57b`), `arms_differ_verified=False`.** *Surviving: LLM
    ratings do carry attestation signal (+0.1852, p=0.0054, n=108). That is not the claim made.*
  - **REFUTED -- `exp_read_grow_adaptor_pyp_kn_breadth_v1`: THE GATE CANNOT FAIL.** `kn_covered =
    (count>0) OR (...)` is a STRICT SUPERSET of flat coverage by construction. **Its "3/3 seeds" is
    ONE measurement printed three times** (identical gain 0.037475 across seeds; the tables do not
    depend on the salt). A **Zipf-count null with no linguistic mechanism reproduces the preemption
    correlation** (-0.60 vs the observed -0.5639 against a -0.15 gate). **On the only genuine
    generalization test -- 132 unseen items -- KN scores 0.1439 vs its OWN scramble 0.1591, WORSE
    in 2 of 3 seeds.**
  - **QUALIFIED -- `exp_information_foraging_reading_v1`: A FLOOR-BEATER, NOT A SHELF-BEATER.**
    FORAGE genuinely beats RANDOM (185 vs 38 of 3000, z=10.1) -- **but FROZEN, the fixed schedule
    foraging exists to REPLACE, scores HIGHER (0.0743 vs 0.0617).** The headline compares only
    against RANDOM. *Any claim that the decision organ improved reading must say this.*
  - **QUALIFIED -- `exp_lexicon_coverage_audit_barrier2_v1`: the COVERAGE half is UPHELD EXACTLY**
    (independently re-implemented: 2077 sentences, 2605 verb tokens, 568 types; union 0.9893/0.9648;
    every figure reproduces to 4 dp). **The second half is a SINGLE-RATER, UNBLINDED LLM
    HAND-AUDIT BY THE AUTHORING AGENT OF THE PREDICTION IT WAS TESTING**, no inter-rater
    reliability. **Under the stricter rubric THE CELL ITSELF NAMES in `honest_limitations`, it is
    89/120 = 0.7417 [0.657, 0.812] -- BELOW its own 0.80 floor.**
  - **✅ QUALIFIED -- `exp_context_vector_signal_v1`, AND A LONG-OPEN QUESTION IS NOW CLOSED CLEAN.**
    CLAUDE.md records that its figure came from a run whose clean-slate teardown was DENIED and
    silently dropped, that the figure is LOAD-BEARING in MEMORY.md, and that closing it needs a
    clean-slate re-run. **IT DOES NOT: the heartbeat trace settles it.** `_start_marker` 22:49:29.5,
    reading pass logged from unit 0 (22:49:43) to unit 49 (22:53:01), `pass_elapsed_s=208.99`; the
    cache is checked BEFORE the pass and skips it on hit, so **unit-0 heartbeats PROVE a cache
    miss**, and the FULL run wrote to a different directory than the denied smoke.
    **CONTAMINATION DID NOT OCCUR -- DEMONSTRATED, NOT ASSUMED. NO RE-RUN NEEDED.**
    **⚠️ BUT TWO CORRECTIONS TO HOW IT IS CITED: (a) the HARD_PASS IS POST-HOC -- the pre-registered
    ceiling guard fired on SCRAMBLE_SENT 0.9984 and was AMENDED AWAY AFTER THE RUN; the
    prereg-literal verdict is MIDDLE_BAND. (b) STOP QUOTING 0.7830 vs 0.9984 -- it is
    ceiling-saturated, all three nulls sit at 0.995-0.999. QUOTE `argmax_in_own_window_rate` REAL
    0.2871 vs an EXACTLY BAG-MATCHED SCRAMBLE 0.0050 (informative_rate 0.416808 vs 0.416687).
    A RATE-MATCHED TWIN DOES NOT REPRODUCE IT -- the strongest control-passing result in the batch.**
- **🚨 A THIRD FLOOR-DEFECT CLASS, DISTINCT FROM THE IMPORTED-BAR ONE, AND IT IS THE MOST COMMON:
  THE CELL HAD A STRONGER FLOOR ALREADY COMPUTABLE FROM ITS OWN DATA AND DISCRIMINATED AGAINST A
  WEAKER ONE.** Three of six this pass: attestation at **1.0000**, a superset-by-construction
  coverage gate, and FROZEN at **0.0743**. **THE RULE IS NOT JUST "RECOMPUTE THE FLOOR ON THIS
  REPRESENTATION" -- IT IS "RUN THE STRONGEST FLOOR THE CELL'S OWN DATA SUPPORTS".**
  **AND AUDIT "N SEEDS" FOR SEED-DEPENDENCE: three identical numbers are one measurement.**
- **🔬 FIRST SIX VETTED (`a2e65896`, AUDIT-ONLY, all recomputed off disk from per-item arrays, never
  from `verdict_msg`). ONE REFUTED, TWO SUSPENDED, THREE QUALIFIED. NOT ONE IS UPHELD AS CLAIMED.**
  - **REFUTED -- `exp_base_reader_grounded_relations_coref_v1`.** Headline `coref_lift=0.714,
    p=0.000` is on **SEVEN questions**, and that p is **resample degeneracy**: bootstrapping 7 paired
    diffs gives (2/7)^7 = 0.00016. **Exact paired McNemar on the same 7: p=0.0625, which FAILS its own
    alpha.** Worse, **the cell RAN a real floor arm that scores 5/7 on that slice** -- full vs floor
    p=1.0000 -- and then did not use it as the discriminator. Its NOCOREF control removed **0** items.
    *Surviving secondary: relation_lift over all 25 items, full vs floor exact p=0.0215. That holds.*
  - **SUSPENDED -- `exp_read_grow_foundation_realprose_glassbox_ie_v1`.** Its only floor is a
    **HARDCODED LITERAL `1.0`** (line 749) imported from a DIFFERENT cell on a DIFFERENT corpus (23
    pre-cleaned tuples, where that cell's own docstring says accuracy is 1.0 BY CONSTRUCTION). No
    floor was ever run on this cell's 34 sentences. **This is the SAME defect that suspended 21 arms
    on 08-18 -- and it was already present in JULY.**
    **✅ AND THERE IS A v2 THAT IS THE REAL RESULT: `..._realprose_glassbox_ie_v2` -- 46 sentences,
    correct_rate 0.891 against a REAL STANDALONE baseline of 0.565, delta +0.326, hardcoded stub
    REMOVED. CITE v2. v1 SHOULD NOT APPEAR IN THIS DOCUMENT AT ALL.**
  - **SUSPENDED (UNDERPOWERED) -- `exp_online_knowledge_condenser_selectional_v1`**, the
    best-designed of the six: real held-out split, explicit leakage guard, 4,151 mining sentences.
    **But n=48. FULL 0.750 [0.6275, 0.8725] against a SHUFFLE floor of 0.650 -- the CI lower bound
    sits BELOW the shuffle mean. z=1.07, p=0.285. The "+0.10" is 4.8 items.** Its gate was a bare
    point estimate. **Separating 0.75 from 0.65 at 80% power needs n~350.**
  - **QUALIFIED -- `exp_read_grow_construction_induction_dop_fragments_v1`, and it is the STRONGEST
    thing in the queue.** Only cell on a real external corpus (UD English-EWT, 846 sentences).
    **Scramble binds HARD and is deprel-multiset-preserving: 2/124 vs 44/124, 0/156 vs 44/156, 0/171
    vs 50/171 across three seeds; CI-separated 0.355 [0.271, 0.439] vs scramble upper ~0.038;
    `split_overlap=0`.** *Narrower than "construction induction": the input is GOLD UD `upos`+`deprel`,
    so parsing is ORACLE-SUPPLIED, and the metric is COVERAGE, not correctness (tunable 0.508 /
    0.355 / 0.25 by min_count). Its own verdict says FEASIBILITY PROBE -- that is the honest label.*
  - **QUALIFIED (toy) -- `exp_read_grow_openvocab_fastmap_v1`:** real mechanism, **26 hand-authored
    sentences, 3 nonce words, 5 query cues**; `ABSTAIN_BASELINE=0.0` BY CONSTRUCTION; 5 seeds vary
    only the codebook, so **n=1 dataset**; no CI, no floor, no scramble. Its NO_CONFIRM control DOES
    bind (removed 2 false facts).
  - **QUALIFIED (sharply) -- `exp_read_grow_oov_verb_extension_v1`:** `OOV_VERB_BASE_LEX` (line 165)
    **hardcodes munch->eats, pursue->chases, dwell->live -- THE SAME TABLE GENERATES THE SENTENCE AND
    SCORES IT**, and `coverage_current_pooled = 0.0` by construction, so "+88.2pp" is a gain over a
    definitional zero. Real residue: the morphology inverter. Its OOS control removed **0** items.
  - **🎯 THE CHEAPEST FIX IN THE WHOLE BACKLOG, and it needs no new experiment: SEVERAL CELLS ALREADY
    COMPUTED THE RIGHT FLOOR AND THEN DISCRIMINATED AGAINST SOMETHING ELSE. RE-SCORE EVERY LANDED
    CELL AGAINST THE FLOOR IT ALREADY HAS ON DISK.**
  - **NO LLM IN ANY OPERATIONAL PATH (verified by import scan).** But state these wherever "grounded"
    is claimed: WordNet is LIVE in the coref cell's path supplying the animacy that drives
    resolution, beside a 28-entry hand override and a 13-entry name-gender table curated for those 7
    passages; the condenser's 29-entry seed table is LLM-built OFFLINE and read-only (admissible).
  **ROOT CAUSE, FIXED: `tools/substrate_query.sh` -- the MANDATORY prior-work check -- RETURNS ZERO
  BYTES AND EXITS 0, so every "no prior work found" report from every agent and from me was
  vacuous, and the position document got assembled from whatever I happened to stumble into.**
  Replacement `tools/experiment_index.py` (`dc408b95e`) indexes all 8,834 cells, answers in about a
  second, and **PRINTS HOW MANY ROWS IT SCANNED BEFORE ITS RESULTS**, so an empty answer can never
  again pass for an established absence. **QUERY IT BEFORE WRITING ANY "WE HAVE NEVER" SENTENCE.**
- **⏸️ HALTED ON A WEEKLY USAGE LIMIT (resets 1pm America/New_York). NOT a code, permission or design
  failure -- the scaling-curve cell was dispatched and its agent died on the API limit before writing
  anything. NOTHING IS RUNNING. NOTHING IS HALF-WRITTEN. NO PARTIAL ARTIFACT EXISTS TO CLEAN UP.**
  **RESUME HERE, AND THE WHOLE BRIEF IS ALREADY DECIDED -- DO NOT RE-DERIVE IT:**
  **BUILD: a CORPUS SCALING CURVE, not a single endpoint.** Rebuild the usage representation from
  `data/corpora/simplewiki/simplewiki_clean_v1.txt` at NESTED subsets -- ~0.6M (reproduces today's
  regime as the anchor), 2M, 6M, 20M, 42M tokens -- each smaller set a SUBSET of the larger so the
  curve is about SIZE, not about which text. Score every rung on the dissociation instrument.
  **REPORT MEDIAN CONTEXTS PER EVALUATION WORD at each rung -- that, not raw token count, is the
  quantity that governs a second-order statistic and it is what makes the curve interpretable.**
  **THE PRE-COMMITTED READINGS, decided BEFORE any number exists:** RISING and reaching ~0.5 by 42M
  -> scale was a genuine precondition we never met, and every "this mechanism does not work" verdict
  in this programme was reached where it COULD NOT have worked and must be RE-OPENED, not re-quoted.
  RISING but extrapolating to need MUCH MORE THAN ~50M -> **THE MACHINERY IS NOT BRAIN-FAITHFUL, and
  this is the MOST USEFUL outcome the cell can produce** (report the extrapolated requirement
  explicitly). FLAT -> supply was never binding; the mechanism answers the wrong question; scale
  hypothesis closed. NON-MONOTONIC -> the informative case; report it, do not smooth it.
  **WHY THE CRITERION IS BRAIN-FRAMED AND NOT AN EXCUSE (OWNER, and it is the point of the cell):**
  *"the brain doesn't need 600000 words - if we've set up the machinery right, shouldn't it work?"*
  A child hears on the order of millions of words a year and has real vocabulary by 4-6, so TENS of
  millions of tokens is roughly child scale. **623K is BELOW that -- we have been starving it, which
  is itself not brain-faithful. But needing 1e8-1e9 would be an ADMISSION THE MACHINERY IS WRONG,
  because no child gets that. That is what makes this falsifiable rather than a fudge.**
  **CONTROLS THAT ARE NOT OPTIONAL:** rank-matched null at EVERY rung
  (`tools/rank_matched_null_dissociation.py`) -- without it, a rise toward 0.5 is indistinguishable
  from information destruction, which is exactly the claim that was retracted today; all four floors
  AND the bar RECOMPUTED per rung (a bigger corpus is a DIFFERENT representation, so never import
  0.5431 / 0.5510 / 0.5943 / 0.6317); `F_SCRAMBLE` as a POLICY over >=500 permutations at the 95th
  percentile, reusing the fixed implementation already in
  `experiments/exp_crossview_convergence_hub_v1.py`; CI half-width AND null p95 beside every margin,
  with any rung whose half-width exceeds the chance-to-bar interval marked UNDERPOWERED rather than
  given a verdict; evaluation population HELD FIXED across rungs; checkpoint per rung (42M is a long
  run and must resume).
- **🚨🚨🚨 THE FINDING OF THE NIGHT, AND IT REFRAMES EVERY NEGATIVE ABOVE: WE HAVE BEEN MEASURING
  EVERYTHING ON 623,522 TOKENS. THE METHODS WE KEEP TESTING COME FROM A LITERATURE THAT OPERATES AT
  1e8-1e9. WE ARE 160x TO 1,600x BELOW THE REGIME THEY WERE BUILT FOR.**
  Measured just now, off disk: the store corpus every arm tonight was built on is **34,169 sentences
  / ~623,522 tokens**. **`data/corpora/simplewiki/simplewiki_clean_v1.txt` -- 2,779,032 lines,
  ~41,918,879 tokens, 252 MB -- HAS BEEN SITTING ON DISK THE WHOLE TIME AND WAS NEVER USED TO BUILD
  THE STORE. It is ~67x larger than what we measure on.** *We used it tonight only as a source of
  definition sentences, never as the usage corpus.*
  **WHAT THIS REFRAMES:** SGNS reading BELOW its own untrained control; dependency-typed contexts
  adding nothing; the drill's own note that symmetric-coordination and typed contexts are *"the
  right idea, measured on 1e8-1e9 tokens; our corpus is ~1e6"*; and the definitional teacher channel
  sitting AT CHANCE. **SUBSTITUTABILITY IS A SECOND-ORDER STATISTIC -- it needs enough contexts per
  word to compare two words' context DISTRIBUTIONS. At 0.62M tokens most words have far too few.**
  **⚠️ DO NOT OVERSELL THIS EITHER, AND I HAVE ALREADY OVERSOLD ONCE TONIGHT: MORE DATA CANNOT FIX A
  MECHANISM THAT ANSWERS THE WRONG QUESTION.** Co-occurrence accumulated over 42M tokens is still
  co-occurrence. **The honest claim is that SCALE IS A PRECONDITION WE HAVE NEVER ONCE MET, not that
  scale is the answer.** Every "this mechanism does not work" verdict in this programme was reached
  in a regime where the mechanism could not have worked, and that is a DIFFERENT statement from the
  mechanism being wrong. **CHEAP AND DECISIVE: rebuild the usage view on simplewiki and re-measure
  the incumbent. Nothing else should be built until that number exists.**
- **🔴 CROSS-VIEW CONVERGENCE HUB: CLEAN NEGATIVE, `B_NEGATIVE` FIRED AS PRE-COMMITTED. THE
  BEST-CONTROLLED CELL OF THE SESSION, AND THE FIRST BUILT FROM THE BIOLOGY RATHER THAN FROM WHAT
  WAS LYING AROUND.** `experiments/exp_crossview_convergence_hub_v1.py`, all 16 mechanism arms fail.
  Primary `HUB_CCA_BOTH` **0.3129 [0.2630, 0.3644]** against a **RECOMPUTED** bar of **0.5510**;
  margin **-0.2880**. **NOT UNDERPOWERED -- the CI upper bound sits 5.7 half-widths below the bar**,
  so this is a resolved negative, not a width.
  **✅ WHY THE NEGATIVE IS TRUSTWORTHY, and it clears every trap that caught us earlier:** BOTH trap
  pairings stayed dead (0.0446 / 0.1375, `ANY_TRAP_CLEARS_ITS_OWN_BAR` false) so it is not a trap
  artifact; held-out split 3,064 fit / 617 eval with eval words excluded from the SVD basis,
  vocabulary, CCA, ridge, lambda AND k*; all four floors NOT_SEPARATED, known-answer 0.9612, random
  0.4919; **the coverage control removed 40 of 242 rows (16.5%) -- IT BINDS**, unlike the one that
  removed 0 of 242 earlier tonight. A **planted-positive self-test** refused the cell until the
  pipeline could recover a planted invariant (now hub 0.9934, raw views 0.0000).
  **🔴 RETRACTED WITHIN THE HOUR BY THE BRAIN DRILL (`9f27cc5e9`) -- I RELAYED THE 0.06 -> 0.31 MOVE
  TO THE OWNER AS "GENUINELY STRIPS CO-OCCURRENCE". IT IS NOT. THERE IS ZERO MEASURED EXTRACTION.**
  **A RANDOM 8-DIMENSIONAL PROJECTION OF THE INCUMBENT STORE -- WHICH NEVER SEES THE DEFINITIONAL
  CHANNEL AT ALL -- READS 0.3079 [0.2697, 0.3495]. THE ARM READS 0.3129, INSIDE THAT BAND.**
  Dose-response on RANK ALONE reproduces the whole effect: k=2 -> 0.4127, k=8 -> 0.3079, k=32 ->
  0.1770, k=128 -> 0.0798, k=256 -> 0.0536 (centring alone 0.0536, so it is RANK, not centring).
  **AND WORSE: pipeline-matched -- same whitening, same rho, same k*=8, ONLY THE DIRECTIONS
  RANDOMISED -- the null reads 0.3312 and BEATS the real `HUB_CCA_X` (0.2458) IN 200 OF 200 DRAWS.
  THE CROSS-VIEW-CHOSEN DIRECTIONS ARE WORSE THAN RANDOM ONES.**
  **🚨 THE GENERAL LESSON, AND IT IS A NEW FLOOR WE HAVE NEVER HAD: WHEN THE BASELINE SITS FAR BELOW
  CHANCE, DESTROYING INFORMATION MOVES THE SCORE TOWARD 0.5 AND READS AS PROGRESS. THE ENTIRE
  INTERVAL (0.06, 0.50) IS REACHABLE BY PURE DEGRADATION, AND NOT ONE FLOOR IN OUR BATTERY CATCHES
  IT.** *Any future "we moved from 0.06 toward 0.5" claim is void until it beats a RANK-MATCHED
  null.* Control now exists: `tools/rank_matched_null_dissociation.py`.
  **ALSO: the teacher channel was AT CHANCE BEFORE THE HUB WAS BUILT ON IT -- `A_DEF` 0.4780
  [0.4223, 0.5350], NOT separated from 0.5.** *I quoted 0.4780 as a point value; it is a width.*
  **TWO SETUP WEAKNESSES NAMED: the channel-independence preflight has a CEILING (r >= 0.95) but NO
  FLOOR, and the pairing sat at r=0.0363 with held-out cosine 0.0512 -- the channels were nearly
  UNRELATED, which is as fatal as being redundant; and `lam_rel=1.0` was selected AT THE GRID
  BOUNDARY in 3 of 4 pairings with the objective still climbing, so k*=8 is a truncated-search lower
  bound, not an optimum.**
  **SCOPE, as pre-registered: one definitional channel, one usage channel, one LINEAR extractor,
  one instrument, n=202. It says the missing ingredient is not a second view OF THIS KIND.**
- **🚨 A LICENSING DEFECT THIS CELL FOUND THAT REACHES BACKWARDS INTO EVERY RUN WE HAVE GATED:
  `F_SCRAMBLE` WAS A SINGLE COIN FLIP.** Its first smoke voided on `F_SCRAMBLE` 0.4266
  [0.3701, 0.4867] -- **one permutation's own CI excludes 0.5 about 5% of the time BY CONSTRUCTION,
  and across four floors that voids or passes roughly 18% of runs ON NOISE ALONE.** Measured
  single-draw false-fire rate **0.010-0.080 across 17 floors** -- that is the receipt, not an
  estimate. **FIXED HERE: `F_SCRAMBLE` is now a POLICY over 500 permutations with the bar term taken
  from the 95th percentile of that distribution -- which RAISED the bar and made it the BINDING
  term (0.5510).** *So this cell was judged against a HARDER bar than any predecessor.*
  **OPEN AND NOT YET ASSESSED: every earlier licensing decision in this programme used the
  single-draw form. That does not invalidate them, but it means an unknown fraction turned on a coin
  flip, and the fix belongs in the shared instrument, not in one cell.**
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
- **🔴 LANDED (`1b79ae57b`) -- SENSORIMOTOR CHANNEL: BRANCH (B) FIRED, EXACTLY AS PRE-REGISTERED AT
  `73edbca69`. THE PERCEPTUAL ROUTE IS CLOSED AT THIS RESOLUTION, AND THE MECHANISM IS THE VALUABLE
  PART.**
  Best arm `SM11_Z_NEG_EUCLID` **0.6039 [0.5439, 0.6644]** against a **credible bar of 0.6791**
  (margin **-0.0752**). **AND IT IS WORSE THAN THAT: IT SITS BELOW THE CONSTANT/PROTOTYPE FLOOR'S OWN
  POINT VALUE (0.6195). 0 OF 6 GRID POINTS CLEAR; ALL SIX CIs OVERLAP THAT FLOOR.** Coverage **166 of
  242** matched units, **557/617 = 90.3% of words -- independently reproducing the drill's §3.2
  figure**, so this is not a coverage failure.
  **🔬 THE MECHANISM, AND IT IS THE FINDING: THE ONLY THING THAT DISCRIMINATES IS A *QUERY-INDEPENDENT
  PER-WORD GENERICITY SCORE* -- ONE THAT NEVER COMPARES THE TWO WORDS AT ALL -- READING 0.6195,
  CI-SEPARATED ABOVE CHANCE AND BEATING EVERY PAIRWISE DISTANCE.** Centring collapses cosine
  0.5990 -> 0.5381 while euclidean is unmoved: **the cosine "signal" was carried by the SHARED
  PROTOTYPE DIRECTION.** Both cells sit in a narrow cone (within-pair cosine 0.8768 vs 0.8434) and
  **effective dimensionality is 6.26 OF 11.** *So the norms do carry a real signal -- "how generic is
  this word" -- and it is NOT "are these two words alike". That is the constant/prototype floor's
  signature, which is precisely what the drill predicted.*
  **✅ THE NEGATIVE IS REAL AND WAS CHECKED BEFORE ANY BRAIN TALK (discipline 17's first clause):**
  instrument still licensed at n=166 (four floors CI-include 0.5; incumbent 0.0884); the
  **planted-separable self-test fires at the deciding n or the cell aborts**; scramble changes 100%
  of scores. **NOT A POWER PROBLEM -- the best arm is below the floor's POINT value, so no amount of
  n converts it.** *Concreteness alone (1 dim): 0.5388 vs its own bar 0.6256 -- also beaten by its
  own floor.*
  **⚠️ TWO DISCLOSURES, BOTH THE AGENT'S OWN:** (1) known-answer reads **0.9448 [0.9204, 0.9654]** vs
  a 0.95 **point** gate -- **fails strict-point by 0.005, passes CI-inclusive**; the branch was driven
  by the CI form, both printed, decided and written into the docstring BEFORE the FULL run. (2)
  **`F_PROTOTYPE_MAGNITUDE__CONC1` = 0.3195: `SET_S` PAIRS ARE RELIABLY MORE CONCRETE THAN `SET_P`.**
  *The matcher balances on frequency/length/POS -- NOT on rating-norm properties -- so **discipline 16
  is live here in a new form: the POPULATION is unbalanced on the very axis this channel measures.***
  **WHAT IT DOES AND DOES NOT CLOSE: it refutes THIS RESOLUTION (11 dims), NOT GROUNDING.** And the
  trade is now measured rather than assumed: **Binder's 65 dimensions discriminate far better but
  cover 9.2% of eval words / 5.0% of anchors, and a unit needs ALL FOUR words covered -- which
  collapses the instrument below the "a win on 20 pairs is not a win" line. NO ASSET WE CURRENTLY
  HOLD SITS ON THE GOOD SIDE OF THE COVERAGE-RESOLUTION TRADE.** *The image-derived relational subset
  (57.9%) is a different KIND of signal and a separate cell.*
- **[SUPERSEDED -- LANDED ABOVE] SECOND LANE (08:05) -- `sensorimotor-discrimination`. THE MOST CONSEQUENTIAL TEST OF THE NIGHT,
  AND IT IS PRE-REGISTERED TO FAIL IN A SPECIFIC WAY. DO NOT RESPAWN.**
  **Question, deliberately narrow: does a PERCEPTUAL profile separate `SET_P` from `SET_S` AT ALL?
  A SIGNAL THAT CANNOT DISCRIMINATE CANNOT TEACH**, so this gates every downstream supervision idea.
  Data verified on disk by me: `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv`,
  16.4 MB, 39,707 rows, all 11 mean dimensions present. **NOT text-derived, NOT WordNet-derived, NOT
  an LLM -- which is exactly why it is admissible where every other candidate was circular.**
  **Branches pre-committed at `73edbca69` (6.43) BEFORE dispatch. THE FAILURE MODE IS NAMED IN
  ADVANCE: `SET_S` pairs are same-POS same-domain nouns ("calcium/carbonate") that may share a
  sensorimotor profile just as the synonyms do, so this channel may behave like the
  constant/prototype floor -- OUR STRONGEST. IF THAT FIRES IT REFUTES THIS RESOLUTION (11 dims), NOT
  GROUNDING**, and the report must name what resolution would be needed rather than concluding
  grounding fails. *Binder's 65 dimensions discriminate better but cover 9.2% of eval words.*
  **IT IS A DISCRIMINATION TEST, NOT A SUPERVISION BUILD -- if it passes, the supervision cell is a
  SEPARATE decision with its own pre-commitment.**
- **🔵 FIRST LANE (07:20) -- `typed-density-sweep`. DO NOT RESPAWN.**
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
