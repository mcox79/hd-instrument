# STATUS -- THE RECOVERY ENTRY POINT. READ THIS, THEN THE PLAN.

AS OF: 2026-08-23, LOOP ARMED | branch `dataprep/mcguffey-graded-corpus` | origin push needs USER AUTH | **NOTHING IS RUNNING** | ❓ **BOARD: Q115 + Q116 OPEN, BOTH WAITING ON THE OWNER.** *Q115:* should the shared save-location helper be REQUIRED for new cells, so the un-reproducible pile stops growing. *Q116:* should we formally STOP trying to learn meaning from text statistics and commit to supplied knowledge + reasoning -- **evidence gathered since filing cuts partly AGAINST my own recommendation there.** Q113 (08-22): cell work + `hdi_*` spawns AUTHORIZED; the `notes/problems/` briefs are the solver's, do not work them here. Q111 STANDING: testbed owns ALL integration, solvers never write `hdlab/`. Q110 STANDING: operational calls are mine, board is for owner-only decisions. Q102/106/107/108/109/112 ANSWERED/WITHDRAWN AND DISCHARGED (per STATUS_SPEC sec 3 tier 3 + the citation rule -- full text `notes/QUESTION_LOG.md`; Q109's credit-assignment investigation moved to `STATUS_LESSONS.md` "Q109 CREDIT ASSIGNMENT"). *Q103/104/108 share one pattern: filed before testing the constraint being complained about.*
   ✅ **CLOSED TODAY (08-22), one line each, full text on disk at the named note:** the grounding
   quality answer is `3/100 MEANINGFUL, 19 RELATED, 78 NOISE` blind, scramble_ratio 0.077, no
   correctness measure exists in the cell (`THE_GROUNDING_ANSWER_...`); best-evidenced grounding
   result (`graded_divisive_comparator`) is real but MISNAMED -- it relieves a d=256 CAPACITY
   bottleneck, not an ability (`THE_BEST_EVIDENCED_GROUNDING_RESULT_IS_MISNAMED_...`); 156 smoke
   rows carry a HARD_PASS their FULL run does not, hazard did NOT bite, only 1 would pass the
   evidence gate (`156_SMOKE_RUNS_...`, `THE_SMOKE_CITATION_HAZARD_DID_NOT_BITE_...`); the
   certification gate ran ZERO of 456 tests for two days behind a false `RESULT: PASS`, now fixed,
   true state 96 files / 403 functions / 32 witnesses / zero genuine failures
   (`THE_CERTIFICATION_GATE_HAS_RUN_ZERO_...`, `THE_COMPLETE_VERIFICATION_STATE_...`); a `git stash
   pop` briefly overwrote one file with a stranger's June stash, restored from HEAD, canonical store
   untouched (`NEAR_MISS_I_POPPED_A_STASH_...`); Q103's "only 40 usable pairs" was my own 60k-cap
   artifact -- the shelf is 28 corpora / 286,069 sentences / 111 balanced pairs, WITHDRAWN. **ONE
   STRUCTURAL FINDING spans three of tonight's dead ends: one representation does two jobs needing
   OPPOSITE things -- grounding must delete the word, identification needs it present (word alone
   scores 0.9687 vs 0.6423 word+sentence; CONTEXT DILUTES identification, it is a LOOKUP). The form
   organs are already built and unwired.**
   **READ `notes/BUILD_PLAN_post_audit_2026-08-19.md` FIRST BLOCK -- THEN `## POSITION` BELOW.**

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

