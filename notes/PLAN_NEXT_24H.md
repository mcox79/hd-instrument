# PLAN -- THE NEXT 24 HOURS

**Rewritten 2026-08-16 by a docs-only pass, at HEAD `94d005cf3`, branch
`dataprep/mcguffey-graded-corpus`.** *(Previous version of this file was written at `fa38d15a9` and is
fully superseded.)*

Built on `notes/drill_computational_theory_what_each_organ_computes_2026-08-16.md` (commit
`82d1ee8d5`). `notes/LONG_TERM_PLAN.md` is Director-owned and was **read, not edited, by this pass**;
where this plan contradicts it, this plan states so and the Director adjudicates.

**Scope of this pass, stated up front so nothing is mistaken for work done:** this pass rewrote one
document. **It authored no experiment cell, ran no cell, spawned no subagent, signalled no process,
and committed nothing.** Every item below is a specification for whoever executes it.

**Read this before quoting any number.** Eight numbers have been retracted in three days, several of
them the Director's. Every figure here is marked either **VERIFIED ON DISK BY THIS PASS** with its
artifact path, or **AGENT MEASUREMENT** with its `.claude/scan-out/` fragment named. Those are
different classes of evidence and they are never merged. Where this pass could not verify a figure it
is **left out and said to be left out**, not carried forward.

---

## 0. THE RULE THAT GOVERNS EVERY ITEM BELOW -- COPY THE COMPUTATION, SWEEP THE PARAMETER

**This is new, it is the drill's most portable finding, and it goes first because it changes how
every other item is designed.**

- **A brain COMPUTATION is derived from THE PROBLEM**, and the problem is one we share. Separation
  before completion. A dense cue addressing a sparse store through a learned map. An error residual
  as the learning signal. Generate-and-test with a verifier that is not the generator. Two systems
  because one set of weights cannot serve two timescales. **Copy these exactly.**
- **A brain PARAMETER is derived from A CONSTRAINT**, and the constraints are ones we do not share: a
  metabolic budget, a wiring volume, a development time, evolutionary path dependence. 0.2% sparsity.
  Seven gamma cycles per theta. A five-hour tagging window. A particular expansion ratio.
  **Treat every one as a HYPOTHESIS TO SWEEP. Never adopt one as a value.**

**The evidence in our own table, and nobody had read it this way until the drill.** Our most explicit
parameter copy -- the pinned MTL 0.2% active fraction -- was the **worst point in its own sweep,
monotonically** (0.0396 at f=0.002 against 0.0744 dense; *AGENT MEASUREMENT,
`.claude/scan-out/sparsify-right-object.json`*). Our one 100%-fidelity component copied a STRUCTURE
and held under a partial cue. **The components that have most clearly hurt us are the ones where we
copied a number; the components that have most clearly helped are the ones where we copied an
operation.**

**Operationally, per item:** the design must name which of its choices is a COMPUTATION being copied
and which is a PARAMETER being swept. A parameter presented as pinned is barred under the standing
fidelity gate, and this is the specific form that violation has been taking.

**STATUS OF THIS RULE: it is the Director's strategic read, labelled a hypothesis pending VET, not a
measured verdict.** ITEM 12 is the cheap test of it and needs no new run.

---

## 1. THE STANDING CAVEAT -- OUR SUBSTRATE'S CORE OPERATION IS UNPINNED IN THE BRAIN

**This sentence attaches to every VSA-dependent item in this plan and to every claim built on one.**

