# PLAN -- THE NEXT 24 HOURS

**Rewritten 2026-08-17 by an audit/docs-only pass, at HEAD `daad41b48`, branch
`dataprep/mcguffey-graded-corpus`, around section 9 of `notes/COMPACTION_HANDOFF_2026-08-17.md`.**

**SUPERSEDED-BY NOTICE.** The previous version of this file (2026-08-16, 14 items, 92,629 B) is
**fully superseded by this one** and is preserved verbatim at commit **`da678875c`**. It was
UNTRACKED; it was committed unchanged before this rewrite specifically so that superseding it does
not destroy it. Nothing in it was silently deleted -- its still-live items are carried forward in
section 5 with pointers, and the three items it got wrong are retracted in section 0 by name.

**Scope, stated up front so nothing is mistaken for work done:** this pass rewrote documents. **It
authored no experiment cell, ran no cell, spawned no subagent, signalled no process, and demoted,
re-labelled or deleted no metrics.json, atom or registry row.**

---

**UPDATE, LATER THE SAME DAY (2026-08-17, second audit/docs-only pass, at HEAD `0652e20a5`).**
**ITEM 1 and ITEM 2 are both DONE.** Their outcomes, and which stop-if fired for each, are recorded
in their own blocks in section 4 and summarised here:

| item | landed | which stop-if fired | what it licenses |
|---|---|---|---|
| ITEM 1 -- is the answer in the cue at all | `eec21487d`, `data/exp_cue_information_audit_v1/` | **(iii)** -- `U0_UNCOMPRESSED` 0.0849 beats `C0_PROJECTED_256` 0.0711, +0.0138 [+0.0083,+0.0195], CI-separated | the information IS in the cue; the 256-dim compression is a MEASURED DEFECT; ITEM 3's capability half is UNBLOCKED with 0.0849 as the measured target |
| ITEM 2 -- verbs at n=222 | `0652e20a5`, `data/exp_verb_target_space_n222_v1/` | **(ii)** -- does not clear, but the null width fell to ~0.11 as predicted | retraction 2 closes as **MEASURED**, not confirmed and not withdrawn; a verb-channel build is licensed citing THIS measurement and never the retired n=86 one |

Every figure in this update block was re-derived from the two `metrics.json` files with `.venv`
python by the second pass, not read from any agent's report. **ITEM 3's capability half is now
unblocked and an agent is building it; this pass authored nothing for it and did not open
`experiments/` or `hdlab/` for writing.** A new correction, **C35**, was filed against section 8b(D)
of the handoff -- see `notes/STATUS.md` CORRECTIONS and `notes/STATUS_LESSONS.md`.

---

**EVIDENCE CLASSES, never merged.** Every figure below is marked **RECOMPUTED** (this pass opened
the artifact and re-derived it with `.venv` python), **ON DISK** (the artifact records it and this
pass read the field), or **AGENT MEASUREMENT** (exists only in another actor's fragment; attributed,
never adopted). The full verification table, including **the two handoff figures this pass could NOT
reproduce and therefore did not use**, is in `notes/plan_status_compaction_report_2026-08-17.md`.

---

## 0. THE RETRACTIONS. READ THESE BEFORE QUOTING ANYTHING FROM THE LAST THREE DAYS

**THE HEADLINE IS THE ERROR PATTERN, NOT THE THREE NUMBERS: THE DIRECTOR READ AN UNDERPOWERED NULL
AS A CAPABILITY STATEMENT THREE SEPARATE TIMES IN ONE SESSION.** The three are unrelated in subject
and identical in shape -- a margin was compared with a floor without anyone asking whether the
sample could separate ANY effect at that n, or whether the "floor" was a level or merely a width.

Each is recorded as a dated correction with the superseded claim preserved. **None is a silent
rewrite.** Stubs live in `notes/STATUS.md` as C32-C34; full reasoning in `notes/STATUS_LESSONS.md`.

### RETRACTION 1 (2026-08-17) -- "0 of 7,769 banked cells meet the bar"

- **SUPERSEDED CLAIM, verbatim:** *"7,769 banked cells scanned (`verdict_bar_check.py`,
  `c0802fc36`): 0 MEET the bar."* Carried in `notes/STATUS.md` POSITION and TOOLING STATE through
  the 2026-08-16 revision, and in `MEMORY.md`'s banner. The intermediate **"2 of 7,772"** is retired
  with it.
- **SUPERSEDED BY:** `data/verdict_bar_reports/verdict-bar-20260817T002627Z.json` -- 7,789
  metrics.json enumerated by `os.walk` over an absolute data dir; **MEETS_BAR 1**, FAILS_BAR 7,770,
  NO_EVIDENCE 18. *ON DISK.*
- **AND THE SURVIVOR IS ITSELF REJECTED** on four grounds, so the corrected figure must never be
  quoted as good news: its matched pool admits a fitted constant at 0.7354 against chance 0.0625; it
  is the EXACT-KEY regime and not the operating point; the cell declines a cell-level verdict
  (`verdict = "COMPUTED"`); and its margin was overstated 4.20x once its own declared orthographic
  floor stopped classifying as a non-floor.
- **WHY IT WAS WRONG:** the count was taken before the constant-floor role was wired in AND before
  claim-arm selection was made allowlist-based. **"0 of N" was never a statement about the corpus.
  It was a statement about the checker.**

### RETRACTION 2 (2026-08-17) -- "our instrument cannot resolve verbs even when handed the right answer"

- **SUPERSEDED CLAIM:** that the existing 12-dim target space cannot order verb pairs even for a
  known-answer arm -- used to motivate building a new channel.
- **STATUS AS OF 2026-08-17 (CLOSED): MEASURED.** Not confirmed and not withdrawn. It was SUSPENDED
  because it was unmeasurable at n=86; ITEM 2 has now measured it at n=222 and the result stands as
  a real, CI-honest negative rather than an artifact of sample size. *RECOMPUTED off
  `data/exp_verb_target_space_n222_v1/metrics.json`:* K1_OWN_NORMS rho **0.2607** [0.1282, 0.3841]
  (half-width 0.128); strongest floor `F_SCRAMBLE_PERM_P95` **0.1152** against the plan's own
  null-width orientation 1.645/sqrt(221) = **0.1107** -- the null genuinely tightened, so this is
  NOT a repeat of the n=86 failure; margin **+0.1452 [-0.0496, +0.3379] NOT_SEPARATED**;
  row-permutation **p = 0.001**. Contrast strata, each on its own floors, never crossed: nouns
  n=666 **+0.2065 [+0.1015, +0.3102] ABOVE**; adjectives n=111 **-0.0074 NOT_SEPARATED**
  (permutation p 0.060). **A verb-channel build is licensed and must cite this measurement. The
  n=86 number is RETIRED and may not be quoted again.**
- **The two statistics disagree and both are reported rather than picking the flattering one:** the
  permutation test says the verb correlation is real; the paired bootstrap on the margin says its
  interval still crosses zero. The bar is the bootstrap, so the arm does not clear.
- **THE MEASUREMENT IT RESTED ON, *ON DISK*:**
  `data/exp_thematic_relation_supply_bridged_grounding_v2/metrics.json`,
  `HILLS_2009_NOUN_VERB_FALSIFIER.known_answer_K1.V` -- n=**86**, rho 0.2576 [0.0401,0.4524], floor
  (scramble p95) **0.1776**, margin **+0.0801 NOT_SEPARATED**.