### 2026-08-22 -- 🚨 **THE STORE FIX IS REFUTED, AND NO SOLVER WORK HAS TOUCHED THE SUBSTRATE YET**
**3 solutions in: `eval_bank_too_small` SOLVED (a DATA file, 124 scorable), `stored_terms_are_stems`
PARTIAL (nothing live to fix), `flat_store_destroys_the_code` REFUTED.** 🔻 **ZERO of the three
changed `hdlab/`. Every substrate edit today is the strategy session's own.** *Owner asked; that is
the honest answer.*
🔑 **THE REFUTATION: addressed storage reads exact-key `0.9954` and held-out `0.1399`, against a
first-order COUNTING floor of `0.3242` (`-0.1843`, CI excludes 0). It can RECITE, not RECOGNISE.**
*Info-free twin `0.0000`, scramble `0.0000`, 2AFC positive control `0.7433` -- the instrument works,
so the failure is real. Verified to six decimals against `metrics.json`.*
🧠 **AND IT REPRODUCES A KNOWN CLIFF FROM A NEW DIRECTION** -- a circular WordNet oracle reads
`0.8787` at exact key and `0.0365` under a partial cue. **Two unrelated mechanisms, same wall: this
is a property of how the cue meets the store.**
✅ **MY BRIEF ASKED THE WRONG QUESTION (owner caught it): it said WIRE the store we have. The store
we have does not work.** ➡️ **NEW PROBLEM `store_survives_a_partial_cue` at PRIORITY 2** -- design
one, bar = beat `0.3242` held-out CI-separated; **a rigorous negative is an explicit PASS.**
🖥️ *GUI: priorities + MY RATING columns are wired (`13806bac1`) but the running window
started 13:15, BEFORE that commit -- **it must be RESTARTED to show them.** Not a bug, a stale process.*
📎 `RANDOM_CREDIT_BEATS_THE_REAL_MECHANISM_...`; briefs in `notes/problems/`.

### 2026-08-22 -- 🚨 **`read(n_sentences=N)` IS A CEILING; `max_patches` (default 4) BINDS FIRST**
`read(3000/6000/10000)` all returned `1,060`: `substrate.py:548` breaks at `patch_i >= max_patches` -- ONE LAP,
budget discarded, nothing runs out of text. **Raise `max_patches`, not `n_sentences`.** Successive calls decay
(`1,060->240->220`) via cached forager rho, never reset. 🔻 *DEFLATED BY ITS OWN ENUMERATION: no cell uses the
failing shape -- all bind `chunk=400` and loop, delivering `81%`. Do NOT quote `13%` as our exposure.*
✅ *Guarded `e335fa220` (`short_read` on `ReadResult`, survives `to_dict()`); mechanism in the docstring `37d628d95`.*

### 2026-08-22 -- ✅ **A REPLAYED CHECKPOINT IS NOT A REPRODUCTION; ENFORCED IN CODE**
**`399`/`7,868` landed cells (`5.1%`) replay on re-run -- same verdict, `elapsed 0.0s`, no work done.**
`tools/reproduction_check.py` makes the unsafe reading unrepresentable (no `__bool__`; no before-snapshot ->
`INDETERMINATE`). 🚫 *Casts doubt on NO landed number -- only on whether re-running one verifies it.*
📎 `--census` recomputes it; brief `notes/problems/harness_cannot_recompute/`.

### 2026-08-22 -- 🔑 **THE MEANING ASSET IS NOT SHORT OF WORDS; THE LOOKUP CANNOT INFLECT**
`grounded_similarity.py:165` is a raw-string lookup: we hold `country`, miss `countries`. **TOKEN coverage
`0.6035 -> 0.7350` via our own `normalize_lemma` (+13.2 pts, zero new norms)** -- so **`+14,704 words to norm`
counts INFLECTED FORMS OF ALREADY-NORMED WORDS.** *Substitution verified (3,629 pairs, median `0.7605` vs random
`-0.0131`); irregulars add only `+1.42`, so REUSE `normalize_lemma`.*
⛔ **UNREACHABLE TODAY: `read()` NEVER CONSULTS THE ASSET** -- `0` calls, positive-controlled, table never
loaded; matches the B5 slot (`NEEDS_ADAPTER`). **Fix the lookup, re-run a reading task, NO MOVEMENT IS EXPECTED.**
🔑 **THE VERB HOLE IS OURS, NOT THE ASSET'S:** SimLex, only word class changing -- ASSET NOUN `+0.2745`
(null `0.0732`) and VERB `+0.2607` (null `0.1241`) BOTH CLEAR, `z=0.192` NOT separated, on `99.6%` of SimVerb;
our LEARNED channel has noun `0.1310` and **verb INSIDE its null.** ⚠️ *ADJECTIVES unresolved AND unanswerable
on our assets -- SimLex's `111` is every adjective pair we own.* 🔻 *Withdrawn: "the lookup fix IS the verb
fix" -- our UPOS tagger shows recovery enriched for CONTENT WORDS (VERB `2.58x`, NOUN `2.25x`).*
🚫 **COVERAGE, NOT CAPABILITY -- no task run; `grounded_similarity.py` deliberately UNCHANGED.**
📎 `THE_VERB_HOLE_IS_OURS_...`, `THE_NORMS_LOOKUP_DOES_NOT_LEMMATISE_...`; brief at priority 7.