> **No recording has shown a population of neurons computing an algebraic binding operation over two
> full-rank vector codes. There are three live candidate accounts of how the brain binds --
> algebraic (VSA), coarse-coded conjunctive (O'Reilly), and synchrony (Hummel/von der Malsburg) --
> and all three have published objections. THE BINDING PROBLEM IS OPEN. We built as if VSA had won,
> and we drilled inside the frame six times without once drilling the critique of it.**

*(Drill section 7. Its own scan's summary sentence: the evidence "focus[es] primarily on computational
models inspired by neuroscience rather than direct neurobiological evidence of vector symbolic binding
in the brain." Gain fields are the nearest measured multiplicative interaction and they are a SCALAR
gain against a tuning curve, not the product of two vector codes.)*

**What this changes, concretely and in both directions.**

1. **Relabelling, and it is not cosmetic.** The substrate's representational choice is
   **OUR-INVENTION-BEING-TESTED**, not biology. Under the standing fidelity gate, presenting an
   invention as pinned emits no score at all -- **and by that standard our whole representational
   substrate has been mislabelled.** Every brief, prereg and organ row that calls VSA binding
   brain-derived needs that word changed. This is bookkeeping the Director owns.
2. **It is NOT "abandon the substrate", and overcorrecting here would be its own failure.** VSA has
   real biological anchors (the fly's random expansion into Kenyon cells with k-winner inhibition;
   grid modules as a residue-like high-dimensional code; gain fields), one strong neural-implementation
   existence proof (Eliasmith's Spaun, circular convolution in spiking LIF neurons), the only clean
   answer to Jackendoff's challenges that does not require synchrony, and one genuine advantage over
   its leading rival -- **role-filler independence, which coarse-coded conjunctive coding lacks.**
3. **The rival's organ is ours and we shelved it on the wrong grounds.** `hdlab/perirhinal_conjunctive.py`
   is the conjunctive account's organ. It lost CI-separated below flat -- **with a conjunction operator
   we chose by convenience and cannot justify** (section 5, row 9). Do not shelve it on the score.
   Revive it when a computationally justified conjunction operator exists.
   *Caveat carried from the drill's own Part E: "we own this account's organ" is a NAME-level claim and
   needs a runtime check of the module before it is acted on. This pass did not do that check either.*
4. **"UNFALSIFIED IS NOT CONFIRMED."** No experiment has falsified VSA as a brain theory because none
   has been designed. Stop reading the absence of a refutation as support.

**The three consequences that are actionable in the next 24 hours are ITEMS 1, 3 and 4.**

---

## 2. WHERE WE ARE

### 2.1 There is ONE isolated blocker and it is measured to four decimal places

**A partial cue does not produce the right address.**

The sparse key addresses the store **1.0000 of the time from the store's own rows** -- zero collisions
among 5,491 keys at expand-dim 2048 / sparsity 0.02 / 41 active units, mean margin 0.8072 -- and
**0.0325 of the time from the partial cue** (n=1997, 1,591 distinct items addressed).
*VERIFIED ON DISK BY THIS PASS: `data/exp_cue_to_store_translation_v1/metrics.json`,
`A8b_KEY_COLLISION_AUDIT` and `A8_MECHANISM_DIAGNOSTICS`.*

In plain language: **the filing system works perfectly if you hand it the exact card it already holds,
and works 3% of the time if you describe the card. Real reading is always the second case.**

Three consequences, and they matter more than the number:

- **The July "link-not-reconstruct" design is NOT refuted -- it was never reached.** Its LINK stage is
  proven correct by self-test; its ADDRESS stage never delivers. A failure at the address stage is not
  evidence about the indexing architecture behind it.
- **The autoassociative completer is not failing either. It is pointed at the wrong kind of cue.**
  The same pipeline reads 1.0000 on a degraded-copy cue and 0.0325 on a description/context cue.
- **Why the address fails is measured:** the partial cue's cosine to its own stored row is **0.1621**.
  *VERIFIED ON DISK, `FITTED_MAPS/PARTIAL_CUE/cos_cue_to_its_OWN_stored_row_on_TEST`.* A sparsifier
  keeping the top 2% of an expansion turns a 0.16 alignment into a near-random active set. **The cue
  never gets close enough for the key to matter.**

**And the theory says our reading of this as a "defect" was backwards.** We measured the cue at
participation ratio 202.04/256 against the store's 88.74/256, called the cue's higher rank a defect,
and spent a whole cell engineering the cue LOWER-rank. Treves & Rolls 1992's two-input argument says
the retrieval cue SHOULD be a numerically large, dense cortical pattern addressing a sparse store
through a learned, associatively-modified matrix. **Our 2.3x rank ratio is an UNDER-mismatch on both
sides.** The cell measured no gain, which is what the theory predicts. *(Drill section 2c. The brain's
comparison figure -- rat entorhinal layer II ~2e5 cells into ~1e6 dentate granule cells, a ~5x
expansion into a code then ~100x sparser -- is AGENT MEASUREMENT / lit-sourced,
`.claude/scan-out/partial-cue-transfer-drill.json`.)*

### 2.2 WHAT LANDED SINCE THE LAST PLAN

**(a) THE 47-FOUNDATION FULL GRID IS DONE. The prior plan carried it as "in flight at 18/47, never
read". It finished.**
*VERIFIED ON DISK BY THIS PASS: `data/exp_foundation_neighbourhood_purity_v1/metrics.json`, written
2026-08-16T15:13, 261,817 B, `grid=full`, 47 foundations, population n=2358, ruler-mode gate PASS
(`RUN_MODE=full`, `V=4096`, `CORPUS_BYTES=64,000,000`), verdict
`A_FOUNDATION_CLEARS_THE_BINDING_FLOOR`, 47/47 units in `scratch/fpb_full.log`.*

It confirms the smoke gate and it adds three things the smoke could not say:

| arm | margin over the incumbent constant floor 0.2070 | band |
|---|---|---|
| `F24_FUSE_ALL3_STATIC_w1.00` | **+0.1917 [+0.1671,+0.2163]** | ABOVE |
| `F20_FUSE_GLOVE_w1.00` | **+0.1196 [+0.0950,+0.1442]** | ABOVE |
| `F10_SUPPLY_GLOVE_m5_eta0.50` (**our operator, better supply**) | **+0.1012 [+0.0772,+0.1251]** | ABOVE |
| `F03_OURS_THEMATIC_m5_eta0.50` | **-0.0743 [-0.0950,-0.0534]** | **BELOW** |
| `F00_INCUMBENT_OURS_COOCCURRENCE` | **-0.1608 [-0.1790,-0.1433]** | **BELOW** |

*ALL VERIFIED ON DISK BY THIS PASS, `summary.BAR_arm_by_arm`, key `B_vs_INCUMBENT_CONSTANT_PROTOTYPE_0.2070`.*

1. **21 of 47 foundations clear the binding floor, and every single one of them is a static-table
   supply or fusion arm (GloVe / word2vec / fastText). NOT ONE arm whose supply is OURS clears.**
   That is a sharper and less comfortable statement than "a static foundation clears the floor".
2. **The consolidation trap is now demonstrated, not warned about.** `F03_OURS_THEMATIC` reads
   **+0.1318 [+0.1179,+0.1459] ABOVE its OWN constant floor** and **-0.0743 BELOW the incumbent's
   0.2070**. Same arm, two floors, opposite verdicts. **Bind against `max(own, incumbent)`, always.**
3. **Purity predicts the exact-key read-out and predicts NOTHING about the partial cue.** rho against
   `B_EXACT_KEY_NATIVE` is **0.961** (n=45) and against `A2_SEMANTIC` **0.9603**; against
   `B_PARTIAL_CUE` it is **-0.0167** (n=40) and against `A1_SENTENCE` **-0.2356**, where participation
   ratio tracks at **+0.7053**. The smoke's 0.32 for the sentence cue does not survive the full grid.
   **Do not generalise purity past the exact key.**
4. **The partial cue still does not move.** `PARTIAL_CUE_vs_INCUMBENT` is **-0.0012 NOT_SEPARATED** for
   the best GloVe supply and **-0.0067 BELOW** for thematic. A foundation good enough to clear the
   floor at exact key buys nothing under a partial cue. **That transfer is the isolated blocker.**

**(b) THE CONSTANT/PROTOTYPE FLOOR IS NOW THE BAR'S REQUIRED FOURTH ROLE (`85b9aac78`, an ancestor of
HEAD -- VERIFIED), AND EVERY HISTORICAL BAR DECISION USED A THREE-FLOOR MAX.** The role did not exist
in `tools/c3_gate.py`, so **all 7,789 banked cells were judged against
`max(orthographic, frequency, scramble)` with its strongest member missing.** Worse: a constant floor
classified as `None`, which is the TREATMENT class, so **a zero-query-information ranking was eligible
to carry a cell's claim.**
**Only 12 of 7,789 cells record a constant-floor margin at all; 7,777 never ran one.**
*VERIFIED ON DISK BY THIS PASS, `data/verdict_bar_reports/verdict-bar-20260817T002627Z.json`,
`constant_floor_coverage`. Reproduction and corpus A/B are AGENT MEASUREMENT,
`.claude/scan-out/gate-constant-floor-fix.json`.*
**This is withholding, not refutation.** No cell is demoted. The four cells the unfixed tool passed
now read `NO_EVIDENCE / NO_CONSTANT_FLOOR`, which says "we cannot tell", not "it fails".

**(c) `matched_candidate_sets` WAS VOID AND IS REBUILT. EVERY MATCHED-POOL NUMBER IS WITHDRAWN.**
The old construction discarded the multiplicity of the gold-marginal draw and resolved a tie-heavy
trigram channel by ascending anchor index, so the same few anchors became distractors repeatedly and a
fitted constant could exploit an item-independent fact. Measured fitted-oracle readings on that pool
range **0.3873** (the preserved legacy construction in the module's own negative control) to **0.9042**
(conditioned form, on the feeling-match cell's population), against a chance of **0.0625**. The rebuilt
stratified marginal-preserving pool reads **0.0829**, and the check is now a callable run on every pool
built rather than a warning in a docstring.
*AGENT MEASUREMENT, `.claude/scan-out/pool-floor-integrity.json`; the 0.9042 is
`.claude/scan-out/feeling-match-rejector.json`. Four cells' matched blocks are listed there; nothing
was demoted, re-labelled or deleted.*

**(d) THE CORPUS PASS COUNT IS 1, AND THAT SURVIVOR IS REJECTED ON FOUR GROUNDS.**
*VERIFIED ON DISK BY THIS PASS: 7,789 scanned, `MEETS_BAR` 1, `FAILS_BAR` 7,770, `NO_EVIDENCE` 18;
the one cell is `exp_cue_to_store_translation_v1`.*
The four grounds, in the order they were found:
1. **The pool under it fails its own oracle check** -- block `P3_MATCHED_K15|EXACT_KEY` records a fitted
   constant at 0.7354 against chance 0.0625, and (c) now shows that is a real construction defect.
2. **It is the exact-key regime, not the operating point.** The same arm on the same cell's table:
   `P3_MATCHED|PARTIAL_CUE` -0.0295, `P1_OPEN|EXACT_KEY` -0.0776, `P1_OPEN|PARTIAL_CUE` -0.0931,
   `P1b_OPEN_MORPHBLOCK|PARTIAL_CUE` -0.0809. On both open pools in both regimes the CONSTANT floor
   beats it.
3. **The cell declines a cell-level verdict.** `verdict = "COMPUTED"`, `verdict_msg = "see RESULTS;
   gates are per-condition"`. *VERIFIED ON DISK BY THIS PASS.* It ships eight instruments; the checker
   scores a cell on its best arm anywhere.
4. **Its margin was overstated 4.20x.** `+0.0445 -> +0.0106` once `F1b_ORTHO_PREFIX` -- the cell's OWN
   declared binding floor -- stopped classifying as a non-floor and entered the min.
   *AGENT MEASUREMENT, `.claude/scan-out/pool-floor-integrity.json`.*

**"0 of 7,769" is retired. So is "2 of 7,772". The current figure is 1 of 7,789 and it does not touch
the open-vocabulary read-out.**

**(e) THE FEELING-MATCH REJECTOR GENERALISES WHERE ATTESTATION IS STRUCTURALLY BLIND -- AND THE AFFECT
CHANNEL DID NONE OF THE WORK.** On unattested candidates the attestation incumbent scores **exactly
0.0625**, this pool's chance, with 0.9375 tie mass; the profile rejector scores **0.1003**, which is
**+0.0267 [+0.0058,+0.0476] over max(four floors)**, **+0.0376 over attestation**, and survives both the
frequency (**+0.0373**) and concreteness (**+0.0355**) controls through the identical estimator. It also
reproduces the owner's TWO MODES, where attestation's separation is **exactly 0.0000 with CI [0,0]**.
**But three columns of affect are indistinguishable from three columns of rater noise** (+0.0014
[-0.0078,+0.0105] and -0.0170 [-0.0376,+0.0033], both NOT_SEPARATED). **The win is "having a per-word
semantic profile at all", not feeling.** The cell's own landed verdict string overstates and must not
be quoted.
*AGENT MEASUREMENT, `.claude/scan-out/feeling-match-rejector.json`, full run n=5733 / 1197 unattested.*
**The live hypothesis is now REGISTER, not valence** -- the owner's own illustration, "think" versus
"contemplate", is formality and effortfulness, which is not what valence/arousal/dominance measures.
See ITEM 7.

**(f) THE CONFIDENCE EFFECT REPLICATED AND IT DETECTS ONE THING: "I AM ABOUT TO RETURN THE QUERY
WORD".** AUROC 0.665 [0.6152,0.7121] reproduces exactly, is not frequency (rho 0.0026), and holds in
both split-halves. **95.76% of the hits ARE the query word**; AUROC against the label "the argmax is
the query word" is 0.665 CI-ABOVE. **The landed instrument masks that word out of the pool by
construction, and there the AUROC is 0.4962 NOT_SEPARATED, beating the random-abstain band at 0 of 14
rates -- while a purely orthographic policy ("answer only long words") scores 0.5652 CI-ABOVE.** On the
naming block a query-rarity policy that understands nothing scores 0.7801 against our 0.665, paired
-0.1151 CI-separated BELOW.
*AGENT MEASUREMENT, `.claude/scan-out/confidence-calibration-replicate.json`.*
**The fidelity reading, which is the useful part:** our signal is OUTPUT-side (it reads the peakedness
of a finished ranking) and the brain's feeling-of-knowing is substantially CUE-side (available before
retrieval resolves, which is why the owner's Q12 give-up policy is executable at all). Ours can only
fire once the answer is already on top. **Named divergence with a direction, not a ceiling.**

### 2.3 THE FLOOR, AND THE RULE THAT KEEPS BEING BROKEN

**The standing bar, no exceptions:** a **CI-separated margin over
`max(orthographic, frequency, scramble, CONSTANT/PROTOTYPE)`** on the **identical scorer, n, pool and
gold**, never a bare absolute number, plus a known-answer arm proving the instrument and a null arm
proving the effect, failing independently.

**The binding floor set on the open read-out pool** (`data/exp_cue_to_store_translation_v1/metrics.json`,
`P1_OPEN`, test half n=1997) -- **ALL VERIFIED ON DISK BY THIS PASS:**

| arm | hit@1, tie-corrected |
|---|---|
| **F4_CONSTANT_PROTOTYPE** | **0.1382** |
| F1_ORTHO_TRIGRAM | 0.0872 |
| F1b_ORTHO_PREFIX | 0.0578 |
| F2_FREQUENCY | 0.0200 |
| F3_SCRAMBLE_NULL | 0.0105 |
| *(not a floor)* ORACLE_CONSTANT_FITTED_ON_GOLDS | 0.1678 |
| *(for contrast)* A0_RAW_INCUMBENT exact key | 0.0446 |
| *(for contrast)* A0_RAW_INCUMBENT partial cue | 0.0250 |

**🚨 THERE ARE NOW AT LEAST FIVE DIFFERENT CONSTANT FLOORS ON FIVE DIFFERENT POPULATIONS, AND THEY ARE
NOT CORRECTIONS OF EACH OTHER.**

| value | population | source |
|---|---|---|
| **0.1382** | open read-out pool, n=1997 test half | *VERIFIED ON DISK* |
| **0.1390** | same pool, landed full n=3994 | *VERIFIED, `exp_task_degeneracy_v1`* |
| **0.2070** | foundation-purity population, n=2358, 47 foundations | *VERIFIED ON DISK, this grid* |
| **0.062445 / 0.065163 / 0.006454** | the feeling-match cell's balanced/unattested/open pools | *AGENT MEASUREMENT* |
| **0.1390 / 0.0121 / 0.2028 / 0.0579 / 0.0805** | the confidence cell's five blocks | *AGENT MEASUREMENT* |

**RULE, and it is the one this project has broken most often: a floor is computed ON THE ITEM'S OWN
POPULATION. Never import 0.1382 and never import 0.2070. Both are real; neither travels.** Every item
in section 4 says "computed on this item's own population" and means it literally.

**Three further floor rules, all earned:**
- **REPORT TIE CONVENTIONS BOTH WAYS.** A top-50 spelling comparison flips from +0.0105 NOT_SEP to
  +0.0641 ABOVE depending on convention, because the floor holds 15.27% tie mass and we hold 0.0%.
- **CONSOLIDATION DESTROYS THE STORE'S OWN CONSTANT FLOOR.** Demonstrated on the full grid in 2.2(a).
  Bind against `max(own, incumbent)`.
- **A NUMBER MEASURED AT THE EXACT KEY DOES NOT TRANSFER TO THE PARTIAL-CUE REGIME**, which is the real
  one. State the cue regime beside every retrieval number.

### 2.4 What is already known to have failed, so nobody re-runs it

- **Bridging with the thematic hub is a MEASURED NULL.** rho 0.0270 against floors 0.0412 / 0.0209 /
  0.0900 on the identical stratum (n=394), NOT_SEPARATED, with **both** known-answer arms passing
  (K1 0.3301, K2_ORACLE 0.2893). Bridged codes keep identity (96.1% distinct) and lose meaning
  (retention 0.0819). The **external curated graph fails too** (0.0457, NOT_SEP). *(DO-NOT-REDO 38.)*
- **Free clumping is worth less than nothing.** Hebbian replay reaches the owner's clumping target
  (synonym cosine 0.1214 -> 0.4705) and buys nothing; participation ratio collapses 171 -> 31. Reason:
  **only 0.46% of a word's top-20 store neighbours are its synonyms.** *AGENT MEASUREMENT,
  `.claude/scan-out/synonym-clumping.json`, `b84417941`.*
- **Sparsifying the reading anchor dies on the real task** (DO-NOT-REDO 39).
- **Sparsifying the meaning VALUE is settled and should stop.** The best sparse point (f=0.10) is
  +0.0030 [-0.0030,+0.0088] over dense -- NOT separated. *AGENT MEASUREMENT,
  `.claude/scan-out/sparsify-right-object.json`.* **Theory says why: separation IS the deliberate
  destruction of similarity, so a code optimised to make two similar things orthogonal is optimised to
  make a similarity judgement impossible.** Revive only if the value is being used as an ADDRESS.
- **A learned LINEAR cue-to-store translator buys nothing.** The gold-blind ridge selects lambda=10.0,
  the largest in the grid, for the partial cue against 1e-4 for the exact key -- maximum shrinkage
  preferred, i.e. almost no learnable linear signal. *VERIFIED ON DISK.* **The biology pins that the
  map is LEARNED. It does not pin LINEARITY, and linearity is the part that was tested.**
- **The affect channel as three per-word scalars, for slot rejection.** Shelved on its pre-registered
  brain-framed criterion. See 2.2(e). Revival criteria are register, context-settled affect, or a
  lexical-retrieval bench -- none of them a score.
- **The top1-minus-top2 margin as a model of the brain's monitoring signal.** Shelved: it detects one
  event and the instrument masks that event out. See 2.2(f).

---

## 3. WHAT IS IN FLIGHT -- DO NOT COLLIDE, DO NOT POLL

Attributed by **reading `.pid` files and output-directory listings**, not by signalling or inspecting
any process.

| PID | what it is | disk state as of this pass | note |
|---|---|---|---|
| **18496** | selectional-constraint bridging FULL (`scratch/selbridge_full2.pid`) | `data/exp_selectional_constraint_bridge_v1/` is **EMPTY** | **No arm has been scored. Nothing about it is a result yet.** |
| **30812** | Phase 2 thematic v2 FULL (`scratch/them_v2_full.pid`) | `data/exp_thematic_relation_supply_bridged_grounding_v2/metrics.json` **landed 11:43** | its SMOKE was already a measured null (2.4) |
| **22984** | 47-foundation FULL grid (`scratch/fpb_full.pid`) | **FINISHED.** metrics.json 15:13, 47/47 units | **read in 2.2(a). This item is closed.** |
| *(22588)* | target-space decider SMOKE (`scratch/ts_decider_smoke.pid`) | only `..._v1_smoke/` exists, metrics 09:33; **the FULL directory does not exist** | ITEM 11 |
| *(33256)* | feeling-match rejector worker | `data/exp_feeling_match_rejector_v1/metrics.json` landed 19:03 | read in 2.2(e) |

**Sibling agents active in this session:** `main`, and `cleanup-memory-organ`, **which owns ITEM 1.**
Reference it; do not duplicate it.

**Also do not touch:** `data/foundation/reading_grounding_v1` and `v2_qualityfix` (22+23 MB, no backup,
gitignored); `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*`;
`data/exp_structured_comparator_v1/probes/`.

**Held pending explicit owner authorisation:** the d=256 -> 1024 raise (it rewrites every persisted
anchor store); any merge to `origin/main`; any origin push.

---

## 4. THE SEQUENCED BACKLOG

Ordered by **what blocks what**, not by cost. Do the lowest open item. If it is blocked, say so in one
line and take the next.

Every item carries: **the question -> the brain structure (and whether we are replicating it or
substituting something convenient) -> the can-fail design -> the floor -> the stop-if -> the runner ->
the dependency.** An item with no floor is not ready to run.

---

### ITEM 1 -- THE CLEANUP MEMORY, SCORED ON ITS OWN RECOVERY AXIS. *TOP. Sibling `cleanup-memory-organ` is on it -- reference, do not duplicate.*

- **The question.** VSA's own theory says unbinding returns a NOISY vector that is useless until it is
  cleaned against an item memory -- Plate says so himself. **So a VSA system's capability is set by its
  CLEANUP MEMORY, not by its algebra: the algebra is a compression scheme and the intelligence is in the
  cleanup.** Ours is measured inert five times. **Does a cleanup memory recover the UN-BOUND ITEM?**
- **Why this is item 1 and not item 6.** It re-reads five banked nulls at once, and the re-reading is
  worth more than the criticism that produced it:

  ```
  exp_hub_spoke_word_g3_cleanup_rescore_v1   reading through cleanup changed the vector by 1.192e-07
  exp_att1_iterative_attractor_cleanup_v1    lift +0.005, basin 1.00x
  exp_cleanup_graded_attractor_vs_argmax_v1  +0.003
  exp_att1_..._krotov_v1                     HARD_FAIL -0.020
  ca3_completion partial cue                 cosine to target +39% relative, argmax recovery 0.0711 -> 0.0709
  ```
  *(Drill section 7d. This pass did not independently recompute these five; they are the drill's
  transcription of banked verdicts.)*
  **All five were scored on "does completion help the downstream task". The theory says the right
  question is "does the cleanup recover the un-bound item", which is the completer's own known-answer
  axis. The one cell that measured that axis found the completer moves the state toward the target in
  cosine WITHOUT changing which pattern is nearest. In VSA terms that is a cleanup memory that cannot
  clean up** -- a component-level diagnosis we did not have.
- **Brain structure, and are we replicating it or substituting something convenient?** CA3 recurrent
  auto-association. **PINNED:** the recurrent anatomy, the capacity theory `p ~ k*C / (a * ln(1/a))`,
  and that CA3-NMDA knockouts impair completion from a degraded cue specifically. **UNPINNED and
  therefore OURS:** the update rule -- Hopfield sign-update and modern-Hopfield softmax are both our
  imports, and `alpha = 0.5` was shipped labelled "brain-canonical", which is an invention wearing a
  pinned label. **CONTESTED, and it must be reported as contested:** whether CA3 is a discrete attractor
  at all. Leutgeb 2007 reports graded continuous CA3 responses; continuous-attractor accounts treat CA3
  as a manifold. **If CA3 is continuous, "settle to the nearest stored pattern" is the wrong operation
  and our three floored attractor nulls are less informative than they look.**
- **The one closed-form design equation in the whole drill that we are not using.**
  `p ~ k*C/(a ln(1/a))`. This is a COMPUTATION, not a parameter: it tells you how capacity trades
  against sparseness. Use it to SIZE the cleanup, and sweep `a` rather than adopting 0.002.
- **Can-fail design.** Primary measure is **RECOVERY OF THE UN-BOUND ITEM**, not downstream hit@1.
  Arms on one population: `A0_NO_CLEANUP`; `T1_CLEANUP` at swept `a`; `K1_ORACLE_CLEANUP` (allowed the
  gold, must approach 1.0 or the instrument is dead); `N1_RANDOM_CODEBOOK` (must sit at `A0`);
  and the discriminating arm the drill's contest demands -- **`T2_CONTINUOUS_SETTLE` against
  `T1_DISCRETE_ARGMAX_SETTLE`**, because the field does not agree which one CA3 is.
- **Floor.** Recovery must clear `max(orthographic, frequency, scramble, constant/prototype)`
  **recomputed on this item's own population**, CI-separated, both tie conventions.
  **Never import 0.1382 or 0.2070.**
- **Stop-if.** (i) `K1_ORACLE_CLEANUP` fails to approach 1.0 -> `INSTRUMENT_STILL_LOOSE`, publish no
  quality number. (ii) `T1` moves cosine toward the target without changing the argmax at every `a`
  across the swept range -> **that is the diagnosis, and it is a real finding about VSA, not about us**:
  report that a cleanup memory built on our codes cannot change a decision, and say what the stronger
  brain-faithful version would be before calling the route exhausted. (iii) `T2_CONTINUOUS` and
  `T1_DISCRETE` are indistinguishable -> our geometry cannot see the field's own open question, and the
  cell has not adjudicated it.
- **Runner.** `cpu_runner_local` for smoke and self-test; **`cpu_runner_0`** for the swept full grid.
- **Dependency.** None. **Blocks:** the re-read of the five nulls above, and every capability claim that
  rests on VSA algebra.

---

### ITEM 2 -- IS THE ANSWER IN THE CUE AT ALL? *The decisive test. BLOCKS 3 AND 4.*

- **The question.** Before any of our machinery touches it, **does the partial cue contain enough
  information to identify the target?** If it does not, no expansion, no completer, no translator and no
  addressing scheme can help, and the blocker relocates upstream to **what we write**, not how we
  compress it.
- **Why this is now possible.** The held-out sentence behind every partial cue is **exactly
  reconstructible** -- checked on 400 items, max absolute error **0.000e+00** -- so the cue can be
  decomposed into its parts. *AGENT MEASUREMENT, `.claude/scan-out/address-information-audit.json`.*
- **The one-variable control the encoder identity makes possible.** `context_vector(graded=True)` is a
  sum over content-word tokens of a hash-seeded bipolar vector, so `cos(store_row, cue)` and
  `cos(raw_count_vector_a, raw_count_vector_i)` **differ by exactly one thing: the 256-dimensional
  random projection.** An UNCOMPRESSED arm is therefore a genuine one-variable control on our encoder,
  and `H^T p_a == mat[a]` is a bit-level self-test that the two representations are the same object.
- **Brain structure.** None is claimed and none should be fabricated. **This is an information audit of
  our own encoder, not a model of anything.** Saying so is the honest answer; inventing an anatomy to
  fill the box is the laundering the fidelity gate bans.
- **Can-fail design.** `U0_UNCOMPRESSED` (raw sparse count vectors) versus `C0_PROJECTED_256` (the live
  encoder) on the identical store, cue, pool and gold. Primary measure: **addressing accuracy**
  (`addressed_item_IS_the_query_word`), against the verified incumbent **0.0325 partial / 1.0000 exact**.
  Secondary: hit@1 against the full four-floor set.
- **Floor.** Addressing must clear a **size-matched random-key control** CI-separated; hit@1 must clear
  `max(four floors)` **computed on this item's own population** CI-separated. Report the exact-key arm
  alongside as the known-answer (it must stay at 1.0000).
- **Stop-if.** `U0_UNCOMPRESSED` also lands near 0.0325 -> **the information is not in the cue.** ITEMS
  3 AND 4 ARE VOID AND MUST NOT BE RUN. **That is a valuable negative and should be reported loudly**,
  because it redirects the whole programme from the cue to the write side -- which is where ITEM 5 already
  lives.
- **Runner.** `cpu_runner_local` (sparse count vectors over 4,000 items is cheap); escalate to
  `cpu_runner_0` only if the full type vocabulary makes the dense contrast large.
- **Dependency.** None on anything in flight. **Blocks ITEMS 3 and 4.**
- **Status.** Cell was being authored at `experiments/exp_cue_information_audit_v1.py`; **that file is
  NOT on disk as of this pass. NO NUMBER EXISTS.**

---

### ITEM 3 -- EXPAND BEFORE YOU SPARSIFY. *BLOCKED BY ITEM 2.*

- **The question.** The brain's retrieval-cue stage **expands** before it sparsifies. We project into
  256 and then sparsify. **Does a genuine expansion before sparsification lift partial-cue addressing
  above 0.0325?**
- **Brain structure, replicate or substitute.** Entorhinal layer II -> dentate gyrus -> CA3.
  **PINNED as a COMPUTATION:** expansion, then sparse recoding, then completion; and that the three
  spaces are NOT commensurate -- commensurability is a design goal nowhere in the brain. The separation
  and completion inequalities were MEASURED, not asserted (Neunuebel & Knierim 2014: the dentate
  representational change EXCEEDS its entorhinal input's; the CA3 change is LESS than both).
  **PARAMETERS, therefore SWEPT NOT ADOPTED:** the ~5x expansion ratio, the ~100x sparsening, the 0.2%
  active fraction. **OURS:** the expansion operator itself.
- **Can-fail design.** Identical store, identical cue, **one variable: the dimensionality of the
  cue-to-key stage.** Sweep 256 (incumbent) -> 2048 -> 8192, each followed by top-k sparsification, with
  the sparsity level **swept rather than set to the MTL band**. `A8b` already shows **zero collisions
  among 5,491 keys at 2048 / 0.02** *(VERIFIED ON DISK)*. Arms: the sweep, plus a **size-matched
  RANDOM-expansion control at each level** (an expansion carrying no structure), plus the exact-key
  known-answer arm at each level.
- **Floor.** Addressing must clear the size-matched random expansion **CI-separated at the same level**;
  hit@1 must clear `max(four floors)` **computed on this item's own population**. **Report the
  between-projection-draw standard deviation next to the CI** -- item bootstraps are blind to
  shared-randomness variance and every cell built on a random projection must report it.
- **Stop-if.** Addressing flat across all three expansion factors while the exact-key arm stays at
  1.0000 -> compression is not the defect; **retire the expansion route and record it with its numbers**,
  writing down what was tested and what the stronger version would be.
- **Runner.** **`gpu_runner_0`** at 8192 (dense matmuls over the full anchor set; 8 GB VRAM, 0.9 cap);
  `cpu_runner_0` at 2048 and below.
- **Dependency.** **HARD DEPENDENCY ON ITEM 2.** Do not run it "to be sure".

---

### ITEM 4 -- LINK-NOT-RECONSTRUCT: SPARSIFY THE ADDRESS, KEEP THE VALUE DENSE. *BLOCKED BY ITEM 2. Informed by ITEM 3.*

**This is the item TWO INDEPENDENT LITERATURES converge on, it was designed on 2026-07-04, and it has
never been built.**

- **The question.** Our store is one flat object asked to be both key and value, scored by cosine in one
  space. **Does a SPARSE ADDRESS pointing at a DENSE GRADED VALUE, returned by LINK and never
  reconstructed, beat the flat store under a partial cue?**
- **Why the confidence in this design is higher than in either route alone.** Route one: hippocampal
  indexing theory (Teyler & DiScenna; Teyler & Rudy 2007; Goode 2020) says the hippocampus computes a
  sparse POINTER SET and **the content never enters it**; retrieval is reinstatement of the linked
  cortical pattern. Route two: the four sparsity objectives. **Capacity/interference wants the key
  sparse; efficient coding of statistics wants the value dense and graded.** They are different
  objectives with different optima and the literature routinely conflates them, and so did we -- we
  applied the capacity objective's optimum and then measured the efficient-coding objective's quantity.
  **Two literatures, arrived at independently, prescribe the same unbuilt design.**
- **Brain structure, replicate or substitute.** **CONTESTED at the top level and it must be reported as
  contested.** There are four live accounts of what the hippocampus computes -- index (a sparse address
  with a linked value), conjunctive autoassociative store (a compressed content vector), relational map
  (an EDGE), predictive map (a discounted-future occupancy). **Our flat store is the conjunctive account
  done WITHOUT the sparsity that account's own capacity equation requires.** Goode 2020 proposes they
  reconcile at different levels; that reconciliation is a proposal, not a measurement.
  **PINNED as an architecture:** indexing, on engram-tagging and optogenetic reactivation.
  **UNPINNED and therefore OURS:** the index ALLOCATION rule -- nothing in the literature says which
  cells get recruited.
- **The regime switch, which we have not got at all.** O'Reilly & McClelland 1994 is titled "avoiding a
  trade-off" and the field's resolution is a **REGIME SWITCH, NOT A PARAMETER SETTING**: encoding mode
  runs the mossy-fibre path with recurrents suppressed, retrieval mode runs the direct perforant path
  with recurrents dominant, and the switch is neuromodulatory (Hasselmo's SPEAR; high ACh = encode, low
  ACh = retrieve). **PINNED as a switch; the gain values are UNPINNED and get swept.**
  **We have one store, one path, one operating point for both write and read.** Build the switch; do not
  tune a single operating point.
- **Can-fail design.** One variable at a time, in this order:
  1. `A0_FLAT` -- the incumbent.
  2. `T1_SPARSE_KEY_DENSE_VALUE` -- key sparsified (level SWEPT), value left dense and graded, retrieval
     by LINK, never by reconstruction.
  3. `T2_PLUS_REGIME_SWITCH` -- distinct write and read paths with swept gains.
  4. `C1_SPARSE_BOTH` -- the thing we already did, as the control that isolates which object the
     sparsification belongs to.
  5. `K1_ORACLE_ADDRESS` -- hand the correct address; the LINK stage must return ~1.0 or the instrument
     is dead. *(The July design's LINK stage is already self-test-proven; this re-proves it in place.)*
  6. `N1_RANDOM_ADDRESS` -- must sit at chance.
- **Floor.** CI-separated over `max(four floors)` **recomputed on this item's own population**, on the
  **PARTIAL CUE**, which is the operating point. Report the exact-key arm beside it, never instead of it.
  Both tie conventions.
- **Stop-if.** (i) `T1` ties `A0_FLAT` on the partial cue with `K1_ORACLE_ADDRESS` passing -> the
  address, not the store's architecture, is the limit, and the work goes back to ITEM 3.
  (ii) `C1_SPARSE_BOTH` matches `T1` -> the key/value distinction is not what is doing the work and the
  two-literature convergence is refuted for our geometry; say so plainly.
  (iii) any known-answer arm fails -> `INSTRUMENT_STILL_LOOSE`, publish nothing.
- **Runner.** `cpu_runner_local` smoke; `cpu_runner_0` for the swept full grid. GPU only if ITEM 3 pushes
  the address stage to 8192.
- **Dependency.** **HARD DEPENDENCY ON ITEM 2** (if the information is not in the cue, this is void).
  Reads ITEM 3's chosen expansion. **Does not depend on ITEM 1**, but a working cleanup would change
  which retrieval variants are worth arming.

---

### ITEM 5 -- SURPRISE-WEIGHTED UPDATE. *NEW. Independent of the cue chain -- this is the WRITE side. Cheapest item with real theory support.*

- **The question.** Our learning rule is `self._sums[lemma] += ctx_vec`. **Every occurrence is weighted
  1.** Two independent literatures say weight it by surprise. **Does a surprise-weighted accumulator beat
  the uniform one?**
- **The convergence, and it is the drill's strongest build recommendation after ITEM 1.**
  - **Predictive coding:** the feedforward signal is not the sensory signal, it is the RESIDUAL
    `x - x_hat` weighted by precision. **The N400 IS lexico-semantic prediction error, with an
    implemented computational model** (Nour Eddine, Brothers, Wang & Kuperberg 2024, *Cognition*),
    tracking the N400's dynamics and its sensitivity to lexical variables, priming, context and their
    higher-order interactions. So: `delta ~ precision * (observed_context - predicted_context)`, and
    **an unsurprising occurrence should teach approximately nothing.**
  - **Word learning:** Medina et al. 2011's exposure census -- **~90% of natural exposures are
    UNINFORMATIVE, ~7% highly informative.** An informative-encounter SELECTOR is a REQUIRED upstream
    component, not a workaround.
  - One says weight by surprise; the other says most exposures carry nothing. **Same instruction from
    two directions. We implement neither.**
- **Brain structure, replicate or substitute.** Hierarchical cortical predictive coding.
  **PINNED-ENOUGH-TO-BUILD-ON:** that the brain's signal for learning a word from context is a
  prediction error, that it is measurable, and that it has a working computational model.
  **CONTESTED, loudly, and never to be quoted as pinned:** the free energy principle is widely charged
  with being a mathematical tautology, true by definition rather than by empirical test. **The useful
  formulation of the defence is itself the concession to adopt: the FEP is not falsifiable, but a
  PROCESS THEORY of how a particular system minimises free energy is. Quote a process theory or quote
  nothing.** Also contested: whether explicit error UNITS exist, and whether prediction error drives
  LEARNING or only ATTENTION/GAIN.
- **Compatibility, which is a useful narrowing.** **COMPATIBLE with VSA, RIVAL to Hebbian accumulation.**
  Nothing in vector-symbolic algebra forbids a residual update; `acc += (ctx - predicted)` is still a
  bundle, still glass-box, still one matmul. **Adopting predictive coding costs us nothing
  architecturally and does not touch the no-LLM invariant.**
- **Can-fail design.** One variable: the update weight. `A0_UNIFORM` (weight 1, the incumbent);
  `T1_RESIDUAL` (`delta ~ precision * residual`); `T2_TOP_K_INFORMATIVE` (an explicit
  informative-encounter selector keeping the most surprising ~7-10%, the rate **SWEPT** rather than
  adopted from Medina); `C1_RANDOM_SUBSET` matched in TOKEN COUNT to `T2` -- **this arm decides the
  item**, because reading fewer occurrences is a different corpus, not a better rule; `K1_ORACLE_WEIGHT`
  (weights fitted on the gold, must be far above); `N1_SHUFFLED_WEIGHTS` (must sit at `A0`).
- **Floor.** CI-separated over `max(four floors)` **recomputed on this item's own population and its own
  scorer**. Whichever instrument is used -- the rho instrument or hit@1 -- name it, and do not compare
  across the two.
- **Stop-if, and this must be PRE-REGISTERED as a possible null cause rather than discovered afterwards.**
  Our "prediction" has to come from the store we are criticising, so early in training the residual is
  just the observation and the change is a no-op. **If `T1` is bit-identical or near-identical to `A0`,
  the finding is the BOOTSTRAPPING PROBLEM, not a refutation of surprise weighting** -- report it as
  such, and the stronger brain-faithful version (a separate predictor, or a warm-start) is the next
  build. Second stop-if: `C1_RANDOM_SUBSET` matches `T2` -> the gain is corpus size, not selection.
- **Runner.** `cpu_runner_local` for smoke; `cpu_runner_0` for the swept full grid. It is an
  accumulator change over the reading loop.
- **Dependency.** **NONE. This is the one item in the plan that is independent of the entire cue chain,
  and it is where the programme goes if ITEM 2 says the information is not in the cue.**
- **Calibrated expectation, stated so a null is not a surprise.** The drill puts
  P(a surprise-weighted accumulator beats the uniform one, CI-separated) at **~0.35** after the standing
  lit-scan penalty.

---

### ITEM 6 -- A VERIFIER THAT IS NOT THE GENERATOR. *BLOCKED ON THE OWNER'S WORD (see 6.4).*

- **The question.** Does a **propose -> test -> reject -> re-propose** loop beat a single `argmax` on the
  identical store, cue, scorer, n, pool and gold?
- **What the drill added to the design, and it is the load-bearing part.** Two literatures -- one about
  RETRIEVING a known word, one about LEARNING a new one -- specify the same control structure:
  ```
  GENERATE   candidates by parallel activation from the semantic/lemma level (NOT a serial scan)
  RANK       by activation
  TEST       each against a criterion that is NOT the generator
  REJECT     and re-propose
  STOP       on a VALUE criterion, not on exhaustion
  ```
  Lexical access: two-stage concept -> lemma -> word form, dissociated by anomia; **the field has settled
  on PARALLEL ACTIVATION WITH COMPETITIVE SELECTION and serial lexicon scanning is refuted**; selection
  is a competitive normalisation, a Luce ratio over activations, **not an argmax over a fixed list.**
  Word learning: **PROPOSE-BUT-VERIFY** (Medina 2011; Trueswell 2013) -- commit to ONE hypothesis, then
  confirm or abandon it at the next informative encounter, with no partial credit to alternatives.
  **THE CRITICAL PROPERTY: THE VERIFIER MUST NOT BE THE GENERATOR.** If the test is the same function as
  the proposal, the loop cannot fail informatively -- the top-ranked candidate always passes.
  **`canonicalize_fast` is `argmax` over cosine: a generator with no verifier and no reject step.**
- **And we own the stopping rule's organ, unwired.** The owner's Q12 "not worth it" is a VALUE-BASED
  stopping rule, formally the marginal-value theorem (Charnov 1976). **`hdlab/information_foraging.py` --
  807 lines, `ForagingController` + `RhoTracker` + `DepletionEstimator` + `oracle_mvt_optimum`, Charnov
  and Hayden cited in-module -- exists, is NOT pipeline reachable, and nobody has connected it to
  retrieval.** Wire it; do not build a parallel stopper.
- **Brain structure, replicate or substitute.** Lemma-level competitive selection (left IFG BA45/47 is
  PINNED as the structure that selects among competing lexical candidates), with tip-of-the-tongue as the
  regime where the fast parallel process fails. **PINNED:** the two-stage architecture; TOT as a
  transmission deficit with above-chance partial phonological access -- the owner's "I often have a sense
  of what the first letter is" independently reproduces Brown & McNeill 1966. **CONTESTED:**
  discrete-serial versus cascaded activation to phonology; and whether TOT interlopers CAUSE the block or
  merely accompany it (the field currently leans symptom). **OURS, INVENTION UNDER TEST:** the specific
  rejection test and the termination rule.
- **Can-fail design.** Arms on the identical pool:
  - `A0_SINGLE_ARGMAX` -- the incumbent.
  - **`A0_BUDGET_MATCHED`** -- the incumbent allowed to score the SAME NUMBER of candidates the loop
    scores. **This arm decides the item.** A loop that examines more candidates is a bigger search, not
    a better algorithm, and without this control a win is uninterpretable.
  - `T1_PROPOSE_REJECT` -- treatment; **the rejection test uses no gold and must be a DIFFERENT FUNCTION
    from the generator.** If the verifier is cosine, the item has not been run.
  - `T2_PLUS_MVT_STOP` -- the same loop terminated by `information_foraging`, i.e. on value rather than
    on exhaustion.
  - `K1_ORACLE_REJECTOR` -- known-answer; a rejector allowed the gold must approach 1.0.
  - `N1_RANDOM_REJECTOR` -- null; must sit at or below `A0`.
- **Floor.** CI-separated over `max(four floors)` **computed on this item's own population**. On the open
  read-out pool test half that max is the CONSTANT floor -- but **compute it, do not import 0.1382.**
  Report the balanced-pool ladder beside the open pool, never instead of it, and never cross the two.
  Both tie conventions, both ways.
- **Stop-if.** (i) `T1` ties `A0_BUDGET_MATCHED` -> the loop is a bigger search, not a better algorithm;
  say so plainly and stop proposing variants. (ii) `K1_ORACLE_REJECTOR` fails to reach 0.70 ->
  `INSTRUMENT_STILL_LOOSE`, publish no quality number. (iii) `N1` tracks `T1` -> the effect is the extra
  scoring, not the rejection.
- **A hard precondition this plan adds, from 2.1.** A propose-reject loop needs a proposer that is right
  sometimes. **Ours addresses correctly 3.25% of the time under a partial cue.** Either run this item at
  the EXACT KEY and label it a construction proof that does not transfer, or run it after ITEM 4. Do not
  run it on the partial cue and report a null as a fact about the algorithm.
- **Runner.** `cpu_runner_local` for smoke and self-test; **`cpu_runner_0`** for the full grid. A cosine
  loop over 5,491 x 256 with a few iterations does not need a GPU.
- **Dependency.** **BLOCKED ON THE OWNER'S WORD** about the path (6.4). The composed cell is waiting.

---

### ITEM 7 -- THE REGISTER CHANNEL AS THE VERIFIER'S FEATURE. *Sibling authoring. Feeds ITEM 6.*

- **The question.** The owner described the rejection criterion as *"trying to match it to the feeling of
  the word... 'think' versus 'contemplate' have very different feelings -- one is informal one is more
  thoughtful and purposeful."* **That is REGISTER / FORMALITY / effortfulness, and it is not what
  valence-arousal-dominance measures. We tested the wrong three numbers against the owner's own
  illustration.** Does a register channel work as a rejection criterion where affect did not?
- **What is already measured, and it changes the question before any treatment number exists.** On a
  pre-registered list of 30 informal/formal synonym pairs the register columns order the pair correctly
  27-30 times out of 30 -- **AND SO DOES WORD LENGTH ALONE, 29 out of 30.** So the pair test licenses
  that these columns carry register ordering and **cannot on its own separate register from spelling
  length**. The other half: **log corpus frequency orders the same 30 pairs 1 out of 30** -- the informal
  member is almost always the MORE frequent word -- so whatever register is here, **it is not the
  frequency floor renamed; frequency and register point in opposite directions on the owner's own
  example.** The cleanest column is the OneStopEnglish Advanced-minus-Elementary contrast (27/30,
  correlation with length **0.025**), and it is the only one holding topic fixed.
  *AGENT MEASUREMENT, `.claude/scan-out/register-channel.json`, design gate run before the cell existed.*
- **Brain structure, replicate or substitute -- and the honest answer is UNPINNED.**
  The fragment says so and does not fabricate an anatomy. The nearest defensible statements are weaker
  and recorded as such: **selection among competing lexical candidates is left IFG BA45/47 (PINNED as a
  structure, and it is what a REJECTOR is)**; register-appropriateness to a social situation is usually
  discussed with medial-prefrontal / temporo-parietal social-cognition circuitry, recorded as
  PLAUSIBLE-BUT-NOT-PINNED and not built on. **The channel itself is OUR-INVENTION-BEING-TESTED.**
- **Can-fail design.** Register profile through the identical estimator as the affect rejector, plus four
  controls that are the point of the cell: **WIDTH-MATCHED NOISE** at the same column count, max-draw over
  5 seeds (never the mean); **LENGTH-ONLY**; **FREQUENCY-ONLY**; **LENGTH+FREQUENCY** ("register is the
  floors renamed"); and the decisive arm, **REGISTER RESIDUALISED on length, syllables and log frequency**
  -- what is left of register once both floors are linearly removed from every column.
  Also: **`SENSORIMOTOR_12` plus THREE NOISE COLUMNS = 15 dims**, the arm the sibling cell disclosed as
  missing, which until it exists leaves the +0.0174 unattested gain confounded with width.
- **Floor.** `max(four floors)` **computed on this cell's own population under all three tie conventions**.
  **0.1003, 0.1382 and 0.2070 are NOT to be imported as comparators** -- the profile rejector is
  re-measured here as an arm because the stratum differs.
  **`P_MATCHED_K15` MUST NOT BE USED AT ALL** (2.2(c)).
- **Stop-if.** (i) Indistinguishable from width-matched noise with both known-answer arms passing -> what
  we built is not a channel; shelve on that brain-framed criterion, not on a score. (ii) Survives noise
  but dies against LENGTH+FREQUENCY -> register is the floors renamed; that is the most likely way this
  fails and the design is built around it.
- **Runner.** `cpu_runner_local` smoke; `cpu_runner_0` full.
- **Dependency.** None. **Feeds ITEM 6:** a verifier needs a criterion that is not the generator, and this
  is the leading candidate for it.
- **Status.** `experiments/exp_register_channel_rejector_v1.py` is **NOT on disk as of this pass.
  NO TREATMENT NUMBER EXISTS.** *(VERIFIED ON DISK BY THIS PASS.)*

---

### ITEM 8 -- THE DUAL-HUB DISCRIMINATOR: A SECOND STORE, OR A SECOND CONTROL SETTING? *Downgraded from settled to CONTESTED.*

- **What changed, and this is a correction to what we adopted last night.** We adopted the dual-hub
  account as though it were settled. **It is CONTESTED, and the two readings imply different builds.**
  Schwartz et al. 2011 (*PNAS*, VLSM double dissociation) and Mirman, Landrigan & Britt 2017 support two
  anatomically separate hubs. **Lambon Ralph's group read the temporo-parietal effects as SEMANTIC
  CONTROL demands rather than a second STORE** -- the controlled-semantic-cognition framework treats ATL
  as the single representational hub and IFG/pMTG as a control network that reshapes access to it. Under
  that reading, thematic relations are not stored elsewhere; they are RETRIEVED under different control
  settings from the same store. `notes/LONG_TERM_PLAN.md` section 4 currently carries the dual-hub
  reading as **[PINNED]**. **On this drill's evidence that label is too strong and the Director should
  downgrade it to CONTESTED.** *(This plan does not edit that file.)*
- **The question, which is the discriminating test.** If the dual-hub account is right we need a second
  STORE. If the control account is right we need a second CONTROL SETTING over one store -- **which is
  `ORGAN_MAP` C3's multiplicative gain, already built once and HARD_FAIL.**
- **The formal statement that makes the test constructible.** Taxonomic similarity is
  **SUBSTITUTABILITY** (dog/wolf fill the same slot); thematic similarity is **COMPLEMENTARITY**
  (dog/leash co-occur in an event and cannot substitute). **Those are different metrics over the same
  vocabulary, and no single vector space can express both as "high cosine" without collapsing them.**
  That bears directly on why pouring a thematic channel into a sensorimotor rating space may not land --
  which the target-space drill found independently, from the norms' own authors.
- **Brain structure, replicate or substitute.** ATL hub versus temporo-parietal system.
  **PINNED:** the lesion double dissociation exists. **CONTESTED:** what it means.
  **PINNED and separate:** the ATL computes nonlinear cross-modal mappings expressing DEEP conceptual
  similarity, and backward connections are consistently STRONGER than forward -- the anatomy of a
  generative model, not a feedforward encoder. **Our hub is a feedforward sum with no back-projection to
  the spokes at all.** That is a named, un-built organ: **the hub-to-spoke return path.**
- **Can-fail design.** One population, two treatments, one variable:
  `T1_SECOND_STORE` (a separate thematic store with its own address) versus
  `T2_ONE_STORE_TWO_CONTROL_SETTINGS` (the multiplicative gain re-armed as a control setting rather than
  as a fix), against `A0_ONE_STORE_ONE_SETTING`. The discriminator is that **the two accounts predict
  different failure profiles**: a second store should help on items where the two relations conflict; a
  control setting should help uniformly and should be recoverable by re-reading the SAME store.
  Plus a taxonomic/thematic **conflict stratum** built from pairs where substitutability and
  complementarity disagree, which is where the accounts separate at all.
- **Floor.** `max(four floors)` **recomputed on the conflict stratum itself** -- floors are not portable
  between strata. Known-answer and null arms required. **Report the conflict stratum's n and its power;
  a stratum built from disagreement is small by construction and an underpowered primary is how a real
  effect gets banked as a null.**
- **Stop-if.** Both treatments NOT_SEPARATED from `A0` with known-answer arms passing -> our geometry
  cannot see the field's own distinction, and the honest report is that **we cannot adjudicate it**, not
  that either account is refuted. Record which stronger, more brain-faithful version would be needed.
- **Runner.** `cpu_runner_local` smoke; `cpu_runner_0` full.
- **Dependency.** None. Independent of the cue chain.

---

### ITEM 9 -- THE SUCCESSOR REPRESENTATION ON OUR OWN THEMATIC GRAPH. *Cheap, glass-box, never run.*

- **The question.** `M(s,s') = E[sum_k gamma^k * 1{s_k = s'}]`, i.e. `M = (I - gamma*P)^-1` -- place
  fields are rows of `M`, grid cells its eigenvectors (Stachenfeld, Botvinick & Gershman 2017).
  **Do rows of `M` computed on our own thematic graph beat the first-order co-occurrence arm?**
- **Why the drill flagged it, and this is the Director's strategic read, a hypothesis pending VET.**
  Our strongest recent positive was thematic-graph consolidation: replay-partner synonym purity 4.4x,
  channel 0.2417 -> 0.2795, open-vocabulary read-out 0.0462 -> 0.1069, clearing four matched controls --
  **and confirming a PRE-WRITTEN prediction that the pull would be SECOND-ORDER. A second-order relational
  pull, learned from co-participation, that beats first-order, is the empirical signature of a
  successor-like representation.** `ORGAN_MAP` D7 lists the successor representation as MISSING and gives
  its equation. `ORGAN_MAP` D4 records that the replay SELECTION function's leading normative candidate
  (Mattar & Daw 2018, `priority = GAIN x NEED`) computes NEED from **exactly that missing `M`**.
  **So we may have measured the signature of an organ we have not built, twice, in two components,
  without connecting them.**
  *(The 0.0462 -> 0.1069 figures are quoted from `notes/STATUS.md` / `LONG_TERM_PLAN.md` via the drill and
  were NOT re-derived by the drill or by this pass.)*
- **Brain structure, replicate or substitute.** Hippocampal predictive map.
  **PINNED as a representational SIGNATURE:** place-field skewing in directed environments; hippocampal
  pattern similarity mirroring a graph's COMMUNITY STRUCTURE; successor-like representation found in
  human hippocampus **and V1**. **CONTESTED, and the contest is about the LEARNING RULE:** TD learning is
  not known to be implemented in hippocampal networks, and George et al. 2023 show STDP plus theta phase
  precession approximates `M` without TD. **A real objection to record:** `M` is POLICY-DEPENDENT -- a map
  of what you DO, not of what IS -- which is a genuine problem for it as a general memory theory.
  **`gamma` is a PARAMETER: sweep it, do not adopt a value.**
- **Can-fail design.** `A0_FIRST_ORDER` (the incumbent co-occurrence pull) versus `T1_SR_ROWS`
  (rows of `M` at swept `gamma`) on the identical graph, stratum and scorer, plus
  `C1_DEGREE_MATCHED_EDGE_SHUFFLE` as the null (an `M` computed on a shuffled graph of the same degree
  sequence) and `K1_ORACLE` as the known-answer.
- **Floor.** `max(four floors)` **recomputed on the same stratum the thematic result was scored on**, so
  the comparison is against the measured null of 2.4 and not against zero.
- **Stop-if.** `T1` flat across the whole `gamma` sweep -> **our multi-hop tail is noise by d3 and `M`'s
  value lives in the multi-hop tail**; record that the graph, not the equation, is the limit, and stop.
- **Runner.** `cpu_runner_local`. It is a matrix inverse of a graph we own.
- **Dependency.** None. **It is cheap, glass-box, uses no external asset, and has never been run.**
- **Calibrated expectation.** The drill puts P(a direct SR arm beats the first-order arm, CI-separated)
  at **~0.35** after the penalty, low because our graph is sparse and the same 1-hop-only ceiling that
  killed `grounding_snowball` applies.

---

### ITEM 10 -- READ THE SELECTIONAL-CONSTRAINT BRIDGING RESULT. *PID 18496 in flight. This item is a READ.*

- **The question.** Does bridging by the **verb's selectional constraint** -- which is what the owner
  actually did -- beat bridging by **copying graph neighbours**, which is what we built? Given *"the tove
  ran across the road"*, the owner used "ran implies legs implies animal", then EPISODIC recall ("rabbits
  and deer which I've SEEN cross roads"), then produced a DISTRIBUTION over categories. **They never
  copied a neighbour word.**
- **Do not re-dispatch.** `data/exp_selectional_constraint_bridge_v1/` is **EMPTY as of this pass**
  *(VERIFIED ON DISK)*. **No arm has been scored. Nothing about it is a result yet.** When it lands, read
  the arms off disk.
- **The comparison that matters, and it is not against zero.** Thematic-hub bridging is already a measured
  null (2.4). Selectional bridging must be scored **against that, on the same stratum**, or the
  comparison is meaningless.
- **Floor.** CI-separated over `max(orthographic, hardened-frequency, scramble, constant)` **recomputed on
  the bridged-endpoint stratum itself**. Required arms: `K1_OWN_NORMS` and `K2_ORACLE_BRIDGE` as
  known-answer; a **degree-and-frequency-matched EDGE SHUFFLE** as the null; **morphology-blocked edge
  deletion** as the decisive spelling-leakage control. The both-endpoints stratum is **underpowered by
  construction (n=66)** and must be reported as such, never quietly dropped.
- **Stop-if.** Also NOT_SEPARATED with both known-answer arms passing -> **that is the SECOND real null on
  bridging**, and `LONG_TERM_PLAN.md`'s Phase 2 kill condition fires: grounding does not propagate through
  our relations and the substrate needs a genuinely different acquisition mechanism. **This is the most
  important negative result available to this project. Report it loudly if it happens** -- and before
  calling the route exhausted, write down what was tested and what the stronger, more brain-faithful
  version would be.
- **Runner.** Extraction already local. Any FULL re-score -> `cpu_runner_0`.
- **Dependency.** PID 18496. Nothing else may write its output directory.

---

### ITEM 11 -- THE TARGET-SPACE DECIDER FULL. *Smoke landed; the FULL was never run. Deflated by ITEM 2.2(e).*

- **The question.** Hold the bridging mechanism FIXED and vary ONLY the target space. If bridged semantic
  retention rises when the space includes AFFECT, the target space was the limit and the mechanism is
  sound. If retention stays flat while each space's own known-answer arm passes, the mechanism is the
  limit and the target space is exonerated.
- **Why it is deflated but not dead.** The feeling-match rejector already answered the affect question on
  a different bench and the answer was NO -- **three columns of affect are indistinguishable from three
  columns of rater noise** (2.2(e)). **But that cell's own disclosed caveat is that the task may not be
  the organ's task**: slot-filling prediction from a corpus is a THEMATIC-FIT task, and the owner's
  introspection was about lexical retrieval. So this item asks a genuinely different question and should
  be run -- **with the expectation lowered and stated in advance.**
- **The decisive control is already in the design.** `TS4_WIDER_UNINFORMATIVE_23` widens by the same
  number of dimensions from the same source file with **no new channel**. **If TS4 raises bridged
  retention as much as TS2, the affect story is refuted and the direction dies.** That sentence is the
  cell's own, written before the run.
- **Brain structure.** Binder's seven experiential attribute blocks; our 12-dim space covers two of them.
  **PINNED:** that the blocks are dissociable. **OURS:** that three per-word VAD scalars are a faithful
  operationalisation of the affect block -- and the sibling cell already named that as the divergence
  ("three scalars is not the block, and we truncated to what happened to be on disk").
- **Floor.** The sibling cell's floor set, **recomputed per target space on the identical stratum**, now
  including the constant/prototype fourth role -- **the smoke went `MEETS_BAR` -> `NO_EVIDENCE
  (NO_CONSTANT_FLOOR)` under the fixed gate, so the FULL must run one or it cannot be judged.**
  `K1_OWN_NORMS` and `K2_ORACLE_BRIDGE` known-answer; `N1_NULL_ARM_MATCHED_REWIRE` null.
  Design gate already confirmed: `n=372 PASS, POS = {A 43, N 250, V 79}`.
  **`K1_OWN_NORMS` was flagged as possibly a REFERENCE arm the cell labels as a treatment arm. Resolve
  that label before quoting any margin.**
- **Stop-if.** TS4 matches TS2 -> refuted, direction dies, record it. Any known-answer arm fails ->
  `INSTRUMENT_STILL_LOOSE`, publish nothing.
- **Runner.** Smoke already local; FULL -> `cpu_runner_0` (12-15 dims is cheap but multi-seed).
- **Dependency.** PID 22588 owns `data/exp_target_space_*`.
- **Carry the scope warning with every quote.** The +0.1013 ceiling diagnostic that motivated this cell
  has **no floors, no null arm, and clears nothing.** It decided what enters the cell; it is not evidence
  about the cell's outcome. *AGENT MEASUREMENT, `.claude/scan-out/target-space-drill.json`, `03055c7fa`.*

---

### ITEM 12 -- PARAMETER-DIVERGENCE VERSUS COMPUTATION-DIVERGENCE. *A re-analysis of evidence we already own. NO NEW RUN.*

- **The question.** Section 0 asserts that **fidelity OF THE COMPUTATION predicts outcome and fidelity OF
  THE PARAMETERS does not.** That is testable on data already on disk: score each of `ORGAN_MAP`'s 38
  organ divergences as PARAMETER-divergence or COMPUTATION-divergence and check which class predicts the
  floored outcome.
- **Why the existing fidelity-predictor test is not evidence.** Our fidelity score is UNVALIDATED at
  6 points with exactly ONE positive-class member. **Six points with one positive cannot produce a p-value
  below 1/6 = 0.167 under a random-ranking null, no matter how good the score is.** Any monotone score
  that ranks the single positive first achieves exactly that. **`p ~ 0.17` is the CEILING OF THE DESIGN,
  not a measurement of the score.** "UNVALIDATED" is a statement about our experimental design.
- **What the literature actually says, because it is scoped rather than absent.** Yamins & DiCarlo and the
  Brain-Score programme found task performance and NEURAL PREDICTIVITY positively correlated over a wide
  range, replicated for language models predicting human neural and behavioural data (Schrimpf 2021).
  **Against:** Linsley/Feng/Serre 2023 find DNN neural predictivity progressively WORSENING as models
  improve on ImageNet; Nonaka 2021 find brain-likeness NEGATIVELY correlated with recognition performance
  across 29 DNNs. **The asymmetry that makes the owner right in our case: both of those measure fidelity
  ABOVE A HIGH PERFORMANCE BASELINE, where every model already works. The break happens at the TOP. We are
  at the BOTTOM** -- our 0%-fidelity component is the sha256 hash encoder, which is the structure-axis null
  by construction, and 0% fidelity with 0 capability is the relationship's left endpoint, not a
  coincidence.
- **Can-fail design.** The `ORGAN_MAP` 38-organ classification was produced by a different pass, on
  different evidence, before the scoring scheme existed -- **so it is an independent label set with real
  `n`.** Score concordance of the floored outcome against (a) the existing fidelity score and (b) the
  PARAMETER/COMPUTATION split. **The split predicting better than the raw score is the finding; the raw
  score predicting better refutes section 0.**
- **Floor.** A permutation null over the label assignment, and a **power statement stated first**: report
  how many of the 38 carry a floored result at all. **The drill's expectation is that most do not, which
  is itself the finding and means the fidelity-predictor question is blocked on the same evidence gap as
  everything else.**
- **Stop-if.** Fewer than ~15 of the 38 carry a floored result -> **the test is underpowered by
  construction; report that and do not publish a concordance number.** Publishing an underpowered
  concordance is exactly how a real effect gets banked as a null.
- **Runner.** None -- desk re-analysis over banked artifacts.
- **Dependency.** None. **It is the cheap test of the rule at the top of this plan, and it protects
  against that rule hardening into unexamined doctrine.**
- **Calibrated expectation.** The drill puts P(a properly-powered 38-organ concordance finds a positive
  fidelity-outcome relationship) at **~0.55**, P(monotone all the way up) at **~0.20**.

---

### ITEM 13 -- PUBLISH THE CORRECTED BAR BASE RATE. *Desk. Cheap. Do it early.*

- **What is on disk.** *VERIFIED ON DISK BY THIS PASS,
  `data/verdict_bar_reports/verdict-bar-20260817T002627Z.json`:* 7,789 metrics.json enumerated by
  `os.walk` over an absolute data dir; `MEETS_BAR` **1**, `FAILS_BAR` 7,770, `NO_EVIDENCE` 18;
  classes `SATURATED_CEILING` 265, `STRING_PASSES_BAR_FAILS` 3, `NO_FLOOR` 2,967, `NO_CI` 6,
  **`NO_CONSTANT_FLOOR` 39**, `AGREES` 4,293, `NO_VERDICT` 216; `n_flagged` 3,496.
- **Three stale strings now in circulation, all of which must stop being quoted.**
  1. **"0 of 7,769"** -- superseded. It is still in `notes/STATUS.md`.
  2. **"2 of 7,772"** -- that morning's intermediate; superseded the same day.
  3. **"the checker has a known false-pass defect, do not trust a MEETS_BAR"** -- the fix landed
     (`85b9aac78`, VERIFIED an ancestor of HEAD), and two further fixes landed after it.
- **The qualification that must travel with the corrected number.** **The one pass does not touch the
  open-vocabulary read-out and is rejected on four grounds (2.2(d)). "We underperform a spell-checker"
  is untouched by any of this.**
- **A small coupling defect found by this pass and not repaired.** The report's own `the_bar` field still
  reads *"a CI-SEPARATED margin over max(orthographic, frequency, scramble)"* with no constant term,
  although its class counts prove `constant_prototype` is wired. **A description string that lags the code
  it describes** -- the same fault class as the `STATUS.md` / `session_start_hook.py` literal drift.
  `tools/**` is on this pass's do-not-touch list; **filed for the tool owner, not attempted.**
- **Action.** `notes/STATUS.md` is Director-owned and was NOT edited by this pass. Until the Director
  updates it, anyone quoting "0 of 7,769" must quote the correction beside it.
- **Floor / stop-if.** Not applicable -- bookkeeping, not a measurement.
- **Runner.** None; desk.

---

### ITEM 14 -- THE REMAINING FLOOR-LEXICON RESIDUE. *`tools/**` -- BLOCKED FOR THIS PASS. Filed as a directive.*

Three open items, each reported with its enumeration by the agent that found it, none repaired:

1. **44 distinct `ortho` keys across 44 cells remain UNCLASSIFIABLE by design** (fail-closed), because
   the token collides between orthogra**phy** and orthogo**nality**. One of them -- bare `ORTHO` in
   `exp_orthographic_floor_comparator_v1` -- **is believed to be a real orthographic floor** and resolves
   only on a name rule the agent declined to add. Conservative and reported rather than rescued by
   loosening. *AGENT MEASUREMENT, `.claude/scan-out/pool-floor-integrity.json`.*
2. **`tools/floor_battery.py` is UNTRACKED in git** (`?? tools/floor_battery.py`). **Three cells and two
   fragments have now flagged this.** The cross-check test that asserts `c3_gate.REQUIRED_FLOOR_ROLES`
   and `floor_battery.FLOOR_SET_REQUIRED` agree **SKIPS on a clean checkout**, so on a fresh clone the
   guard against exactly the drift that caused 2.2(b) is INERT. `tools/exp_checkpoint.py` is unregistered
   too.
3. **`exp_task_degeneracy_v1` still publishes its matched block as "a task on which neither a constant nor
   a speller can win", which is FALSE as that block was built** (2.2(c)). The cell was not modified.

**Floor / stop-if.** Not applicable; the gate is a regression test that fails before the change and passes
after. **Runner.** `cpu_runner_local`. **Filed for the tool owner. Not attempted.**

---

## 5. COMPONENTS WITH NO THEORETICAL JUSTIFICATION AT ALL

**This is a first-class section because it is the more damning finding.** Section 4's items are places
where theory and implementation DIVERGE. **These are places where no computational theory in the drill
proposes what we did, so there is nothing to diverge FROM.** Each is to be **justified, replaced, or
explicitly marked as OUR INVENTION UNDER TEST.** Marking is a legitimate outcome; silence is not.

| # | component | where | what theory says about it | disposition |
|---|---|---|---|---|
| 1 | **the exhaustive cosine argmax read-out** | `reading_grounding_loop.canonicalize_fast:770`; `concept_encoder:564` | **NOTHING. There is no neural analogue of an exhaustive cosine argmax over 5,491 stored items and none of the drill's eight theories proposes one.** The field has SETTLED on parallel activation with competitive selection and REFUTED serial lexicon scanning; selection is a Luce ratio, not an argmax over a fixed list. | **REPLACE -- ITEM 6.** It is the decision variable of the entire substrate. |
| 2 | **`sign()` as the terminal operation, 34 sites in 12 modules** | enumerated in `ORGAN_MAP` sec 1 | no theory proposes it; VSA's binary-spatter family PERMITS it and its own capacity theory PENALISES it; it is mathematically a prototype extractor, the signature of a DEGRADING hub. Separately: **random PERMUTATION outperformed circular CONVOLUTION on paired associates stored in a single trace** (Kelly, Mewhort & West 2015) and `hdlab/random_indexing.py:219` already implements the order-sensitive permutation variant, which the live path does not use. | **JUSTIFY OR REPLACE.** The permutation arm is free and unrun. |
| 3 | **`d = 256`** | `grounding_acquisition_loop.py:79` | chosen by nothing. VSA superposition capacity is roughly `O(d / log d)` at fixed retrieval fidelity; **2,377 concepts at d=256 is outside the regime where the algebra is supposed to work at all.** `ORGAN_MAP` B4 measured 16x the dimensionality buying **+0.0843, more than any mechanism change this programme has produced**, with crosstalk falling exactly as `1/sqrt(d)`. **The theory told us that in advance and we found it by sweeping.** | **ARITHMETIC -- FIX IT.** Held: the raise rewrites every persisted anchor store and **needs explicit owner authorisation.** |
| 4 | **`GROUNDED_CAP = 0.45`** | `grounded_similarity.py` | a hard cap structurally preventing the grounded channel from ever crossing the 0.50 link threshold. No theory. Measured effect: **76.2% of SimLex pairs collapse onto two values.** | **REPLACE.** And `grounded_similarity()` must never be used as a scorer. |
| 5 | **`SENSE_MATCH_THRESH = 0.45`** | banked-fact acceptance | no derivation. **55.5% of banked facts beat "nothing matched" by less than 0.05.** | **JUSTIFY OR SWEEP.** |
| 6 | **`VOTE_MARGIN = 0.15`** | `wordnet_polarity_propagation.py` | no derivation, and the module **ABSTAINS on its own docstring's motivating example** at margin 0.0141. | **JUSTIFY OR SWEEP.** |
| 7 | **unweighted shared-feature overlap** | `lexical_similarity.py` | worse than unjustified -- it is the **precise inverse** of the distinctiveness weighting the Conceptual Structure Account predicts (Tyler & Moss). | **REPLACE.** |
| 8 | **equal weighting of every occurrence** | `ConceptSpace.observe` | two literatures say weight by surprise. **Nothing says weight by 1.** | **REPLACE -- ITEM 5.** |
| 9 | **the conjunction operator** | `perirhinal_conjunctive.py` | the owner's own example. `ORGAN_MAP` marks the algebraic form OURS/UNPINNED; the literature does not fix one; **and the rival account says it is a learned lookup, not an operator at all.** | **MARK AS INVENTION UNDER TEST. Do not shelve on the score** (section 1, point 3). |
| 10 | **`alpha = 0.5` labelled "brain-canonical"** | `iterative_attractor.py` | **an invention wearing a pinned label, and it shipped.** Caught by the fidelity honesty gate; listed here because it is the ARCHETYPE of this whole table. | **ALREADY CAUGHT. Keep it in the list as the exemplar.** |

**THE PATTERN, and it is the reason this section exists.** Every entry is a place where a NUMBER or an
OPERATOR was chosen once, by convenience, and became load-bearing without anyone asking what computes it.
**The read-out is the worst case because it is universal: every arm this programme has ever scored was
scored through an operation with no theoretical justification of any kind.** That does not invalidate the
comparisons BETWEEN arms -- they share the operation -- **but it means the LEVEL of every number we own is
set by a component nobody chose deliberately.**

**Also unbuilt, and named here so they are not lost between sections:**
- **The hub-to-spoke RETURN PATH.** The field's current best statement of the ATL hub's operation is a
  LOOP -- pattern completion via a compact abstract label feeding BACK onto shallower unimodal features
  (Jackson, Rogers & Lambon Ralph 2021) -- and backward connections are consistently STRONGER than forward.
  **Our hub is a feedforward sum with no back-projection at all.**
- **The CROSS-MODAL RECONSTRUCTION objective.** In every implemented hub model the hub is trained by
  ERROR-DRIVEN learning to reproduce ANY spoke's pattern from ANY other spoke's. **The similarity space is
  what EMERGES from that objective; it is not the objective. We built the output shape of a process we
  never ran.** *(CONTESTED whether error-driven is required, and it must be reported as contested -- but
  the fact that we implemented the CLS ARCHITECTURE with an objective no CLS model uses is a real, named,
  unexamined divergence, and it sits directly upstream of the 0.46% synonym-purity number.)*
- **The LEARNED cue-to-store TRANSLATOR.** Treves & Rolls' two-input argument requires a learned
  heteroassociative map from a dense cue space into a sparse store space. **We own zero cue-to-store
  map-fitting primitives** (enumerated across the `hdlab/` modules by the partial-cue drill). What we
  tested was LINEARITY, which the biology does not pin.
- **The EDGE as the store's primary object.** Under the relational-memory account the primary stored object
  is an EDGE, and **a store that cannot answer about a pair it never saw has missed the point of the
  organ.** Our store's primary object is a per-word accumulated vector; our relations live in a separate
  `.pkl`. **The store cannot represent the object that account says is primary.**

---

## 6. STANDING OPERATOR DECISIONS -- CARRIED FORWARD SO THEY ARE NOT LOST

None of these is a research item. All are open and none is taken.

### 6.1 The 238 flagged-and-cited cells -- OPEN, NOT TAKEN

**238 flagged cells ARE cited by an index** -- their overstatement has already propagated into the cert
ledger or the capability registry. *VERIFIED ON DISK BY THIS PASS,
`verdict-bar-20260817T002627Z.json`, `reconciliation.n_cited_and_flagged` = 238, against 633 cited-and-on-disk,
7,147 on-disk-but-cited-by-no-index, and 9 cited-but-not-on-disk.*

**Recommended default (Director's call, silence is safe): mark all 238 IN PLACE as bar-flagged-and-cited
so nobody quotes them, and do NOT retract the citing indexes wholesale.** A blanket retraction would demote
results never re-checked on disk -- the exact "no demotion without a fresh on-disk re-check" fault that
produced roughly 11 wrong demotions in 48 hours. Adjudicate by hand, in the order the citations are
load-bearing.

**A new consideration that arrived today and does not change the recommendation.** 39 cells now carry
`NO_CONSTANT_FLOOR` and 12 of 7,789 record a constant floor at all. **That is withholding, not refutation.**
Do not fold it into the 238 decision; they are different actions on different populations.

### 6.2 The 4 missing preregs said to block GPU dispatch -- UNCONFIRMED ON DISK, AGAIN

**Neither the previous pass nor this one could verify this item, and both say so rather than working
around it.** How the previous pass enumerated: both queue files empty; every `notes/*.md` and
`.claude/scan-out/*.json` grepped for `GPU dispatch` returning only June/July hand-offs; `4 prereg`,
`preregs missing`, `NO_PREREG` returning no current hit; `RECOVERY_PROGRAM.md` one unrelated hit.
**Carried as an operator-asserted item with its status stated. It is not dropped and it is not presented as
verified.** Whoever asserted it should name the four anchors; then the gate is one command per anchor,
because `tools/queue_add.py` refuses a script lacking `--self-test`/`--smoke` or a `--prereg`, so the
blocker is real in principle even where no instance could be located.

### 6.3 The 98 ARCHIVE-tier re-runs -- RECOMMENDED DEFAULT IS **NO**

Of the ~128 checkpoint-collision-affected cells, waves 0-2 cover 30 results at stake. **The remaining 98 are
ARCHIVE tier: 77 at N <= 4096, 21 at N >= 8192.** *VERIFIED ON DISK BY THIS PASS in `notes/PLAN.md` section
8 ("THE REMAINING 98 -- ARCHIVE tier. STOP HERE AND ASK"), decision D5.* Lowest value at the highest cost.

**Recommended default: do NOT re-run them. Mark them collision-affected in place so nobody quotes them, and
stop after wave 2. Record that the default was taken.**

**Precondition if any re-run does happen:** migrate the affected cell to the config-aware checkpoint API
**or** run into a fresh output directory. Re-running on the old contract into a directory holding the smoke
partial now raises rather than silently succeeding -- a failed run instead of a wrong number, but still a
wasted run.

### 6.4 THE BLOCKED PATH -- `experiments/exp_propose_reject_retrieval_v1.py`. **THE COMPOSED CELL IS WAITING ON THE OWNER'S WORD.**

**The state, verified rather than inferred.** *VERIFIED ON DISK BY THIS PASS: the file
`experiments/exp_propose_reject_retrieval_v1.py` DOES NOT EXIST.* A one-line write to that path is denied
while **other names in the same directory land normally** -- `experiments/exp_feeling_match_rejector_v1.py`
(85,382 B, 18:44) and `experiments/exp_confidence_calibration_replicate_v1.py` both landed today, and both
of their fragments record **`BLOCKED_PATH_HONOURED: experiments/exp_propose_reject_retrieval_v1.py was NOT
written to. New filename used.`**

**Two agents have now routed around it rather than retrying a variant, which is the correct behaviour under
the disclosure rule.** The cost is that **ITEM 6 -- the only item that attacks the read-out ALGORITHM rather
than its inputs, and the only owner answer that CONTRADICTED our architecture -- has no home.**

**This is the owner's call and nobody else's.** Three ways to unblock, in the order this plan recommends:
1. **Say the path is fine** and it gets written there.
2. **Name a different path** and ITEM 6 is authored there in one step.
3. **Confirm the block is deliberate**, in which case ITEM 6 ships under a new name and this entry closes.

**Do not attempt a fourth thing.** Retrying a variant of a denied write is exactly the failure mode the
disclosure rule exists to prevent, and the two agents who hit it did the right thing.

### 6.5 STATUS and MEMORY cap escalations -- BOTH PROPOSED, NEITHER ENACTED, AND THE MEASUREMENT HAS MOVED

- **`notes/STATUS.md` is 9,725 B against an 8,704 B cap -- OVER BY 1,021 B.** *VERIFIED ON DISK BY THIS
  PASS (`wc -c`).* The previous plan recorded the overage as ~720 B and the pre-authorised escalation step
  3 as a raise to **9,216 B**, measured and PROPOSED in `notes/STATUS_SPEC.md` section 7 but **not enacted**.
  **That proposal is now insufficient: 9,725 > 9,216.** Escalation steps 1 and 2 are spent, and never-trim
  stubs alone cost 4,536 B of the budget.
  **Recommended default: enact a raise, and measure it against the CURRENT file rather than re-proposing
  9,216.** The alternative is to keep paying the cost in silent drift, and the split's own logic says the
  state file's budget must track the stub list.
  **Do NOT close the gap by evicting a never-trim entry.** The never-trim class grows monotonically by
  design; that is why STATUS was split from the uncapped `notes/STATUS_LESSONS.md` in the first place.
- **`notes/STATUS.md` is also STALE in two places that matter, and both are the Director's to fix.**
  *VERIFIED ON DISK BY THIS PASS:* its header records `HEAD 03055c7fa` when HEAD is **`94d005cf3`**, and its
  POSITION section still reads **"0 of 7,769 banked cells meet the bar"** (see ITEM 13). **Its four
  machine-parsed literals are intact** (`AS OF:`, `## POSITION`, `## TOP ITEM`, `## WHAT IS RUNNING`) -- do
  not reword them; `session_start_hook.py` and `board.py` grep for them.
- **`MEMORY.md` is 18,227 B against its own ~17 KB target -- OVER BY ~819 B.** *VERIFIED ON DISK BY THIS
  PASS.* Its maintenance rule says to fold a category's whole tail rather than thin current descriptions.
  No escalation is proposed there and the rule is being met by folding, not by raising.

---

## 7. ROUTING -- WHICH RUNNER EACH ITEM GOES TO

| item | runner | why |
|---|---|---|
| 1 cleanup memory on its own axis | `cpu_runner_local` smoke, then `cpu_runner_0` | swept `a`, multi-seed, cosine work |
| 2 cue information audit | `cpu_runner_local`, escalate to `cpu_runner_0` | sparse count vectors over ~4,000 items |
| 3 expand-not-compress | **`gpu_runner_0`** at 8192; `cpu_runner_0` below | dense matmuls over the full anchor set at high `d` |
| 4 link-not-reconstruct | `cpu_runner_local` smoke, `cpu_runner_0` full | GPU only if item 3 pushes the address to 8192 |
| 5 surprise-weighted update | `cpu_runner_local` smoke, `cpu_runner_0` full | an accumulator change over the reading loop |
| 6 verifier-not-generator | `cpu_runner_local` smoke, `cpu_runner_0` full | cosine loop over 5,491 x 256; no GPU needed |
| 7 register channel | `cpu_runner_local` smoke, `cpu_runner_0` full | 5 columns, multi-seed, permutation-calibrated |
| 8 dual-hub discriminator | `cpu_runner_local` smoke, `cpu_runner_0` full | |
| 9 successor representation | `cpu_runner_local` | a matrix inverse of a graph we own |
| 10 selectional bridging | already local (PID 18496); FULL re-score -> `cpu_runner_0` | |
| 11 target-space decider FULL | `cpu_runner_0` | 12-15 dims, cheap, multi-seed |
| 12 parameter-vs-computation | none -- desk | re-analysis of banked artifacts |
| 13 corrected bar base rate | none -- desk | |
| 14 floor-lexicon residue | `cpu_runner_local` | a regression test, not an experiment. `tools/**` -- blocked |

**Runner facts that constrain routing.** `gpu_runner_0` is an RTX 4060 Ti with **8 GB VRAM and a 0.9
fraction cap** -- a cell needing more than ~7 GB does not belong there; shrink the batch or take the wall
time on `cpu_runner_0`. `cpu_runner_0` is the remote box at 10 of 12 logical cores, below-normal priority,
240-minute idle exit; **"it's only CPU but it takes hours" goes there, not on the local box.**

**The dispatch path, not to be shortcut.** The cell author smokes locally and **returns** the exact
`queue_add` command; the orchestrator ships remote and owns post-ship verify; verify with
`python tools/verify_landing.py <anchor>` and accept exit 0 only -- **a `status=completed` in a queue file
is not evidence a full run finished.** If verify says the metrics file is missing while the remote shows a
terminal state, that is the sync-cadence gap: run
`python tools/orchestrator/scp_recover_landing.py --verify-after <anchor>` and only call a landing missing
after **that** also fails.

**Detached local runs:** `Start-Process` with separate stdout and stderr files and a PID written by the
script itself. `run_in_background` on an Agent call backgrounds a process only for the launching agent's
lifetime and is not OS-level detachment.

---

## 8. WHAT WE ARE NOT DOING IN THE NEXT 24 HOURS

- **Not tuning selection.** It is the symptom, not the defect. **But note the sharper statement this drill
  supplies:** `LONG_TERM_PLAN.md` files "selection" as the failing component without naming what is missing
  from it. **What is missing from it is a verifier that is not the generator** -- that is ITEM 6, and it is
  a build, not a tune.
- **Not stirring the store.** Free clumping reached the owner's target and bought less than nothing.
- **Not sparsifying the meaning VALUE again.** Settled, with a theoretical reason (2.4). Revive only if the
  value is being used as an ADDRESS -- which is ITEM 4, and there it is the KEY being sparsified.
- **Not making the cue lower-rank.** The theory says the cue should be DENSER than the store. Already
  shelved; the drill supplies the quantitative argument.
- **Not re-running thematic-hub bridging.** A measured null with both known-answer arms passing, and the
  external curated graph fails too.
- **Not sparsifying the reading anchor.** DO-NOT-REDO 39.
- **Not re-proposing divisive normalisation.** Measured null, and the reason is mathematical: cosine is
  invariant to a scalar denominator.
- **Not using `matched_candidate_sets`-built pools for any claim** until a pool is rebuilt with the fixed
  construction and passes `pool_admits_a_winning_constant`.
- **Not quoting the headline 4.80%** as a diagnosis. It is a joint number over every component.
- **Not wiring a spelling channel in to clear a floor.** A floor is cleared by understanding, never adopted.
  That is how the retired ">=10%" gate was gamed. **And note the register channel's own risk (ITEM 7): word
  length alone orders the owner's 30 pairs 29/30, so an unresidualised register channel IS a spelling
  channel.**
- **Not adopting a brain PARAMETER as a value.** Section 0. Every one is swept.
- **Not calling VSA settled.** Section 1. It is invention under test until something pins it.
- **Not raising d from 256 to 1024**, not merging to `origin/main`, not pushing. All three need explicit
  owner authorisation and one rewrites every persisted anchor store while concurrent work is live.

---

## 9. HOW WE WILL KNOW THE NEXT 24 HOURS WORKED

In order. Each is a CI-separated margin over the strongest floor **computed on its own population**, never
a bare number.

1. **We know whether our cleanup memory can recover an un-bound item** (ITEM 1). Either outcome is progress:
   it either restores the load-bearing half of our own framework, or it converts five downstream nulls into
   one component-level diagnosis and tells us the algebra is doing the work alone.
2. **We know whether the answer is in the cue at all** (ITEM 2). Either outcome is progress: it either
   licenses the address work (ITEMS 3, 4) or it relocates the blocker upstream to what we WRITE -- where
   ITEM 5 already is.
3. **We know whether a surprise-weighted update beats weighting every occurrence by 1** (ITEM 5). This is
   the cheapest item with two independent literatures behind it, and it is the only one that is independent
   of the entire cue chain.
4. **The blocked path is resolved and ITEM 6 has a home** (6.4). This costs the owner one sentence and
   currently blocks the only lead that attacks the read-out algorithm.
5. **Two in-flight cells are READ rather than left unread** (ITEMS 10, 11). An unread run is a run that did
   not happen -- and the 47-foundation grid spent hours unread before this pass read it.
6. **The corrected bar base rate stops being quoted wrongly** (ITEM 13).

**The honest position on timing, unchanged.** We are before step 1 of the long-term plan. The first moment
this system does something a trivial baseline cannot is when the read-out clears the **spelling** floor at
hit@1 -- and it currently sits below a **constant** floor that itself clears spelling. Everything in this
window builds the conditions for that, and none of it is that.

**And the frame that governs how every negative here is read.** The brain grounds new word meanings from a
small sensory core plus experience, at a fraction of our text budget. **The capability is demonstrated.**
Every null below is a fact about our implementation, never about the capability. Before any direction is
called exhausted, write down what was actually tested and what the stronger, more brain-faithful version
would be -- **then test THAT.**

**With one addition this drill earned, and it cuts the other way.** *"Do it the way the brain does"* is not
a single instruction. **It is two: copy the COMPUTATION exactly, and treat the PARAMETER as a hypothesis.
Our worst result copied a number. Our best copied an operation.** A miss that came from copying a number is
not evidence against brain fidelity -- it is evidence that we applied fidelity to the wrong object.

---

## 10. DISCLOSURE

**No tool call in this pass was denied at any point.** Nothing was retried as a variant and no step was
silently skipped.

No deletion token was issued, alone or bundled with work. No `git add -A`. No origin push. No commit. No
subagent spawned. No LLM in any path. No experiment authored, smoked or dispatched.

**Protected paths: READ ONLY, none written.** `data/foundation/**` never opened. `notes/LONG_TERM_PLAN.md`,
`notes/BOARD.md`, `notes/STATUS.md`, `notes/ORGAN_MAP.md`, `CLAUDE.md`, `preregs/**`, `experiments/**`,
`hdlab/**`, `tools/**` and `data/capability_registry.jsonl` were read (or not opened) and **not modified**.
`notes/PLAN.md` and `notes/STATUS_SPEC.md` were read and not modified.

**Live runs 18496 / 30812 / 22984 and the sibling agents were never signalled, never inspected and never
polled.** Their state in section 3 was established by **reading `.pid` files and directory listings on
disk**, which is a read of an artifact and not an observation of a process.

**Files written by this pass:** `notes/PLAN_NEXT_24H.md` (this file, rewritten in place) and
`.claude/scan-out/plan-theory-rewrite.json`. Nothing else.