- **WHY IT PROVES NOTHING (*RECOMPUTED*):** that floor, 0.1776-0.1814, is
  **1.645/sqrt(85) = 0.1784** -- **THE FLOOR IS THE NULL DISTRIBUTION'S OWN WIDTH AT THAT n.** No
  arm of any quality separates there. The cell says so itself in `pos_stratified_note` and
  `G0_power_gate`; the reader did not.
- **THE TEST THAT SETTLES IT IS ITEM 2 AND IT NEEDS NO NEW ASSET.**

### RETRACTION 3 (2026-08-17) -- "the constant/prototype floor is the binding one"

- **SUPERSEDED CLAIM:** that the constant/prototype floor, being the strongest member on the open
  read-out pool (0.1382 / 0.1390), is the binding floor generally.
- **FALSE AS A GENERAL CLAIM. Two populations where it is the WEAKEST of the four:**
  - bridging stratum n=394: **-0.1959** (optimistic tie; midrank -0.1977, pessimistic -0.1996; tie
    mass 0.287). *AGENT MEASUREMENT*, `.claude/scan-out/collect-completed-runs.json`, computed by
    that agent's own script `.claude/scan-out/constfloor/const_floor_bridging.py`, which reproduced
    the n=394 / 412-bridged stratum exactly.
  - selectional-bridge stratum n=308: **-0.2253**. *ON DISK*,
    `data/exp_selectional_constraint_bridge_v1/metrics.json`, `floors.F_CONSTANT_PROTOTYPE`. An
    independent instance of the same reversal, on a different stratum, from a different cell.
- **THE MECHANISM:** on a hit@1 instrument a constant ranking wins whenever the gold is a popular
  item, so it is strong. On a PAIR-CORRELATION instrument, giving every bridged word the SAME code
  makes the pair ordering ANTI-correlated with the gold, so it is weak. **A floor's strength is a
  property of the SCORER, not of the floor.**

**THE STANDING RULE THESE THREE BOUGHT, now `STATUS.md` STANDING DISCIPLINE 14 and also written into
`MEMORY.md`:**

> **REPORT THE CI HALF-WIDTH AND THE NULL p95 AT THAT n BESIDE EVERY MARGIN. A WIDTH IS NOT AN
> EFFECT.** If the margin's CI is wider than the gap it must clear, the arm cannot separate no matter
> how good the underlying thing is, and the result is a statement about the sample, not the system.

---

## 1. THE STANDING RULES THAT GOVERN EVERY ITEM BELOW

These are not preamble. Each one has been broken, at a cost, in the last week.

1. **A GATE IS A CI-SEPARATED MARGIN OVER `max(orthographic, frequency, scramble,
   constant/prototype)`**, on the identical scorer, n, pool and gold, **with every floor recomputed
   on the item's OWN population**, plus a known-answer arm proving the instrument and a null arm
   proving the effect, failing independently. Never a bare absolute number.
2. **NEVER IMPORT 0.1382, 0.2070 OR -0.1959.** Every one is real on its own population and none
   travels. There are at least five different constant floors on five different populations and they
   are not corrections of each other.
3. **REPORT THE CI HALF-WIDTH AND THE NULL p95 AT THAT n BESIDE EVERY MARGIN.** (Section 0.)
4. **REPORT TIE CONVENTIONS BOTH WAYS**, never silently the flattering one. One top-50 comparison
   flips from +0.0105 NOT_SEPARATED to +0.0641 ABOVE on tie mass alone.
5. **A NUMBER MEASURED AT THE EXACT KEY DOES NOT TRANSFER TO THE PARTIAL CUE**, which is the real
   operating point. State the cue regime beside every retrieval number.
6. **COPY THE BRAIN'S COMPUTATION EXACTLY; TREAT EVERY BRAIN PARAMETER AS A HYPOTHESIS TO SWEEP.**
   A computation is derived from the problem and the problem is one we share (separation before
   completion; a dense cue addressing a sparse store; an error residual as the learning signal;
   generate-and-test with a verifier that is not the generator). A parameter is derived from a
   constraint we do not share (0.2% sparsity, seven gamma cycles, a five-hour tagging window).
   **Our worst result copied a NUMBER; our best copied an OPERATION.** Every design below must name
   which of its choices is a computation being copied and which is a parameter being swept. *This is
   the Director's strategic read, labelled a hypothesis pending VET, not a measured verdict.*
7. **VSA ALGEBRAIC BINDING IS UNPINNED IN THE BRAIN.** No recording shows a neural population
   computing an algebraic binding over two full-rank vector codes; there are three live accounts
   (algebraic, coarse-coded conjunctive, synchrony) and all three have published objections. **Our
   substrate's core operation is OUR-INVENTION-UNDER-TEST, not biology, and every brief, prereg and
   organ row calling it brain-derived is mislabelled.** This is not "abandon the substrate": VSA has
   real anchors and one strong neural-implementation existence proof. **Unfalsified is not
   confirmed.**
8. **THE ONLY DISQUALIFYING INVARIANT IS NO LLM AT INFERENCE.** The owner ruled that a foundation
   may be built however is most efficient -- evolution installed the brain's -- **so a static,
   offline-built asset is ADMISSIBLE**. Holding ourselves to a from-scratch standard was stricter
   than the brain. An LLM anywhere in the operational flow remains disqualifying.
9. **SET THE REGIME PER ORGAN, NOT GLOBALLY.** The owner: *"we have a phase diagram for substrate --
   we can set all variables, including dimensionality, wherever we want for each process."* Stop
   asking "what is OUR sparsity".
10. **`tools/verdict_bar_check.py` HAS FALSE-PASSED FOUR TIMES** (planted-answer arm; a literal
    `oracle_` arm; a floor's own rise credited as our margin; a known-answer arm selected as
    claim-carrying). Run it, report its class, **never rely on its verdict** -- state arm-by-arm
    margins. *The four instances are the 08-17 handoff's enumeration; this pass verified the tool's
    current output (1 MEETS_BAR of 7,789), not the four historical instances.*
11. **NEVER use `grounded_similarity()` as a scorer** (76.18% of SimLex pairs land on two values),
    never use a `matched_candidate_sets`-built pool for a claim until it passes
    `pool_admits_a_winning_constant`, and note `--smoke` in argv silently switches the imported ruler
    to V=512/8MB (`ruler_mode_gate` at `experiments/exp_task_degeneracy_v1.py:121`).
12. **A FLOOR IS CLEARED BY UNDERSTANDING, NEVER ADOPTED.** Wiring a spelling channel in to clear a
    spelling floor is how the retired ">=10%" gate was gamed.

---

## 2. WHERE WE ARE, IN ONE PAGE

### 2.1 The blocker, and it is now measured twice over

**A PARTIAL CUE DOES NOT PRODUCE THE RIGHT ADDRESS, AND A CHEATING ORACLE PROVES THE CAP IS
STRUCTURAL.**

*ON DISK / RECOMPUTED, `data/exp_foundation_neighbourhood_purity_v1/metrics.json`, grid `full`, 47
foundations, population n=2358, ruler-mode gate PASS, known-answer arms **0.9807-1.0000 on 47 of
47**:*

| | exact key | partial cue |
|---|---|---|
| purity predicts retrieval at | rho **0.961** (n=45) | rho **-0.0167** (n=40) |
| range across the 47 foundations | 0.0129-0.8787, a **68.1x** span | 0.0064-0.0365 |
| circular WordNet ORACLE, allowed to cheat | **0.8787** | **0.0365** |