### 2026-08-21 -- ✅ **EVICTED TO `STATUS_LESSONS.md` (search "THREE-WAY COMPARISON"): the F5
three-way comparison that set what to build on. Closed; nothing since has moved it.**

## TOP ITEM -- **I HAD BEEN MEASURING THE CHANNEL BOTH PLANS OF RECORD ALREADY RULED OUT.**

🔻 **THE SCOPING CORRECTION (08-22): "a 1970s baseline beats us EVERYWHERE" over 16 measures was
wrong -- ALL SIXTEEN ARE THE WORD-SIMILARITY CHANNEL**, which `SUBSTRATE_CHARTER` (08-05) and
`PLAN_grounded_semantic_organ_build` had already ruled out and MEASURED (bag-of-words scores
`0.5167` = chance, gold sense handed to the classifier). ✅ On the GROUNDING organ the picture
inverts: `0.962-1.000` vs bow's `0.500-0.517` on the same items. The 16 measurements stand; only
"everywhere" was wrong.

🧭 **THE DIRECTION HAS A NAME, SET 08-06/08-07, NOT BY ME: ANCHOR + PROPAGATE** -- ground a small
affective anchor and reason outward (antonyms are distributional twins, so good/bad is in neither
grammar nor text statistics). 🚨 The build plan cited `PLAN_B` zero times (grep) -- two plans, only
one read; that is why the night went where it did.

✅ **WHAT IS BUILT AND PASSING:** *`bridge1_governor_grounding` HARD_PASS `0.967`; `confirmation_test`
RULING_CONFIRMED (the PREDICTED failure at `0.500`); `twostage_event_situation_v2` HARD_PASS B `1.000`
C `1.000`; a 12-WORD seed via `wordnet_polarity_propagation` -> `0.833` held-out, seed-ablation `0.000`.*
🎯 **DOUBLE DISSOCIATION: each subset's MATCHED scramble degrades, the UNMATCHED one does not.**
🔻 **SCALE: n = 21/12/12/8 and one `Cgen 1.000` IS n=2 -- that number carries NOTHING (p=0.25).**
⚠️ **VERIFICATION: those numbers are READ, NOT REPRODUCED. Re-running gives `elapsed 0.0s` -- checkpoints
REPLAY and the no-op is INDISTINGUISHABLE FROM A PASS.** *`--self-test` DOES recompute and reproduced the
pattern. Scope measured: `399` of `7,868` landed cells, 5.1%.*

✅ **OPEN VOCAB FULLY DIAGNOSED, NOTHING REPAIRED:** `B` 10/12=`0.8333`, `Bgen` 6/8=`0.750`, and ALL
FOUR ERRORS HAVE AN ADVERSARIAL PATIENT (`enemy` x2, `rival`, `thief`). **THE ANIMACY MAP CANNOT
EXPRESS `ADVERSARIAL`** -- an expressiveness gap, not a lookup bug (WordNet supplies it for 7/8). It
misses `rival` correctly: WordNet files it under `contestant`, hostility is in the gloss not the
taxonomy -- exactly the part both plans say needs SITUATION context. The `== "UNK"` guard is a
deliberate hand-off, not a defect -- DO NOT TOUCH IT. 🔻 Three retractions getting there (root
fault: compared `v2.lookup_animacy` vs the real lookup, and the closed arm does not consume it) --
the answer was in the cell's docstring at line 52, read past twice over four turns.

