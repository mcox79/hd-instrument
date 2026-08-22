# STATUS -- THE RECOVERY ENTRY POINT. READ THIS, THEN THE PLAN.

AS OF: 2026-08-21 LATE (autoloop `auto_cdc11bb529`), LOOP ARMED | branch `dataprep/mcguffey-graded-corpus` | origin push needs USER AUTH | **NOTHING IS RUNNING** | **BOARD: Q102 OPEN. Q103 FILED AND WITHDRAWN BY ME WITHIN THE HOUR -- its premise ("9 books", "only 40 usable pairs") was MY OWN 60k alphabetical CAP; the shelf is 28 corpora / 286,069 sentences / 111 balanced pairs -- MY OWN "the gain is genuinely untested" IS WITHDRAWN: ORGAN_MAP 10.1 A1 measured it 08-14, form organ 0.0870 vs live substrate 0.0480, CI-separated, on a task with a spelling shortcut; Q98 approved the write-rate extension WITH a stopping rule; Q99 done.** | 🧠 **ONE STRUCTURAL FINDING, upstream of THREE dead ends tonight: ONE REPRESENTATION IS DOING TWO JOBS THAT NEED OPPOSITE THINGS -- grounding must DELETE the word (correct, else it learns 'artery means artery'); identification needs it PRESENT -- **VETTED 08-21: the word ALONE scores 0.9687 vs 0.6423 for word+sentence (chance 0.0167), so CONTEXT DILUTES identification and the job is a LOOKUP. DO NOT quote 0.1417/0.4750 as evidence about CONTEXT -- it is SELF-REFERENCE**. THE FORM ORGANS ARE ALREADY BUILT AND UNWIRED.** | **READ `notes/BUILD_PLAN_post_audit_2026-08-19.md` FIRST BLOCK (133 lines, from 6,895) -- it carries the 16 withdrawals and the method -- THEN `## POSITION` BELOW**

Rules: `STATUS_SPEC.md`; stubs resolve in `STATUS_LESSONS.md` (uncapped). FOUR literals
MACHINE-PARSED, never reword: `AS OF:`, "POSITION", "TOP ITEM" and "WHAT IS RUNNING"
(`session_start_hook.py`, `board.py`). **Inside a section use `###`, never `##`.**
*NEVER let a line BEGIN with one of those literals even when merely NAMING it -- which is why the
four names above are in DOUBLE QUOTES, not backticks. **AND THE OPPOSITE FAILURE HAPPENED HERE ON
2026-08-21: quoting them in BACKTICKS that were never closed swallowed the two REAL headings into
this paragraph** -- one before `### 2026-08-21` and one before the TOP ITEM heading -- so
`board.py` wrote MISSING REQUIRED LITERAL for BOTH, into the owner-facing board, and the file
still LOOKED complete because every section BODY was present. **A heading is not the same object as
its section: grep the four literals, never eyeball the content.** Restored the same day.
**RUN `python tools/board.py self-test` AFTER ANY EDIT TO THIS HEADER.***

## POSITION

### 2026-08-21 -- THE THREE-WAY COMPARISON THAT DECIDES WHAT F5 BUILDS ON

| arm, paired hit@1 discrimination, 4 sets | median | verdict |
|---|---|---|
| untrained codebook (nothing read) | **~0** | CIs span zero -- donates nothing |
| **THE TRAINED SUBSTRATE** | **+16.3 pp** | **`REPLICATED`, all 4 CIs exclude zero** |
| second-order counting (**the bar**, upper bound **+44.2**) | +29.4 pp | `REPLICATED` |

**LEARNING BOUGHT SOMETHING REAL** -- 0 -> +16.3 pp, same representation and comparison, the only
difference being 7,535 sentences read. First replicated positive from our side on this task.
**AND IT DOES NOT CLEAR THE BAR** (best CI +30.8 vs gate +44.2), reproducing the standing position
*at or below counting* on a task that did not exist when that position was formed.
**AND THE PAIRED TEST NOW SAYS WE ARE MEASURABLY BEHIND, not merely not-ahead:
`SUBSTRATE - COUNTING = -0.142 per item over 478 items, 95% CI [-0.203, -0.082]`, SEPARATED.**
Marginal CIs overlapped, which is NOT a test of a difference; the paired test is. `notes/THE_TRAINED_SUBSTRATE_SCORES_16pp_...md`


## TOP ITEM -- **DIMENSION BUYS THE LOOKUP, NOT THE UNDERSTANDING. D1 MUST BE ARGUED ON IDENTIFICATION.**

