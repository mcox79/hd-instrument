# COMPACTION HANDOFF -- 2026-08-17, written by the Director

**READ THIS AFTER `notes/STATUS.md` AND BEFORE ACTING.** It carries what one very long session
established, what it RETRACTED, and the two agents left mid-task. Everything here was measured on
disk; where a number comes from an agent's fragment rather than an independent recompute, it says so.

---

## 1. THE ERROR PATTERN THAT COST THE MOST -- CHECK EVERY CLAIM BELOW AGAINST IT

**THE DIRECTOR READ AN UNDERPOWERED NULL AS A CAPABILITY STATEMENT THREE SEPARATE TIMES TONIGHT.**
This is the single most important lesson of the session. Before believing any negative in this
project, ask: *was the sample large enough for the margin to separate AT ALL?*

- **"0 of 7,769 banked cells meet the bar"** -- RETRACTED. The unfixed checker passed 4; with the
  constant floor wired in and claim-arm selection made allowlist-based it passes 1, and that
  survivor is itself rejected on three grounds. The figure was stale twice over.
- **"Our instrument cannot resolve verbs even when handed the right answer"** -- SUSPENDED, probably
  false. At n=86 a Spearman CI half-width is ~0.215 and that stratum's floor (0.1814) was itself
  ~1.645/sqrt(85) = 0.178, i.e. **the floor was the null-distribution width**. A +0.0801 margin
  could not separate there regardless of the space's quality. **SimLex holds 222 verb pairs; we used
  86. Re-measure K1_OWN_NORMS on all 222 in the EXISTING 12-dim space before building anything.**
- **"The constant floor is the binding one"** -- FALSE in general. On the bridging population it
  computed to **-0.1959**, the WEAKEST of the four. Compute it per population, every time.

**Corollary rule, now standing: report the CI half-width and the null p95 at that n BESIDE every
margin.** A width is not an effect.

---

## 2. THE FINDING THAT DOMINATES THE PROGRAMME

**THE PARTIAL CUE IS STRUCTURALLY DEAD, AND A CHEATING ORACLE PROVES IT.**
Across 47 foundations at full scale (all 47 landed, KA 0.9807-1.0):

| | exact key | partial cue |
|---|---|---|
| purity predicts retrieval at | **rho 0.961** | **rho -0.0167** |
| range across foundations | spans 68x | spans only 0.0064-0.0365 |
| circular WordNet ORACLE (allowed to cheat) | **0.8787** | **0.0365** |

**An oracle that cannot beat 0.037 is not a supply problem, a purity problem, or a mechanism
problem.** Something structural makes the partial cue uninformative. **Diagnosing that is the top
open question** and every downstream build is aimed at the wrong thing until it is answered.
Only a two-stage cue moves it at all -- CI-separated but tiny (0.0225 -> 0.0322 max).

---

## 3. WHAT WAS BUILT AND WHAT IT SETTLED

- **A REAL CLEANUP MEMORY** (`hdlab/vsa_cleanup_memory.py`), proven not inert: fixed points 1.0000,
  idempotent, capacity falling on VSA theory's own O(d/log d) scale, KA/NULL breaking independently.
  **The five banked nulls SURVIVE it.** It produces the first cleanup lift this programme has
  measured (+0.0033 and +0.0078, CI-separated in 2 of 3 pools) while every arm stays far below the
  binding floor (-0.1135 open pool). **That REMOVES the "the load-bearing half was missing" defence
  and makes those negatives stronger, not weaker.** Of the five: three reconfirm, one was quoting a
  bundling-degeneracy field rather than any cleanup measurement, and one is not a null at all but a
  CI-separated HARM.
- **THE WRITE/READ ASYMMETRY IS THE ONE LIVE POSITIVE.** Sparsifying the address never beats a dense
  address outright, but MATCHES it at 1% occupancy if you expand first and read with a dense cue --
  and the asymmetry wins **9 of 9 matched pairs by 1.4x to 6.3x**. This is the owner's per-process
  regime point showing up as a measured effect.
