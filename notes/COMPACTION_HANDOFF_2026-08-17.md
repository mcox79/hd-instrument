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

## 8. TWO AGENTS STOPPED MID-TASK, BOTH WAITING ON ONE INSTRUCTION

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
- **The binding-operator choice is EMPIRICALLY NULL at full mode** across two cells and six operators
  (`K_cliff` 750/750/750 for Hadamard/HRR/FHRR with 0.0 shift; `K*` 500/500/500 for cyclic-shift /
  permutation / phase-rotation with **0.000 separation**).
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

## 9. THE NEXT THREE THINGS, IN ORDER

1. **Diagnose the partial-cue structural cap.** Nothing downstream is worth building until this is
   answered. If the answer is "the cue does not carry the identity", the programme redirects upstream
   to what the cue is made of -- **and that is a GOOD outcome, not a defeat.**
2. **Re-measure verbs at n=222** and either retract or confirm the target-space claim.
3. **Build sparse-address / dense-value per-organ**, which three independent lines now agree on: the
   theory drill, the owner's per-process answer, and the 9-of-9 write/read asymmetry.