*Three sweeps, 28 corpora round-robin, floors recomputed at every point.*
1. **READING MORE DOES NOT HELP.** *Queries FIXED, only profile depth varying:* `0.1900 / 0.2100 /
   0.2133 / 0.1900 / 0.1967` (depths 5-41) -- **rises to ~10 then flat; the live median word already
   gets ~10.** ⚠️ *My first cut showed a DECLINE and I nearly called it "write less" confirmed: the
   query set was growing with the depth.*
2. ✅ **DIMENSION BUYS IDENTIFICATION.** `128 0.1061 | 256 0.1435 | 512 0.1776 | 1024 0.2057 |
   2048 0.2268`, **SCRAMBLE recomputed at every d and flat at chance.**
   ***`1024-256 = +0.0622, CI [+0.0443,+0.0797]`, 48 of 60 lemmas, EXCLUDES ZERO.***
3. 🔻 **AND IT DOES *NOT* BUY MEANING.** *829 SimLex pairs identical at every d, so the corpus
   confound CANCELS; null = 200 shuffles per d.* `128 0.0974 | 256 0.0944 | 512 0.1032 |
   1024 0.1071 | 2048 0.0874`. ***`1024-256 = +0.0127, CI [-0.0305,+0.0559]` -- SPANS ZERO*** and
   DROPS at 2048. **NOT the usual underpowered dodge: half-width `0.0432`, so an
   identification-sized `+0.0622` WOULD have been detected. A BOUNDED negative.**

4. 🔻 **WITHDRAWN WITHIN THE HOUR -- "the one change that makes it better" IS NOT ESTABLISHED.**
   *Dropping high-df context words moves in-sample `0.1071 -> 0.1558` at `d=1024`. I reported a
   held-out `+0.0433` CI `[+0.0002,+0.0994]` as EXCLUDING ZERO from **200** resamples. At **2,000**:*
   **`d=256` (WHAT SHIPS) `-0.0050` `[-0.0629,+0.0365]`; `d=1024` `+0.0434` `[-0.0117,+0.0940]` --
   NEITHER excludes zero.** *I reported the favourable draw.* ⚠️ **METHOD: 200 resamples cannot place
   a BOUND near zero; raise the count before reading one.** `DROPPING_264_UBIQUITOUS_...`
5. 🔀 **The FILTER DISSOCIATION still stands and does NOT depend on the withdrawn claim.**
   *Same filter:* **MEANING `0.1071 -> 0.1558 -> 0.0988` (COLLAPSES past the optimum);
   IDENTIFICATION `0.2057 -> 0.2160 -> 0.2169` (FLAT).** *The dissociation rests on the COLLAPSE,
   which is far too large to be noise -- not on the small gains, which are not established.*

6. ⭐ **THE LEARNED CHANNEL HAS NO SIGNAL ON VERBS: `+0.0000` on SimVerb-3500's 2,651 covered pairs
   (null p95 `0.0372`)** *(Gerz et al. 2016 -- cite it)* **and `-0.0002` on SimLex's 203 verb pairs
   (null `0.1398`). TWO INDEPENDENT BENCHMARKS, BOTH AT ZERO.** *Within SimLex, one scorer, only word
   class changing:* **NOUN 534 `0.1310` (null `0.0843`) CLEARS; VERB INSIDE; ADJ 92 `0.2207` (null
   `0.1931`) clears barely.** ➡️ ***WEAK ON NOUNS, ABSENT ON VERBS.*** ✅ *Coverage cutoff DISCHARGED:
   OURS inside its null at 41/20/10/5 sentences, down to 97% of verbs.*
   🎯 **CONTROL THAT SPLITS IT:** `COUNTING raw 0.0025 INSIDE | COUNTING+idf 0.0689 CLEARS |
   OURS 0.0000 INSIDE | SUPPLIED norms 0.2983`. ***Our zero is a REAL DEFICIT vs a text rival; but
   every text arm is 4.3x below the human-rated one.*** 🚫 *SUPPLY, NOT LEARNING.*
   🔑 **AND THE MECHANISM IS NOW KNOWN -- see the co-occurrence entry under WHAT IS RUNNING.**
   `ON_VERBS_THE_LEARNED_CHANNEL_HAS_NO_SIGNAL_AT_ALL_n2651_...`