➡️ **FRONTIER: REAL PROSE / CREDIT-ASSIGNMENT -- MEASURED TO EXHAUSTION THIS SESSION.** The WALL
REPRODUCES: both cells landed 08-07, their lemmatizer was repaired 08-13 (a real confound I
identified) -- re-ran today, `primary 0.4722` IDENTICAL to four digits, same `HARD_FAIL`; confound
hypothesis REFUTED, wall is STRONGER (`_is_verblike` fires on the SURFACE form, so the repair
changed each mistake's NAME, not its DECISION). **The precision problem is LIGHT VERBS, not junk:**
53.2% of credited exposures are not loaded; of 173 error types, 46 are genuine verbs carrying no
outcome information. My morphology thread addressed only `5.4%` of credited tokens (measured 3x,
progressively smaller) -- I RETRACT calling it "the cheapest high-value fix". Local-window credit is
measured out: coverage is NOT the cause, precision ~47% dominated by light verbs. RETURNS TO WHAT
BOTH DOCUMENTS SAID: REPLACE THE WINDOW -- but that build's causal component is reducible to
connective-else-most-recent by its own VET, and needs mention-annotated CoNLL the loop does not
produce.
`I_RE_RAN_THE_WALL_...` `THE_OPERATIVE_NUMBER_IS_5_4_PERCENT_...` `SCOPING_THE_PRESCRIBED_BUILD_...`

## 🌙 THE NIGHT OF 2026-08-21 -- **COLLAPSED. NOT THE ONLY COPY: every row lives in its named note
AND in the plan's consolidated top block. Do NOT re-expand.**

| # | the number that carries it |
|---|---|
| **H2/E3/B4** | Foraging read its way to `textbook_biology 0.63245` (register headline WITHDRAWN). Coref "salience" is PROVABLY a mention-count (`argmax_count_fraction 1.0`, n=89) and that HARD_FAIL is UNDERPOWERED. Spelling beats the meaning read-out at rank 1 (`0.0767` vs `0.0480`) but the substrate WINS the full ranking (`37.0` vs `54.0`) -- **the defect is PRECISION AT THE TOP.** [`T1_`,`T2b_`,`T2c_`,`T5b_`] |
| ⭐ **RATE** | **WRITE LESS: `0.0710 -> 0.3079` at p90, 4.3x -- BUT A RATE-MATCHED RANDOM GATE MATCHES IT.** *Prediction-error gating REFUTED; the gain is RATE.* ⛔ every arm stays BELOW co-occurrence. [`THE_RATE_SWEEP_...`] |
| **NORMS12** | 829 identical pairs, one scorer: `SUPPLIED euclid 0.2876 | cosine 0.2176 | LEARNED d=1024 0.1071 | d=256 0.0944`. **EUCLID BEATS COSINE BY `+0.0700`, MORE THAN OUR WHOLE ARM CLEARS ITS NULL (`0.0440`).** ✅ `GROUNDED_CAP=0.45` is a MEASURED SAFETY PROPERTY. 🚫 SUPPLY, NOT LEARNING. [`SUPPLIED_BEATS_LEARNED_2_69x_`,`THE_CAP_IS_PRINCIPLED_`] |
| **CHANCE?** | **CORRECTED, I OVER-REACHED:** the trained substrate is **+16.3 pp REPLICATED** over an untrained codebook. **But `SUBSTRATE - COUNTING = -0.142` CI `[-0.203,-0.082]` SEPARATED**, cross-task: `counting RAW 0.0885 | OURS 0.1071 | counting+IDF 0.1835 | supplied 0.2876`, **`IDF - OURS = +0.0764` CI `[+0.0263,+0.1278]`.** 🚫 **ANY CLAIM HERE MUST CLEAR `0.1835`.** ⚠️ *Word-similarity channel ONLY -- see TOP ITEM.* [`COUNTING_WITH_ONE_STANDARD_WEIGHTING_`] |

## WHAT IS RUNNING

- 🏗️ **OPERATING MODEL (OWNER 08-22): STRATEGY SESSION + SOLVER SESSIONS.** This session keeps the  10k view, writes briefs and INTEGRATES; solvers solve one bounded problem. **THE ORDER LIVES IN EACH  `notes/problems/<slug>/PROBLEM.md` FRONTMATTER (`priority:`) -- ENUMERATE, NEVER MIRROR.** *`11`  open, `5` solved+reviewed. Q111: solvers never write `hdlab/`.* `notes/problems/README.md`
- 🧠 **SOMATOTOPY HOLDS AT POWER: THE MOTOR DIMENSIONS CARRY VERBS (08-23).** **ACTION − PERCEPTUAL on verbs `+0.0651` `[+0.0306,+0.1005]`, CI-SEPARATED**, 3,487 SimVerb pairs. *At `n=222` the same test said NOTHING -- the fix was POWER, not caution.* 🔻 **SINGLE dissociation**; the noun half includes zero. ⚠️ *I framed this as "nobody had checked" -- FALSE, the 08-22 entry above says the asset clears on verbs. My prior-work check read the brief, not STATUS. The NEW part is the dimension split.* *Witness: `test_sensorimotor_covers_the_verb_hole.py`.*
- 🚨 **AND THE CHANNEL CANNOT GATE LINKS ALONE -- THIS CHANGES WHAT PRIORITY-1 ASKS FOR (08-23).**
  The brief says use it *INSTEAD* of co-occurrence. **As a DECIDER it cannot work, structurally.**
  `GROUNDED_CAP 0.45` < `SIMILARITY_LINK_THRESHOLD 0.5`, so as shipped it **links `0` of `877`
  genuinely-similar verb pairs. ZERO.** 🔻 **And uncapping is not the fix: at `0.5` unclamped it
  links `66.0%` of similar AND `37.3%` of DISSIMILAR pairs.** 📉 **No threshold rescues it** --
  swept `0.30`->`0.95`, best margin `+0.287` occurs AT `0.50`, where it already sits.
  *Threshold-free **AUC `0.7002`** -- real signal, nowhere near separable.*
  ➡️ **IT IS A CONTRIBUTOR, NOT A DECIDER.** ⚠️ *NOT a licence to raise the cap -- the `0.05` gap
  is what makes "contribute, do not decide" enforceable in code.*
  *Witness: `test_the_channel_cannot_gate_links_alone.py`.* *Witness: `test_sensorimotor_covers_the_verb_hole.py`.*
- 🔍 **THE OTHER HALF OF THE PRIORITY-1 DIAGNOSIS, PRICED -- AND BOTH OBVIOUS FIXES FAIL (08-23).**
  *Measured with the sensorimotor channel BECAUSE it has signal to lose; our own codes would confuse
  format-loss with nothing-there.* **STORING is fine: `+0.3107` raw -> `+0.2920` in our 256-dim dense
  bipolar format (94%), info-free arm `-0.0112`.** 🚨 **COMBINING is the bottleneck: k=2
  distractors -> 47% of raw, k=8 -> `+0.0808` (26%, null `0.0338`).**
  🚫 **SPARSITY DOES NOT RESCUE IT** -- swept `1%`->`100%`, every density collapses to ~`+0.08`;
  retention says `44%` vs `26%` but ABSOLUTE says `+0.0912` vs `+0.0764`. **A RATIO WHOSE DENOMINATOR
  YOU ALSO CHANGED IS NOT A RESULT** (I built that control first; my initial verdict said the
  opposite). ✏️ **NOR DOES AN ADDRESSED SLOT, AND I HAD WRITTEN THAT ADVICE INTO THE BRIEF BEFORE
  TESTING IT.** Addressing works as ADDRESSING (right key recovers at cos `+0.3336`, wrong key
  `-0.0037`) **but buys NO signal: `+0.0536` vs `+0.0670` at k=8, WORSE at k=32 -- binding PERMUTES
  interference, it does not remove it.**
  ➡️ **SURVIVING RULE: keep the number of items in one superposition SMALL, or give meaning its OWN
  STORE rather than a key into a shared one.** 🧠 *Cortex does not superpose meaning into one
  shared vector at all -- it keeps separate populations and addresses them.* ⚠️ *Algebraic binding is
  our-invention-under-test, not biology.* *Three witnesses; all three reverify commands in the brief.*
- ✅ **Q115 EXECUTED (08-23): new cells are GATED, the backlog is INVENTORIED.** *Pre-commit refuses a new `experiments/*.py` that writes a result without the shared helper, added files only, controlled both ways.* 🔻 **COVERAGE `~21%` IS WITHDRAWN -- the truth is `71.2%`** (`3,495` of `4,908` re-runnable; `1,413` replay). **THE "1 BY 1" LIST: `425` assert a result, `135` of those are CITED by a steering doc -- those `135` are the real list.** *`tools/reproducibility_inventory.py` regenerates it.*
- ✅ **THE FOUNDATION LOADS NOW, AND RESUMING DOES NOT HELP GROUNDING (08-23).** *A matched read goes `168` -> `9` new groundings and precision sits at its RANDOM floor in every arm; a permuted-label DECOY matches RESUMED exactly (`0/164`), so it is anchor geometry, not meaning.* **RETIRED PREDICTION: "degeneracy falls as vocabulary grows". Persistence is NECESSARY, NOT SUFFICIENT -- never bill it as a grounding fix.** *Pinned in the constructor, positive-controlled.*
- 🖥️ **GUI TAB 9 "SUBSTRATE" -- the whole pipeline on one screen, from `data/substrate_progress.json`.** Every row shows when it was last re-checked and goes amber at 3 days / red at 7. 🔻 **THE DURABLE LESSON: the real bug behind *"there is STILL no priority"* was a GUI launched 08-22 13:15 and never restarted -- a feature that ships into a process nobody restarts has not shipped.**
- 📘 **ENUMERATE THE FIELDS THAT EXIST BEFORE CALLING ONE MISSING** -- one line, `sorted({k for r in rows for k in r})`. *Now in `CLAUDE.md` Evidence discipline 2 (loaded every session) with both incidents that earned it, and a DO-NOT-BUILD-A-TOOL note.*
- 🔻 **RETRACTED SAME DAY -- "THE DURABILITY GATE IS HOLLOW" WAS MY OWN WRONG-FIELD ERROR.** *I measured `gate_decision_target` while `revival_criteria` sat filled on `41` of `42`. It reached a note, the plan, STATUS and a session-start check. Hook corrected and verified silent; the note carries the retraction at its top.*
- 🧪 **BOTH PATHS DRIVEN END TO END 08-23 -- write path healthy, read path cannot refuse.** *Carried and kept current by GUI tab 9 stages 3 and 5.*
- 🧠 **TWO SESSIONS, ONE ORGAN -- RECONCILED 08-23, AND IT CORRECTED ME TWICE.** *Synthesis:
  **the 52 seeds are CLUSTERED BY POLARITY (`+0.0232` vs null `[-0.0076,+0.0087]`), so Stage B reads
  WHICH HAND-LABELLED CLUSTER a target landed beside -- it is NOT reading valence off the graph.**
  A concurrent session's finding that WordNet distance carries no valence stands; my purity result
  survived its baseline (`0.800` vs random-5 `0.600`). Now filed as `propagate_along_the_relation`.*
- 🔧 **COORDINATION FIXED 08-23:** *two sessions worked one organ unaware; the claim queue could only claim PRE-EXISTING rows, so starting new work was unannounceable. `dispatch_queue.py announce` adds-and-claims in one step.*
- ✅ **LANDING CODE AND RUNNING ITS TESTS IS NOT THE SAME ACT.** *A piped pytest's exit code is `tail`'s -- I committed a brief twice on a red cert. **Now enforced by a pre-commit hook**, so it cannot recur by memory.*
- ✅ **EVICTED TO `STATUS_LESSONS.md` 08-23, AND NOW OWNED BY THE FILED BRIEF  `substrate_never_resumes` (priority 3):** nothing loads a foundation -- `self.foundation_dir` was  assigned and never read, `load_foundation` calls measured at `0`. **Makes the plan's own  way-attractor prediction unreachable (arithmetic, not tuning).** *NOT measured: whether loading  helps -- that is the brief's experiment, not mine.*  `THE_ASSEMBLED_SUBSTRATE_NEVER_LOADS_A_FOUNDATION_...`

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
BELOW the neighbour-copy incumbent*; 44 sparsifying the STORED KEY under a partial cue -- below the
flat store with oracle*; 45 the BASIN EXPLANATION for cleanup nulls -- opposite to prediction*;
46 CUE-SIDE ENGINEERING as a read-out fix -- does not transfer to hit@1*.
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
C32 "0 of 7,769 meet the bar" -> 1 of 7,789, and that survivor is itself rejected; C33 "our
instrument cannot resolve verbs even when handed the answer" -- SUSPENDED at n=86 became MEASURED
NEGATIVE at n=222 (rho 0.2607, margin +0.1452 NOT_SEPARATED, permutation p=0.001) -- cite this,
never the retired n=86 number; C34 "the constant floor is the binding one" FALSE in general -- it
is -0.1959/-0.2253 on the bridging/selectional strata, the WEAKEST of the four; C35 "binding-operator
choice is EMPIRICALLY NULL across two cells/six operators" PART-WRONG THREE WAYS -- a 3-bin
instrument is not a null, wrong cell named, two operators COLLAPSE; never varied on any job this
programme runs on; C36 "d 256->8192 moves partial-cue addressing" MIXES READ REGIMES -- matched, the
conclusion (dimensionality does nothing for addressing) STRENGTHENS; C37 "B1 IS A CLIFF" WITHDRAWN/
INVERTED -- those are cos_syn/rel/unrel, not vocabulary strata; OUR 0.002 is correct and counting's
0.830 is the defect. Full text of C33-C37: `STATUS_LESSONS.md`.


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
HALF-WIDTH + NULL p95 BESIDE EVERY MARGIN -- A WIDTH IS NOT AN EFFECT (cost 3x, C32-C34). 15 A
GRID'S RESOLUTION IS PART OF ITS VERDICT -- a 3-value-grid equality is a BIN not a measurement
(C35); state swept values + queries/point. 16 A FLOOR IS SPECIFIC TO ITS REPRESENTATION, NOT ONLY
ITS POPULATION -- 0.5431 (bag-of-words) was quoted as THE bar for 2 days then misapplied to
arc-built arms (real floor 0.6317); rebuild the floor whenever the representation changes. 17
EVERY NEGATIVE GETS A BRAIN-FIDELITY DRILL, EVERY TIME (owner 08-18) -- ask WHICH BRAIN STRUCTURE,
replicating vs substituting, what closes the gap; FIRST ask if the negative is even real (4 of
08-18's were measurement defects, not results). SAFETY: brain-drill queries use general biology
terms only, never our architecture/organs/operators/dims/results. 18 GATE ON THE FLOOR'S UPPER
BOUND, NOT ITS POINT VALUE -- CREDIBLE BAR = floor + its own 95% half-width; if no achievable
score could clear it, the point is UNTESTABLE, not negative.
Full text of 14-18 (verbatim, nothing shortened in substance): `STATUS_LESSONS.md`
"STANDING DISCIPLINES 14-18 -- FULL TEXT MOVED FROM STATUS.md 2026-08-22".