**The oracle's 0.0365 is the single best partial-cue reading anywhere in the grid.** A foundation
built by consulting the answer key cannot beat 3.7% under the operating cue. **That is not a supply
problem, a purity problem or a mechanism problem.** The only thing that moves it at all is a
two-stage cue: 0.0225 -> **0.0322** at best.

Two measured facts constrain the diagnosis, both *ON DISK* in
`data/exp_cue_to_store_translation_v1/metrics.json`: the partial cue's cosine to its OWN stored row
is **0.1621**, and the same pipeline addresses **1.0000 at the exact key and 0.0325 under the
partial cue** (n=1997). A sparsifier keeping the top few per cent of an expansion turns a 0.16
alignment into a near-random active set, so **the cue never gets close enough for the key to
matter.** In plain language: the filing system works perfectly if you hand it the exact card it
already holds, and 3% of the time if you describe the card. Real reading is always the second case.

### 2.2 What landed since the previous plan, and what each thing settled

**(a) SELECTIONAL-CONSTRAINT BRIDGING LANDED. IT IS THE SECOND MEASURED NULL ON BRIDGING AND IT IS
WORSE THAN THE FIRST.** *ON DISK*, `data/exp_selectional_constraint_bridge_v1/metrics.json`,
`run_mode full`, elapsed 5330 s, verdict `SELECTIONAL_CONSTRAINT_BRIDGE_DOES_NOT_CLEAR_THE_FLOOR`,
mtime 2026-08-17T00:32. **Caveat carried deliberately: no `.pid` file on disk names the process the
operator described as live and none was modified on 08-17, so what is on disk is a COMPLETE full;
if a live process later rewrites it, re-check the mtime before quoting.**