➡️ **SO D1 (`256->1024`, which REWRITES EVERY PERSISTED STORE) improves a LOOKUP.** *Q65 = "do
whatever is ideal"; standing caution = backup + no concurrent session; still climbing at 2048 on
identification, so 1024 is not obviously the target.*
⚠️ **SOBERING AND UNCHANGED BY ANY OF THIS: meaning rho `~0.10` against a null p95 `~0.065` -- barely
clear of noise at EVERY dimension. Room is not what stands between us and understanding.**
`THE_LIMIT_IS_DIMENSIONAL_...` `DIMENSION_BUYS_THE_LOOKUP_NOT_THE_UNDERSTANDING_...`
*(Prev top item "wire definitional direct-bank" CLOSED -- already live, 212 of 402 rows.)*

## 🌙 THE NIGHT OF 2026-08-21 -- **ONE LINE PER FINDING. FULL TEXT IN THE NAMED NOTE.**

*Compressed from 7,155 B on 2026-08-21 late. Every row's detail is in its note AND in the plan's
consolidated top block; nothing here is the only copy. **Do not re-expand: this section was 24% of a
file already over cap.***

| # | finding, with the number that carries it |
|---|---|
| **META / PROCESS** | **All 4 planned thrusts were ALREADY ANSWERED ON DISK; the defect was ORDER, not omission.** *The full process ledger -- 9 prior-work catches, the 2 new reads (`symbol_corrections.py`, `cite_check.py`), the 28-corpora shelf correction, the alphabetical live reader, the registry lost-update, the stale board header, the GUI crash, and the detector I did NOT build -- now lives in the plan's consolidated top block. **Evicted from here 08-21 late: it was the only copy of nothing.*** [`METHOD_REVIEW_...`] |
| **H2** | The anti-skew organ **read its way to `textbook_biology 0.63245`** while WINNING on its own currency. **MVT is a LEAVE rule, silent on WHERE TO GO.** *Register-inversion headline WITHDRAWN (7.6x bias under a 1.2x margin).* [`T1_foraging_...`] |
| **E3** | **Coreference "salience" is PROVABLY a mention-count** -- `argmax_count_fraction = 1.0` on all 89 competitive decisions. **`base_principle_b` beat a COUNTER, not a cue account.** [`T2c_...`] |
| **E3b** | ...and that `HARD_FAIL` **cannot support its own verdict**: n=89, scramble ABOVE treatment, 2 of 3 params hand-set. **Re-label UNDERPOWERED.** [`T2b_...`] |
| **B4** | **Spelling beats the meaning read-out at rank 1** (`0.0767` vs `0.0480`), survives the strictest tie convention -- **but the substrate WINS the full ranking `37.0` vs `54.0`. THE DEFECT IS PRECISION AT THE TOP.** [`T5b_...`] |
| **B4b** | **The live grounding path reads a GRADED field with a SIGN-QUANTISED query** -- `canonicalize:776` hardcodes `np.sign`; `:663` calls that pairing *"worse than either"*. [`T3_...`] |
| ⭐ **RATE** | **WRITE LESS: `0.0710 -> 0.3079` at p90, 4.3x, no new mechanism -- BUT a RATE-MATCHED RANDOM GATE MATCHES IT AT EVERY THRESHOLD.** *So prediction-error gating is REFUTED; the gain is RATE.* ⛔ **every arm stays BELOW co-occurrence.** [`THE_RATE_SWEEP_IS_ALREADY_DONE_...`] |
| **NORMS12** | **SUPPLIED human ratings, 12 dims -- and measured 08-21 against what we LEARNED on 829 IDENTICAL pairs, one scorer: `SUPPLIED euclid 0.2876 | SUPPLIED cosine 0.2176 | LEARNED d=1024 0.1071 | LEARNED d=256 0.0944` (nulls 0.063-0.076). 2.69x.** *The archive's 2.7x was an inference across two cells on different pair sets; this is its first honest test.* 🎯 **EUCLID BEATS COSINE BY `+0.0700`, MORE THAN OUR ENTIRE LEARNED ARM CLEARS ITS OWN NULL (`0.0440`).** ✅ **`GROUNDED_CAP=0.45` IS A MEASURED SAFETY PROPERTY, NOT A CRIPPLING -- I had been quoting it as a defect and was WRONG:** raw cosine cannot separate `sofa/couch 0.968` from `apple/orange 0.952`, so the cap sits BELOW the 0.50 merge threshold to make a false identity merge impossible BY CONSTRUCTION; only the TOP is flattened. *Its own escape clause is "this SAME metric" -- and 3 measurements say euclid beats cosine on exactly that contrast.* 🚫 **SUPPLY, NOT LEARNING -- the organ's docstring forbids reporting it as the substrate having learned perceptual structure.** ⚠️ token coverage 60.4%. [`SUPPLIED_BEATS_LEARNED_2_69x_...`] [`THE_CAP_IS_PRINCIPLED_...`] |
| **CHANCE?** | **CORRECTED, I OVER-REACHED:** three measurements do NOT license "at or near chance" -- the trained substrate is **+16.3 pp REPLICATED** over an untrained codebook. **But `SUBSTRATE - COUNTING = -0.142` CI `[-0.203,-0.082]` SEPARATED: measurably BEHIND counting.** ⭐ **AND THAT NEGATIVE IS NOW CROSS-TASK (08-21 late).** *Same 829 SimLex MEANING pairs, different scorer, different population:* `counting RAW 0.0885 | OURS d=1024 0.1071 | counting +IDF 0.1835 | supplied norms 0.2876`; **`IDF - OURS = +0.0764` CI `[+0.0263,+0.1278]`, EXCLUDES ZERO.** ✅ *We DO beat RAW counting -- the loop is not doing nothing.* 🔻 **But ONE standard weighting (idf) is worth `+0.0950` where our whole learned signal clears its null by `0.0440`.** 🚫 **ANY CLAIM ON THIS BENCHMARK MUST CLEAR `0.1835`, NOT raw counting and NOT a shuffle -- I had been using the weak floor all night.** [`COUNTING_WITH_ONE_STANDARD_WEIGHTING_...`] [`THREE_INDEPENDENT_MEASUREMENTS_...`] |