- **SURPRISE-WEIGHTING: clean null with a named cause.** Our surprise signal is DEGENERATE (median
  0.875 where 1.0 is exact orthogonality), so there is no informative tail; selection never beats a
  token-matched random subset in 11 of 12 comparisons.
- **PHASE 2 BRIDGING (full, 5.1 h): a clean, well-controlled NULL.** All five bridge arms
  NOT_SEPARATED on every large stratum (B1 0.0270, B5 0.0406, perm p 0.30). Identity 96.12% distinct
  / meaning 8.19% retained reproduces the smoke exactly. **The noun-verb falsifier FIRES**: the
  ORACLE arm uses no graph and shows the same profile, so by the cell's own pre-registered rule the
  asymmetry belongs to the TARGET SPACE, not to any ordering mechanism.

---

## 4. THE METHOD CORRECTION (owner-driven, and it changes how we choose what to build)

The owner asked whether we were drilling **how the field thinks the computation works**, not just
anatomy. We were not. The drill that followed
(`notes/drill_computational_theory_what_each_organ_computes_2026-08-16.md`) is the most consequential
of the session:

- **OUR SUBSTRATE'S CORE OPERATION IS UNPINNED.** VSA algebraic binding is NOT established as what
  the brain does; two live published rivals, each with published objections; the binding problem is
  open. **We built as if VSA had won and never drilled the critique of our own foundation.** Mark the
  substrate choice INVENTION-UNDER-TEST, not biology.
- **Theory PREDICTS our sparsity result** (the pinned MTL band was the worst meaning zone) because
  **separation IS the destruction of similarity** -- and prescribes **SPARSIFY THE ADDRESS, KEEP THE
  VALUE DENSE**, which is the unimplemented 2026-07-04 LINK-NOT-RECONSTRUCT design reached
  independently from a second literature.
- **13-row theory-vs-implementation backlog** plus **10 components with NO theoretical justification
  at all**, headed by the exhaustive cosine argmax read-out that sets the level of every number we own.
- **THE REFINEMENT THAT SHOULD GOVERN EVERY FUTURE ITEM: copy the brain's COMPUTATIONS exactly
  (problem-derived, shared by anything solving that problem) and treat every brain PARAMETER
  (constraint-derived, not shared) as a hypothesis to SWEEP. Our worst result copied a NUMBER; our
  best copied an OPERATION.**
- On whether fidelity predicts performance: **supported at low fidelity** (published brain-similarity
  correlations), **bounded at high fidelity** (two studies find it inverting at the top), and
  **untested here for power reasons** -- 1 positive in 6 cannot yield p below 1/6, so "UNVALIDATED"
  described the study design, not the score.

---

## 5. OWNER INPUT THAT IS LOAD-BEARING (BOARD Q1-Q13)

The owner's introspection is a measuring instrument nothing else supplies. Two answers changed builds:
- **Q13 / D1 -- PER-PROCESS REGIMES:** *"we have a phase diagram for substrate - we can set all
  variables, including dimensionality, wherever we want for each process. The brain does some in
  sparse space, some in dense, and we have the ability to change them on the fly."* **Stop asking
  "what is OUR sparsity" and specify it PER ORGAN.**
- **Q3 -- FOUNDATION IS FREE TO BUILD:** *"the brain began with hundreds of millions of years of
  evolution instilling a foundation. we can build that foundation however we want, as long as it is
  a strong foundation, and the operation is not llm."* A static offline-built asset is ADMISSIBLE;
  **an LLM at inference remains disqualifying -- that is THE invariant.**
- **Q8 -- retrieval is PROPOSE-AND-REJECT, iterative, with wrong candidates surfacing and being
  rejected.** Our read-out is a single argmax. The rejector half is validated: attestation separates
  gold from non-gold by +0.1234, surviving frequency-matched (+0.0262) and rate-matched (+0.0035
  NOT_SEPARATED) controls.