This cell implements the owner's OWN answer to how a new word gets its meaning -- bridge by the
**selectional restrictions of the verbs the word is an argument of** ("ran implies legs implies
animal") rather than by copying a co-occurring neighbour's code, which is what we had built. On the
common stratum (n=308; N 259 / V 27 / A 22; Spearman CI half-width 0.1122):

- **CI-separated BELOW the incumbent it was built to beat:** head-to-head **-0.1049
  [-0.2041,-0.0057]**. S2 -0.1176 and S3 -0.1422 are also BELOW; S4 (subject slot only) is -0.0195
  NOT_SEPARATED.
- **Indistinguishable from a random target:** S1 vs `N2_NULL_RANDOM_TARGET` **-0.0015
  [-0.1391,+0.1361] NOT_SEPARATED**. It does beat the slot-rewire null (+0.1139 ABOVE), so the slots
  carry something; the random-target comparison says that something does not identify the word.
- **The instrument was alive** (K1_OWN_NORMS rho 0.3311) and **the mechanism was genuinely
  different** (source-set Jaccard overlap with the incumbent 0.0133; 38.6% of words share no source
  at all; supply real at 8.6 slots / 145 fillers per word).
- **Evidence gap, stated not papered over:** three floor roles recorded (orthographic 0.0503,
  hardened frequency ~0.0000, constant -0.2253), **no scramble floor**; the two seeded null arms
  carry that role instead. Its bar decision is not four-role complete.
- **This is `LONG_TERM_PLAN.md`'s Phase 2 kill condition firing.** Two different bridging mechanisms,
  both with passing known-answer arms, both null. **Grounding does not propagate through our
  relations, and the honest reading is that the substrate needs a different acquisition mechanism.**
  Before calling the route exhausted: what was tested is stage ONE of a THREE-stage account. The
  owner's own description was selectional constraint, then EPISODIC recall of instances, then a
  DISTRIBUTION over categories. We built the first third and scored it with a point estimate.
  *(DO-NOT-REDO 43, revival criterion recorded there.)*

**(b) THE CLEANUP MEMORY IS REAL, AND IT MAKES FIVE BANKED NULLS STRONGER, NOT WEAKER.** *ON DISK*,
`data/exp_cleanup_memory_capability_v1/metrics.json` (`hdlab/vsa_cleanup_memory.py`). Stored symbols
are fixed points at **1.0000**, the map is idempotent, recovery is monotone in cue quality (0.9987
at tau=0.45 against chance 0.00018), capacity is reported on VSA's own `d/log d` scale, and the
known-answer and null arms break independently. It produces **the first cleanup lift this programme
has measured** -- over no-cleanup, partial cue: **+0.0033 [+0.0013,+0.0055] ABOVE** (open pool) and
**+0.0078 [+0.0008,+0.0150] ABOVE** (K49), with K15 +0.0046 NOT_SEPARATED, i.e. **CI-separated in 2
of 3 pools** -- while every arm remains **-0.1135 [-0.1249,-0.1019] BELOW** the binding constant
floor of 0.1390. **This REMOVES the "the load-bearing half of VSA was missing" defence.** The five
banked cleanup nulls were not measuring a broken organ.

**(c) THE WRITE/READ ASYMMETRY IS THE ONE LIVE POSITIVE.** *ON DISK + RECOMPUTED*,
`data/exp_sparse_address_dense_value_v1/metrics.json`, n=3994, partial-cue regime, every rung
computed on its own population (the cell explicitly refuses to import the 0.0325 from a different
population):

- best partial-cue addressing anywhere is **0.0719 [0.0638,0.0796] at a DENSE address** (D=2048);
- a **1%-occupancy address (82 active units of 8192) READ WITH A DENSE CUE matches it at 0.0699
  [0.0621,0.0779]** -- a 100x sparser address for no measured loss;
- the same config read **SYMMETRICALLY** reads 0.0483 [0.0418,0.0548], **1.45x worse**;
- across matched pairs (same regime, D, `a_write`, code type, projection seed; sparse writes only)
  **the dense read wins 18 of 24, ties 5, loses 1 at 0.99x, and the largest gain is 6.27x**.
  *(RECOMPUTED. The handoff's "9 of 9 by 1.4x to 6.3x" does not reproduce under this pairing rule;
  the 6.27x maximum does. See the report's section 1a.)*
- **Sparse never beats dense outright and the whole grid sits at or below ~0.072.** The asymmetry is
  real; the LEVEL is the cap in 2.1.

**(d) SURPRISE-WEIGHTING IS A CLEAN NULL WITH A NAMED CAUSE.** *ON DISK + RECOMPUTED*,
`data/exp_surprise_weighted_update_v1/metrics.json`. The surprise signal is **DEGENERATE** -- median
**0.875**, mean 0.853, p90 1.0128, where 1.0 is exact orthogonality -- so there is no informative
tail to select from. Selection therefore beats a token-matched random subset in only **4 of 18**
point comparisons, never by more than +0.0035. And the residual rule is a near-no-op
(`mean_cos_to_A0_rows` **0.9771** at every eta), which is exactly the **PRE-REGISTERED bootstrapping
cause**: the prediction comes from the store being criticised, so early in training the residual IS
the observation. **That is not a refutation of surprise weighting.** The stronger brain-faithful
version is a SEPARATE predictor or a warm start.

**(e) PHASE 2 THEMATIC BRIDGING, FULL: a clean, well-controlled NULL.** *ON DISK.* B1 rho 0.0270
[-0.0737,+0.1251] at n=394 against floors 0.0412 / 0.0317 / 0.0905 recomputed on the identical
stratum, NOT_SEPARATED, permutation p 0.30; **both known-answer arms ABOVE** (K1 0.3301, K2_ORACLE
0.2893). Bridged codes **keep identity** (96.12% distinct) and **lose meaning** (retention 0.0819).
The external curated CSKG arm fails too, so "OUR relations are the limiter" is unsupported.
*(DO-NOT-REDO 38.)*

**(f) THE READ-OUT IS STILL BELOW ITS SPELLING FLOOR.** *ON DISK*,
`data/exp_orthographic_floor_vet_v1/metrics.json`: hit@1 **0.0480** against TRIGRAM-ONLY **0.0870**
and PREFIX-ONLY 0.0588, n=4000 items over 5491 anchors. **"We underperform a spell-checker" is
untouched by everything above.**

---

## 3. WHAT IS IN FLIGHT, AND WHAT IS LANDED-BUT-UNREAD

Established by **reading `.pid` files, directory listings and mtimes** -- not by signalling,
inspecting or polling any process.

| thing | disk state | note |
|---|---|---|
| `exp_selectional_constraint_bridge_v1` | `metrics.json` **COMPLETE full**, 196,353 B, mtime 08-17T00:32 | described by the operator as live under **pid 3828**; **no `.pid` file on disk names 3828 and none was modified on 08-17**. Read it; re-check mtime before quoting. |
| `exp_thematic_..._v2` FULL | landed 08-16 | read in 2.2(e) |
| 47-foundation FULL grid | landed 08-16 15:13, 47/47 | read in 2.1 |
| `exp_cleanup_memory_capability_v1` | landed 08-16 22:38 | read in 2.2(b) |
| `exp_sparse_address_dense_value_v1` | landed 08-16 22:56 | read in 2.2(c) |
| `exp_surprise_weighted_update_v1` | landed 08-16 22:24 | read in 2.2(d) |
| `exp_cleanup_basin_conditional_v1` | landed 08-16 22:41 | **NOT YET READ by anyone. Read it before designing ITEM 3's basin arms.** |
| `exp_target_space_vs_bridge_mechanism_v1` | SMOKE only; the FULL directory does not exist | parked, section 5 |

**RESOLVED 2026-08-17 (later pass).** The two agents that had stopped mid-task on a denied fragment
`Write` -- `partial-cue-structural` (ITEM 1) and `verb-target-space` (ITEM 2) -- were resumed with
the "write findings to `notes/`" instruction and **both finished**. Their cells, findings notes and
commits are in the UPDATE block at the top of this file. **Now live instead: an agent is building
ITEM 3 in `experiments/` and `hdlab/`. Do not edit either tree while it runs.**

| landed today | metrics | findings note |
|---|---|---|
| `exp_cue_information_audit_v1` | `data/exp_cue_information_audit_v1/metrics.json` | `notes/cue_information_audit_v1_findings_2026-08-17.md` |
| `exp_verb_target_space_n222_v1` | `data/exp_verb_target_space_n222_v1/metrics.json` | `notes/item2_verb_target_space_n222_measurement_2026-08-17.md` |

**Do not touch:** `data/foundation/reading_grounding_v1` and `v2_qualityfix` (22+23 MB, no backup,
gitignored); `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*`;
`data/exp_structured_comparator_v1/probes/`.

**Held pending explicit owner authorisation:** the `d=256 -> 1024` raise (it rewrites every persisted
anchor store), any merge to `origin/main`, any origin push.

---

## 4. THE THREE ITEMS, IN THE ORDER THEY BLOCK EACH OTHER

Do the lowest open item. If it is blocked, say so in one line and take the next. Each carries: the
question -> the brain structure (and whether we are replicating it or substituting something
convenient) -> the can-fail design -> the floor -> the stop-if -> the runner -> the dependency.
**An item with no floor is not ready to run.**

---

### ITEM 1 -- DIAGNOSE THE PARTIAL-CUE STRUCTURAL CAP. *TOP. NOTHING DOWNSTREAM IS WORTH BUILDING UNTIL THIS IS ANSWERED.*

- **THE QUESTION.** Before any of our machinery touches it: **does the partial cue contain enough
  information to identify the target at all?** If it does not, no expansion, no completer, no
  translator and no addressing scheme can help, and the blocker relocates upstream to **what we
  WRITE**. That outcome is a good one and must be reported as such.
- **WHY IT IS NOW CONSTRUCTIBLE, AND THE SUB-QUESTION THAT DECIDES ITS SHAPE.** The held-out
  sentence behind every partial cue is **exactly reconstructible**: 400 of 400 items checked, max
  absolute error **0.000e+00**, from a read-only shim over the cached anchor matrix. *AGENT
  MEASUREMENT, `.claude/scan-out/address-information-audit.json`.* **This corrects a claim both the
  drill and the cue-store cell carried -- the per-occurrence context stream is NOT persisted, but it
  IS recoverable, and "never persisted" was being read as "gone".** Check recoverability before
  concluding absence. If recovery does NOT reproduce in the resumed run, say so and run the reduced
  design; do not fabricate the cue-kind split.
- **BRAIN STRUCTURE: NONE IS CLAIMED AND NONE SHOULD BE FABRICATED.** This is an **information audit
  of our own encoder**, not a model of anything. Saying so is the honest answer; inventing an anatomy
  to fill the box is exactly the laundering the fidelity gate bans. *(The adjacent brain claim that
  IS pinned belongs to ITEM 3, not here: Treves & Rolls' two-input argument says a numerically large
  DENSE cortical cue should address a SPARSE store through a learned map -- our cue/store rank ratio
  of 2.3x is an UNDER-mismatch on both sides.)*
- **THE ONE-VARIABLE CONTROL THE ENCODER'S IDENTITY MAKES POSSIBLE.**
  `context_vector(graded=True)` is a sum over content-word tokens of a hash-seeded bipolar vector, so
  `cos(store_row, cue)` and `cos(raw_count_vector_a, raw_count_vector_i)` **differ by exactly one
  thing: the 256-dimensional random projection.** An UNCOMPRESSED arm is therefore a genuine
  one-variable control on our own encoder, and `H^T p_a == mat[a]` is a bit-level self-test that the
  two representations are the same object.
- **CAN-FAIL DESIGN.** On the identical store, cue, pool and gold:
  - `U0_UNCOMPRESSED` -- raw sparse count vectors, no projection. **The arm that decides the item.**
  - `C0_PROJECTED_256` -- the live encoder (the incumbent).
  - `K1_EXACT_KEY` -- known-answer; **must stay at 1.0000** or the instrument is dead.
  - `N1_RANDOM_KEY` -- size-matched random address; must sit at chance (1/n_anchors).
  - If recovery holds: a **CUE-KIND SPLIT** -- context sentence vs synonym-set vs word-onset -- each
    scored separately, because the owner's description of a partial cue has TWO parts (onset and
    same-meaning neighbours) and our machinery implements a third (a degraded copy).
  - Primary measure: **addressing accuracy** (`addressed_item_IS_the_query_word`). Secondary: hit@1.
- **FLOOR.** Addressing must clear the **size-matched random-key control, CI-separated**. hit@1 must
  clear `max(orthographic, frequency, scramble, constant/prototype)` **computed on this item's OWN
  population**, both tie conventions. **Report the CI half-width and the null p95 at that n beside
  every margin.** Report the exact-key arm alongside, never instead of. **Never import 0.1382,
  0.2070 or -0.1959.**
- **STOP-IF.** (i) `U0_UNCOMPRESSED` also lands near the incumbent's level -> **the information is
  not in the cue**; the address-side build in ITEM 3 is void AS A CAPABILITY CLAIM and the programme
  redirects to the write side. **Report this loudly; it is the most valuable outcome available.**
  (ii) `K1_EXACT_KEY` is not 1.0000 -> `INSTRUMENT_STILL_LOOSE`, publish no quality number.
  (iii) `U0` beats `C0` CI-separated -> the compression is the defect and ITEM 3 becomes an
  expansion question with a measured target.
- **RUNNER.** `cpu_runner_local` (sparse count vectors over ~4,000 items is cheap); escalate to
  `cpu_runner_0` only if the full type vocabulary makes the dense contrast large.
- **DEPENDENCY.** None. **BLOCKS ITEM 3's capability claim.**
- **STATUS: DONE, 2026-08-17, commit `eec21487d`.** *(The line this replaces read: "NOT on disk as
  of this pass. NO NUMBER EXISTS." That was true when written and is now superseded.)*
  **STOP-IF (iii) FIRED.** All figures below RECOMPUTED from
  `data/exp_cue_information_audit_v1/metrics.json` by a later audit pass, not taken from any report.
  - Primary measure, addressing accuracy, n=3,994, chance 1/5,491 = 0.000182:
    **U0_UNCOMPRESSED 0.0849** vs **C0_PROJECTED_256 0.0711**, decisive margin **+0.0138
    [+0.0083, +0.0195]**, half-width **0.0056**, band **ABOVE**. `K1_EXACT_KEY` **1.0000** on both
    regimes (instrument alive); `N1_RANDOM_KEY` **0.0003** (chance, as designed).
  - **THE ANSWER: the information IS in the cue, and our own 256-dim random projection is throwing
    part of it away.** The compression is a measured defect. ITEM 3's capability half is UNBLOCKED
    and 0.0849 is its measured target. Stop-if (i) did NOT fire, so the programme does NOT redirect
    to the write side on this evidence.
  - **DEFLATION THAT MUST TRAVEL WITH IT:** 0.0849 is still about eight percent. The gain is real
    and small; the read-out ceiling is untouched (both regimes sit BELOW their own binding floors at
    hit@1, C0 -0.1167 [-0.1284,-0.1054], U0 -0.0631 [-0.0727,-0.0536]).
  - **THE PRECONDITION HELD.** Exact recoverability of the held-out sentence reproduced on **every**
    eligible item (n=3,994, `max_abs_error 0.0`, `ALL_EXACT True`), not the 400-item sample the
    earlier agent fragment checked, plus a store-side encoder identity `H^T P_a == mat[a]` that was
    **bit-exact on all 5,491 anchors** and that the fragment never ran. It is no longer an unadopted
    agent measurement. The regression gate reproduced the landed C0 number exactly (0.0223).
  - **THE CUE-KIND SPLIT IS THE PART THAT SHOULD CHANGE A BUILD.** The owner's description of a
    half-remembered word had TWO parts and we serve only one: same-meaning words **+0.0113
    [+0.0080, +0.0148] ABOVE**; word onset **0.0 [-0.0013, +0.0013] NOT_SEPARATED**, with both
    onset arms at 0.0008 against a random key at 0.0003-0.0005. The reason is structural, not
    tuning: our only onset channel is the word's **first four characters hashed as one whole
    symbol** (`ONSET_LEN = 4`), which cannot resemble anything unless a stored word IS that string.
    *(The findings note calls this a "single-character-prefix" cue; that description is wrong, the
    code uses four. Corrected here, off the source.)* **A BOARD QUESTION IS OPEN on whether to build
    a real onset channel; it is not assumed.**

---

### ITEM 2 -- RE-MEASURE VERBS AT n=222, AND EITHER RETRACT OR CONFIRM THE TARGET-SPACE CLAIM. *Cheap, desk-scale, and it settles a live retraction.*

- **THE QUESTION.** At a sample size where a margin could separate at all, **can the EXISTING 12-dim
  space order verb pairs when a known-answer arm is handed the right answer?** This measures the
  INSTRUMENT, not a capability, and the write-up must say so in those words.
- **WHY IT IS ITEM 2 AND NOT A FOOTNOTE.** The claim that it cannot is currently **SUSPENDED**
  (section 0, retraction 2) and it is load-bearing: it is the stated motivation for building a new
  channel into the target space. **Building a channel on a suspended claim is how a session spends a
  day on the wrong object.** Until this lands, no channel work is licensed.
- **THE POPULATION, AND THE TRAP IN IT.** `data/encoder_eval_benchmarks/simlex999.txt` holds
  **222 verb pairs** (RECOMPUTED by counting the file: N 666, V 222, A 111). The bridged stratum used
  **86** because bridging requires one endpoint to be held out; **`K1_OWN_NORMS` needs no bridge and
  can run on all 222.** **These are two different populations and no number may cross between them**
  -- floors, nulls and CIs are all recomputed on the 222.
- **BRAIN STRUCTURE, replicate or substitute.** The target space is our operationalisation of
  Binder's experiential attribute blocks; our 12 dims cover 2 of 7. **PINNED:** that the blocks are
  dissociable. **OURS, INVENTION UNDER TEST:** that a handful of per-word scalars is a faithful
  operationalisation of a block. **No new channel is built in this item** -- it is a measurement of
  what we already have, which is why it is cheap.
- **CAN-FAIL DESIGN.** One population (222 verb pairs), one scorer (the same 12-dim L2-normalised
  cosine and Spearman rho against SimLex gold used by the bridging cell), arms:
  - `K1_OWN_NORMS` -- the known-answer arm; the thing being measured.
  - `F_ORTHOGRAPHIC`, `F_FREQUENCY_HARDENED`, `F_SCRAMBLE_PERM_P95`, `F_CONSTANT_PROTOTYPE` -- all
    four floors, all recomputed on these 222 pairs.
  - `N1_SCRAMBLE` with at least 2,000 permutations, reported as p95 AND as a permutation p-value.
  - The 666-noun and 111-adjective strata run identically, as contrast, each with its own floors --
    **the noun/verb comparison must never be made across populations.**
- **FLOOR.** CI-separated over `max(four floors)` on the 222-pair population, both tie conventions.
  **Report, in the same sentence as the margin: the Spearman CI half-width at n=222 and the scramble
  p95.** For orientation only, the null width scales as ~1.645/sqrt(n-1): **0.1784 at n=86 and
  ~0.1107 at n=222.** If the measured p95 at 222 does not fall accordingly, that is itself a finding
  about the null construction and must be reported.
- **STOP-IF.** (i) `K1` clears `max(four floors)` CI-separated at n=222 -> **retraction 2 is
  CONFIRMED: the space CAN order verbs, the "verbs are unresolvable" claim is dead, and no channel
  build may cite it.** (ii) `K1` does NOT clear at n=222 while the null width has fallen to ~0.11 ->
  **the claim is now MEASURED rather than asserted**, and only then is a channel build licensed --
  with the brain-framed question ("which experiential block is missing?") asked before the tool
  question. (iii) The scramble p95 at n=222 is still of the same order as the margin ->
  `POWER_INSUFFICIENT AT EVERY AVAILABLE n`; report that SimLex cannot answer this question and name
  what benchmark could.
- **RUNNER.** `cpu_runner_local`. It is a cosine and a Spearman over 222 pairs plus permutations.
- **DEPENDENCY.** None. Does not touch ITEM 1's population or ITEM 3's store.
- **STATUS: DONE, 2026-08-17, commit `0652e20a5`.** *(The line this replaces read: "No cell on disk.
  The agent that owns it stopped mid-task." Superseded.)* **STOP-IF (ii) FIRED.** All figures
  RECOMPUTED from `data/exp_verb_target_space_n222_v1/metrics.json` by a later audit pass.
  - Population recounted from the benchmark file itself: N 666, V 222, A 111, total 999 -- as the
    plan expected.
  - Verbs n=222: K1_OWN_NORMS rho **0.2607** [0.1282, 0.3841], half-width **0.128**. Floors on this
    population only: orthographic 0.0183, frequency 0.0341, constant/prototype 0.0536, **scramble
    p95 0.1152** (strongest). Margin over the strongest floor **+0.1452 [-0.0496, +0.3379]**,
    **NOT_SEPARATED**. Row-permutation **p = 0.001** over 2,000 draws. It clears the other three
    floors CI-separated; the scramble floor is the one it fails.
  - **WHY THIS IS NOT THE n=86 FAILURE AGAIN, WHICH IS THE WHOLE POINT OF THE ITEM:** the plan
    predicted the null width would fall to 1.645/sqrt(221) = **0.1107**; the measured scramble p95
    came in at **0.1152**, a ratio of 1.04. The null tightened exactly as predicted, so the negative
    is now a property of the space and not of the sample. That is stop-if (ii), not (iii).
    *(Stop-if (iii)'s wording -- "p95 still of the same order as the margin" -- overlaps (ii) and
    both numbers are given here so a reader can check the adjudication rather than take it. The
    cell itself declined to adjudicate, and said so in its own verdict message.)*
  - Contrast strata, own floors, never compared across populations: nouns n=666 **+0.2065
    [+0.1015, +0.3102] ABOVE**; adjectives n=111 **-0.0074 [-0.2666, +0.2479] NOT_SEPARATED**,
    permutation p 0.060.
  - **RETRACTION 2 CLOSES IN THE "MEASURED RATHER THAN ASSERTED" DIRECTION.** A verb-channel build
    is licensed by the plan's own wording for this branch -- after the brain-framed question ("which
    experiential block is missing?") -- and **must cite this n=222 measurement. The n=86 number is
    retired.**
  - Independent reproduction worth keeping: this cell's noun stratum puts the constant/prototype
    floor at **-0.1247**, a second, differently-constructed instance of retraction 3's reversal.
    Direction only; the number is not importable.

---

### ITEM 3 -- BUILD SPARSE-ADDRESS / DENSE-VALUE, PER ORGAN. *THREE INDEPENDENT LINES AGREE. Its EFFICIENCY half is unblocked; its CAPABILITY half is blocked by ITEM 1.*

- **THE QUESTION.** Our store is one flat object asked to be both key and value, scored by cosine in
  one space, with **one operating point for both write and read**. **Does a SPARSE, EXPANDED ADDRESS
  pointing at a DENSE GRADED VALUE -- returned by LINK, never reconstructed, with the write and read
  regimes set independently -- beat the flat store under a partial cue?**
- **WHY THE CONFIDENCE IS HIGHER THAN FOR ANY OTHER BUILD, AND WHAT THAT CONFIDENCE IS NOT.** Three
  lines that did not consult each other agree:
  1. **The computational-theory drill:** separation IS the destruction of similarity, so the
     capacity objective wants the KEY sparse while the efficient-coding objective wants the VALUE
     dense and graded. Two different objectives with two different optima, routinely conflated -- and
     we conflated them, applying the capacity optimum and then measuring the efficient-coding
     quantity.
  2. **The owner's Q13 answer:** set the regime PER PROCESS; the brain does some in sparse space and
     some in dense.
  3. **A measured effect:** the write/read asymmetry in 2.2(c), 18 of 24 matched pairs, up to 6.27x.
  **What it is not:** a route to a big number. The same grid's ceiling is ~0.072 addressing under a
  partial cue. **Expect an efficiency win and state that expectation before running.**
- **BRAIN STRUCTURE, replicate or substitute -- and it is CONTESTED at the top level.** Four live
  accounts of what the hippocampus computes: **index** (a sparse address with a linked value),
  **conjunctive autoassociative store** (a compressed content vector), **relational map** (an EDGE),
  **predictive map** (discounted-future occupancy). **Our flat store is the conjunctive account done
  WITHOUT the sparsity that account's own capacity equation requires.**
  - **PINNED as an ARCHITECTURE:** indexing, on engram-tagging and optogenetic reactivation.
  - **PINNED as a COMPUTATION:** expand, then sparsify, then complete; and the three spaces are NOT
    commensurate (Neunuebel & Knierim 2014 measured the dentate representational change EXCEEDING
    its entorhinal input's while the CA3 change is LESS than both).
  - **PINNED as a SWITCH, not a setting:** O'Reilly & McClelland's resolution is a REGIME SWITCH --
    encoding runs the mossy-fibre path with recurrents suppressed, retrieval runs the direct
    perforant path with recurrents dominant, neuromodulatory (high ACh encode, low ACh retrieve).
    **Build the switch; do not tune one operating point.**
  - **PARAMETERS, therefore SWEPT AND NEVER ADOPTED:** the ~5x expansion, the ~100x sparsening, the
    0.2% active fraction. Our one explicit parameter copy -- the pinned MTL 0.2% band -- was the
    worst point in its own sweep, monotonically.
  - **OURS, INVENTION UNDER TEST:** the expansion operator, and the index ALLOCATION rule (nothing
    in the literature says which cells get recruited).
- **CAN-FAIL DESIGN.** One variable at a time, on the identical population, all four floors
  recomputed there:
  1. `A0_FLAT` -- the incumbent, one operating point for write and read.
  2. `T1_SPARSE_KEY_DENSE_VALUE` -- key sparsified (level SWEPT), value left dense and graded,
     retrieval by LINK and never by reconstruction.
  3. `T2_REGIME_SWITCH` -- `a_write` != `a_read`, both swept independently; **this is the arm the
     asymmetry predicts wins.**
  4. `C1_SPARSE_BOTH` -- the thing we already did, as the control that isolates WHICH object the
     sparsification belongs to.
  5. `K1_ORACLE_ADDRESS` -- hand it the correct address; the LINK stage must return ~1.0 or the
     instrument is dead.
  6. `N1_RANDOM_ADDRESS` -- must sit at chance.
  - **Report the between-projection-draw standard deviation beside every CI** (the existing grid
    already does this in `BETWEEN_PROJECTION_DRAW_SD`): item bootstraps are blind to shared-randomness
    variance, and every cell built on a random projection must report it.
  - **Read `data/exp_cleanup_basin_conditional_v1/metrics.json` first** -- it landed 08-16 22:41 and
    nobody has read it; it is the basin-stratified companion to the cleanup organ and it constrains
    which settle arms are worth arming.
- **FLOOR.** CI-separated over `max(four floors)` recomputed on this item's own population, **on the
  PARTIAL CUE, which is the operating point**, both tie conventions, with the CI half-width and null
  p95 beside every margin. Report the exact-key arm beside it, never instead of it.
- **STOP-IF.** (i) `T1` ties `A0_FLAT` on the partial cue with `K1_ORACLE_ADDRESS` passing -> the
  ADDRESS, not the store's architecture, is the limit; the work goes back to ITEM 1's answer.
  (ii) `C1_SPARSE_BOTH` matches `T1` -> the key/value distinction is not doing the work and the
  two-literature convergence is refuted for our geometry; **say so plainly.** (iii) any known-answer
  arm fails -> `INSTRUMENT_STILL_LOOSE`, publish nothing. (iv) **the whole sweep sits at or below the
  ~0.072 addressing ceiling already measured** -> the item bought EFFICIENCY (a 100x sparser address
  at no loss), not capability. **Report it in exactly those words and never quote it as a retrieval
  win.**
- **RUNNER.** `cpu_runner_local` smoke; `cpu_runner_0` for the swept full grid; `gpu_runner_0` only
  at D=8192 with dense matmuls over the full anchor set (8 GB VRAM, 0.9 cap).
- **DEPENDENCY.** **The CAPABILITY claim has a HARD DEPENDENCY ON ITEM 1** -- if the information is
  not in the cue, a better address cannot recover it. **The EFFICIENCY claim does not**, because the
  1%-occupancy match is already measured; that half may proceed as a wiring task at any time.
- **STATUS 2026-08-17: THE DEPENDENCY IS DISCHARGED AND THE CAPABILITY HALF IS UNBLOCKED.** ITEM 1
  fired stop-if (iii): the information is in the cue and the 256-dim projection is what loses it, so
  this item becomes an EXPANSION question with a measured target of **0.0849** addressing (against
  the incumbent's 0.0711) rather than an open bet. **An agent is building it now**; this docs pass
  authored nothing for it and opened neither `experiments/` nor `hdlab/` for writing.
  **Two constraints on the write-up, fixed before it lands, so they cannot be chosen afterwards:**
  stop-if (iv) still stands -- if the sweep sits at or below the ~0.072-0.085 band it bought
  EFFICIENCY, not capability, and must be reported in those words -- and **the phase-diagram pass
  (`32cc8ce71`) says the `d=256 -> 1024` raise is justified for the comparison job and NOT for the
  addressing job, so dimensionality here is a swept variable and not an adopted setting.**

---

## 5. PARKED BACKLOG -- CARRIED FORWARD, NOT RE-DERIVED, NOT DELETED

Every item below was specified in full in the superseded plan at commit **`da678875c`** (section 4,
items 1 and 5-14). **Nothing here has been re-verified by this pass.** They are parked, not closed;
open that commit for the design, floors and stop-ifs before running any of them.

| parked item | why it is parked rather than in section 4 | where its spec lives |
|---|---|---|
| the cleanup memory on its own recovery axis | **ANSWERED while it was still item 1** -- 2.2(b). What remains is the `T2_CONTINUOUS_SETTLE` vs `T1_DISCRETE_ARGMAX` discriminator, because the field does not agree whether CA3 is a discrete attractor at all | `da678875c` item 1 |
| expand-before-sparsify | absorbed into ITEM 3, whose sweep covers D=256/2048/8192 | `da678875c` item 3 |
| surprise-weighted update | **ANSWERED** -- 2.2(d). Revive only with a SEPARATE predictor or a warm start | `da678875c` item 5 |
| a verifier that is not the generator | **BLOCKED ON THE OWNER'S WORD** about a denied path; and its precondition fails anyway -- a propose-reject loop needs a proposer that is right sometimes, and ours addresses 3.25% of the time under a partial cue | `da678875c` item 6 and 6.4 |
| the register channel as the verifier's feature | feeds the blocked item; and its own primary control is severe (word length alone orders the owner's 30 pairs 29/30, so an unresidualised register channel IS a spelling channel) | `da678875c` item 7 |
| the dual-hub discriminator | its conflict stratum is small by construction; **do not run it until section 0's power rule can be satisfied on that stratum** | `da678875c` item 8 |
| the successor representation on our own thematic graph | cheap and never run, but it sits downstream of two bridging nulls on the same graph | `da678875c` item 9 |
| the target-space decider FULL | deflated: the affect question was answered NO on a different bench, and ITEM 2 must land first | `da678875c` item 11 |
| parameter-divergence vs computation-divergence | desk re-analysis, no run; it is the cheap test of standing rule 6 and protects it from hardening into doctrine | `da678875c` item 12 |
| publish the corrected bar base rate | **DONE by this pass** -- section 0 retraction 1, and `notes/STATUS.md` now carries 1 of 7,789 | -- |
| the floor-lexicon residue | `tools/**` is do-not-touch for this pass; filed for the tool owner | `da678875c` item 14 |

---

## 6. STANDING OPERATOR DECISIONS -- OPEN, NONE TAKEN

Carried forward unchanged. None is a research item.

1. **The 238 flagged-and-cited cells.** 238 flagged cells are cited by the cert ledger or the
   capability registry, so their overstatement has already propagated. **Recommended default
   (Director's call, silence is safe): mark all 238 IN PLACE as bar-flagged-and-cited so nobody
   quotes them, and do NOT retract the citing indexes wholesale** -- a blanket retraction would demote
   results never re-checked on disk, which is the exact fault that produced ~11 wrong demotions in
   48 hours. The 39 `NO_CONSTANT_FLOOR` cells are a DIFFERENT population and a different action:
   that is **withholding, not refutation**.
2. **The 4 missing preregs said to block GPU dispatch.** **Unconfirmed on disk by two successive
   passes, and both said so rather than working around it.** Whoever asserted it should name the four
   anchors.
3. **The 98 ARCHIVE-tier re-runs.** **Recommended default: NO.** Mark them collision-affected in
   place and stop after wave 2.
4. **The blocked path `experiments/exp_propose_reject_retrieval_v1.py`.** A one-line write is denied
   there while sibling names in the same directory land. Two agents routed around it rather than
   retrying a variant, which is correct. **Three ways to unblock, owner's choice: say the path is
   fine; name a different path; or confirm the block is deliberate.** Do not attempt a fourth thing.
5. **`notes/STATUS.md` cap.** Re-measured 2026-08-17 at **11,571 B against the 8,704 B cap**, with
   **5,120 B of that in never-trim stubs alone**. The 2026-08-16 proposal of 9,216 B is now
   insufficient. **Two options are measured and PROPOSED, NOT ENACTED, in `notes/STATUS_SPEC.md`
   sec 7: raise to 12,288 B, or -- recommended -- move the DO-NOT-REDO / CORRECTIONS stub index into
   an uncapped `notes/STATUS_CLOSED.md`, which lands STATUS at ~8,580 B and needs no raise at all.**
   Director's call. **Do NOT close the gap by evicting a never-trim entry.**

---

## 7. WHAT WE ARE NOT DOING IN THE NEXT 24 HOURS

- **Not building a new target-space channel** until ITEM 2 says whether the claim that motivates it
  survives at n=222.
- **Not re-running either bridging mechanism.** Two measured nulls, both with passing known-answer
  arms, and the external curated graph fails too.
- **Not sparsifying the meaning VALUE, and not sparsifying the reading anchor.** Settled, with a
  theoretical reason: separation IS the deliberate destruction of similarity, so a code optimised to
  make two similar things orthogonal is optimised to make a similarity judgement impossible. Revive
  only where the object being sparsified is an ADDRESS -- which is ITEM 3.
- **Not making the cue lower-rank.** The theory says the cue should be DENSER than the store; our
  2.3x ratio is an under-mismatch on both sides.
- **Not stirring the store.** Free clumping reached the owner's target (synonym cosine 0.1214 ->
  0.4705) and bought nothing; participation ratio collapsed 171 -> 31, and only 0.46% of a word's
  top-20 store neighbours are its synonyms.
- **Not quoting the headline 4.80% as a diagnosis.** It is a joint number over every component.
- **Not wiring a spelling channel in to clear a floor.** Standing rule 12.
- **Not adopting any brain PARAMETER as a value.** Standing rule 6.
- **Not calling VSA settled**, and not overcorrecting into abandoning it. Standing rule 7.
- **Not raising `d` 256 -> 1024, not merging to `origin/main`, not pushing.** All three need explicit
  owner authorisation and one of them rewrites every persisted anchor store while other work is live.
- **Not trusting `director_kb_query.py`.** Its ingest is livelocked (10.65 GB, self-terminated at its
  own 45-minute limit) while Task Scheduler reports it healthy. Results are STALE.

---

## 8. HOW WE WILL KNOW THE NEXT 24 HOURS WORKED

Each is a CI-separated margin over the strongest floor **computed on its own population**, reported
with its CI half-width and null p95, never a bare number.

1. **We know whether the answer is in the cue at all** (ITEM 1). Either outcome is progress: it
   licenses the address work or it relocates the blocker to what we WRITE.
2. **We know whether the 12-dim space can order verbs at a sample size that can separate** (ITEM 2),
   and retraction 2 closes in one direction or the other. **This is the cheapest item on the list.**
3. **We know whether a per-organ sparse-address / dense-value store beats the flat one under a
   partial cue** (ITEM 3), or that it bought efficiency rather than capability -- which is still a
   result, stated as one.
4. **The two stopped agents are resumed with one sentence each**, and the blocked path gets the
   owner's word.
5. **`data/exp_cleanup_basin_conditional_v1/metrics.json` is READ.** An unread run is a run that did
   not happen; the 47-foundation grid sat unread for hours and it carried the session's biggest
   finding.

**The honest position on timing, unchanged.** We are before step 1 of the long-term plan. The first
moment this system does something a trivial baseline cannot is when the read-out clears the
**spelling** floor at hit@1, and it currently sits below a **constant** floor that itself clears
spelling.

**And the frame that governs how every negative here is read.** The brain grounds new word meanings
from a small sensory core plus experience, at a fraction of our text budget. **The capability is
demonstrated.** Every null above is a fact about our implementation, never about the capability.
Before any direction is called exhausted, write down what was actually tested and what the stronger,
more brain-faithful version would be -- **then test THAT.** With the addition this week earned, which
cuts the other way: *"do it the way the brain does"* is two instructions, not one -- **copy the
COMPUTATION exactly, and treat the PARAMETER as a hypothesis.**

---

## 9. WHAT NEEDS CHANGING IN `notes/LONG_TERM_PLAN.md` -- REPORTED, NOT EDITED

That file is **DIRECTOR-OWNED and was not opened for writing by this pass, nor by the later
2026-08-17 pass.** Five things in it are now stale, in descending order of cost. **Items 1 and 2
were re-checked on disk on 2026-08-17 and both are still unfixed at that date.**

0. **BEFORE ANY OF THE BELOW: THE FILE HAS NEVER BEEN COMMITTED.** `git log -- notes/LONG_TERM_PLAN.md`
   returns nothing and `git check-ignore` does not match it: **32,823 B of strategy exists in exactly
   one uncommitted copy on disk.** That is the same state `PLAN_NEXT_24H.md` was in before it was
   preserved verbatim at `da678875c`, and the same hazard class as the no-backup foundation stores.
   **Commit it UNCHANGED first, then make the edits below** -- otherwise the first edit is also the
   only version. This pass did not commit it because the file is Director-owned and this pass was
   instructed not to touch it; the hazard is reported, not acted on.

1. **ITS PHASE 2 KILL IS RECORDED AS FIRED, WITHOUT THE SUSPENSION THAT FOLLOWED IT.**
   `LONG_TERM_PLAN.md` line 343 carries the banner *">>> THIS KILL CONDITION FIRED, 2026-08-17. TWO
   INDEPENDENT MECHANISMS, BOTH NULL, BOTH GATED. <<<"*. That banner is now **half superseded** by
   `COMPACTION_HANDOFF_2026-08-17.md` section 8b(B): the bridging instrument cannot CI-separate a
   cue carrying under about 60% of the target's identity, and the thematic arm the kill fired on
   carried 21-22%, so **the kill is WITHDRAWN for thematic neighbour-copying and only RE-WORDED for
   the selectional route** (whose cue is genuinely near-empty). The file's own power caveat further
   down is not the same statement and does not cover it. **The generalisation "grounding does not
   propagate through our relations", which that section DOES license, does not survive either --
   nothing below 60% was visible in that instrument at all.** *(This pass did not re-verify 8b(B)'s
   numbers; it confirmed only that `data/exp_cue_regime_one_variable_v1/metrics.json` exists at
   `run_mode: full` with verdict `BRIDGE_CUE_CARRIES_IDENTITY_NO__LAMBDA_STAR_0p60`.)*
2. **Section 4 carries the DUAL-HUB account as `[PINNED]`** -- still present at line 185, unchanged
   as of 2026-08-17. It is **CONTESTED**: Lambon Ralph's group reads the temporo-parietal effects as
   SEMANTIC CONTROL demands over one store rather than a second store, and the two readings imply
   different builds (a second STORE vs a second CONTROL SETTING). Downgrade the label. Presenting a
   contested reading as pinned is the exact thing the standing fidelity gate bars, so this one is a
   rule violation and not only a staleness.
3. **Section 2 rows 3, 4 and 6** are superseded by the storage findings and by correction C30
   ("retrieval fine / we tie spelling" was exact-key and optimistic-tie only).
4. **Section 6's "GloVe would raise our number tomorrow and teach us nothing -- ceiling reference
   only"** is superseded by the owner's Q3 ruling (a foundation may be built however is efficient;
   only an LLM at inference is disqualifying) and by the measured consequence: **21 of 47 foundations
   clear the binding floor and every one of them is a static-table supply or fusion arm.**
5. **ADDED 2026-08-17: anywhere the file treats a substrate setting as decided, it is leaning on a
   phase diagram that does not exist.** The recovery pass (`32cc8ce71`) enumerated 7,804 result
   files from the filesystem and found **23 of 42 parameter-by-operation squares never measured**,
   about 59 files varying dimensionality and about 21 varying sparsity, and six separate diagrams on
   six scorers that may not be merged. The practical consequence for this file: the `d=256 -> 1024`
   raise is justified for the comparison job and NOT for the addressing job, and **the binding
   operator -- our core operation -- has never been varied on any job this programme runs on** (see
   correction C35). Nothing here needs a new decision; it needs the word "measured" removed from
   places where the measurement was never made.

---

## 10. DISCLOSURE

**No tool call in this pass was denied at any point.** Nothing was retried as a variant and no step
was silently skipped.

No deletion token was issued, alone or bundled with work. No `git add -A`. No origin push. No
subagent spawned. No LLM in any path. No experiment authored, smoked or dispatched. No process
signalled, inspected or polled -- every liveness statement in section 3 comes from reading `.pid`
files, directory listings and mtimes, which is a read of an artifact.

**Protected paths, read-only, none written:** `notes/LONG_TERM_PLAN.md`, `notes/BOARD.md`,
`notes/COMPACTION_HANDOFF_2026-08-17.md`, `CLAUDE.md`, `data/foundation/**` (never opened),
`preregs/**`, `experiments/**`, `hdlab/**`, `tools/**`, `data/capability_registry.jsonl`.

**Files written by this pass:** `notes/STATUS.md` (rewritten), `notes/STATUS_LESSONS.md` (appended),
`notes/STATUS_SPEC.md` (sec 7 proposal appended, cap literal unchanged), `notes/PLAN_NEXT_24H.md`
(this file, rewritten after committing the superseded version at `da678875c`),
`notes/plan_status_compaction_report_2026-08-17.md`, and
`C:\Users\marsh\.claude\projects\D--AI\memory\MEMORY.md`.