## WHAT IS RUNNING

- ⬜ **NOTHING IS RUNNING.**
- 🔑 **THE FORK IS ANSWERED: TEXT *DOES* SEPARATE OPPOSITES FROM SYNONYMS -- AND WE INVERT IT.**
  *Full shelf, freq-matched, RANDOM-pair negative control PASSES (`8.64` lowest):* **cond "X and/or Y"
  ANTONYMS `0.0782` vs SYNONYMS `0.0269` (2.91x) vs RANDOM `0.0022` (34.8x)**; %never-co-occur `13.3`
  vs `19.0` vs `47.6`. 🎯 **THE CHAIN, EVERY LINK MEASURED: antonyms CO-OCCUR -> our encoder builds
  2nd-order profiles and CONVERTS co-occurrence INTO SIMILARITY -> antonyms are our CLOSEST pairs
  (`0.2062` > syn `0.1727`) -> verbs read `0.0000`. NOT a missing feature, an INVERTED one.**
  ⚠️ *LIMITS: COHYPONYMS 2nd at `0.0356` ("cats and dogs") so it detects COORDINATED, not ANTONYM,
  antonyms lead them only 2.20x; only 7.8% of antonym co-occurrences fire; NO arm built.*
  ⚠️ *The instrument REFUSED TWICE first: v1 broken statistic (PMI + 0.5 smoothing), v2 broken
  CONTROL (SimVerb `NONE` = no WordNet relation, NOT unassociated). Both refusals correct.*
  `THE_SIGNAL_FOR_OPPOSITION_IS_IN_THE_TEXT_...`
- 🎯 **SEED PRICE MEASURED: ~50-100 GROUNDED WORDS ALREADY PROPAGATE; PAST ~400 MORE BUYS ~NOTHING**
  (concreteness, the gated column: `50 0.2114` vs null `0.1239` | `400 0.3783` | `2000 0.4323`).
  🔻 **BUT IDF AT 200 SEEDS (`MEAN15 0.2971`) BEATS OURS AT 2,000 (`0.2638`) -- 10x THE GROUNDING
  TO NOT MATCH IT; 16th measure where counting leads.** 🔬 *And OUR nearest-seed cosine is HIGHER
  (`0.3965` vs `0.2415`) while carrying LESS -- ANISOTROPY. `DO NOT REDO 27` (common-mode) has a
  revival `*`; criterion NOT yet read, NOT claimed met.* 🔻 **2 OWN-SCRIPT DEFECTS REPORTED: the
  25-seed row is DEGENERATE (constant prediction -> exactly 0.0000, the reachability signature) and
  `null95` gates CONCRETENESS ONLY, not MEAN15.** ⚠️ *Random seed = pessimistic; K still unswept.*
  `HOW_SMALL_CAN_THE_GROUNDED_SEED_BE_...`
- 📏 **This file sits just inside its 28,672 B cap.** *It was 30,147 B at the start of 2026-08-21
  late. What paid for it was EVICTION, not trimming -- twice now: the night-findings table
  (7,155 -> 3,303 B) and this section, which had filled with FINISHED work. **When it next needs
  space, delete a duplicate; do not shave words.*** `STATUS_SPEC.md` sec 6.