- **Q10 -- rejection matches on the FEELING of a word** ("think" vs "contemplate"). A sibling proved
  the profile rejector GENERALISES where attestation is structurally blind (0.1003 vs exactly chance
  0.0625 on unattested candidates, +0.0267 over max(four floors), surviving frequency and
  concreteness controls) -- **but AFFECT contributed nothing once width-matched against noise.
  REGISTER IS NOT VALENCE**; register/formality is the live hypothesis and **WORD LENGTH is its
  primary control** (length alone orders the validation pairs 29/30).

**Question quality is itself a defect surface:** an audit found **8 of 11 open decisions fail the
rules** -- never use a bare identifier, state what is currently true before asking, ask one thing.
Rewrites are drafted in `notes/QUESTION_LOG.md`.

---

## 6. INSTRUMENT STATE -- DO NOT TRUST THESE WITHOUT READING

- **`tools/verdict_bar_check.py` has FALSE-PASSED FOUR TIMES** (planted-answer arm; literal `oracle_`
  arm; a FLOOR'S OWN RISE credited as our margin; and a KNOWN-ANSWER arm selected as claim-carrying).
  Run it, report its class, **never rely on its verdict** -- state arm-by-arm margins.
- **The constant/prototype floor is now the bar's FOURTH role**, but **only 12 of 7,789 cells ever
  recorded one**, so every historical bar decision used a three-floor max.
- **`matched_candidate_sets` WAS VOID and is rebuilt** (old fitted-oracle constant 0.3873-0.9042
  against chance 0.0625). All matched-pool numbers were withdrawn. **`eligB` is still suspect** --
  admits a constant at 0.1715 against chance 0.0101.
- **NEVER use `grounded_similarity()` as a scorer** -- 76.18% of SimLex pairs land on two values.
- **`--smoke` in argv silently switches the imported ruler** to V=512/8MB; `ruler_mode_gate` exists at
  `experiments/exp_task_degeneracy_v1.py:121`.
- **A number may not cross scorers, pools or populations.** Eight retractions in three days.

---

## 7. OPERATIONAL STATE

- **`.claude/scan-out/` REFUSES FILE CREATION** -- four attempts tonight (two agents, two from the
  Director's main thread) all denied with the ambiguous string, while `notes/`, `tools/`,
  `experiments/` and `verification/` all accept writes. **Write fragments to `notes/` until the owner
  says otherwise.** Not routed around deliberately, in case the block is intentional.
- **`experiments/exp_propose_reject_retrieval_v1.py` IS A BLOCKED PATH** -- even a one-line write is
  denied while other names in the same directory land. The composed cell waits on the owner's word.
- **Liveness:** `tools/pid_reconcile.py` now reports DEAD-BUT-CLAIMED-LIVE and is wired into the
  session hook. All 39 pid files were dead; **two of the three "lost" runs had COMPLETED CLEANLY** --
  dead is not the same as failed.
- **`hd_director_kb_continuous_ingest` is LIVELOCKED** (10.65 GB, self-terminated at its own 45-min
  limit) while Task Scheduler reports it healthy. **Treat `director_kb_query.py` results as STALE.**
- **The dashboard is fixed and usable**: every row answerable, per-row evidence timestamps, a
  commentary box wired into both hooks. Launch:
  `D:\AI\hd-instrument\.venv\Scripts\python.exe D:\AI\hd-instrument\tools\status_gui.py`
- **Autoloop ARMED at 200.**

---

## 8. TWO AGENTS STOPPED MID-TASK, BOTH WAITING ON ONE INSTRUCTION -- **RESOLVED, SEE 8c**

**Both were resumed with the "write your findings to `notes/`" instruction and both finished on
2026-08-17.** Their results are 8c(1) and 8c(2). The rest of this section is kept because the
recoverability lesson in it is the reason 8c(1) was constructible at all.

Both stopped CORRECTLY on a denied fragment `Write` and refused to work around it. **Resume each with:
write your findings to `notes/` instead of `.claude/scan-out/`.**
1. **`partial-cue-structural`** -- diagnosing what caps the partial cue at ~0.037 even for an oracle.
   Blocking sub-question: were the held-out sentence's raw TOKENS persisted, **or are they
   RECOVERABLE?** (A sibling found a "never persisted" claim was true about persistence and FALSE
   about recoverability, reproducing the cue bit-for-bit from a read-only shim. **Check recoverability
   before concluding absence.**) That decides whether the cue-kind split and the word-order arms are
   constructible at all.
2. **`verb-target-space`** -- must run **K1_OWN_NORMS on all 222 SimLex verb pairs in the existing
   12-dim space FIRST**, before building any channel, per section 1.

**Also live:** `exp_selectional_constraint_bridge_v1` (pid 3828), fixed and past the crash point --
its `selftest()` was poisoning `_ORTHO_CACHE` with a ~60-row fixture the real run then indexed past.

---

## 8b. LANDED **AFTER** THIS FILE WAS FIRST WRITTEN -- THESE SUPERSEDE SECTIONS ABOVE

**(A) THE READ-OUT CEILING IS DIAGNOSED. THIS IS THE MOST IMPORTANT FINDING OF THE SESSION.**
Commits `10213434e`, `30a34dee5`; `notes/readout_ceiling_findings_2026-08-17.md`.

**Our store encodes CO-OCCURRENCE (syntagmatic: "appears near"). The task scores SUBSTITUTABILITY
(paradigmatic: "could replace"). For most items the correct answer's MEDIAN co-occurrence with the
query is EXACTLY ZERO -- it never shares a sentence with the query anywhere in the corpus.**

- **The answer IS in the store** -- rank curve CI-separated above a per-item random-ranking null at all
  11 values of k (4.77x at k=1) and above a permuted-cue null at all 11 (margins 4.9x-11.3x their own
  CI half-widths); median gold rank **37 of 5,491** against 203 expected. **So "content is missing" is
  FALSIFIED.** The defect is WHICH RELATION WAS ENCODED, not whether anything was stored.
- The winners are **collocates, not failed synonyms**: 79.3% have no close WordNet relation; they
  co-occur with the query **4.24x** more than the correct answer does. Qualitatively:
  `abbey -> highclere`, `absorb -> pigment`, **`absence -> presence`** -- an antonym, the textbook
  co-occurrence failure, since opposites share contexts.
- **39 read-out arms across two cells; NONE clears the binding floor, none beats the incumbent.**
  Includes the SUCCESSOR REPRESENTATION (ORGAN_MAP D7's "never run" organ) -- now run, CI-separated
  BELOW at all four gammas, worse as gamma rises: propagating through a graph whose multi-hop tail is
  noise adds noise.
- **Analytic closure of 29 arms:** the hubness correction and the constant floor are THE SAME OBJECT
  (corr 0.9995), so subtracting it removes signal.
- **THE ONE UNTRIED STRUCTURE IS THE BRAIN'S:** a shortlist plus **a verifier that is not the
  generator** (the owner's BOARD Q8 propose-and-reject). Measured oracle ceiling **0.1715 at k=5** and
  0.2604 at k=10, against the 0.1390 floor. **This is the only remaining road on this instrument.**
- Caveat the agent flagged rather than buried: the 0.1390 floor is partly a generous gold (the word
  `work` alone is correct for 13.9% of items), which is why the primary finding was stated against the
  per-item random-ranking curve instead.

**(B) THE PHASE 2 KILL IS WITHDRAWN FOR ONE MECHANISM AND RE-WORDED FOR THE OTHER.**
`exp_cue_regime_one_variable_v1`, verdict `BRIDGE_CUE_CARRIES_IDENTITY_NO__LAMBDA_STAR_0p60`.
**lambda* = 0.60 CONFIRMED** at full grid on all three configs, all four ladders, all three
definitions, morphology-blocked control reproducing exactly. The bridging instrument **cannot
CI-separate a cue carrying under ~60% of the target's identity**; the retrieval instrument's threshold
is 0.05.
- **The arm the kill fired on carried 21-22%.** Margin **-0.0566 [-0.1901,+0.0771]**, CI half-width
  **0.1336 = 2.4x the margin**, `MARGIN_NARROWER_THAN_ITS_OWN_CI = True`. **It could not have
  separated regardless of mechanism.** Population identity proved three ways, reproducing the landed
  numbers bit-for-bit including the exact `B1 0.0270` the kill fired on.
- **KILL WITHDRAWN** for thematic neighbour-copy (23.5-26.1% equivalent -- a power statement, the
  FOURTH underpowered null this session). **RE-WORDED, NOT WITHDRAWN,** for selectional bridging
  (0.0-2.6% equivalent, NOT_SEPARATED from a random word's code -- that estimator's cue is genuinely
  EMPTY). **But the generalisation "grounding does not propagate through our relations" DOES NOT
  SURVIVE** -- nothing under 60% was visible either way.
- Gates: KA rho 0.3311 (+0.2350 ABOVE), NULL 0.0118 NOT_SEPARATED, monotonicity 1.0000 on all four
  ladders. **The constant floor was the WEAKEST of the four here (-0.2253 / -0.1977); scramble p95
  binds.** Third time that assumption was wrong.

**(C) "THE PARTIAL CUE IS STRUCTURALLY DEAD" IS RETRACTED.** At full scale it addresses at 0.0711
against chance 0.00018 (**390x**), carries a derived **12-18% exact-key-equivalent**, and beats a
marginals-matched non-informative filler on 7 of 10 rungs. **The cue carries real information.**
What caps us is the READ-OUT, independently of the cue: a PERFECT cue (exact-key addressing 1.0000)
still yields hit@1 **0.0481**, CI-separated BELOW the constant floor 0.1390 by **7.3x its own CI
half-width**. **No rung clears at any cue quality.** So the ~0.037 oracle cap was TWO defects quoted
as one: a graded, non-structural ADDRESSING deficit, and a READ-OUT CEILING.

**(D) THE SUBSTRATE-BASIS REVIEW -- the owner's named first post-compaction topic.** Verified off disk
but **its write was denied, so it exists only in the agent's transcript**; re-issue it. Findings:
- **[CORRECTED 2026-08-17 -- SEE C35 IN `notes/STATUS.md` AND `notes/STATUS_LESSONS.md`. THE CLAIM
  BELOW IS PRESERVED VERBATIM AND MUST NOT BE QUOTED WITHOUT ITS CORRECTION.]**
  ~~**The binding-operator choice is EMPIRICALLY NULL at full mode** across two cells and six
  operators (`K_cliff` 750/750/750 for Hadamard/HRR/FHRR with 0.0 shift; `K*` 500/500/500 for
  cyclic-shift / permutation / phase-rotation with **0.000 separation**).~~
  **What survives:** among the three standard algebraic operators, no instrument we have built could
  resolve a difference. **What does not:** "null" is a three-bin grid artifact (FHRR reads 0.8000
  against Hadamard's 0.2889 inside the very bin that produced the word "invariant"); the second half
  names the wrong cell and is superseded rather than absent; and two of the six operators COLLAPSE
  (0.0720 and 0.0000 against about 0.81). Full working in 8c(4).
- The one clean live-path format cell (`data/exp_capacity_vs_format_2x2_livepath_v1`, full, floored,
  projection-draw-controlled) puts `sign()` at +0.0585 and d=256 at +0.0635 -- roughly equal and
  additive -- **but the graded gain is NULL on open-vocabulary hit@1.**
- **The cell justifying `sign()` (`exp_bipolar_quantization_quality_cpu_v1`) is SMOKE-MODE with NO
  FLOORS and NO CIs, and is contradicted by two later full-mode cells.**
- All three quoted landmarks reproduce exactly but are ISOLATION proofs; the arc is verified:
  `1.000 -> 0.954 -> 0.919 (tied control 0.700) -> 0.063 fails its bar under matched difficulty ->
  CONJUNCTIVE_HURTS, CI-separated below flat`.
- **THE SEPARATION THAT MATTERS FOR THE OWNER'S DECISION: the FORMAT costs a few points; the WRITE
  RULE puts the system below its own constant floor.** Do not conflate them.

---

## 8c. LANDED **AFTER** SECTION 8b -- FOUR MORE, AND ONE OF THEM CORRECTS THIS FILE

Written by a later audit/docs-only pass on 2026-08-17. **Every number in this section was
re-derived from the artifact with `.venv` python by that pass; none was taken from a report, a
verdict message or another agent's summary.** That pass authored no experiment, ran none, dispatched
nobody, and did not open `experiments/` or `hdlab/` for writing.

**(1) THE ANSWER IS IN THE CUE, AND OUR OWN COMPRESSION IS THROWING PART OF IT AWAY. This is the
most consequential of the four, and it unblocks a build.**
`data/exp_cue_information_audit_v1/metrics.json`, commit `eec21487d`, findings in
`notes/cue_information_audit_v1_findings_2026-08-17.md`.

On one identical store, cue, pool and gold (n=3,994 items, 5,491 candidate addresses, chance
1/5,491 = 0.000182), addressing accuracy:

| arm | value |
|---|---|
| raw uncompressed count vectors (`U0_UNCOMPRESSED`) | **0.0849** |
| the live 256-dim projection (`C0_PROJECTED_256`) | **0.0711** |
| handed the exact key (`K1_EXACT_KEY`, both regimes) | **1.0000** |
| a size-matched random key (`N1_RANDOM_KEY`) | **0.0003** |

Decisive margin **+0.0138, 95% CI [+0.0083, +0.0195], half-width 0.0056, CI-SEPARATED**. The cell's
own stop-if (iii) fired: **the 256-dimensional compression is a MEASURED DEFECT**, the information
IS in the cue, and the address-side build is licensed as a capability claim with **0.0849 as the
measured target**. Deflation that travels with it: 0.0849 is still about eight percent, and the
read-out ceiling is untouched -- both regimes remain CI-separated BELOW their own binding floors at
hit@1.

**The precondition this rested on is no longer an unadopted agent measurement.** Exact
recoverability of the held-out sentence reproduced on **every** eligible item (3,994 of 3,994, max
absolute error 0.000e+00), not on the 400-item sample the earlier fragment checked, and the run
added a store-side encoder identity check the fragment never ran (`H^T P_a == mat[a]`, **bit-exact
on all 5,491 anchors**).

**The cue-kind split is the part that should change a build.** The owner's Q4 introspection named
TWO parts to a half-remembered word, and we serve one of them:
- same-meaning words: **+0.0113 [+0.0080, +0.0148] ABOVE**;
- the word's starting sound: **0.0 [-0.0013, +0.0013] NOT_SEPARATED** -- exactly zero, because our
  only onset channel is the word's **first four characters hashed as a single whole symbol**
  (`ONSET_LEN = 4`), which cannot resemble anything unless a stored word IS that four-character
  string. **We have no channel that can represent a word's onset.** A board question is open on
  whether to build one; it is not assumed.

**(2) VERBS RE-MEASURED AT n=222. RETRACTION 2 CLOSES AS *MEASURED*, NOT CONFIRMED AND NOT
WITHDRAWN.** `data/exp_verb_target_space_n222_v1/metrics.json`, commit `0652e20a5`, findings in
`notes/item2_verb_target_space_n222_measurement_2026-08-17.md`.

- Verbs n=222: known-answer arm rho **0.2607** [0.1282, 0.3841], half-width **0.128**. Strongest
  floor (scramble p95) **0.1152** against the predicted null width 1.645/sqrt(221) = **0.1107** --
  **the null genuinely tightened, so this is NOT a repeat of the n=86 failure** where the floor
  simply WAS the null's own spread. Margin **+0.1452 [-0.0496, +0.3379] NOT_SEPARATED**;
  row-permutation **p = 0.001**. Stop-if (ii) fired.
- Nouns n=666: **+0.2065 [+0.1015, +0.3102] ABOVE**. Adjectives n=111: **-0.0074 NOT_SEPARATED**,
  permutation p 0.060. Never compared across populations.
- **Section 1 of this file must be read with this update: the entry "SimLex holds 222 verb pairs; we
  used 86 -- re-measure before building anything" is now DISCHARGED.** A verb-channel build is
  licensed **citing this measurement and never the retired n=86 one**.

**(3) THERE IS NO MAPPED PHASE DIAGRAM, AND THE RECOLLECTION THAT THERE IS ONE HAS A TRACEABLE
SOURCE.** `notes/substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md`, commit
`32cc8ce71`.

The history was enumerated from the filesystem, never from a registry or an index: 8,661
directories, **7,804 `metrics.json`**. *(Re-walked by this pass: 8,662 directories and 7,807
`metrics.json`, the difference being exactly the three files this session added --
`exp_cue_information_audit_v1`, its smoke, and `exp_verb_target_space_n222_v1`. Nothing in the
original enumeration is missing; the two sets were diffed by path, not by count. Re-run minutes
later it read 8,663 and 7,808, the fourth file being the ITEM 3 agent's first smoke landing live.
Script, promoted out of `scratch/` so this does not cite a wiped directory:
`tools/phase_diagram_recovery/verify_metrics_enumeration.py`.)* Of those files, about **59 vary dimensionality**, about **21 vary
sparsity**, and **2 cells vary the expansion factor**. The note's own classification tally:
**23 of 42 parameter-by-operation squares have never been measured**, 13 are usable. Six separate
diagrams on six different scorers, which under this project's own rules may not be merged.

The "we have a phase diagram, 55-65% covered" recollection most likely traces to
`notes/director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`, whose overall estimate reads
*"~55-60% -> 60-65%"* while **its own line items say dimensionality "Outer ~10%" and sparsity
"<5%"**. And the sparsity sweep the owner's Q13 note leans on **has no cell under `data/` at all**
-- it lives in `scratch/sparsify_right_object/`, which `.gitignore` line 83 excludes and
`tools/clear_scratch.py` periodically wipes. Promote it before the next clear.

**(4) THE CORRECTION TO THIS FILE'S OWN SECTION 8b(D), FILED AS C35.** The claim that the
binding-operator choice is "empirically null at full mode across two cells and six operators" is
**wrong in three separate places**, and one of the corrections is itself a correction of the
phase-diagram note. Verified by opening all eleven relevant `metrics.json` files.

- **The `750/750/750` half REPRODUCES** -- `data/exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}`,
  all `run_mode: full`, all `HARD_FAIL_BINDING_OP_CAPACITY_INVARIANT`, `K_cliff` 750 for Hadamard,
  circular-convolution HRR and FHRR with shift 0.0. **But the capacity axis had only THREE values,
  [150, 750, 1350], and all three operators landed in the middle one. A three-bin instrument cannot
  report a difference smaller than a bin. That is a RESOLUTION LIMIT, NOT A NULL.**
- **And the same files' own per-point scores contradict the word "invariant".** At the middle grid
  point, top-1 by seed: FHRR **0.8667 / 0.7333 / 0.8000** (mean 0.8000) against Hadamard
  **0.2667 / 0.2667 / 0.3333** (mean 0.2889) and circular-convolution **0.3667 / 0.2000 / 0.3333**
  (mean 0.3000). At the top grid point, FHRR 0.4444 against Hadamard 0.1000. **FHRR is 2.77x
  Hadamard at the same point, on all three seeds.** The cell reports no confidence interval at all;
  an approximate two-proportion check by this pass (three seeds x 30 queries pooled as n=90, normal
  approximation, queries treated as independent -- an optimistic assumption, since queries within a
  seed share one bundle) puts that gap at **+0.5111 with an approximate 95% half-width of 0.1249**.
  The "null" is the `K_cliff` read-out quantising a large difference into one bucket.
- **The `K* 500/500/500 with 0.000 separation` half DOES reproduce, in a cell neither the handoff
  nor the phase-diagram note named** -- `data/exp_substrate_order_binding_family_v1_seed_{13,19}`,
  `run_mode: full`, verdict `HARD_FAIL_ORDER_BINDING_INVARIANT`, `K_star_per_op` = 500 for
  cyclic-shift, random-permutation and phase-rotation, `max_sep=0.000` -- again on a **three-value
  grid, K in [50, 500, 2000]**, 50 queries per point, and **only 2 of 3 seeds landed** (seed 7's
  `metrics.json` holds no phase map and records `RUNNING` at 0.15 s elapsed). **It is SUPERSEDED,
  not absent:** the later cell of the same family, `exp_substrate_order_binding_family_v2_seed_{7,13,19}`
  (also full, a discriminator-targeted load sweep, 60 queries per point), returns
  `MIDDLE_BAND_PARTIAL` with **the winner changing by seed** -- cyclic-shift / random-permutation /
  phase-rotation = 0.2667 / 0.1833 / 0.2167 (seed 7), 0.2333 / 0.2000 / 0.2333 (13), 0.2167 /
  0.2500 / 0.2000 (19).
  **THEREFORE THE PHASE-DIAGRAM NOTE'S OWN WORDING -- "that does not reproduce ... is not what is on
  disk" -- IS ITSELF TOO STRONG AND IS CORRECTED HERE.** It reproduces in the v1 cell and is
  superseded by the v2 cell. This is standing discipline 7 (no demotion without a fresh on-disk
  re-check) applying to a correction rather than to a result.
- **The summary omitted that two of the six operators COLLAPSE.** In
  `data/exp_substrate_seqbind_binding_op_family_v2_seed_7` (full), per-operator mean top-1 over its
  five sequence-length points: Hadamard **0.8160**, circular-convolution HRR **0.8360**, tensor
  product **0.7720**, XOR-on-binary **0.0720**, sum-modulo-N **0.0000**. That cell's own separation
  metric is `max_log2_sep = 3.322` -- which is log2(500/50), a **tenfold** gap -- **not 0.000**. Its
  `K_cliff` is 500 for the three algebraic operators and **50** for the other two. And note the
  handoff named the wrong operators for this cell: it is Hadamard / HRR / tensor product here, not
  cyclic-shift / permutation / phase-rotation.

**THE STANDING FACT TO RECORD ALONGSIDE, and it is the load-bearing half: the binding operator has
never been varied on any operation this programme actually runs on.** All four binding-operator cell
families score top-1 retrieval from a bundle on a SYNTHETIC corpus (every `corpus_provenance` string
begins `synthetic_substrate_`), at **30, 50, 50 and 60 queries per point** respectively -- *(the
"50 queries per point" figure in circulation does not reproduce; it is right for two of the four)* --
and **not one of the eleven files contains a confidence interval, a bootstrap or a permutation
test.** Zero binding cells score on the comparator, on addressing, or on open-vocabulary read-out.

**So "unfalsified" here means "never tested", not "confirmed".** The honest statement is: among the
three standard algebraic operators the difference is smaller than any instrument we have built could
see, and one of them (FHRR) is visibly better at the one grid point where the others are not
saturated; two non-algebraic operators are decisively worse. **"We tested it and it does not matter"
and "we have never been able to tell" are different claims, and only the second is supported.**

---

## 9. THE NEXT THREE THINGS, IN ORDER

1. ~~**Diagnose the partial-cue structural cap.**~~ **DONE 2026-08-17 -- see 8c(1).** The answer is
   the opposite of the feared one: the cue DOES carry identity, and our own 256-dim compression is
   what loses part of it. No redirect upstream.
2. ~~**Re-measure verbs at n=222.**~~ **DONE 2026-08-17 -- see 8c(2).** Neither retracted nor
   confirmed: MEASURED. A verb-channel build is licensed on this number and never on the old one.
3. **Build sparse-address / dense-value per-organ**, which three independent lines now agree on: the
   theory drill, the owner's per-process answer, and the write/read asymmetry. **Its capability half
   is UNBLOCKED as of 8c(1) and an agent is building it; treat `experiments/` and `hdlab/` as owned
   while that runs.** It is now an EXPANSION question with a measured target (0.0849 addressing
   against the incumbent's 0.0711), and dimensionality is a SWEPT variable here, not an adopted
   setting -- per 8c(3), the `d=256 -> 1024` raise is justified for the comparison job and not for
   the addressing job.
4. **NEW, and it is a question for the owner rather than a build:** we have no channel that can
   represent the starting sound of a word, which is one of the two things the owner's own
   introspection said a half-remembered word is made of (8c(1)). A board question is open.