- ✅ **FINISHED AND CLOSED (one line each; detail is in the named note and in the plan's top block):**
  - **`exp_graded_vs_signed_query_v1` -- `np.sign` at `:776` COSTS ALMOST NOTHING. CLOSED.**
    `Q_GRADED 0.0480 / median 37.0` vs `Q_SIGNED 0.0455 / 41.0`; paired **`+0.0025` CI95
    `[-0.0030,+0.0080]` NOT SEPARATED**; positive control reproduces the C3 headline EXACTLY.
    **`:663`'s "worse than either" is unsupported at this scale.** ⚠️ **AND I PARTLY RE-DERIVED THIS
    ON 08-21 LATE** on the MEANING benchmark (`graded x signed` sits between the two at d=256 and is
    marginally best at d=1024) **without reading this entry first -- in the file I re-read every
    continuation.** *Ninth prior-work catch; the earlier one has a CI and mine did not.*
  - **`diagnose_read_with_loaded_foundation`: refusal delta `279 vs 380 = 1.36x`, NOT the 22x
    headline, which was 93% PRE-EXISTING.**
  - **`ReadResult.n_grounded` WAS STRUCTURALLY ALWAYS ZERO** -- `substrate.py:608` read
    `n_grounded_cumulative`, `checkpoint()` emits `cumulative_grounded`, **the same two words
    TRANSPOSED**. Now raises; self-tests PASS; no landed cell affected. **A STATIC scan for this bug
    class DOES NOT WORK (1,925 -> 132 suspects, all legitimate reads). WHAT FOUND IT WAS A
    CONTRADICTION BETWEEN TWO FIELDS OF ONE OUTPUT** (`n_grounded=0` beside `anchors +68`).
    ***Make outputs print quantities that CONSTRAIN EACH OTHER.***
  - **WHY WRITING LESS HELPS (owner Q98):** `exp_crosstalk_capacity_law_v1_gpu_v1`
    `MEASURED_MECHANISM` -- crosstalk over raw keys DOMINATES Hebbian capacity, **r 0.976, n=11**;
    rivals' partials go NEGATIVE. **Our keys sit AT the Welch bound, so "better keys" is closed by
    GEOMETRY; the two remaining levers are FEWER ITEMS and MORE DIMENSIONS.**

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
**C37 "B1 IS A CLIFF: ours 0.931/0.304/0.002 vs counting 0.859/0.852/0.830" -- WITHDRAWN/INVERTED.
Those are cos_syn/cos_rel/cos_unrel (SYNONYM/RELATED/UNRELATED), NOT vocabulary strata. A LOW tier-3
is the GOAL -- vessel vs anger should read ~0 -- so OUR 0.002 IS CORRECT AND COUNTING'S 0.830 IS THE
DEFECT: its syn-to-unrel range is 0.0285 vs our 0.9287, hence ordered_frac 0.379 vs 0.966. "The bar
is 0.830" is VOID, it targeted the baseline's PATHOLOGY. Coverage 29/29 on ALL arms: NO tier
measures out-of-lexicon behaviour. Survives: the cell's own coverage_scope, 86 hand-authored
concepts, open-vocabulary "NOT claimed here". CAUSE: took "cliff" from ORGAN_MAP and propagated to
3 docs without opening metrics.json -- the defining phrase sat in the SAME verdict sentence I lifted
the numbers from. A DOCUMENT'S INTERPRETATION IS NOT EVIDENCE; DISK-VERIFY OUR OWN NOTES, ORGAN_MAP
INCLUDED. Caught ONLY by asking whether the FIX could reach the problem -- which also TESTS WHETHER
THE PROBLEM IS REAL.**


## STANDING DISCIPLINES -- NEVER-TRIM -- LESSONS
1 NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% -- cost TWO experiments, the
2nd claiming to have FIXED the 1st; gate on KNOWN-ANSWER RECALL. 2 SERIALIZE MEASUREMENT vs CODE
CHANGE (2x). 3 A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night; C31 = 5th;
**6th 08-21, TWO NEW FORMS: (a) A CHECKER THAT CHECKS A *SUBSET* REPORTS GREEN ON A BROKEN FILE --
the session hook's own positive control asserted "the real STATUS.md parses clean" and PASSED while
2 of its 4 required headings were GONE, because it guarded only the 2 IT consumes. A POSITIVE
CONTROL IS ONLY AS BROAD AS ITS ASSERTION. (b) A CONTROL THAT FIRES INTO A FILE NOBODY RE-READS IS
NOT YET A CONTROL -- `board.py` DID fail loud, into `BOARD.md`, and it sat. Fixed: all 4 literals
guarded at session start, PROVEN by firing on the real pre-fix file, not only on fixtures**).
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
