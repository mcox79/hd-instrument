# STATUS -- THE RECOVERY ENTRY POINT. READ THIS, THEN THE PLAN.

AS OF: 2026-08-26 -- NOW RUNS FROM `C:\AI\hd-instrument` (moved off the USB, verified); the session-only architect cron `0d126b4a` is DEAD and the "PID 3412 experiment RUNNING" note below is STALE (both gone); NEWEST STATE IS THE 2026-08-26 ENTRY UNDER POSITION BELOW | branch `dataprep/mcguffey-graded-corpus` | origin push needs USER AUTH | ⚠️ **RUNNING: `exp_aimed_reading_register_controlled_v1.py --mode full` -- worker PID `3412` (~`626` MB), started `09:58`, `2` units in, `units.jsonl` fresh. NOT SPAWNED BY THIS SESSION: DO NOT KILL IT.** *Its recorded PID `31824` is the venv SHIM at 4 MB and reads as dead -- the worker is its CHILD. Judge it by `units.jsonl` mtime, never by the shim's counters.* *(The old `PID 37304` warning here was STALE -- that process is gone, verified with `Get-Process`.)* | ✅ **Q117 ANSWERED 08-24 04:02: *"why not fix the bar, and re run the past results. let's do this right."* HALF EXECUTED, HALF FILED, AND THE SPLIT IS THE POINT.** The spelling floor was `~78%` MORPHOLOGICAL LEAKAGE (`nation/national`); stem-stripped it falls `0.0867 -> 0.0193` and OVERLAPS its own info-free twin. **`score_space_gain_and_topk_ci_v1.py` COULD self-fix -- it owns an `A6_TRIGRAM_ONLY` arm, so it RE-MEASURED its own floor in-harness at `0.019500` CI `[0.015250,0.024000]`.** 🚫 **`per_row_gain_c3_vet_v1.py` COULD NOT: it owns NO trigram arm and only ever imported the constant, so it now REFUSES to grade** (`[BAR NOT CALIBRATED FOR THIS GOLD]`, exit 3, refusal fired under `--smoke` as a positive control). **DO NOT PASTE `0.019500` INTO IT -- different item construction, different scorer; no number crosses scorers or populations.** Completing it is **PRIORITY 1 `the_gate_cannot_measure_its_own_floor`**. *Note the direction: this made results HARDER to publish, never easier.* | ✅ **08-24 THE SUBSTITUTABILITY WALL IS BROKEN AND PHASE 1 IS REDIRECTED.** Cross-modal distillation -- the grounded hub TEACHES a direction over PPMI+SVD, no gold -- reads `0.8388` CI `[0.8031,0.8720]`, beating its info-free twin's MAXIMUM over 200 draws. **Split by hub coverage 08-24 (`python tools/split_distillation_by_hub_coverage.py`): hub-covered `0.8263`, hub-UNCOVERED `0.8669` CI `[0.8062,0.9220]` -- so it is NOT carried by the covered subset, and both hub-BLIND controls are FLAT across the split (`-0.0051`, `+0.0166`), ruling out a difficulty artifact.** ⚠️ **Honest claim is NOT WORSE, never BETTER: the difference `+0.0410` CI `[-0.0353,+0.1091]` SPANS ZERO.** ➡️ **So Phase 1's "+14,704 hand-rated words" is probably the wrong purchase -- project the norms we have.** 🚫 *Still LABEL-free but NOT RESOURCE-free: the teacher is the supplied Lancaster table.* | 🔌 **08-24 WIRING THE DISTILLATION WIN IS BLOCKED ON ONE NAMED, MISSING ORGAN -- FOUND BY RUNNING THE CODE, NOT BY GREP.** **`hdlab/grounded_similarity` IS live (in the `36`-module eager closure of `import hdlab.substrate`) and RETURNS `0.45` FOR `sofa/couch`, `apple/orange` AND `dog/cat` -- IDENTICAL, all three pinned at `GROUNDED_CAP`.** *Its own docstring calls this a principled ceiling: uncapped they read `0.968`/`0.952`/`0.932`, synonym and sibling fully overlapping, and "not something a different threshold on this SAME metric can fix."* **THAT CEILING IS EXACTLY WHAT DISTILLATION BREAKS** (grounded alone `0.5513` -> taught `0.8388`). 🚫 **BUT THE TAUGHT DIRECTION NEEDS A WORD-CONTEXT VECTOR AT INFERENCE AND THE LIVE PATH HAS NONE:** the hand lexicon is ~`230` concepts, `grounded_similarity` is norms-only, and **`hdlab/ppmi_sparse_encoder` IS NOT A WORD-CONTEXT SPACE -- it is CHAR-TRIGRAM (spelling) by its own docstring, and is NOT in the live closure** (nor is `composed_encoder_v3` nor `sensorimotor_spoke`). ➡️ **PRIORITY 2 `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`.** ⚠️ **DO NOT RAISE `GROUNDED_CAP` -- and it would not help: `0.968` vs `0.952` does not separate. The channel is MISSING, not mis-tuned.** 🔻 *HYPOTHESIS, NOT MEASURED: that our meaning step reading `0.051` (backwards) is CAUSED by its only live word-description being a spelling code -- which would make the organ and the `~78%`-morphology floor the same thing. Converging, unproven.* 🔻 *AND MY CLOSURE LIST IS AN EAGER-IMPORT TRACE -- it structurally cannot see lazily-imported organs, and the substrate builds organs lazily. Quote it with its method or re-derive it by running a read.* | 🚨 **BOARD: Q119 IS OPEN -- the repo lives on a USB stick while a 2TB NVMe sits idle, and that is the certification "hang".** Cold open `15.40 ms` vs warm `0.96 ms`; ~`11,000` cold opens ~= `165 s` against a measured `167 s` one-line-test startup. **Every tool here pays it** -- a `data/` grep timed out at `320 s` during this very session. *TWO WRONG ANSWERS CAME FIRST (a concurrent session; then antivirus, off a BROKEN control comparing cold files to a just-WRITTEN one). Do not re-diagnose it; answer Q119.* | Q116 ANSWERED 08-23 -> **PRIORITY 2 `does_learning_from_reading_deserve_to_continue`** (owner declined to settle it by decision and asked for a measurement; **a clear loss is an explicit PASS**). Q115 ANSWERED + EXECUTED 08-23: new cells GATED by the pre-commit hook, coverage re-measured at **`71.2%`, not `~21%`**. Q113 (08-22): cell work + `hdi_*` spawns AUTHORIZED; the `notes/problems/` briefs are the solver's, do not work them here. Q111 STANDING: this session owns ALL integration, solvers never write `hdlab/`. Q110 STANDING: operational calls are mine, board is for owner-only decisions. Q102/106/107/108/109/112 DISCHARGED (full text `notes/QUESTION_LOG.md`). *Q103/104/108 share one pattern: filed before testing the constraint being complained about.*
   🗺️ **DERIVED VIEWS -- DO NOT RESTATE THEM HERE, THEY ROT. `python tools/substrate_map.py`**
   joins the `38` organs, `10` pipeline stages, `22` briefs and the registry and rebuilds on every
   run: `--gaps` worst-first, `--organ B3`, `--brief <slug>`, `--progress`. **Solvers may use it.**
   ✅ **CLOSED 08-22, one line each, full text at the named note:** grounding quality is
   `3/100 MEANINGFUL, 19 RELATED, 78 NOISE` blind (`THE_GROUNDING_ANSWER_...`); the best-evidenced
   grounding result is real but MISNAMED -- it relieves a d=256 CAPACITY bottleneck, not an ability
   (`THE_BEST_EVIDENCED_GROUNDING_RESULT_IS_MISNAMED_...`); 156 smoke rows carry a HARD_PASS their
   FULL run does not, hazard did NOT bite (`156_SMOKE_RUNS_...`); the certification gate ran ZERO of
   456 tests for two days behind a false `RESULT: PASS`, now fixed
   (`THE_CERTIFICATION_GATE_HAS_RUN_ZERO_...`); Q103's "only 40 usable pairs" was my own 60k-cap
   artifact, WITHDRAWN. **ONE STRUCTURAL FINDING spans three of those dead ends: one representation
   does two jobs needing OPPOSITE things -- grounding must delete the word, identification needs it
   present (word alone `0.9687` vs `0.6423` word+sentence; CONTEXT DILUTES identification, it is a
   LOOKUP). The form organs are already built and unwired.**
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

### 2026-08-28 (LATEST) -- ✅ **PHASE-DIAGRAM AUDIT INTEGRATED (owner-DONE, EXCELLENT — a rigorous NEGATIVE on N); the FORAGING solution is newly POSTED (I recommend DONE, awaits owner verdict); learner still awaits verdict.**
**READ THIS FIRST after compaction; then the entries below + `CONSOLIDATION_PHASE_LOG.md`.**
✅ **INTEGRATED `dimensional_phase_diagram_audit_of_the_current_organs` (EXCELLENT, owner-DONE):** re-verified FIRST-HAND
(`test_dim_phase_diagram.py` 18/18 PASS, positive-control cliff seen). **Dimensionality (N) is NOT a performance lever
anywhere** — register real-task decode FLAT across D=256..8192 (STRUCTURAL @1024; wall = front-end LINKING not capacity),
meaning sparse-EXACT, stores already at N_DIM=8192 (brief's "all at D=1024" premise FALSE on disk). BEYOND the bar: a 4-law
store-family census + the identification of **CODE ORTHOGONALITY as the dominant fidelity axis** (DG decorrelation recovers
0.74→0.98). Two integrity self-corrections carried (synthetic cliff = a known closed form; the "multihop directedness defect"
was a naive-store artifact, the real organ is fine). NO hdlab landed (correct for a negative); proposed follow-on landings
QUEUED (CA3/resonator readout swap ~4× — overlaps p2; orthogonality+precision audit axes + DG-decorrelation pre-store check;
adaptive readout controller). Audit §2b folded; +0.88 cortical-read datapoint ROUTED to
`the_consolidated_cortical_store_is_written_but_never_read`. priority cleared.
🆕 **NEW SOLUTION POSTED — `the_reader_cannot_choose_what_to_read_next` (foraging, SOLVED, awaits owner_verdict — I RECOMMEND
DONE).** Strong + honest: it REFUTES the brief's MVT/learning-progress forager on disk (that exact mechanism was already built
+ REFUTED for the neighbouring problem — LP carries no between-source info) and delivers the BRAIN-faithful winner —
COMPREHENSIBLE INPUT / ZPD (Krashen i+1, Vygotsky): read the source with the most NEW words in mostly-known sentences. Beats
FROZEN 0.0314 AND RANDOM 0.0287 → **0.0813**, register-controlled, CI-sep on 3/3 seeds; info-free twin 0.0150 loses; and it
SELF-REFUTES its own upgrade hypothesis (stricter 0.85/adaptive thresholds STARVE at a 1000-word seed → a rigorous can-fail
negative + a mechanism for why the operating point is competence-dependent). ON DONE: reverify FIRST-HAND
(`test_reading_comprehensible_input.py` 6/6), land the default-off hdlab diff (shelf-as-readable-universe via
`corpus_registry` + comprehensible-input selector COMP_THRESH=0.5 w/ adaptive hook + within-source MVT leave on
grounding-yield); do NOT land the refuted LP selector or a separate EVC-halt.
🎯 **QUEUE (integrate ONLY on `owner_verdict: DONE`): p2 learner (SOLVED, recommend DONE — see the prior entry for the
reverify+land recipe + the SAFETY GATE); p3 foraging (SOLVED, recommend DONE, above); p5 ToM-reeval + p6 transitive = no
solution yet.** ⚠️ The uncommitted `data/capability_registry.jsonl` + untracked `verification/test_*.py` are OTHER
sessions'/solvers' — do NOT commit them.

### 2026-08-28 -- 🧭 **COMPACTION SNAPSHOT: p1 FULLY LANDED + verified; ToM landed; the FACTORIZED MEMORY STORE landed (dense→sparse gap ~closed); the LEARNER solution is IN + recommended DONE (awaits owner verdict); reasoning phase seeded. IDLE, waiting on owner verdicts.**
**READ THIS FIRST after compaction; then `CONSOLIDATION_PHASE_LOG.md` (steps 0-20 + the RESUME STATE at its top) + the entries below.**
🔌 **LANDED this session (all default-off islands, witnessed FIRST-HAND, registered):**
- **p1 scalar-magnitude RULER — FULLY LANDED + real-data verified:** `hdlab/fractional_power_encoding.py` (log-Weber code) +
  `hdlab/scalar_adjective_operation.py` (the ruler) + `hdlab/meaning_operation_router.py` (word-class routing). Reproduces
  the human comparison win on real Warriner data 0.758 (`exp_p1_landed_organs_live_payoff_v1.py`). FOLLOW-ON refinements
  (NOT blocking): `quality_relation` Ch.B linear→FPE-log regrounding + wire dim-select to `semantic_control`.
- **Theory of Mind:** `hdlab/belief_partition.py` (per-agent false-belief, 1.000 on real-English passages). Residual = the
  observation-cue front-end (packaged as p5 `theory_of_mind_residual_is_the_observation_cue_front_end`).
- **FACTORIZED two-system memory store (the p2 proven-ready follow-on — the named dense→sparse fidelity gap, ~CLOSED):**
  `hdlab/graded_temporal_context.py` (GradedTemporalContext + EventSegmentedContext — the "when" + event boundaries) +
  `hdlab/factorized_entity_store.py` (content × context × order + race-to-stop set-return + gist routing); the sparse-DG
  "what" half was ALREADY landed (`hdlab/dg_pattern_separation.py`). REMAINING (follow-on): sparse-DG content backend merge;
  path-integration scaffold; wire the N400 boundary detector → EventSegmentedContext; LitBank-scale validation → REMOTE box.
🎯 **QUEUE (integrate ONLY on `owner_verdict: DONE`): p2 `optimize_and_validate_the_learner_before_it_grows_the_foundation`
= SOLVED, awaits verdict — I RECOMMEND DONE. It is EXCELLENT-caliber + PARTIAL(mixed): dependency-typed (grammar-shaped)
context beats PPMI CI-sep + 2.5x data-efficient (BAR1 WIN); online==batch so the update-rule premise is refuted-by-argument
(BAR2 escape); net-neutral-not-harmful in the full pool (BAR3); the SAFETY GATE fired — growth adds real value BUT corrupts
~1-in-4 previously-correct answers UNIFORMLY → NOT safe to turn on UNCONDITIONAL growth, safe only behind a regression-checked/
versioned-rollback gate. ON DONE: reverify FIRST-HAND (`verify_structured_context_learner.py`), land the dependency-typed
learner + reliability-weighted fusion, KEEP foundation-growth OFF behind the gate. p4 phase-diagram = SOLVED, awaits verdict
(a rigorous NEGATIVE, EXCELLENT, reverified — no hdlab landing, just fold audit; ready). p3 foraging + p5 ToM-reeval + p6
transitive-comparison = no solution yet.**
🧭 **NEXT PHASE = comprehension→REASONING** (p1's comparison is the first glass-box reasoning primitive; the comprehension
baseline is essentially established — the full-3-axis was RE-SCOPED to a low-priority completeness check, dominated by the
broad entity+meaning axes, see LOG STEP 20 REFINEMENT). First reasoning problem PACKAGED (PROPOSED, owner steers):
`transitive_comparison_reasoning_over_the_magnitude_ordering` (p6). **NEXT STRATEGY STEPS (mine): integrate the learner on
DONE; the comparison-in-comprehension measurement (first reasoning-phase reader test); the p1 follow-on refinements. Heavy
runs (full-3-axis, factorized-store LitBank validation) → REMOTE box.** ⚠️ **The uncommitted `data/capability_registry.jsonl`
lines + untracked `verification/test_*.py` are OTHER sessions'/solvers' — NOT this session's; do NOT commit them.**

### 2026-08-28 -- ✅✅ **TWO STRANDED SOLUTIONS INTEGRATED (owner-authorized in-session): THEORY OF MIND (belief-partition organ LANDED) + p1 SCALAR-MAGNITUDE RULER (accepted EXCELLENT; hdlab landing = a careful multi-module port, QUEUED)**
Owner clarified the stranded-solution handling: ToM was the one that "missed the verdict" → integrate; p1 was owner-DONE →
integrate; the phase-diagram is STILL RUNNING → left alone (reverted my premature edits). Both re-verified FIRST-HAND.
**✅ THEORY OF MIND INTEGRATED (EXCELLENT):** `theory_of_mind_is_proven_only_in_a_synthetic_microworld` (reverify 2/2 PASS).
Per-agent belief partition (an agent who did NOT observe keeps the STALE binding = false belief) on the substrate's OWN
organs: belief-acc **1.000** on 26 real-English false-belief passages, CI-sep over shared-reality 0.357 (leaks → fails
false-belief), always-initial 0.643, twin losing; reality intact; interference-robust. 🔌 **LANDED `hdlab/belief_partition.py`**
(`BeliefPartition` + `believed_location` gate; witness PASS; registered `belief_partition_v1`, default-off). Honest scope:
authored real-English gold (mechanism demo, not corpus-general), 1.000 uses ORACLE observation (end-to-end 0.821), first-order
only; residual = the OBSERVATION-CUE front-end. `state_of_mind.py` is coref (mislabelled), NOT ToM. **📦 OWNER MUSING: ToM may
want a DEDICATED solver re-eval (strengthen: corpus-mined gold + the observation-cue front-end) — PACKAGE as a follow-on
AFTER p1 (owner "P1 first").**
**✅ p1 SCALAR-MAGNITUDE RULER ACCEPTED (EXCELLENT, owner-DONE):** `build_the_composed_scalar_magnitude_meaning_channel`
(reverify ALL PASS). The composed magnitude "ruler" + word-class operation-ROUTER beats every sub-op + the incumbent cosine
CI-sep, router beats gloss-only + magnitude-only with EXACT N/V no-regression, FPE-log preserves Weber; as a COMPARISON
system it beats the incumbent CLEANLY (0.758 vs 0.552, distance effect +0.340, congruity AUC 1.000 vs incumbent 0.215 —
the cosine INVERTS). Solver CORRECTED the brief: pole+degree = ONE oriented place code (not three ops). 🔌 **hdlab LANDING SUBSTANTIVELY DONE 2026-08-28 (the two HEADLINE deliverables + the FPE foundation landed + witnessed,
default-off islands): `hdlab/fractional_power_encoding.py` (log-Weber code) + `hdlab/scalar_adjective_operation.py` (the
magnitude RULER) + `hdlab/meaning_operation_router.py` (word-class routing). All three registered; witnesses PASS first-hand.
→ THE LEARNER'S SUBSTRATE-VALIDATION DEPENDENCY (conceptual_meaning + scalar_adjective_operation + the router) IS SATISFIED —
"✅ p1 landed" SIGNAL SENT TO OWNER.** FOLLOW-ON refinements (NOT in the learner's path, tracked): `quality_relation` Ch.B
linear→FPE-log (needs regrounding its lexicon with the grounded-degree data) + wire dim-select to `semantic_control`.
Both AUDIT UPDATEs folded (§2b). 🎯 **QUEUE: p1 landed (2 refinements follow-on); learner (p2, substrate-validation NOW
UNBLOCKED + rule-optimization already runnable); foraging (p3); phase-diagram (p4, STILL RUNNING). NEXT STRATEGY (mine):
the 2 p1 follow-on refinements; the factorized-store + N400 + full 3-axis remain (heavy → remote).**

### 2026-08-27 -- 🧭 **NEXT PHASE FRAMED + THE LEARNER PACKAGED (owner-directed): comprehension→REASONING; and the learn-from-reading learner is PROVEN-but-OFF → OPTIMIZE + safety-validate it as a solver problem BEFORE it grows the foundation, p1 LANDED FIRST**
Owner steer this session: (1) NEXT PHASE = the reader crosses from COMPREHENSION to REASONING — p1's magnitude/COMPARISON op
is the first glass-box reasoning primitive; the meaning system becomes multi-operation + demand-routed (the pattern the whole
substrate converged on). (2) **LEARNING FROM READING is PROVEN-worth-continuing (Q116 owner-DONE: a PPMI-SVD arm over 38M
simplewiki tokens beats floors 15-40x, STILL CLIMBING at the corpus ceiling; fuses with the hub on WordSim) BUT is currently
OFF — every reading/learning organ is an ISLAND; the foundation is STATIC offline-built (the pivot design). We are NOT
learning at runtime.** (3) Owner: "set the learner as a problem to OPTIMIZE before you turn it on… validate the shit out of it
with the UPDATED substrate before it grows the foundation." **📦 PACKAGED `optimize_and_validate_the_learner_before_it_grows_the_foundation`
(priority 2):** beat the PPMI-SVD baseline with a brain-faithful ONLINE PREDICTIVE/Hebbian learner (not batch factorization),
NET-IMPROVE the updated substrate (fused/demand-routed with conceptual_meaning + p1's ruler, no regression, dissociations
preserved), and a HARD SAFETY GATE (growing the foundation must improve downstream comprehension, info-free growth control
not helping, corruption-risk quantified) — a rigorous "don't turn it on yet" is a PASS. **🔗 HARD DEPENDENCY: p1 must be
LANDED first** (validate the learner against the COMPLETE meaning system, not a stale target) — the rule-optimization half is
p1-independent and can start now; the substrate-validation half waits for p1. 🎯 **QUEUE: p1 (SOLVED, awaits owner_verdict —
integrate FIRST), learner (p2, gated on p1), phase-diagram (p4). NEXT STRATEGY (mine): integrate p1 when owner-DONE → then
the learner solver runs; the FACTORIZED two-system store + N400 segmentation + full 3-axis remain, heavy runs → remote box.**

### 2026-08-27 -- ✅ **ENTITY-STORE FAN FIX INTEGRATED (owner-DONE, EXCELLENT) -- the p2 submission CORRECTED the brief (the fan is an ADDRESSING COLLISION, not superposition blur) then built the maximally faithful FACTORIZED two-system store; hdlab cheap core LANDED (SET-RETURN decode)**
`the_entity_store_is_a_dense_bundle_that_fans` (p2). Re-verified FIRST-HAND: **core witness 21/21 + frontier witness 26/26**
(ran both myself). One of the strongest submissions. **Diagnosis:** the measured LitBank fan (decode 0.945@few->0.657@many,
slope 0.288) is an ADDRESSING COLLISION + argmax readout, NOT superposition blur -- unique-(entity,slot) decodes at 1.0000
at EVERY load level; top-m recovers the co-slot set at ~1.0; 22.7% of (entity,sentence) keys hold >1 verb. **Fix
(brain-faithful, CI-sep):** finer conjunctive temporal key (TCM drift) + SET-RETURN read (CA3 reactivation) flatten slope
0.288->~0.000, info-free order twin loses (1.0 vs 0.502). **Frontier (built + real-data validated):** the maximally
faithful store is FACTORIZED (sparse DG exact-recall x graded temporal context, read separately, bound only at storage) ->
BOTH fan-flat 0.001 AND contiguity 0.585 on real LitBank where a single key trades them; matches Bausch 2026 human
single-unit data + TEM. Sparse DG relocated to its true home (high-load exact-recall capacity: holds 1.0 to N=800 where the
organ falls to 0.78; residual similarity-gated 3.5x). Honest deflations self-flagged (retrievability not comprehension;
set-return ~= pointer on this data; kWTA partial-cue deficit unfixed). 🔌 **hdlab LANDED (cheap proven core, Q111):
`cleanup_set` + `decode_set` (SET-return) on BOTH register backends (`situation_model_accumulate` +
`situation_model_multibank`); additive, decode() byte-unchanged; witness `test_situation_setreturn_organ.py` PASS both
backends; registered `situation_register_setreturn_v1`.** 📦 **QUEUED proven-ready follow-on hdlab landings (larger, NOT
this commit): finer conjunctive temporal key; the FACTORIZED two-system store (sparse DG + graded context); schema/gist;
CMR race-to-stop; path-integration + local-rule-SR scaffolds -- heavy LitBank-scale validations route to the remote GPU
box.** Review EXCELLENT + SOLVER REVIEW; priority cleared; AUDIT UPDATE folded (§2b, corrects the fan-effect entry).
🎯 **CONSOLIDATION QUEUE: p2 + p3 DONE. REMAINING — p1 `build_the_composed_scalar_magnitude_meaning_channel` (SOLVED,
awaits owner_verdict), p4 `dimensional_phase_diagram_audit_of_the_current_organs` (no solution yet). NEXT strategy steps
(mine): the N400 PE event-segmentation wiring + the factorized-store follow-on landing + the FULL 3-axis end-to-end (now
with the convergent-cue read + set-return decode + p2's store direction). The convergent-cue gain is predicted to COMPOUND
with the sparse store (recalibrate w).**

### 2026-08-27 -- ✅ **CONVERGENT-CUE COMPOSITION INTEGRATED (owner-DONE, EXCELLENT) -- the p3 handoff came back SOLVED: the brain's retrieval rule (log-Bayes PRODUCT of the episodic + meaning posteriors) BEATS the strongest floor, fused is refuted, the double dissociation holds -> hdlab organ LANDED**
`compose_the_reader_by_convergent_cue_not_independent_conjunction` (the p3 I packaged + handed off THIS session; owner
finalized it fast). Re-verified scaffold-free FIRST-HAND (`test_convergent_cue_composed_reader.py` 7/7 PASS). The
convergent-cue read `argmax_c [log softmax(epi/tau_e) + w·log softmax(sem/tau_s)]` (CA3 pattern completion +
reliability-weighted cue combination) **beats the STRONGEST floor meaning-solo 0.6998 -> 0.7438 (+0.044 CI-sep
[0.030,0.058])** held-out n=3681. Decisive control: the shuffled-EPISODIC twin FALLS BELOW meaning-solo -> the win needs
REAL episodic evidence = genuine convergence (not meaning relabeled); fused one-pool loses (+0.384) + kills the
dissociation; double dissociation preserved; lift localised (rescues 20.5% of meaning-solo-WRONG). Brain-faithful: product
rule PINNED, calibrated `w` honestly OUR-INVENTION. **The solver CAUGHT my brief's straw floor (0.119, below either solo)
and re-aimed correctly at meaning-solo** -- upheld the measurement bar better than my brief. Rule AT ceiling (0.744 vs
oracle 0.750); residual = the dense store -> **gain predicted to COMPOUND with p2's sparse store**. 🔌 **hdlab LANDED
(Q111): `hdlab/convergent_cue_reader.py` (`convergent_pick`; ports pick_convergent_rw + tau calibration verbatim;
DEFAULT_W=12 dense-store calibration; graceful degradation = the dissociation); witness `test_convergent_cue_reader_organ.py`
PASS first-hand; registered `convergent_cue_reader_v1` (BUILT/ISLAND, default-safe).** Review EXCELLENT + SOLVER REVIEW;
priority cleared; AUDIT UPDATE folded (§2b). 🎯 **CONSOLIDATION QUEUE: p3 DONE. REMAINING in flight — p1
`build_the_composed_scalar_magnitude_meaning_channel` (SOLVED, awaits owner_verdict), p2 `the_entity_store_is_a_dense_bundle_that_fans`
(SOLVED, awaits owner_verdict), p4 `dimensional_phase_diagram_audit_of_the_current_organs` (owner-surfaced, no solution yet).
Integrate p1/p2 ONLY on owner_verdict: DONE. NEXT strategy step (mine, deferred behind p2): wire the N400 PE event-segmentation
into the live register; then the FULL 3-axis end-to-end with the convergent-cue read + p2's store.**

### 2026-08-27 -- 🧩🧠 **CONSOLIDATION STEPS 17-19: front-end WIRED + measured; the ENTITY×MEANING axes COMPOSE end-to-end (both load-bearing); a brain-foundationality drill on the COMPOSITION found the combination-rule fidelity gap and HANDED IT OFF as a solver problem**
Three focused strategy steps this session (all committed, HEAD 5152ee15e; full ledger `notes/CONSOLIDATION_PHASE_LOG.md`
STEPS 17-19). **STEP 17 — wired the landed `graded_role_assigner` into the composed front-end + measured OFF-vs-ON
leak-free** (held-out n=4078): overall 0.739->0.751 (+0.011 CI-sep), hard pre-verbal slice 0.576->0.600 (+0.024),
canonical preserved, twin losing — the LANDED organ reproduces the solver's held-out lift (baked static validities deliver).
**STEP 18 — first COMPOSITION of two landed organs on ONE cross-sentence task** (`exp_composed_reader_entity_meaning_paraphrase_v1.py`;
answer a PARAPHRASED who-did-what about a PRONOUN-LINKED entity — needs entity-binding AND meaning-recognition): FULL 0.119
vs ENTITY_OFF 0.034 (+0.085) vs MEANING_OFF 0.000 (+0.119) vs twin 0.066 (+0.053), all CI-sep -> **BOTH axes load-bearing;
neither inert**; FULL ≈ meaning-solo 0.700 × entity-solo 0.167 (composes ~independently). **STEP 19 — brain-foundationality
drill on the WIRING** (owner "ensure brain foundational"): separate-pools is EVIDENCE-PINNED (double dissociation: semantic
dementia vs hippocampal amnesia) ✅, but the strict INDEPENDENT AND is only a late-merge decision — the faithful RETRIEVAL
mechanism is CLS CONVERGENT-CUE pattern completion (meaning cue gives TOP-DOWN support to the entity read), which should
BEAT the independent product. **HANDED OFF (owner 08-27 "handoff significant problems to the solvers"):
`compose_the_reader_by_convergent_cue_not_independent_conjunction` (p3) — READ-side counterpart of p2's store fix; baseline
to beat 0.119; must PRESERVE the double dissociation.** AUDIT UPDATE folded (§2b). 🎯 **CONSOLIDATION STATE: front-end axis
DONE (landed+wired); entity+meaning shown to COMPOSE. 4 solver problems in flight, THREE now SOLVED-awaiting-owner_verdict
(integration imminent — LEAVE ALONE until owner-DONE): p1 `build_the_composed_scalar_magnitude_meaning_channel` (SOLVED),
p2 `the_entity_store_is_a_dense_bundle_that_fans` (SOLVED), p3 `compose_the_reader_by_convergent_cue_not_independent_conjunction`
(SOLVED); p4 `dimensional_phase_diagram_audit_of_the_current_organs` (owner-surfaced dimensionality audit, no solution yet).
Integrate each ONLY on owner_verdict: DONE. 🔌 **NEXT STRATEGY STEP (mine, Q111, DEFERRED behind p2/p3 to avoid a register
moving-target): wire+measure the BUILT-but-ISLAND `n400_coherence_monitor` (prediction-error EVENT-SEGMENTATION = the
"when to write" the situation register is missing) into the live register OFF-vs-ON.** The FULL 3-axis end-to-end + the
p2/p3-refined re-run remain (all gated on the imminent integrations).**

### 2026-08-27 -- ✅ **MEANING OPERATION-ROUTING INTEGRATED (owner-DONE, EXCELLENT/SOLVED) -- 2nd of 3 parallel solvers: meaning-similarity is OPERATION-SPECIFIC per word class; the adjective SIGNED-MAGNITUDE op clears CI-separation AT POWER on an independent human gold; the magnitude CODE is FPE(log degree), validated to 240k human trials**
`the_meaning_read_out_is_one_operation_where_the_brain_has_three` (parallel solver p3). Re-verified scaffold-free
FIRST-HAND (`verify_perclass_meaning_operations.py` ALL CHECKS PASS). The adjective signed-magnitude op (GloVe projection
onto a bipolar axis ANCHORED by the explicit WordNet antonym relation) recovers human magnitude CI-separated over BOTH
the incumbent conceptual cosine AND the random-axis twin on an INDEPENDENT non-WordNet gold (Warriner VAD + Brysbaert,
n~3600-5300 -- the n=111 power wall RESOLVED): **valence 0.724 vs incumbent 0.165 (+0.559 CI-sep)**, Moyer distance effect
present. **REFINES the brief: the cosine is wrong for adjectives ONLY** (verbs win with the gloss). Exceptional depth
(probes A-H, all controlled): opposition RELATIONAL not geometric; ATOM single-axis REFUTED; perceptual grounding doubles
concreteness; intensity is MARKEDNESS not geometry; the magnitude CODE is FPE(log degree) in FHRR (log PINNED by Laughlin
efficient coding), **VALIDATED against 240k human number-comparison trials** (Weber kernel predicts RT rho 0.96). Self-caught
a signed-rho bug; honest negatives (VerbNet does not beat the gloss). AUDIT UPDATE folded (§2b). 🔌 **NO hdlab landed;
EARNED proven-ready:** `scalar_adjective_operation` + operation-routing-by-word-class + FPE-log upgrade of quality_relation
Ch.B. Review EXCELLENT + SOLVER REVIEW; priority cleared. 📦 **NO successor packaged.**
🎯 **CONSOLIDATION: 2 of 3 parallel solvers integrated (p1 front-end + p3 meaning). p2 (entity store) submitted, AWAITS
owner_verdict — integrate when owner-DONE.** 🔌 **`graded_role_assigner` (p1) is LANDED (commit 540cdb8c1, witness PASS,
default-off ISLAND).** **RESUME-HERE (read `notes/CONSOLIDATION_PHASE_LOG.md` steps 0-16 for the full durable ledger):
PENDING = (1) ✅ PACKAGED as a PROBLEM (owner 08-27): `build_the_composed_scalar_magnitude_meaning_channel` (p1) — a solver
composes the p3-proven magnitude sub-ops into one deployable channel + router + FPE-log Ch.B upgrade; INTEGRATE + LAND when
owner-DONE; (2) wire the landed
front-end/meaning organs into resolve_patient / the meaning read-out (flagged, live-measured — the composition step); (3)
the full whole-reader end-to-end measurement (harness `exp_composed_reader_litbank_full_v1.py` ready). All 3 organ axes
individually validated in comprehension (front-end 0.74 vs 0.52; entity 0.18 vs 0.06; meaning paraphrase 0.75 vs 0.01).**

### 2026-08-27 -- ✅ **FRONT-END NON-CANONICAL FIX INTEGRATED (owner-DONE, EXCELLENT/SOLVED) -- 1st of 3 parallel solvers: a ROUTED graded cue-competition (Competition Model) beats the front-end on non-canonical structure; the residual is UPSTREAM (meaning-supply + coref + incremental parser), NOT a cue defect**
`the_front_end_mishandles_non_canonical_argument_structure` (parallel solver p1). Re-verified scaffold-free FIRST-HAND
(`test_noncanonical_role_assigner.py` 6/6 PASS, held-out n=4078). A HYBRID graded cue-competition assigner (MacWhinney/Bates
Competition Model over the landed `graded_competition`; learned validities) beats the composed front-end on the
non-canonical slice **0.6000 vs 0.5758 (+0.0242 CI-sep)**, net-positive overall (+0.0113 CI-sep), CANONICAL PRESERVED,
shuffled-validity twin LOSING, seed-robust. **KEY: a FLAT integrator is NET-NEGATIVE -> the faithful Competition Model
ROUTES (word-order stays high-validity, overridden only on marked cues), does NOT replace the cascade.** Deep drills
(rigorous, controlled): the 408 bucket is 95.6% REACHABLE (mechanism gap, mostly relativizer-less reduced relatives);
verb-subcat SUPPLY bound CI-proven then BROKEN with WordNet frames (30->99%); the incremental-parser+reanalysis ARCHITECTURE
route is a rigorous root-caused NEGATIVE (bottleneck = meaning-rep quality of the reanalysis trigger + parser sophistication
+ unwired coref). The solver WITHDREW its own '~7pt coref' overclaim (anti-gaming twin). Honest MODEST magnitude
(slice 0.576->0.600, overall 0.739->0.751). AUDIT UPDATE folded (§2b; front-end "converged" scoped to canonical only).
🔌 **NO hdlab landed; EARNED proven-ready:** a `graded_role_assigner` HYBRID route inside `resolve_patient` (robust graded
voice + relativizer-less gap + graded competition + offline validities; confident routes byte-identical; default-off).
Review EXCELLENT + SOLVER REVIEW; priority cleared. 📦 **NO successor packaged** (the residual routes to EXISTING lines:
meaning-supply, coref, incremental-parser).
🎯 **CONSOLIDATION: p1 integrated -> the improved front-end plugs into the full-reader harness
(`exp_composed_reader_litbank_full_v1.py` SEAM). NEXT: land the `graded_role_assigner` (focused build) + run the FULL
whole-reader measurement with the improved front-end. p2 (entity store) + p3 (meaning op-routing) submitted, AWAIT owner_verdict.**

### 2026-08-27 -- 🎯✅ **CONCEPTUAL-MEANING CHANNEL INTEGRATED (owner-DONE, EXCELLENT/SOLVED) -- the missing ATL conceptual/definitional hub is BUILT + PROVEN (two systems DOUBLE-DISSOCIATE); AND ALL 3 IN-FLIGHT ARE NOW INTEGRATED -> THE CONSOLIDATION TRIGGER IS MET, THE CONSOLIDATION PHASE IS ACTIVE**
`the_reader_has_no_conceptual_meaning_channel` (p3, the LAST in-flight). Re-verified scaffold-free FIRST-HAND
(`test_conceptual_meaning_channel.py` PASS -- ran it myself). **Bar MET:** the missing ATL amodal CONCEPTUAL/definitional
hub is BUILT as a glass-box static asset (WordNet gloss+genus, distinctive-feature IDF, cosine; NO learning/LLM) and beats
a STEELMANNED associative competitor (GloVe-300, not the reader's weak 0.04 system) on human meaning-IDENTITY off-WordNet:
SimLex 0.5210 vs 0.3705 (+0.1505 CI-sep), SimVerb +0.2788; shuffled-gloss twin LOSES; IDF beats unweighted overlap CI-sep.
**DOUBLE DISSOCIATION** (conceptual->similarity, associative->relatedness; crossover +0.197 CI-sep; GloVe wins WordSim
relatedness) -> two systems each winning its own axis. Routing sub-clause = a RECONCILING NEGATIVE (fusion ties/beats
routing for graded rating; routing's home is context selection = the semantic-control organ). Fidelity boundary: ATL
covariance-distillation ties sparse IDF -> distinctiveness is SUPPLY-DEPENDENT (dense->whiten, sparse->IDF). DEEPEST
finding (directional, honestly not gating SOLVED): meaning-similarity is OPERATION-SPECIFIC per word class (one cosine
wrong for adjectives=signed-magnitude, verbs=relational). AUDIT UPDATE folded (§2b + §6/§7). 🔌 **NO hdlab landed; the
conceptual channel + demand-routing + operation-routing QUEUED proven-ready for the consolidation.** Review EXCELLENT +
SOLVER REVIEW; priority cleared. 📦 **NO successor packaged (consolidation policy -- queue drained to zero, by design).**
🎯🎯 **THE 3-PROBLEM TRILOGY IS COMPLETE (all EXCELLENT): parser/role = graded (discrete is the argmax collapse); entity
tracking = attribution-not-prediction + graded binding; meaning = a second ATL conceptual channel. THE CONSOLIDATION
TRIGGER IS MET.** The queue is at ZERO ranked-open (by design). **THE CONSOLIDATION PHASE IS NOW ACTIVE** -- execute
`notes/CONSOLIDATION_PHASE_PLAN.md` (the ordered plan) across subsequent focused rounds: land the queued organs (A/B done; C-J)
in final form, build a ROLE-BALANCED comprehension gold, and measure the composed reader end-to-end (organs OFF-vs-ON, floors +
info-free-twins-must-lose). This is a deliberate MULTI-ROUND build, NOT a heartbeat cram -- one focused step per round.
📋 **RUNNING LOG (compaction-survival, owner-requested): `notes/CONSOLIDATION_PHASE_LOG.md` -- the durable step-by-step ledger
with commit hashes + verification; READ IT to resume mid-phase.** **STEPS 1-5 DONE — ALL ISLAND ORGANS LANDED: graded-competition + ATL conceptual channel + ACT-R salience binder +
INCREMENTAL PARSER + RELCL FILLER-GAP RESOLVER** (`hdlab/graded_competition.py`, `conceptual_meaning.py`,
`salience_binder.py`, `incremental_parser.py`, `relcl_resolver.py`; + pre-phase `predictive_reader.py`,
`semantic_control.py`; witnesses all PASS first-hand; registered `*_v1`; all default-safe islands). BRAIN-FOUNDATIONAL
COHERENCE: the salience binder's graded write REUSES the graded-competition softmax (one divisive-normalization op,
byte-equal); the relcl discrete rule is the noise→0 limit of the same cue-based retrieval. **WIRING brain-foundationality
is a GATE on the composition step** (late-algebraic-MERGE-not-cascade; top-down-meets-bottom-up; one shared graded
currency; separate-pools-never-fuse; discrete=argmax-collapse) — logged in `CONSOLIDATION_PHASE_LOG.md`. **REMAINING rows
(D front-end role-fix, F entity-augment) are WIRING-into-existing-organs done AT the composition step. ✅ THE ROLE-BALANCED
COMPREHENSION GOLD IS BUILT + VERIFIED** (`exp_role_balanced_comprehension_gold_v1.py`; 9446 modern QA-SRL items,
positional-only floor 0.500 vs the McGuffey 0.78 saturation, can-fail PASS; 534 object-relative reversibles as the hard
slice; gold rebuildable-deterministic). **🎯 THE FRONT-END PAYOFF IS MEASURED (STEP 9) -- and a self-checker WALL was drilled + fixed en route.** STEP 8 read a
flat 0.32 (a "wall"); the owner-directed drill ("at a wall, drill to verify we implement correctly") ran an ORACLE-CEILING
probe = 0.49 (impossible if candidates held the answer) -> found a BUG IN MY OWN CHECKER: QA-SRL patient spans are
HALF-OPEN `(start,end)` but were scored as the 2-element SET `{start,end}`. Fix to `range(start,end)`: oracle 0.49->0.97.
**DEFINITIVE (full n=8225, role-balanced fair gold): the composed front-end (voice + word-order + relcl) scores 0.7387
[0.729,0.748], BEATING the positional floor 0.5191 by +0.2118 CI-separated, with the info-free twin 0.296 losing by
+0.43.** -> **the front-end organs EARN THEIR KEEP on a fair modern test where position-guessing = ~0.5.** HONEST:
restricting to incremental candidates slightly HURTS (-0.008; not the lever for single-patient-ID); pre-verbal/reversible
patients 0.582 vs post 0.875 (headroom -> the un-wired LEARNED assigner D). **SCOPE: this is the FRONT-END (who-did-what)
payoff; the FULL composed reader (entity + meaning, CROSS-SENTENCE) is the next measurement. Detail in
`CONSOLIDATION_PHASE_LOG.md` STEP 9.** *Owner discipline for this phase: do the RIGHT things not the easy ones; if things aren't working as
expected, LIBERALLY run brain-foundationality research drills, finer resolution if needed.*

### 2026-08-27 -- ✅ **DISCRETE→GRADED INTEGRATED (owner-DONE, EXCELLENT/SOLVED) -- RESOLVES the substrate-wide "discrete where the brain is graded" deviation: the discrete parser/role organs are the noise→0 argmax COLLAPSE of a graded Bayesian competition, and the distribution's ENTROPY is a shared difficulty currency that beats the shipped binary conflict. 2 of 3 consolidation-gating problems now integrated**
`discrete_where_the_brain_is_graded_in_parsing_and_role_assignment` (p1 of 3 in-flight). Re-verified scaffold-free
FIRST-HAND (`verify_graded_competition_parsing_role.py` ALL CHECKS PASS, live on the real QA-SRL front-end -- suspected my
own checker, ran it). **Bar MET via the AND/OR difficulty-signal clause.** A single graded cue-based competition
(additive-log cue activation → softmax MAINTAINED DISTRIBUTION over candidate role-fillers) IS the pinned Bayesian/FLMP
posterior for discrete cue integration (McClelland 2013 -- a COPIED operation), and the discrete organs are its noise→0
argmax COLLAPSE (graded argmax == the discrete resolver on EVERY item, 0.0[0.0,0.0]). The maintained-distribution ENTROPY
is a valid GOLD-FREE difficulty signal: predicts discrete error +0.384 CI-sep, higher on literature-hard object-extraction
+0.42, info-free twins LOSE (random-settling +0.000, shuffled-validity +0.073), and **it BEATS the substrate's shipped
BINARY route-conflict on REAL QA-SRL (AUC 0.646 vs 0.512, +0.133 CI-sep).** **The ACCURACY clause is a principled
MAP-optimality THEOREM** (graded cannot beat its own argmax on gold accuracy → the value is the DISTRIBUTION/uncertainty,
not the point estimate), NOT a shortfall -- recorded so the audit stops implying a graded accuracy win is available on
English. New deviations logged (dynamics settling-vs-racing UNPINNED; argmax = task-triggered collapse, expose the
distribution); cross-linguistic framing corrected (accuracy-win = German ~50% case, not "freer word order"). AUDIT UPDATE
folded (§1 deviation RESOLVED + §2b + cross-linguistic). 🔌 **NO hdlab landed; QUEUED proven-ready for the consolidation**
(a shared `graded_competition` organ + entropy-as-shared-difficulty-currency feeding N400/write-gating/predictive-reader
surprisal; attachment + role binding kept SEPARATE). Review EXCELLENT + SOLVER REVIEW; priority cleared. 📦 **NO successor
packaged (consolidation policy).**
🎯 **CONSOLIDATION TRIGGER STATUS: 2 of 3 in-flight integrated** (this + entity-tracking). The LAST one,
`the_reader_has_no_conceptual_meaning_channel` (p3), is owner-DONE and integrates NEXT round -- when it lands, the
CONSOLIDATION PHASE fires (`notes/CONSOLIDATION_PHASE_PLAN.md`).

### 2026-08-27 -- ✅ **ENTITY TRACKING COMPOSED END-TO-END INTEGRATED (owner-DONE, EXCELLENT/SOLVED) -- the ENTITY LINE IS CLOSED: correct pronoun linking buys cross-sentence ATTRIBUTION, NOT prediction (a clean dissociation); graded activation-weighted binding is the brain-correct win; 1 of 3 consolidation-gating problems now integrated**
`wire_entity_tracking_end_to_end_on_running_narrative` (p2 of the 3 in-flight) -- a clean WIN + a real dissociation.
Re-verified scaffold-free FIRST-HAND (`test_entity_tracking_end_to_end.py` 7/7 PASS, 183s, on the REAL
`hdlab.situation_model_accumulate` register -- suspected my own checker, ran it). Composing the ACT-R salience binder +
coref threads + the real entity register on LitBank novels: **BAR MET on cross-sentence who-did-what** -- salience-bound
linking 0.1739 beats string-identity 0.0589 CI-sep (pronoun subset +0.115), and the info-free shuffled-link twin LOSES
(ACT-R +0.0731 CI-sep) -> CORRECT binding, not any link, is the source. **DISSOCIATION (decisive the other way):** correct
linking does NOT improve anticipatory prediction -- entity-augment HURTS the gist (-0.219), correct-vs-string-identity
-0.099, even ORACLE -0.131 -> coreference feeds RETRIEVAL, not a predictive prior (neurally supported: reactivation is
PINNED, reinstatement->prediction is untested + here NULL). **DEEPENING WIN:** activation-weighted GRADED binding beats
hard argmax +0.0268 CI-sep (uniform hedging HURTS -> the activation weighting carries it); a temperature sweep is a
divisive-normalization INTERIOR optimum (peak temp~2.0). **FAN EFFECT MEASURED** (oracle decode 0.695->0.608 with
event-count) -> dense->sparse deviation upgraded from suspected to MEASURED. Honest deflations reported against self
(string-identity margin partly structural; ACT-R ~ recency downstream NOT separated; dilution test inconclusive/saturated
proxy). AUDIT UPDATE folded (§2b). 🔌 **NO hdlab landed; QUEUED proven-ready for the consolidation** (graded
activation-weighted softmax pronoun-write; sparse per-entity store = a BUILD proposal). Review EXCELLENT + SOLVER REVIEW;
priority cleared. 📦 **NO successor packaged (consolidation policy -- let the queue drain).**
🎯 **CONSOLIDATION TRIGGER STATUS: 1 of 3 in-flight integrated (this one).** The owner reports ALL 3 problems now
SUBMITTED in the GUI -- but a SOLVED.md is the solver's WIP, NOT a done signal. The other two
(`discrete_where_the_brain_is_graded_in_parsing_and_role_assignment` p1, `the_reader_has_no_conceptual_meaning_channel` p3)
have SOLVED.md but NO `owner_verdict: DONE` yet -> LEFT ALONE, awaiting the owner's verdict. When both reach owner-DONE and
integrate, the CONSOLIDATION PHASE fires (`notes/CONSOLIDATION_PHASE_PLAN.md`).

### 2026-08-27 -- 🧭 **CONSOLIDATION PHASE GREENLIT (owner) + STARTED: the debt-drawdown of proven-but-unwired fixes; semantic-control organ LANDED; PAUSE new organ-problems when the 3 in-flight land**
Owner greenlit the consolidation phase and asked WHEN. **Decided + recorded (owner: "implement your recommendations"):**
**(1) THE TRIGGER = when the 3 in-flight problems integrate** (`discrete_where_the_brain_is_graded...`,
`wire_entity_tracking_end_to_end...`, `the_reader_has_no_conceptual_meaning_channel`). They REFINE the exact organs the
consolidation composes (parser+role-assigner / entity / meaning) — measuring the composed reader before they land would
measure a moving target + force double-landing. **(2) WHEN they land: PAUSE new organ-problem packaging** — do NOT
auto-package a successor for those 3; let the queue DRAIN into the consolidation (land every proven fix in its final
form + build a ROLE-BALANCED comprehension gold + measure the composed reader end-to-end — the payoff number the
agent-saturated McGuffey gold can't give). **(3) MEANWHILE, draw down the debt NOW** with the fixes INDEPENDENT of the
in-flight work (default-off, zero regression). 🔌 **DEBT-DRAWDOWN PROGRESS:** ✅ **semantic-control organ LANDED**
(`hdlab/semantic_control.py::SemanticControl` — gold-blind conflict trigger + graded suppression of the prior;
default-SAFE uncalibrated no-op; witness `test_semantic_control_organ.py` PASS; registered `semantic_control_v1`) — the
in-flight conceptual-meaning solver uses it as its router. **STILL QUEUED for the consolidation (land as rounds free /
at the trigger):** the front-end role-assignment fix (interacts w/ discrete-graded → land at the trigger), the ACT-R
salience binder + entity-augment (interacts w/ entity-end-to-end → at the trigger), the incremental-builder organ
(interacts w/ discrete-graded → at the trigger), the reordered-access meaning read. **📋 THE ORDERED EXECUTION PLAN FOR THIS PHASE IS WRITTEN:
`notes/CONSOLIDATION_PHASE_PLAN.md` (ARMED, not started) — the dependency-ordered landing sequence (A/B landed; C–H gated
on the matching in-flight problem), the end-to-end composition topology, and the measurement design (build a ROLE-BALANCED
gold first; organs OFF-vs-ON; floors + info-free-twins-must-lose). Execute against it when the trigger fires; refine per
each SOLVED at landing.** *Queue: p1 discrete-graded, p2
entity-end-to-end, p3 conceptual-meaning channel — the 3 in-flight; NO successors packaged for them (consolidation policy).*

### 2026-08-27 -- ✅ **ENTITY-BINDING INTEGRATED (owner-DONE, EXCELLENT/SOLVED): binding (who a pronoun is) is GRAMMATICAL-PROMINENCE salience, NOT recency (which is at chance on hard cases) and NOT semantics — completes the BIND half of entity tracking**
`entity_binding_needs_a_modern_pronoun_corpus` — a clean WIN. Re-verified scaffold-free FIRST-HAND (test_gap_pronoun_binding.py
6/6 PASS). On GAP (n=1773 human-labeled same-gender ambiguous pronouns) a grammatical-prominence salience binder resolves
at 0.699, beating string-identity 0.508 (+0.191), recency 0.514 (+0.184), and the shuffled-salience twin (+0.181), all
CI-sep. STRIKING: RECENCY IS AT CHANCE on the hard cases — the cue is GRAMMATICAL PROMINENCE (Centering subject-preference);
binding is structural, NOT semantic (implicit-causality doesn't replicate). Acquired 3 foundation corpora (GAP, IC norms,
LitBank). ACT-R base-level activation unifies the cues (+0.213 over the live formula). AUDIT UPDATE folded (§2b). 🔌 **hdlab
landing EARNED → QUEUED proven-ready** (drop-in ACT-R base-level activation for the pronoun-branch salience()). 📦
**SUCCESSOR packaged** = `wire_entity_tracking_end_to_end_on_running_narrative` (compose bind + predict + coref threads on
LitBank; the downstream marginal value of correct pronoun linking). *(2nd of 2 integrations this round — parser + binding.)*

### 2026-08-27 -- ✅ **INCREMENTAL PARSER INTEGRATED (owner-DONE, EXCELLENT/SOLVED): the batch UD parser is REPLACEABLE — an incremental left-corner builder finds a verb's arguments better (less over-generation); closes the STRUCTURAL half of feed-forward→predictive; surfaces a substrate-wide DISCRETE→GRADED deviation**
`the_argument_parser_is_batch_where_the_brain_is_incremental` — a clean WIN. Re-verified scaffold-free FIRST-HAND
(verify_incremental_argstruct_builder.py PASS). The incremental left-corner builder (eager verb-slot projection, bounded
Now-or-Never, NO arc graph) beats the batch UD parser at candidate-argument identification (+0.0352 F1, n=28,149) via a
precision gain (+0.0998; the batch parser over-generates +1.03 args/predicate); genuinely incremental (prefix-consistent
0.985 vs 0.941, glass-box). HONEST: the win is the EAGER BOUNDED good-enough attachment, NOT prediction/revision (both
~0 on edited prose) — but revision IS brain-faithful (garden-path positive control +0.0852, zero false-fire). Downstream:
the batch parse doesn't earn its place for word-order role assignment; structure helps on passives (+0.0344). Closes the
STRUCTURAL instance of "feed-forward→predictive" (the incremental builder + the predictive reader = two levels of one
predictive front-end; relcl the tail). AUDIT UPDATE folded (§2b + Tier-1 batch-parse-replaceable + Beber structure/role
separation). 🔌 **hdlab landing EARNED → QUEUED proven-ready** (new incremental-builder organ behind a flag as the
candidate source; role assigner unchanged; revision default-OFF). 📦 **SUCCESSOR packaged** =
`discrete_where_the_brain_is_graded_in_parsing_and_role_assignment` (substrate-wide: parsing + role assignment are
discrete where the brain does graded cue-based competition = noise→0 limit of Lewis-Vasishth; test on non-canonical/
ambiguous populations). *(2 new submissions in this round; a 2nd — likely entity-binding — integrated next.)*

### 2026-08-27 -- ✅ **MEANING-CONTEXT INTEGRATED (owner-DONE, EXCELLENT/SOLVED) — BATCH 3 of 3 COMPLETE: CONTEXT overrides the frequency prior on MODERN data (the McGuffey data-limit confirmed; SemCor acquisition VINDICATED), and the missing SEMANTIC-CONTROL organ (LIFG/pMTG conflict trigger + suppression) is BUILT**
`context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark` — the meaning-context question RESOLVED. Re-verified
scaffold-free FIRST-HAND (test_context_override_frequency.py PASS). On held-out SUBORDINATE-congruent SemCor items
(MFS=0 by construction), a structured context-likelihood read recovers the rarer sense at 0.39-0.46, beating chance
(0.17-0.25) + both info-free twins CI-sep, surviving leave-one-DOCUMENT-out. THE MISSING ORGAN BUILT = SEMANTIC CONTROL:
a gold-blind conflict trigger (AUC 0.79-0.81 vs twin 0.58) gating graded suppression of the dominant sense, net-positive
CI-sep, lifting override cases +0.007-0.033. Retired 4 wrong turns (grounded-for-selection, settling=argmax tautology,
diagnosticity, fusion→routing, role-binding). AUDIT UPDATE folded (§2b + §6 semantic-control no-longer-only-THIN + §7).
🔌 **hdlab landing EARNED → QUEUED proven-ready** (default-off reordered-access read + the semantic-control organ; NO
settling/grounding/diagnosticity). 📦 **SUCCESSOR packaged** = `the_reader_has_no_conceptual_meaning_channel` (the #0
next step: the reader is at CHANCE on human meaning-IDENTITY because it only has the associative system — add the ATL
conceptual/definitional hub as a demand-ROUTED 2nd channel, NOT fused).
🎯 **THE 3-PROBLEM BATCH IS COMPLETE (owner submitted all 3; all EXCELLENT):** front-end role assignment RECOVERED
(0.48→0.75, word-order+quote-exclusion); entity-structured situation model (predict-via-content + bind-via-salience);
meaning-context override + semantic control. Queue: p1 argument-parser (batch→incremental, assigned+WIP), p2
entity-binding (assigned+WIP), p8→ the conceptual-meaning channel (NEW). **NEXT-STEPS RECOMMENDATION delivered to owner.**

### 2026-08-27 -- ✅ **ENTITY-STRUCTURED SITUATION MODEL INTEGRATED (owner-DONE, EXCELLENT/SOLVED): AUGMENT the gist with role-conditioned entity memory (beats bag-of-words CI-sep, replicated) — and entity tracking is TWO channels: PREDICT-via-content, BIND-via-salience [BATCH 2 of 3]**
`the_situation_model_tracks_words_not_entities` — a clean WIN. Re-verified scaffold-free FIRST-HAND
(verify_entity_structured_situation_model.py PASS). The entity-structured model (gist + the active entity's
ROLE-CONDITIONED state, retrieved by identity) beats the bag-of-words gist CI-separated (+0.0545, replicated on an
independent split +0.0402); info-free twin (random entity) ACTIVELY HURTS; role-conditioned beats role-blind; naive
REPLACEMENT loses → AUGMENT not replace (brain-faithful). UNIFIES with the retrieval convergence a 4th time (content-
addressable retrieval makes the win larger). SHARP DISSOCIATION: entity PREDICTION uses meaning-memory (content-
addressable); entity BINDING is dominated by SALIENCE/RECENCY (Centering) — keep retrieval for prediction, salience for
the pronoun pick. HONEST small effect (coarse grounded space — the p1 coupling). AUDIT UPDATE folded (§2b). 🔌 **hdlab
landing EARNED → QUEUED proven-ready** (default-off entity-augment of the forward predictor's context; salience-based
binding). 📦 **SUCCESSOR packaged** = `entity_binding_needs_a_modern_pronoun_corpus` (the binding half: does coref/salience
add over string-identity? QA-SRL can't test pronouns). **⏳ BATCH 2 of 3 (p8 meaning-context still coming). NEXT-STEPS
HELD per owner.**

### 2026-08-27 -- ✅ **FRONT-END FIX INTEGRATED (owner-DONE, EXCELLENT/PARTIAL): the wall is RECOVERED 0.48→0.75 (CI-sep over the live baseline); the lever is WORD ORDER + quote-exclusion + a learnable speech-verb class — thematic-fit & animacy REFUTED — but it's majority-floor-bound on the agent-saturated gold [BATCH 1 of 3; next-steps held per owner]**
`the_live_front_end_mislabels_who_did_what_to_whom` — the Branch-B top-priority problem, delivered. Re-verified
scaffold-free FIRST-HAND (6/6 PASS). The fair brain-faithful assigner (core-mention + QUOTE EXCLUSION + speech-verb/
quotative class + the organ's perceptron over selected mentions) beats the live positional baseline CI-separated (0.483
→ 0.747; role-balanced macro 0.191 > majority 0.125). **REFUTES two brief premises:** naive organ wiring is WORSE (0.385);
thematic-fit is NOT the fix — **WORD ORDER dominates English role assignment** (QA-SRL two-animate 0.918 where animacy is
chance; MacWhinney/Bates PINNED). 4 lit-VET'd deepening passes, self-corrected (thematic-fit = real-but-low-validity,
Dowty/Cai; speech-verb class brain-faithfully LEARNABLE from quote co-occurrence, beats a proper null; normalized-recurrence
> perceptron at equal accuracy). **PARTIAL:** ties (not clears) the 78%-agent majority floor on McGuffey plain accuracy —
the clean win is role-balanced + modern QA-SRL (0.93 vs 0.50), pending a role-balanced gold. CONVERGED for natural-corpus
role labeling. AUDIT UPDATE folded (§2b + thematic-role Tier-1). 🔌 **hdlab landing EARNED → QUEUED proven-ready** (default-off
quote-exclusion + speech-verb + core-mention wiring; NO thematic-fit — a multi-part live wiring = focused deliberate build).
📦 **SUCCESSOR packaged** = `the_argument_parser_is_batch_where_the_brain_is_incremental` (the proximity audit's #1 remaining
front-end gap: a batch UD parser vs incremental/predictive structure). **⏳ BATCH 1 of 3 (owner submitting all 3; p2
entity-tracking already in, p8 meaning-context coming). NEXT-STEPS RECOMMENDATION HELD until all 3 integrated, per owner.**

### 2026-08-26 -- 🧭✅ **p1 WIRE-AND-MEASURE INTEGRATED (owner-DONE, EXCELLENT/PARTIAL) -- THE DECISIVE RESULT: the composed organs FAIL end-to-end but WORK on clean inputs → the FRONT-END is the binding constraint (Branch B fired). FHRR CONFIRMED faithful. The fix is an EXISTING islanded learned organ.**
The phase-defining measurement, delivered as a rigorous, well-attributed NEGATIVE (= a full PASS per the bar).
Re-verified scaffold-free FIRST-HAND (`test_wire_organs_endtoend.py`, 9/9 PASS). Composed 3 validated organs into a real
McGuffey entity-role reading task, organs OFF vs ON, identical inputs. **End-to-end through the LIVE front-end: 0.483
[0.410,0.556] — BELOW the trivial majority floor 0.781.** But on CLEAN/oracle inputs the SAME organs hit event 1.000 /
role 0.983, beating the majority floor + the exact-key baseline CI-separated (twin loses) — **the oracle-vs-live contrast
LOCALISES the wall to the FRONT-END; the organs are not broken.** Errors are MISASSIGNMENT-dominant (role 86 > entity 50
> miss 30; 104 OUT-OF-SCOPE roles). **Stage 4 PROVED the lever:** a brain-faithful verb-argument role assigner lifts
end-to-end 0.483→0.736 CI-sep (biggest error = quotative postverbal speaker). **TWO caught+RETRACTED overreaches** →
Stage 7 clean instrument: content-addressable MEANING retrieval DOES recover paraphrase cues (0.528 CI-sep vs count
0.217) — REAL but PARTIAL. Composition = late algebraic MERGE (Norris), not a cascade. **🔒 FHRR CONFIRMED FAITHFUL**
(SEM/Franklin 2020 = HRR+bundling+CLS = our machinery) → keep it; the audit's "binding op unpinned→invention" framing
CORRECTED; store-organization (sparse/indexed) + case-frame content are the FHRR-compatible gaps. 5 AUDIT UPDATEs folded
(§2b + §5 binding correction + §1 front-end-is-the-wall). **🔌 NO hdlab landed** (the decision-shaping negative: do NOT
wire the swamped organs as a comprehension lift). Review EXCELLENT + SOLVER REVIEW; priority cleared.
🧭 **BRANCH B FIRED (`NEXT_STAGE_after_wire_and_measure.md`) — THE NEXT STAGE IS THE FRONT-END.**
📦 **PACKAGED (Branch B execution + restore the ≥3 floor) — NEW p1 `the_live_front_end_mislabels_who_did_what_to_whom`:**
the front-end is the measured wall. **KEY (WIRE-DON'T-ISLAND): the learned organ ALREADY EXISTS** —
`hdlab/thematic_role_labeler.py` (learned Competition-Model role labeler, richer roles incl. EXPERIENCER/RECIPIENT/GOAL
for the 104 out-of-scope, 228 verb frames, islanded since 08-10, ZERO live wirings; its revalidation HARD_FAILED on
modern prose as animacy-dominant). So the problem is **WIRE + MEASURE it into the live reader** (graded constraint-
satisfaction over its animacy-dominance; compose the integrated predictive-reader verb-selectional-preference + the relcl
filler-gap resolver for the two-animate residual), NOT build a new extractor. *Queue: p1 front-end (NEW, the wall) = TOP;
p2 entity-tracking (downstream of the front-end); p8 meaning-context (data-ready, lowest). Proven-ready hdlab landing
PENDING: the forward-prediction organ. p1-wire-and-measure cleared (integrated).*
⏳ **NOTE:** `theory_of_mind_is_proven_only_in_a_synthetic_microworld` was submitted alongside but is NOT owner-DONE (no
OWNER_NOTES) — WIP, left alone; integrate only on an explicit owner_verdict.
🔌 **HDLAB LANDING DONE (heartbeat, WIRE-DON'T-ISLAND): the forward-prediction organ is LANDED** —
`hdlab/predictive_reader.py::PredictiveReader` (`fit(triples)` → `predict`/`surprisal`/`precision`; reuses the validated
`build_centroids` + `-log P` math over `grounded_similarity.grounded_vector`), DEFAULT-SAFE/off-path. Witness
`verification/test_predictive_reader_organ.py` PASS (self-contained construction proof over the REAL grounded space:
predictive surprisal 0.502 << wrong-verb twin 1.851; acc@1 0.923 vs chance 0.333; precision tight 0.985 > diffuse 0.678).
Registered `predictive_reader_v1` (WIRE_CANDIDATE, ISLAND). **Directly serves the top-priority front-end problem** — it
supplies the verb→argument SELECTIONAL PREFERENCE for the two-animate who-did-what cases. No longer "pending". MEASURE on
the live reader before any capability claim.

### 2026-08-26 -- ✅ **p2 predictive-reader INTEGRATED (owner-DONE, EXCELLENT/SOLVED): the reader's missing FORWARD-PREDICTION loop is BUILT -- the verb pre-activates its argument's grounded features, surprisal is a real difficulty signal, and it UNIFIES with relcl (flags reversible cases for syntax)**
The #1 architecture-fidelity gap (feed-forward → predictive) closed. Re-verified scaffold-free FIRST-HAND
(`verify_predictive_reader.py`, 8/8 PASS). BOTH bar routes met on held-out REAL QA-SRL (modern text): the verb (+role)
pre-activates the expected argument's GROUNDED features (Altmann-Kamide/McRae), −log P softmax surprisal beats REACTIVE
+0.199 and an info-free WRONG-VERB twin +0.095 (pseudo-disambig 0.589 vs twin 0.514 AT CHANCE); surprisal is a valid
graded difficulty signal (Spearman 0.239 vs distributional thematic-fit; reversibility AUC 0.619). **THE FREQUENCY
CONFOUND decisively excluded** (frequency-matched distractors + train-only base rates + a twin with IDENTICAL frequency
structure at chance). Glass-box (grounded features + verb key only). Five literature drills; PRECISION-WEIGHTING built
(Friston); the full CROSS-SENTENCE DISCOURSE hierarchy composing the REAL `n400_coherence_monitor` across reconstructed
documents BUILT + WINS (+0.088, twin HURTS). **HONEST MODEST size** — ceiling'd by the 12-dim grounded space (the p1
representation-quality coupling: the MACHINERY is correct now, the PAYOFF scales with representation). **THE UNIFICATION:**
one forward predictor gives BOTH an anticipation win on IRREVERSIBLE role assignment AND a "hand-to-syntax" flag on
REVERSIBLE cases — the exact regime relcl exists for; the two compose (surprisal feeds the relcl route-conflict). LOCUS-
faithful (ATL + angular gyrus). 🔌 **NO hdlab landed, but a landing is EARNED + QUEUED (proven-ready deliberate):** BUILD
the forward-prediction organ — a verb×role → grounded-centroid table (offline-built static asset) + −log P surprisal + a
per-verb PRECISION scalar; default-off; wire surprisal ONCE as shared difficulty infra (relcl route-conflict/write-gating/
N400 confidence). A focused build (the offline table), NOT a heartbeat-cram → the next deliberate hdlab landing. AUDIT
UPDATEs folded (§2b new entry; Tier-5 forward-half-built + the forward predictor + N400 monitor = two levels of one
hierarchy; ATL/AG locus; relcl cross-link; precision PINNED-and-built). Review EXCELLENT + SOLVER REVIEW; priority cleared.
🧭 **NEXT-STAGE NOTE:** this makes **branch B's key organ ready** (`notes/NEXT_STAGE_after_wire_and_measure.md`) — if p1's
attribution shows the front-end is the wall, the predictive reader is already built to lead that branch.
📦 **PACKAGED (restore the ≥3-open floor after p2 cleared) — NEW p2 `the_situation_model_tracks_words_not_entities`:**
the solver's NAMED next foundational build — the running situation-model gist is a bag-of-content-words mean, ENTITY-BLIND;
wire the coreference organ + content-addressable retrieval so mentions bind to persistent ENTITIES and the top-down
prediction is entity-structured. On the convergence (coref + situation model + forward predictor + retrieval), ranked
below p1. *Queue: p1 wire-and-measure (retrieval-first, WIP in) = TOP; p2 entity-tracking (new, ready); p8 meaning-context
(data-ready, lowest). Proven-ready hdlab landing PENDING: the forward-prediction organ. p2-predictive + p7 cleared.*

### 2026-08-26 -- ✅ **p7 relcl parser INTEGRATED (owner-DONE, EXCELLENT/SOLVED): a SPECIALISED filler-gap circuit (route AROUND the HARMFUL arc parser) solves reversible role assignment -- and it UNIFIES with p3 retrieval (filler-gap role binding IS cue-based content-addressable retrieval)**
The front-end fix, delivered -- and it lands on the retrieval-first cluster. Re-verified scaffold-free FIRST-HAND
(`verify_relcl_incremental_fillergap_parser.py`, 8/8 PASS). A brain-faithful incremental filler-gap resolver (active-filler
over UPOS + closed-class relativizers, NO dependency graph) beats the two-line floor CI-separated on a powered BALANCED
held-out reversible set (INC 0.9533 vs 0.4994 at n=4800, ties the oracle 0.9981); **the general `arc_parser` is
MEASURABLY HARMFUL (0.198 < info-free twin 0.305), route AROUND it.** Non-degenerate (PICK_FRONTED control), glass-box
guarded (takes no `heads` arg, invariant to permuting arc heads), gate no-leak + net-positive. **HONEST real-text bound:
fires on 0.75% of QA-SRL, aggregate +0.001** -- the value is CORRECTNESS on the rare hard sentences a situation model
needs, not a headline. **THE DEEP RESULT (two literature drills):** the discrete rule is the noise→0 COMPETENCE LIMIT of
GRADED ADDITIVE CUE-BASED CONTENT-ADDRESSABLE RETRIEVAL (= the p3 operation) -- built + measured, it reproduces
similarity-interference (+0.10 CI-sep) over the substrate's REAL grounded vectors + the reversibility/locality effects
the discrete rule cannot; center-embedding collapse (0.048) is the RETRIEVAL half -> p3, not a parser upgrade. **So
filler-gap role binding UNIFIES with E1/E2/E3** (computational HOMOLOGY, gated on amnesia counter-evidence, NOT neural
identity). Corrects the neural localisation (reversible role binding → pMTG, NOT BA44-movement; Beber 2025). 🔌 **NO new
hdlab organ:** the resolver + the route-conflict UPGRADE (two always-on competing scorers + a conflict term, NOT if/else
-- the solver's own architecture-fidelity finding) fold into p1's retrieval-first composition (front-end the retrieval
sits on), gated on a live number -- consistent with the p2 treatment. AUDIT UPDATEs folded (§2b new entry; tier-1
arc_parser HARMFUL; tier-2 role-labeler mechanism + pMTG localisation; E1/E2/E3 unification extends to the parser). p1
§4b sharpened with the filler-gap front-end detail. Review EXCELLENT + SOLVER REVIEW; priority cleared.
📦 **PACKAGED (to restore the ≥3-open floor after p7 cleared) -- NEW p2 `the_reader_is_feed_forward_where_the_brain_is_predictive`:**
the #1 architecture-fidelity gap the relcl drill surfaced (the reader only REACTS; the brain PREDICTS -- verbs
pre-activate expected fillers; surprisal = the core difficulty signal). Architecture-WIDE, highest blast radius remaining,
but ranked BEHIND p1 retrieval-first (do not jump it) and scoped to BUILD ON the existing `predictive_coding` +
`n400_coherence_monitor` machinery, not re-derive it. *Queue: p1 wire-and-measure (retrieval-first, WIP in) = TOP; p2
predictive-reader (ready, behind p1); p8 meaning-context (data-ready, lowest). p7 cleared (integrated).*
🧭 **NEXT-STAGE READY:** when p1 lands owner-finalized, its per-stage ATTRIBUTION selects the branch — see
`notes/NEXT_STAGE_after_wire_and_measure.md` (A: retrieval WINS → consolidate+scale; B: front-end is the wall →
predictive-reader/front-end; C: content is the wall → meaning-supply). p1 is the decisive fork; p2/p8 are re-ranked by it.

### 2026-08-26 -- ✅ **p2 resolve_retrieval_interference INTEGRATED (owner-DONE, EXCELLENT/SOLVED): the missing organ for the fan effect is CONTEXT REINSTATEMENT at retrieval -- the SAME additive rule + one context feature; on the RETRIEVAL-FIRST critical path**
The fan-effect companion to the retrieval-first wire-and-measure, delivered. Re-verified scaffold-free FIRST-HAND
(`test_context_interference_resolution.py`, 6 assertions PASS). Adding the encoding CONTEXT (TCM Howard-Kahana) to the
additive Lewis-Vasishth activation resolves interference among genuinely SIMILAR memories CI-separated at every fan
level (CTX_ADD 0.928 vs the context-free additive baseline 0.400 at 8 competitors; baseline bit-identical to the live
`AdditiveCueRetrieval`). **Genuinely LEAK-SAFE cue combination** (context alone 0.306 << oracle 0.994; info-free twins
lose) -- not a leaked second key. **Residual fan effect EXHIBITED** (emerges from an ACT-R noisy read, not a penalty) and
correctly COLLAPSES (0.494) when context is non-separable -- the honest boundary. Brain-faithful throughout (TCM context,
Teyler-Rudy context-INDEXING not DG sparsification -- tested with the REAL dg_separate organ, neutral on content). The
solver caught + demoted its OWN soft-oracle (diagnosticity-weighting peeks) -- the "suspect your own checker" discipline.
🔌 **NO new hdlab organ:** `AdditiveCueRetrieval` is already feature-agnostic, so context reinstatement is a USAGE (add a
`context` feature), not a new organ. **The live wiring folds into p1's retrieval-first composition** (store the
situation-model/reading-loop GRADED context -- NOT the sign() default -- as a per-item feature; fixed w_ctx; no gate, no
fan penalty), GATED on a live coref/situation-model number. SYNTHETIC construction proof -- the LOAD-BEARING open
question p1 must answer: is the substrate's ACTUAL context separable across similar memories? (the boundary shows the
mechanism collapses when it is not). AUDIT UPDATEs folded (§2b new entry; the content_addressable fan-effect loop marked
RESOLVED; DG re-framed to context-indexing; context_vector sign()/graded = deviation #4 at the context feature). p1 §4c
sharpened with the validated context-feature detail. Review EXCELLENT + SOLVER REVIEW in PROBLEM.md; priority cleared.
*Queue: p1 wire-and-measure (WIP submission in) = the live proving ground for BOTH retrieval organs; p7 relcl awaiting
OWNER review; **NEW p8** `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark` (packaged to restore the
≥3-open floor after p2 cleared -- DATA-READY via the acquired SemCor+WiC, but ranked LOWEST so retrieval-first holds).
p2 cleared (integrated).*

### 2026-08-26 -- 🧭 **STRATEGIC DECISIONS IMPLEMENTED (owner: "do the right things, not the easy ones; most effective + most brain-foundational"): the programme is WIRE-AND-MEASURE, sequenced RETRIEVAL-FIRST; benchmark acquisition DEFERRED**
Owner asked which decisions move the substrate forward most effectively + most brain-foundationally, given that nearly
every submission surfaces a substrate architecture change. **Decided + implemented (docs, not just prose):**
**(1) The programme is WIRE-AND-MEASURE, not more isolated parts** -- p1 stays the top priority; NO new find-a-part
problems until the accumulated modifications are proven to compose (or diagnosed as swamped).
**(2) SEQUENCE IT RETRIEVAL-FIRST** -- the audit's #1 LIVE deviation is "we query the WRONG memory" (the live reader
stores/retrieves by EXACT-KEY HASH, no partial-cue path; the brain does DG-separate + CA3 content-addressable + read
the consolidated store). THREE integrations (binding, content_addressable, cortical_store) all re-located their fix to
this SAME cluster -- widest blast radius on the shelf. So p1's FIRST end-to-end composition = content-addressable
additive retrieval over the live register + the recollection gate, on a cross-event/partial-cue task -- which DOUBLES
as the front-end attribution test (no gain on the ~0.32 event-extraction front-end ⇒ the front-end is the wall, the
single most important thing to learn). Added as p1 §4c "SEQUENCING PRIOR". Follow-on: N400 segmentation, the meaning
read-out / frequency prior.
**(3) COUPLE p2 (fan effect) as retrieval's companion** -- same content-addressable machinery from the interference
side; one shared build serves both (noted in both briefs). Do the mechanism in p2, prove it end-to-end in p1.
**(4) MODERN-WSD-BENCHMARK -- owner over-rode the deferral ("get it, it's easy") -> ✅ ACQUIRED + VETTED 2026-08-26,
but SHELVED behind retrieval-first (acquiring the data does NOT reprioritise the lane).** **SemCor** (sense-tagged text
via nltk -- subordinate senses attested MANY times: `point` 9 / `field` 10 / `light` 8 subordinate senses each >=2x in
80/352 files; the exact property McGuffey lacked, where rare senses appeared ONCE) + **WiC** (5428/638/1400 balanced
human-judged "same-sense?" pairs, in repo) remove the data block on testing "can context OVERRIDE the frequency prior."
VETTED loader `tools/load_wsd_benchmarks.py` + `data/wsd_benchmarks/MANIFEST.md`. SCWS (continuous-modulation frame) NOT
acquired -- canonical mirrors dead (404/401); optional follow-up. Note: the "none on disk" claim was CURRENTLY true but
understated -- the July `exp_learned_context_wsd_semcor_verbs_v1.py` already imports `nltk.corpus.semcor` (the corpora
just weren't re-downloaded after the C: move). The follow-on meaning problem (context-likelihood as constraint-
satisfaction over a PRE-STORED sense inventory, tested on WiC+SemCor prototypes, grounded-covered subset) is
READY-TO-PACKAGE when sequencing reaches the meaning lane -- NOT now (retrieval-first holds; no new find-a-part problems).
**(5) The FRONT-END fix is already in flight -- p7 relcl parser (SOLVED, AWAITING YOUR REVIEW).** Integrating it
improves the ~0.32 event-extraction front-end the retrieval cluster composes on. → **owner action: review p7.**
Folded into audit §8 (a 🧭 strategic-decisions block heads the leverage ranking). Committed.
*Queue: p1 wire-and-measure (retrieval-first) + p2 fan-effect (coupled) = 2 AVAILABLE; p7 relcl awaiting OWNER review.*

### 2026-08-26 -- ✅ **p6 meaning_win INTEGRATED (owner-DONE, EXCELLENT/PARTIAL): the offline meaning win does NOT transfer to context-SELECTION; the wire-able residual is the frequency PRIOR (gated); + the ARCHITECTURE-MODIFICATION convergence is answered by the WIRE-AND-MEASURE pivot, not more parts**
`the_meaning_win_is_offline_context_free_and_unwired` SOLVED as a rigorous negative (bar option 3). Re-read the FULL
SOLVED FRESH (standing rule) -- and it MATTERED: the FINAL version WITHDRAWS the WIP "grounding hurts the associative
channel (−0.044, n=49)" claim under a power-check (n~154 → +0.017, straddles 0); memory corrected. Re-verified
scaffold-free FIRST-HAND (`test_meaning_win_context_transfer.py` PASS, all 4 checks incl. the power-check). Conditioning
the grounded read-out on context does NOT beat the frequency prior in EITHER meaning system (MFS 0.4637 > uniform 0.3995
CI-sep; every context arm below it; on the frequency-defeating subordinate items grounded is at chance + ties its
info-free twin -0.0043). The offline win is CONTEXT-FREE + SIMILARITY-typed. **Wire-able residual = the frequency PRIOR**
(Duffy & Rayner reordered-access) -- but a LIVE ARCHITECTURAL change, not a flag: the reader is SENSE-BLIND (one blended
vector per lemma) → it needs per-sense representations first → GATED on a downstream measurement, packaged into the
wire-and-measure lane, NOT pre-paid. Subordinate-OVERRIDE (context beating frequency) is DATA-limited: needs a MODERN
WSD benchmark (SCWS/WiC/SemCor), NONE on disk -- an ACQUISITION need surfaced to the owner, not more architecture.
3 AUDIT UPDATEs folded (§2b new entry; §7 condition-on-context tested-negative; §6 semantic-control THIN substrate;
§8-lever-#3 refuted). Review EXCELLENT + SOLVER REVIEW in PROBLEM.md; priority cleared. **NO hdlab landing this
integration** (Q111 honoured; the proposed diff is a live architectural change, deferred to a gated build).
🧭 **STRATEGIC (owner 2026-08-26 "so many solutions point to architecture modifications -- how are we responding?"):**
YES, correct -- nearly every recent submission surfaces a substrate architecture change. The RESPONSE is the
WIRE-AND-MEASURE PIVOT (p1): the accumulated validated organs are default-off ISLANDS; the disciplined move is to
COMPOSE + MEASURE them end-to-end (prove the modifications earn a live capability, or diagnose the binding constraint)
BEFORE finding more parts. The modifications CLUSTER (retrieval architecture · code sparsity/grading · meaning
content-supply · missing control/update organs), and healthily include REFUTATIONS that PRUNE the invention pile
(sign-readout, semantic-switch, DG-separation, "grounding-hurts"). This integration MODELS the response: I did NOT spawn
another isolated-part problem; the frequency-prior wiring goes into the wire-and-measure lane, gated on a live number.
*Queue after p6: p1 wire-and-measure (now also carries the frequency-prior sense-default build) + p2
resolve_retrieval_interference = 2 AVAILABLE; p7 relcl SOLVED but awaiting OWNER review (no OWNER_NOTES yet -- not integrable).*

### 2026-08-26 -- ✅ **p5 one_store INTEGRATED (owner-DONE, EXCELLENT/PARTIAL): the STORE not the schedule was the divergence -- SPARSE coding is the primary anti-forgetting lever; the gap is a retention↔generalisation TRADEOFF (content-bound)**
On real reading, making the cortical code SPARSE + pattern-separated (k-WTA) FLIPS the verdict: dense cortex -> selective
replay is a zero-sum wash; SPARSE cortex -> sparse coding is the PRIMARY anti-forgetting lever (equal-capacity dense
control collapses to 0.000 -> sparsity causal) AND selective replay CI-beats the uniform twin (0.784 vs 0.680). Two-store
necessity measured (sparse retains 0.68-1.0 but generalises ~0.05). FORK B: the live store never forgets -> forgetting is
NOT the live constraint; the wall is CONTENT (generalisation at the first-order floor -- converges with every recent
result). Re-verified 8/8; a model of the protocol (leave-the-family + an independent literature scan correcting 2 of its
own over-claims). 4 AUDIT UPDATEs folded (deviation #5 reframed to the tradeoff; sparse coding load-bearing on WRITE+READ).
🔌 hdlab landing EARNED (ordered: sparse k-WTA code PRIMARY = the p2 cortical-read's lever; uniform interleaved replay
SECONDARY; keep the fast store) -> queued, coordinate with p2. *Queue after p5: NEW p2 resolve_retrieval_interference
(fan effect, solver-surfaced) + p1 wire-and-measure = 2 AVAILABLE TO START; p6/p7 awaiting owner review.*

### 2026-08-26 -- 🔀 **PHASE PIVOT (owner-authorized): from building isolated PARTS to WIRING them together + measuring the reader END-TO-END**
Owner 2026-08-26 asked *"is everything integrated, tied together, and have we tested it end to end?"* -- honest answer:
NO. Every validated organ (N400 segmentation, feature-similarity whitening, content-addressable additive retrieval,
DG/CA3 gate) is landed **off-path / default-off / synthetic-proof-only**, each with its own "measure on the LIVE task
before any capability claim" caveat. **The PARTS are validated + integrated as islands; the composed reader has NEVER
been measured end-to-end.** That is the accumulating WIRE-DON'T-ISLAND debt. ➡️ **NEW p1
`wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end`** -- compose 2-3 landed organs into the live
reader behind flags, measure end-to-end vs today's baseline (identical inputs), per-organ ablation. **DECISIVE EITHER
WAY:** a win = the first end-to-end capability number + wire it in; a well-diagnosed LOSS = we learn the binding
constraint (almost certainly the front-end, event-extraction ~0.32) which re-points the whole programme. This also
answers "almost out of problems?": the NEXT problems are wiring + end-to-end measurement, not more isolated parts.
🔧 **Strategy's own hdlab debt to enable it:** ✅ the additive content-addressable retrieval ALGORITHM is now a
STANDALONE organ (`hdlab/content_addressable_retrieval.py::AdditiveCueRetrieval`, witness PASS -- additive 32/32 vs
composite 0/32 under a dropped feature; registered `content_addressable_retrieval_v1`, off-path). REMAINING wirings (extend the register to
STORE per-feature codes + a `decode_cue` on it; wire the N400 boundary -> `situation_model_accumulate`) are the
COMPOSITION steps the **p1 wire-and-measure brief MEASURES** -- so they are GATED ON the p1 end-to-end result (strategy
lands them ON A WIN, Q111), NOT pre-paid. 🚫 Do NOT pre-land an unmeasured live wiring (measure-before-capability-claim).
The importable ALGORITHMS (content-addressable, N400, whitening, DG/CA3) are landed; the live COMPOSITION is what p1 tests.

### 2026-08-26 -- ✅ **p3 content_addressable_retrieval INTEGRATED (owner-DONE, EXCELLENT/SOLVED): the missing organ is cue-based RETRIEVAL (additive Lewis-Vasishth); it RE-FRAMES the fix**
Content-addressable retrieval over the SEPARATED register beats the LIVE exact-key routes CI-separated under a partial
cue (SEP_CA 0.991 vs HASH 0.287; twins at chance; tie at a full cue -- the Nakazawa CA3 dissociation). Re-verified 8/8
scaffold-free first-hand. **RE-FRAMES the fix (honest self-corrections):** an EQUAL-STORAGE flat store TIES -> separation
is NOT the lever; the genuinely-missing organ is content-addressable RETRIEVAL (the cue-MATCH); the CA3 iterative settle
is NOT load-bearing (1-step argmax ties); DG did NOT help (rigorous negative). **NEW deviation:** the retrieval RULE
should be ADDITIVE (Lewis-Vasishth, already pinned for E3) not a MULTIPLICATIVE composite (which orthogonalises on one
wrong feature and collapses) -- but DEFLATED to mostly-a-tie by the owner-directed real-grounded drill (additive = the
right default for robustness + partial-cue support, not a big everyday lift). REAL open problem = similarity-INTERFERENCE
(the fan effect), which should NOT be "solved" (brain-correct behaviour). 4 AUDIT UPDATEs folded (E2 retrieval deviation;
E1/E2/E3 re-location sharpened; owned fix half-owned; additive retrieval rule). hdlab landing EARNED (default-off additive
`decode_cue` over the separated multibank register + FHRR adapter for `ca3_completer`) -> queued as a focused default-off
landing w/ its own witness. SYNTHETIC construction proof -- measure on the LIVE reading/QA task before any capability claim.
*Queue after p3: p5 one-store (awaiting owner review), p6 meaning-wiring, p7 relcl. Genuinely-open (no submission): p6, p7 -- THIN.*

### 2026-08-26 -- ✅ **p1 TWO-SYSTEMS BUILD INTEGRATED (owner-DONE, EXCELLENT/PARTIAL): the missing FEATURE-SIMILARITY meaning system is BUILT + proven; the semantic-control SWITCH is REFUTED (fixed fusion wins)**
The re-point's #1 brain-foundational lever, delivered. Re-read the FULL SOLVED FRESH (standing rule, owner 2026-08-26
"read it all again every time" -- the solver had added a finer nonlinear-distinctiveness drill + the strong-associative
gate re-test since the WIP read) and re-verified scaffold-free FIRST-HAND (`test_two_meaning_systems_feature_similarity_and_gate.py`
PASS). **BAR #1 MET:** the ATL's "privilege DISTINCTIVE features" = DECORRELATION (WHITEN away the dominant shared
concreteness axis, top PC 26.7% of grounding variance); distinctive-feature-weighted grounding beats RAW grounding
CI-separated on two HELD-OUT golds (SimLex +0.046 CI_lo 0.019, SimVerb +0.023 CI_lo 0.008) and LOWERS relatedness (the
brain signature) -- a REPRESENTATION-level op, different-in-kind from the refuted sign/graded/sparse read-out family.
**BAR #2 REFUTED robustly:** the two systems are better FUSED than SWITCHED (fixed multiplicative fusion beats the
task-gate even with a STRONG associative system, gate−fixed −0.026 CI-sep; the gate ties its random-switch control) --
IFG control is context-driven, a decontextualised word pair gives it nothing to gate on, so the switch belongs to a later
SELECTION task (WSD), NOT graded rating. **FINER DRILL = a fidelity BOUNDARY:** linear whitening suffices; a per-concept
nonlinear distinctiveness doesn't add on a 12-dim continuous space (the next gain is richer feature SUPPLY, not a fancier
transform -- converges with the session's "supply is the wall" theme). 3 AUDIT UPDATEs folded; §8 lever #1 DELIVERED;
review + SOLVER REVIEW in PROBLEM.md; priority cleared.
🔌 **hdlab landing DONE 2026-08-26:** the distinctive-feature WHITENING read-out is LANDED in
`hdlab/grounded_similarity.py` (`distinctive_grounded_vector`/`distinctive_grounded_similarity` -- a NEW uncapped
meaning read-out; the capped link score is byte-identical). Witness `test_distinctive_feature_grounding_organ.py` PASS
(distinctive rho 0.292 > raw 0.245 on SimLex through the organ's OWN transform; whitened covariance exactly identity),
registered `distinctive_feature_grounding_v1` (WIRE_CANDIDATE, ISLAND). Use it as the feature-similarity axis + a FIXED
two-system fusion, NOT a switch. ⚠️ MEASURE on the live read-out before any capability claim.
*Queue: p3 content-addressable retrieval + p5 one-store (both awaiting owner review), p6 meaning-wiring, p7 relcl. p1 integrated.*

### 2026-08-26 -- 🔧 **N400 coherence-monitor ORGAN LANDED (F5, off-path) -- the MISSING event-segmentation organ is now in hdlab**
WIRE-DON'T-ISLAND follow-through on the integrated prediction_error win: **`hdlab/n400_coherence_monitor.py`** promotes
the validated N400 mechanism (a GRADED forward CONTENT prediction error vs the RUNNING event gist, reset per event, EST
relative threshold) into a real organ. **Off-path / DEFAULT-SAFE** (importing it changes NO existing behaviour). Witness
`test_n400_coherence_monitor_organ.py` PASS -- it proves the two load-bearing findings FIRST-HAND: the RUNNING RESET
(F1 1.0 > never-reset anchor 0.44) and the CONTENT SPACE (a near-orthogonal binding-like code is unsegmentable, F1 0.0 =
the p1 sign_quantiser coupling). Reuses the pinned `predictive_coding.running_avg_update`; registered
`n400_coherence_monitor_v1` (WIRE_CANDIDATE, ISLAND). Audit F5 moved **MISSING → BUILT.** **Still a synthetic
construction proof:** wiring it live (boundary → advance `situation_model_accumulate`) + a live-reader measurement is the
next step, before any capability claim. One of the two queued organ landings done; the cortical-read CLS pair remains.

### 2026-08-26 -- ✅ **p4 prediction_error INTEGRATED (owner-DONE, EXCELLENT): the brain's missing UPDATE signal (N400 event-segmentation) is BUILT + proven; fills the MISSING F5 organ**
`the_substrate_does_not_learn_or_update_by_prediction_error` SOLVED via the UPDATE/SEGMENTATION framing. Re-verified
scaffold-free first-hand (`verify_prediction_error_event_segmentation.py` PASS). A GRADED forward CONTENT prediction
error against the RUNNING (reset-per-event) situation-model state segments a discourse near-perfectly -- within-event
cross-role recovery **0.988 [0.980,0.995]** vs FIXED 0.523 / RANDOM 0.438 / FORM_NOVELTY 0.737 (floor) / PERMUTED 0.487,
boundary F1 0.987, all 9 cells, at a MATCHED boundary rate (win is POSITION not rate). **Fills the audit's MISSING F5
(N400 coherence monitor).** Key: the residual must be graded AND in a CONTENT-similar space -- the naive `||Δregister||`
in the near-orthogonal binding space ties no-op = **the p1 sign_quantiser coupling made concrete**. Deviation #6 SPLIT
(UPDATE half = build, WINS; LEARNING half = rigorous negative, deprioritise). 4 AUDIT UPDATEs folded; review + SOLVER
REVIEW in PROBLEM.md; priority cleared.
🔧 **PROVEN-READY hdlab LANDINGS (WIRE-DON'T-ISLAND hygiene; each still needs a LIVE-task check before any capability claim):**
(1) ✅ **N400 organ LANDED 2026-08-26** as `hdlab/n400_coherence_monitor.py` (off-path WIRE_CANDIDATE; witness
`test_n400_coherence_monitor_organ.py` PASS; registered `n400_coherence_monitor_v1`; reuses the pinned EST
`running_avg_update`) -- NEXT: wire a posted boundary → advance `situation_model_accumulate`'s event slot + measure live.
(2) the **cortical-read CLS matched pair** -- STILL QUEUED; SCOPED 2026-08-26 (do not repeat this / do not land theater):
the deviation-#4 rescue (k-WTA sparse coding + frequency-normalised inhibition, 0.025→0.156) is SPECIFIC to the
ASSOCIATIVE (Hebbian frequency-summed) read over the OVERLAPPING (PPMI+SVD) code -- it rescues hub collapse THERE. On
the current GRADED cosine read (`cortical_recall`) sparsity is INERT, and imposing it is the fidelity THEATER the
submission itself flagged (the graded read is sparsity-robust 0.34-0.39). So a faithful landing needs the
overlapping-code + associative-read path BUILT (a real build, not a heartbeat cram); a naive k-WTA option on the cosine
read would be theater. Land when that path exists; MEASURE LIVE before any capability claim (it is architecture-
validation, not a floor-beater).
*Queue: p1 two-systems, p3 content-addressable retrieval, p5 one-store, p6 meaning-wiring, p7 relcl -- all open, unique;
sign_quantiser + prediction_error cleared (integrated).*

### 2026-08-26 -- ✅ **sign() RE-INTEGRATED properly on owner-DONE (verdict PARTIAL); + PROCESS FIX: a directional "yes" is NOT a per-problem owner-DONE (rule reinforced)**
**What went wrong:** I integrated `the_sign_quantiser...` (its READ-OUT half, status REFUTED) off the owner's
DIRECTIONAL "be as brain foundational as possible" -- treating a direction as a per-problem finalization. The solver
was STILL iterating and delivered a FINAL verdict of **PARTIAL**: the read-out refutation stands, BUT in the
BINDING/superposition regime sign() IS a real averaging machine for CORRELATED (graded-semantic) fillers, **COUPLED to
B4 (dense->sparse)** -- graded beats sign CI-separated and GROWING (capacity cliff B*=8 -> B*=12); a joint sign()+B4
GUARDRAIL at the BINDING SITES, **NOT** a "flip binding sites for a win." So my "demote the format foundation" was too
strong -- the format is a LIVE binding-site guardrail (connects to p3 content-addressable retrieval + p5 one-store),
demoted only AS A READ-OUT lever.
**RESOLVED:** the owner then FULLY SUBMITTED it (`owner_verdict: DONE`), and it was RE-INTEGRATED properly. All THREE
regimes re-verified scaffold-free FIRST-HAND: READ-OUT **REFUTED** (sign null; faithful format family + self-supervised
CBOW tie counting ~0.05, below the 0.171 floor -> meaning-SUPPLY wall); BINDING **CONFIRMED** (graded beats sign for
CORRELATED codes, cliff B\*=8->12 at d=256); LIVE **LATENT** (verdict `SIGN_SAFE_TODAY_BUT_BITES_IF_BINDING_MADE_FAITHFUL`
reproduced -- real load meanB=2.85, atomic |cos|0.06 -> gap +0.013 ~0 today; graded-semantic |cos|0.25 -> +0.087 on the
B>4 tail). **Verdict PARTIAL, EXCELLENT.** Priority cleared; review + SOLVER REVIEW in PROBLEM.md; audit §2b has clean
binding-regime + read-out entries; §8 lever #1 demoted only as a READ-OUT lever, ALIVE as a binding-site guardrail.
**Guardrail recorded (B4/binding line, p3+p5):** when B4 makes fillers graded-semantic, the sign()-on-a-bundle sites
(`situation_focus`, `role_slot_summarizer`, `event_bundle`, CA3 `cleanup_family`) go graded in the SAME change. NO
hdlab landing (latent, not a current bug). The **p1 two-systems build stands**.
🔒 **STANDING RULE REINFORCED (owner 2026-08-26): DO NOT integrate ANYTHING without an explicit per-problem owner-DONE.
A chat "yes" to a direction or a recommendation is NOT a done signal. When uncertain, ASK or WAIT -- never infer DONE.**
WHAT STILL STANDS (correctly integrated -- real owner-DONE or unaffected): **cortical_store** (owner-DONE, PARTIAL),
**binding** (owner-DONE). The new **p1 two-systems brief STANDS** (the read-out two-systems finding holds in both the
REFUTED and PARTIAL versions).

### 2026-08-26 -- ✅ **BRAIN-FOUNDATIONAL RE-POINT (owner-endorsed DIRECTION): p2 cortical_store INTEGRATED (owner-DONE); the second-meaning-system BUILD packaged p1 -- ⚠️ the sign() portion here was PREMATURE, see the CORRECTION entry above**
**INTEGRATED (owner-DONE, PARTIAL/EXCELLENT): `the_consolidated_cortical_store_is_written_but_never_read`.**
Re-verified scaffold-free (`test_cortical_store_read_path.py` WITNESS PASS, 6-unit headline). A precise BOTH: the
brain-faithful cortical read BEATS the WRONG (episodic) memory ~10x on transfer, CI-separated over its twin, ablation
bites (0.0000 -> a real drop) -- the read-path defect is REAL and fixable; BUT it ties first-order counting in-domain
and sits at/below its own twin on the powered unseen regime -- so the **residual wall is the consolidated CONTENT/CODE,
not the read.** Deep drill: dev #4 (sparse+inhibition) LOAD-BEARING on the read (0.025->0.156); NEW dev (recurrent
attractor completion HURTS ranking -- re-promotes hubs, so the faithful ranking read is a GRADED population read);
dev #5 CLOSED BY TEST (online CLS process is MORE data-hungry than batch, same data-bound ceiling). 3 AUDIT UPDATEs
folded; committed `f325b1839`. The proposed hdlab CLS matched-pair read is scoped as the next default-off landing
(architecture hygiene + the proven dev-#4 read-op; NOT a floor-beater).
✅ **sign_quantiser INTEGRATED 2026-08-26 (owner-authorized in-session "be as brain foundational as possible"; REFUTED-VALUABLE -- a rigorous negative is a PASS). Re-verified scaffold-free PASS; stale-premise confirmed on disk; 3 AUDIT UPDATEs folded; priority cleared; the second-system BUILD packaged as p1.**
- **`the_sign_quantiser...` -- REFUTED, and it re-points the whole audit.** The `sign()` quantiser (audit DEVIATION
  #2 / the #1 leverage lever) is NOT the averaging-machine bottleneck: graded vs sign = `+0.0015` NULL on the REAL
  open-vocab hit@1 task (re-verified PASS), the graded switch is ALREADY default-ON since 08-14 (confirmed on disk),
  and the ENTIRE brain-faithful code-format family (graded/divnorm/sparse/DG-expand) + a faithful self-supervised
  CBOW learner ALL tie plain counting (~`0.05`), all below a generic-word floor (`0.171`). Only WordNet-SUPERVISED
  learning beats it -> **the wall is meaning SUPPLY, upstream of the sign() and every read-out format.** NEW &
  first-class: the TWO SIMILARITY SYSTEMS are measurable on our reps (distribution carries ASSOCIATIVE relatedness
  WordSim `0.25` but ~0 feature SIMILARITY SimLex `0.04`; grounding carries both `0.42`/`0.21`) + a measured need for
  SEMANTIC CONTROL (task-gating). ⚠️ Corpus-age is NOT this instrument's confound (`load_corpus_v5` is MODERN, not
  McGuffey -- the solver's disk-checked correction; reconcile with the standing McGuffey note per instrument).
⏳ **STILL AWAITING OWNER -- do NOT integrate (no owner_verdict):** **`the_substrate_does_not_learn_or_update_by_prediction_error` -- SOLVED (a clean POSITIVE):** a GRADED forward
  prediction error (N400 = ||Delta situation-model||) segments a discourse and gets the right content into memory --
  within-event cross-role recovery ~`0.99` vs baselines ~`0.52`/`0.44`, CI-separated, twins lose. Awaiting owner review.
🔗 **THE CONVERGENCE (the strategic headline):** cortical_store + sign_quantiser + the 08-26 meaning re-frame ALL land
on the SAME wall -- meaning SUPPLY/CONTENT + the two-similarity-systems architecture (grounding + tight-window
structure) + semantic-control gating -- **NOT the code FORMAT, the read MECHANISM, or the `sign()`.**
📋 **STRATEGIC FORK RESOLVED (owner 2026-08-26: "be as brain foundational as possible") -> EXECUTED.** (1) sign()
refutation accepted + integrated; audit updates folded; representation-FORMAT foundation DEMOTED (audit §8 lever #1).
(2) queue re-pointed -- the second-meaning-system BUILD is now p1, above representation-format. (3) standing meaning
metric -> human relatedness/similarity, NOT taxonomic WordNet. GUARDRAIL held against the "buy-more-norms treadmill":
the new p1 is a NARROW testable BUILD (feature-similarity from grounding + tight-window structure + a semantic-control
gate), NOT "supply more norms" (projecting the ones we own already covers the gap).
*Queue after re-point: **p1** `the_substrate_has_one_meaning_system_where_the_brain_has_two` (NEW brain-foundational
build), **p3** content-addressable retrieval, **p5** one-store, **p6** meaning-wiring, **p7** relcl -- all
genuinely-open, priorities unique; **p4** prediction-error awaiting owner. sign() cleared (integrated).*

### 2026-08-26 -- ✅ **p3 BINDING INTEGRATED (EXCELLENT): the OPERATOR is VALIDATED; the deviation RE-LOCATES to the RETRIEVAL architecture**
The binding foundation is RESOLVED. At EQUAL storage our compressed FHRR bind **BEATS the two writable brain
theories** (tensor-product, conjunctive) -- an efficient choice, NOT a liability; TPR loses to FHRR in every
exact-cue cell. ➡️ **The real deviation is one level up: flat-superposition RETRIEVAL.** We superpose many bindings
into one vector and un-mix on demand; the brain SEPARATES into slots + retrieves CONTENT-ADDRESSABLY, so a partial
cue still works -- a brain-faithful version (theta-gamma) recovers **~5x more under a degraded cue, CI-separated, at
equal storage** (0.128 vs 0.025), twins losing (predicted by the CA3 partial-cue dissociation, Nakazawa 2002).
**Load-bearing negative:** CA3 cleanup on a flat read TIES argmax -- you cannot clean out of superposition; fix the
STORAGE. **The substrate ALREADY OWNS the fix (`ca3_completer` + `dg_pattern_separation`, both default-off) but
wires them so the advantage is lost.** Synthetic construction proof, NOT a downstream win -- measure LIVE before any
capability claim. AUDIT UPDATED (E1 re-located; unifies E1/E2/E3 under content-addressable retrieval). Re-verified
scaffold-free (`verify_binding_operator_stress.py` PASS).
🔌 **BOTH DONE (owner 2026-08-26: "do the right thing, not the easy thing; move to be more brain-foundational"):**
- ✅ **Rec A LANDED (default-OFF):** `bundling.bundle(vectors, norm="l2")` + the coupled `atoms.similarity(..., cosine=True)`
  readout -- the per-component normaliser only ever HURTS (L2/raw-sum beat it 32/32). Witness
  `test_bundle_l2_normaliser_coupled.py` PASS (default BYTE-IDENTICAL; L2+cosine 0.419 >= default 0.344 under a
  partial cue; regression clean). ⚠️ MEASURE ON THE LIVE READING TASK BEFORE FLIPPING (isolation win != capability).
- ✅ **Rec B PACKAGED as p3** `content_addressable_retrieval_over_a_separated_store` -- the RE-LOCATED foundational
  deviation and the ~5x lever: wire content-addressable retrieval (`ca3_completer` + `dg_pattern_separation`,
  owned/default-off) over the SEPARATED `situation_model_multibank` store (which routes by exact-key hash, no
  partial-cue path); prove on the LIVE situation-model task. UNIFIES E1/E2/E3 under one brain mechanism. Coordinate
  with p2 (the READ half). **This is the brain-foundational path made concrete.**
*Queue: p3 now = content-addressable retrieval (the re-located binding deviation); open p1-p7, unique.*

### 2026-08-26 -- 🧠 **FOUNDATION-FIRST QUEUE: the last two un-attacked foundations packaged (owner-directed)**
Owner 2026-08-26: *"attack the foundations first -- if what we have is predicated on anything non-foundational in a
BLOCKING way, we should attack those foundations first."* Confirmed the queue is foundation-first and CLOSED the
set. **NEW QUEUE (all three foundational fixes now sit ABOVE the downstream capability work):**
- **p1 `the_sign_quantiser_makes_the_substrate_an_averaging_machine`** -- the representation FORMAT fix
  (`sign→graded` + dense→sparse folded in; the brain codes graded+sparse, we code 1-bit+dense; ~34 sign sites,
  16x-dims = +0.0843). BLOCKING.
- **p2 `the_consolidated_cortical_store_is_written_but_never_read`** -- read the long-term memory we write but
  never consult (a POSITION error blocking transfer). BLOCKING.
- **p3 `the_core_binding_operator_may_not_be_brain_faithful`** (NEW) -- our single most central operation is
  UNPINNED / 3-way contested; test brain-motivated alternatives vs FHRR on a binding-STRESS task. NOT proven-
  blocking (unfalsified) -- a rigorous negative VALIDATES the invention. The last un-attacked foundation.
- **p4 `the_substrate_does_not_learn_or_update_by_prediction_error`** (NEW 2026-08-26) -- the brain's core
  PREDICTION-ERROR learning + update signal (we learn by cloze, and never update the situation model on surprise;
  the PE organ is islanded + never fires, the N400 monitor is MISSING). Foundational. **p5** meaning-wiring;
  **p6** relcl-parser.
➡️ **CONSOLIDATION NOW PACKAGED (p5) -- THE FOUNDATIONAL SET IS COMPLETE.** Every real foundational deviation the
audit surfaced is now queued: **p1** representation (sign→graded + dense→sparse), **p2** memory-READ, **p3**
binding operator, **p4** prediction-error (learn+update signal), **p5** consolidation (memory-WRITE / selective
replay). **No genuinely-foundational deviation remains unqueued.** Beyond these the audit items are CAPABILITY
(meaning-wiring p6, relcl p7, and unpackaged: coref / discourse / ToM / production), NOT deep foundation -- DO NOT
fabricate foundations to fill the queue (owner 2026-08-26). (additive-vs-multiplicative control C3 is foundational
but BLOCKED behind p1.)
Both proven-ready organ landings DONE (DG/CA3 recall gate -- SPARSE, the brain's sparse coding entering the memory
path; valence Stage-B -- default-off). LONG_TERM_PLAN §3 reconciled with the meaning re-frame (was a stale hazard
for the working solvers). *Meaning-wiring demotion below binding is a recommendation; re-rank if disagreed.*

### 2026-08-26 -- ✅ **p2 `no_automatic_reliability_signal` INTEGRATED (EXCELLENT) -> a self-certifying DG/CA3 recollection organ that beats the counting floor**
The "which source to trust" problem is SOLVED by going DEEPER than the brief (the strengthened-protocol behaviour,
first live proof of it): the solver BUILT the brief's own-geometry mechanism, REFUTED it, found the real bottleneck
was the episodic store (no separable traces), and rebuilt it the hippocampus's way -- **dentate-gyrus pattern
separation + CA3 completion.** Recollection now **SELF-CERTIFIES** (top-5% precision 0.938 vs counting 0.533 on the
same items) and dual-process routing beats the counting floor CI-separated for the FIRST time (route 0.365 vs UB
0.336), ~half the oracle headroom; info-free twin loses, scramble -> 0.00. **Answers board Q118: a label-free
selection signal IS CA3 completion confidence.** 🔌 **DG/CA3 RECOLLECTION-GATE ORGAN LANDED** -> `hdlab/dg_ca3_recollection_gate.py`
(off-path WIRE_CANDIDATE, no behaviour change; witness `test_dg_ca3_recollection_gate_organ.py` PASS; registered
`dg_ca3_recollection_gate_v1`). Wire into the episodic retrieval path (p2 `cortical_store` build) + scale with
reading VOLUME. Fed the first **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (memory tier /
deviation #2; D1 DG moves off "orphan", D2 CA3 gains a self-certifying confidence -- but the cortical-consolidated
read, deviation #3, is NOT closed). **Lever for more = reading VOLUME (coverage), not a cleverer gate.**
✅ **p3 `propagate_along_the_relation` ALSO INTEGRATED (EXCELLENT):** signed valence propagation replaces the
taxonomic Stage B (which carries NO valence); the sign-scramble twin proves the RELATION'S SIGN carries good/bad
(0.726 on 485 vs shipped 0.660 on 326). Deep: **opposition is IRREDUCIBLE** (antonyms similar in every feature
space, so the flip must be an explicit relation) and the **graded readout is hidden** (vote magnitude rho 0.400 with
continuous ratings); universal across POS, sharpest on adjectives (0.8845). 🔌 **Stage-B replacement LANDED in
`hdlab/wordnet_polarity_propagation.py`** -- `dictionary_lookup(..., signed_propagation=True)`, DEFAULT-OFF
(byte-identical when off; verified IDENTICAL to the proven cell mechanism across 22 probes); witness
`test_valence_signed_propagation_landing.py` PASS. Turn on when the valence organ's consumer wants the wider,
sharper axis. AUDIT
UPDATE folded in (affect/valence tier now fidelity-scored). ➡️ **PRIORITY RESHUFFLE DONE (with p2+p3+the audit):
packaged the audit's top-2 unqueued brain-faithfulness deviations. NEW QUEUE (brain-faithfulness blast radius):
p1 `the_sign_quantiser_makes_the_substrate_an_averaging_machine` (the cross-cutting `sign→graded` fix, ~34 sites);
p2 `the_consolidated_cortical_store_is_written_but_never_read` (the wrong-memory / cortical-read fix -- complement
to p2-reliability's episodic win); p3 `the_meaning_win...` (meaning wiring, was p1); p4 `the_relcl_parser...`.
Two organ landings pending (proven-ready deliberate): the DG/CA3 recollection gate + the valence Stage-B
replacement.** *(The meaning-wiring demotion 1->3 is a recommendation -- higher blast radius sits above it; re-rank if you disagree.)*

### 2026-08-26 -- 🧠 **WHOLE-SUBSTRATE BRAIN-FOUNDATIONAL AUDIT, RECONCILED -> `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**
Owner asked whether the substrate had been evaluated deeply against the brain foundation for large-scale gaps /
deviations. It HAD (three scattered audits) but never reconciled or kept current. Produced ONE living reconciled
map (merges ORGAN_MAP's 38 organs + component ledger's 14 + LONG_TERM_PLAN §4). **Headline: only 5 of 38 organs
compute the brain's actual equation; 14 core operations are UNPINNED even in neuroscience (incl. our central
BINDING op) so they are inventions-under-test, not replications; 7 organs are MISSING; ~54% of code is
unreachable.** Two defects outrank any single organ: **(1) we query the WRONG memory** -- answer from the fast
episodic store, never read the consolidated cortical one (a MISSING cortical-read organ, not a ceiling); **(2) a
`sign()` quantiser everywhere** turns the system into an averaging machine (graded flags exist default-OFF).
**IT RE-RANKS THE QUEUE:** the biggest cross-cutting deviations -- `sign→graded`, the cortical-read organ,
dense→sparse coding, the binding operator -- are NOT in p1-p4 and outrank most of the queue on blast radius;
package them as builds converge (p1 meaning-wiring already captures one lever). **Corrections it forced:** the
07-30 component ledger's "coreference/discourse ABSENT" is STALE (both heavily built now); affect/goals/
metacognition are BUILT but never fidelity-scored (a scope gap in the old audit); the plan's "meaning is empty"
premise is weakened by this session's fair-metric re-frame. 🔁 **LIVING REFERENCE:** every brief now cites the
audit; solvers report `AUDIT UPDATE`s during their work; integration folds them back in (README standing rules).

### 2026-08-26 -- 🧠 **TWO OWNER-DONE SOLUTIONS INTEGRATED; THE MEANING LINE IS RE-FRAMED AND THE "WIRING NO" IS RE-OPENED**
**Both re-verified scaffold-free (first-hand, reading no artifact), graded EXCELLENT, priorities cleared.**
🥇 **`the_own_metric_may_reward_frequency_not_meaning` (was p2) -- DECISIVE, and it OVERTURNS the meaning-line verdict.**
The home metric ("for a grounded word, pick one partner that is a ConceptNet neighbour") **WAS scoring frequency, proven
BY CONSTRUCTION:** on a candidate pool where the gold partner and its distractors have IDENTICAL co-occurrence counts,
raw-count argmax reads **exactly chance** (`0.5000`/`0.2000`, zero-width CI). On that FAIR metric, concreteness-stripped
grounded meaning beats the **stronger PPMI floor's UPPER bound** CI-separated at every pool size (`0.741` vs `0.558` at
K=1), info-free twins losing; concreteness, coverage and pseudoreplication all controlled. **p2's discrimination reframe
now CROSSES to the top-1 metric in the SAME currency (accuracy@1, de-confounded) and is scaffold-witnessed.**
➡️ **RETIRE the top-1-argmax-over-co-occurrents grounding-precision metric as the arbiter of "is stage 2 broken" -- it
conflates a weak frequency bias with meaning. The prior "WIRING = NO" (from p2, integrated 08-25) was measured on a
frequency-UNFAIR test and IS RE-OPENED.** 🚫 **DO NOT re-quote "the read-outs lose to counting / wiring NO" as the meaning-
line verdict -- that was the unfair-metric result.** The direction: rank meaning candidates by the **grounded sensorimotor
spoke** (NOT raw count) on the grounded-covered population; extend the co-occurrence store to grounded terms (the landed
`track_all_content_lemmas` flag is exactly that channel). Do NOT add control-gated distributional weighting at this
~200-year-old-corpus scale (the deeper mechanism converged to grounded-alone; no crossover to gate). **THE WIRING IS MINE
TO BUILD/LAND (Q111) -- packaged next.**
🥈 **`organ_abstains_on_two_thirds_of_v2` (was p1) -- the goal organ's 82/124 "I don't know" is DIAGNOSED and HONEST.**
All 82 terminate at `goal_typing.py:1984` because BOTH the goal side (42) and the outcome side (32) are out-of-vocabulary
for its small hand-built lists. The two gaps COMPOUND -- only 7/82 reach an outcome candidate, so broadening goal
recognition converts ~nothing (3/42). Forced to answer, the grounded channel loses to its own info-free twin -> the
silence carries no reachable signal (the organ correctly lacks the meaning to decide). 🚫 **Do NOT hand-extend the closed
lexicons** (not brain-faithful, and the compounding ceiling proves it cannot close the gap). Remedy is UPSTREAM.
🔗 **THE CONVERGENCE, AND IT SETS THE NEXT BUILD:** both integrations point to the SAME missing organ -- **broad grounded
word-meaning supply.** It is now the common blocker for BOTH the goal-bearing line (the goal organ cannot type arbitrary
goals/outcomes without it) AND the meaning-read-out wiring (the read-out needs grounded coverage of the scored terms).
That is the highest-leverage gap.
🗂️ **OPEN QUEUE (enumerated from disk 08-26): 3 open** -- `no_automatic_reliability_signal_reaches_the_source_oracle`
(p3), `propagate_along_the_relation_that_carries_valence` (p4), `the_relcl_parser_is_too_weak_for_filler_gap_role_assignment`
(p5); **the two just-integrated are cleared.** ⏱️ **30-min ARCHITECT cron LIVE (session-only `15610e6f`; survived
compaction -- dies on session EXIT, re-create it then).**

### 2026-08-25 (post-move) -- 🖥️ **MOVED OFF THE USB TO `C:\AI\hd-instrument`; OPEN QUEUE RE-RANKED**
**The project now runs from the internal drive (`C:\AI`), not the USB (`D:\AI`).** Copy byte-verified
(255,631 files match; the substrate's own durability check PASSES -- 178,657 atoms intact). venv REBUILT at
C: with exact prior versions; `import hdlab.substrate`, `board.py self-test`, and a witness test all PASS.
All 15 `hd_*` scheduled tasks + 22 launcher scripts re-pointed D:->C:; only 6 necessary tasks enabled; 6
legacy daemons killed. Claude history + memory (689 files) migrated to the `c--AI` tag. **`D:\AI` is an
UNTOUCHED backup** until the owner deletes it.
🔌 **LANDED THIS ROUND (flag-gated, default-OFF):** Route B `ConceptSpace.track_all_content_lemmas` --
`the_reader` SOLVED change 2. The read loop can now accumulate co-occurrence for EVERY content lemma, not
just seed-known ones, giving `distributional_meaning_channel` the live coverage it needs to score the p2
gate (was ~55 pairs, structurally too few). Additive, default-OFF; existing seed-known-only path byte-for-
byte preserved (witness `test_route_b_separable_context_store.py` 5/5). **ONE PROVEN-READY DELIBERATE hdlab LANDING PENDING** (p5 precise-voice ✅ LANDED 2026-08-26 -- see below;
only `the_reader` change 1 remains -- each needs its own witness + a downstream check): (1) `the_reader` change 1 -- grounding-state
selection hook in the read loop; (2) p5 `the_reading_extractor` -- REPLACE the perceptron patient-selection
path in `hdlab/situation_reader.py` with a word-order + PRECISE-voice rule (passive -> PATIENT before the
predicate; +0.10 on passives; do not weight animacy as an English role cue). **SCOPED 2026-08-25:**
situation_reader's PATIENT selection is currently POSITIONAL-NO-VOICE (`_pick_role_mentions` = nearest
nominal strictly after the predicate = p5's inferior 0.663 arm); the precise-voice flip needs a PASSIVE
SIGNAL at that site (BE-aux within 3 tokens before the pred + past participle) that is NOT wired there
today (the `passive` construction cue lives in `frame_induction`, not at patient selection). So it is a
real multi-part change (detector + flag-gated thread through `_pick_role_mentions`/`_assign_roles` +
witness + downstream check on the situation pipeline), NOT ~4 lines. ✅ **LANDED 2026-08-26 (default-OFF
flag `precise_voice` + `_is_passive_predicate` detector on `_assign_roles`/`_pick_role_mentions`; witness
`verification/test_situation_reader_precise_voice.py` 4/4; existing situation_reader tests unchanged =
default-off byte-identical). AVAILABLE-but-default-OFF -- ACTIVATING it live (thread `toks`+`precise_voice=True`
from the read path) is the next step, gated on a downstream comprehension check.**
🗂️ **OPEN QUEUE RE-RANKED:** p1 `organ_abstains_on_two_thirds_of_v2` (goal-outcome organ refuses 2/3 --
the live goal-bearing blocker; a refusal is more tractable than a wrong answer); p2
`meaning_read_out_untested_on_the_own_metric` (the transfer GATE that unblocks the meaning-read-out WIRING
I own); p3 reliability-signal-to-oracle; p4 valence-propagation; p5 stage-1 extractor. Two integrated
problems had stale `priority:` lines cleared (`the_reader_reads_too_shallow`, `lookup_does_not_lemmatise`).
➡️ **p2 RESOLVED 2026-08-25 (EXCELLENT, re-verified PASS): the read-outs LOSE to first-order COUNTING on
the OWN metric, CI-separated, every seed -- the WordSim/substitutability wins do NOT transfer. WIRING = NO
(do NOT wire meaning_fusion / distributional_meaning_channel into the live reader for meaning assignment).**
🔎 **THE LIVE MEANING-LINE QUESTION IS NOW WHETHER THE OWN METRIC EVEN TESTS MEANING:** p2 found the metric
is carried by RAW FREQUENCY (PMI-normalising it collapses the score ~8x), so every meaning transform loses
BECAUSE it de-emphasises frequency. New priority-2 problem `the_own_metric_may_reward_frequency_not_meaning`
(phase a: build a frequency-controlled metric; phase b: re-test TOPK_GROUNDED + the 3 brain-faithful encoding
arms on it). The sub-threshold brain signal TOPK_GROUNDED (salience-select + grounded-discriminate) beats its
twin CI-separated but its CI touches zero -- promising, not yet a win.
🧠✅ **UPDATE 2026-08-25 (p2 owner-DONE re-integration): THE METRIC-FAIRNESS ANSWER IS PREVIEWED, AND POSITIVE.**
p2's final content scored the SAME ConceptNet gold as DISCRIMINATION (rank neighbours above non-neighbours)
instead of top-1 argmax: on HARD negatives (co-occurring non-neighbours) COUNT falls to `0.210` -- BELOW chance,
it PREFERS co-occurrents -- while GROUNDED reads `0.728` CI-separated, info-free twin at chance. **So the meaning
organs are NOT broken: they distinguish a true neighbour from a mere co-occurrent, which counting CANNOT; "the
read-outs lose" was a property of the frequency-dominated TOP-1 scorer.** Concreteness-controlled residual `0.648`
(the distributional/reading spoke does NOT survive -- it is a co-occurrence proxy; grounded-weighted beats equal
fusion). ⚠️ These discrimination numbers are the solver's CONTROLLED finding but NOT yet scaffold-witnessed (the
reverify covers top-1 only) -- they LAND via the metric-fairness problem. ➡️ **The meaning-line direction is now
GROUNDED-WEIGHTED DISCRIMINATION, not top-1 argmax.** (p5 also re-integrated owner-DONE: elaborate reader REPLACED
by a two-line rule, but the two-line rule is NOT the ceiling -- a filler-gap/dorsal-parser + cue-based-retrieval
FRONTIER is a new problem to package.)

### 2026-08-25 -- 🧠 **MEANING STAGE RESOLVED INTO TWO ORGANS + FULLY PACKAGED; HOURLY ARCHITECT LOOP RUNNING**
**The meaning mechanism is resolved, and it is NOT one thing -- two live organs landed this session,
scoped so neither is mistaken for the other:**
- `hdlab/distributional_meaning_channel.py` -- the SUBSTITUTABILITY specialist (synonym vs associate):
  the taught/distilled direction, reproduces AUC ~`0.84` on the licensed instrument through the live
  Route B store. The SAME direction scores rho `-0.24` on general WordSim, so it is NOT the general
  read-out. Batch-transductive orientation (label-free over the presented pairs).
- `hdlab/meaning_fusion.py` -- the GENERAL meaning read-out: complementary EQUAL-WEIGHT z-fusion of the
  reading spoke (PPMI+SVD over the Route B store) + the grounded spoke; reproduces WordSim `0.4455`,
  beats both spokes, twin loses. **DISTILLATION WAS THE BUG for general similarity; FUSION is the fix**
  (owner-accepted, aimed_reading FORWARD_WORK). Also landed: Route B separable count store
  (`ConceptSpace._ctx_counts`, default-off) + lemmatise-on-miss in `grounded_similarity` (SOLVED lookup).
➡️ **STAGE 2 STILL READS BROKEN ON PURPOSE:** organs are BUILT_NOT_PIPELINE_USED; the wins are on
BORROWED scorers; the live write rule still reads `0.051`.
🎯 **THE STAGE-2 FIX IS NOW FULLY PACKAGED as open, farmed-out problems:**
`meaning_read_out_untested_on_the_own_metric` (the no-number-crosses-scorers GATE: do the wins beat plain
counting on the substrate's OWN metric?), `no_automatic_reliability_signal_reaches_the_source_oracle`
(which-source-to-trust -- the convergent gap an oracle clears at `0.408` vs counting `0.324`),
`the_reader_reads_too_shallow_to_ground_words` (PARTIAL integrated: DEPTH solved robustly, COMPREHENSION is
a budget TRADEOFF -- unlock is reading VOLUME; read-loop changes proven-for-depth but NOT landed, need
flag-gating), `the_reading_extractor_may_not_beat_a_two_line_rule` (stage-1 simplification). **THE WIRING
(meaning read-out -> live reader) IS MINE (Q111), GATED on the transfer-test problem above.**
⏱️ **HOURLY ARCHITECT CRON (session-only, job `0d126b4a`):** each hour -- integrate any awaiting submission
(re-verify -> grade -> review -> land -> commit), map the worst-broken stage (use `data/substrate_progress.json`
directly; `substrate_map` times out on the USB), file the highest-leverage new gap. **IF THIS SESSION EXITS
THE CRON DIES -- re-create it.**
🖥️ **DRIVE MOVE (Q119) STILL PENDING:** `tools/move_repo_to_internal_drive.py` ready + authorized, waiting on
a LONG quiet window (~2-4h copy off the slow USB; all writers + other sessions idle throughout). DELETE the
cron before moving.

### 2026-08-22 -- 🚨 **THE STORE FIX IS REFUTED: IT CAN RECITE, NOT RECOGNISE**
**Addressed storage reads exact-key `0.9954` and held-out `0.1399`, against a first-order COUNTING
floor of `0.3242` (`-0.1843`, CI excludes 0).** *Info-free twin `0.0000`, scramble `0.0000`, 2AFC
positive control `0.7433` -- the instrument works, so the failure is real.* 🧠 **AND A CIRCULAR
WordNet oracle reproduces the same cliff from a new direction (`0.8787` exact-key, `0.0365` partial
cue): a property of how the CUE MEETS THE STORE, not of one mechanism.**
➡️ `store_survives_a_partial_cue` is **PRIORITY 4** -- bar = beat `0.3242` held-out CI-separated;
**a rigorous negative is an explicit PASS.**

### 2026-08-22 -- 🚨 **`read(n_sentences=N)` IS A CEILING; `max_patches` (default 4) BINDS FIRST**
`read(3000/6000/10000)` all returned `1,060` -- ONE LAP. **Raise `max_patches`, not `n_sentences`.**
🔻 *DEFLATED BY ITS OWN ENUMERATION: no cell uses the failing shape. Do NOT quote `13%`.*
✅ *Guarded in code (`short_read` on `ReadResult`).*

### 2026-08-22 -- ✅ **A REPLAYED CHECKPOINT IS NOT A REPRODUCTION; ENFORCED IN CODE**
`tools/reproduction_check.py` makes the unsafe reading unrepresentable. 🚫 *Casts doubt on NO landed
number -- only on whether re-running one verifies it.* ➡️ **Superseded in scope by the Q115 entry
(coverage `71.2%`, backlog inventoried and triaged) and by the 08-23 `reproduce.py` mode fix.**

### 2026-08-22 -- 🔑 **THE MEANING ASSET IS NOT SHORT OF WORDS; THE LOOKUP CANNOT INFLECT**
`grounded_similarity.py` is a raw-string lookup: we hold `country`, miss `countries`. **TOKEN
coverage `0.6035 -> 0.7350` via our own `normalize_lemma`, ZERO new norms** -- so *"+14,704 words to
norm" counts INFLECTED FORMS OF ALREADY-NORMED WORDS.* ⛔ **`read()` NEVER CONSULTS THE ASSET**
(`0` calls, positive-controlled). ⚠️ *ADJECTIVES unanswerable on our assets -- SimLex's `111` is
every adjective pair we own.* 🚫 **COVERAGE, NOT CAPABILITY -- no task was run.**
📎 Brief at priority 8; the verb-hole half is owned by the meaning-channel entry below.

### 2026-08-21 -- ✅ **EVICTED TO `STATUS_LESSONS.md` (search "THREE-WAY COMPARISON"): the F5
three-way comparison that set what to build on. Closed; nothing since has moved it.**

## TOP ITEM -- **THE THREE REVIEWS RE-AIMED THE WORK. TWO ORGANS, TWO OPPOSITE FAULTS.**

### 🥇 **08-23 (CURRENT): WHAT THE REVIEWS CHANGED, AND WHAT IS NOW THE BUILD**
🔻 **THE SIXTEEN-LOSSES PREMISE BELOW IS REFUTED -- read the correction before the block.** P2 built
the STRONG version of learning-from-reading and it clears the strongest floor CI-separated on all
three banks, beating the spelling floor `15-40x`, **with the curve STILL CLIMBING at `38.09M`
tokens.** *The losses tested a WEAK implementation. The route is CORPUS-LIMITED, not exhausted.*
➡️ **NEXT MECHANISM, AND IT IS BRAIN-PINNED: RELIABILITY-WEIGHTED CUE COMBINATION.** P1 showed our
fixed-weight mix lets a strong frequency prior SWAMP a weaker-but-correct grounded channel -- the
channel alone beats chance on subordinate senses (`0.4811` vs `0.3854`), the mix lands BELOW chance
(`0.1415`). **The brain does not combine cues at fixed weights; it weights each by its reliability
(Ernst & Banks 2002 is the canonical measurement). Our rule cannot express that, so it can only ever
reproduce whichever cue is louder.** 🚫 **BUT NOT ON THE BUNDLING ORGAN:** P3 says the fix THERE is
MORE INDEPENDENT SOURCE DIMENSIONS (an 11-dim signal cannot fill a 256-dim code), and a count table
with no rank ceiling is the arm that wins. **TWO ORGANS, OPPOSITE FAULTS -- DO NOT MERGE THEM.**
🚨 **AND THE BAR ITSELF IS IN QUESTION: Q117 (spelling floor `~78%` morphological leakage).**

🔴 **A DIRECTION I ALMOST SET TONIGHT AND THEN REFUTED WITH OUR OWN DATA -- READ THIS BEFORE
PROPOSING "READ MORE".** Two measurements looked like they converged on *reading volume is the
binding constraint*: P2 is still climbing at `38.09M` tokens, and the substrate's vocabulary is
still climbing at `5,200` sentences (`2,270` lemmas at `800` -> `7,334` at `5,200`). **Both are
true and the conclusion does NOT follow. Vocabulary size is an INTERNAL STATISTIC; the standing
rule is that a statistic may DIAGNOSE and never DECIDE.** The OUTCOME is measured in
`data/exp_substrate_resume_helps_v1`, and it is at the floor **in `12` of `12` arms across `3`
seeds**: SUBSTRATE grounding precision `0.0199` (**`3` hits / `151`**) against a `RANDOM_ANCHOR`
floor, paired permutation **`p = 0.2634`** -- *not separated.* **THE SUBSTRATE GROUNDS `168`
MEANINGS AND THREE ARE RIGHT.**
🔴 **AND THEN I CAUGHT MYSELF RUNNING PAST A PRE-REGISTRATION, WITHIN THE HOUR.** The cell that
DEFINES this measurement (`exp_grounding_precision_gold_v1`) pre-committed, before any number
existed: ***"(iv) fewer than ~300 scorable items -> UNDERPOWERED ... do NOT issue a verdict."***
**`0` of `12` arms reach it; max n = `151`.** ➡️ **SO "GROUNDING IS AT CHANCE" IS NOT AN AVAILABLE
CONCLUSION -- NOT MINE, AND NOT THE SUBMISSION'S "sits at the RANDOM_ANCHOR floor in every arm".**
*A pre-registration I did not write is not one I may quietly outgrow.*
🔴🔴 **AND THEN A SECOND CORRECTION THAT RETIRES THE FIRST: THE POWERED MEASUREMENT ALREADY EXISTS
AND I HAD NOT OPENED IT.** *I quoted `exp_grounding_precision_gold_v1`'s power RULE without reading
its RESULTS.* It ran **3 seeds at ~`40,000`-sentence reads**, `UNDERPOWERED: False`, `n_scorable`
**`441`/`441`/`398`**. **THE ANSWER HAS BEEN ON DISK ALL ALONG:**

| seed | n | SUBSTRATE | RANDOM (paired p) | 🔻 **TOP_COOCCURRENT** |
|---|---|---|---|---|
| `101` | `441` | `0.0272` | `0.0045` (**`0.0110`**) | **`0.0590`** |
| `20260819` | `441` | `0.0159` | `0.0023` (`0.0695`) | **`0.0476`** |
| `7` | `398` | `0.0302` | `0.0025` (**`0.0050`**) | **`0.0653`** |

## ✅✅ **08-24: THE FIRST GENUINE BRAIN-FAITHFUL WIN OF THE STRETCH -- COMBINE, DON'T SUBSTITUTE, CONFIRMED ON FAIR GOLD**
**`exp_c3_grounded_fusion_v1` (`run_mode: full`, n=`4,000` over `5,491` anchors, 5,000x paired
bootstrap). OWNER MARKED BOTH REMAINING PROBLEMS `DONE` 08-23 23:55/23:58.**
🔑 **READ THE MORPHOLOGY-STRIPPED (FAIR) GOLD, NOT THE LEAKY ONE -- THE RANKING INVERTS:**

| arm, FAIR gold | hit@1 | |
|---|---|---|
| ✅ **`FUSE_BASE_GROUNDED` -- distributional **+** grounded spoke, NO spelling** | **`0.0790`** `[0.0707,0.0875]` | **BEST ARM** |
| `GROUNDED` alone | `0.0607` `[0.0534,0.0682]` | *fusion beats it, CI-separated* |
| `A1_BASE` (flat bag alone) | `0.0459` `[0.0396,0.0524]` | *fusion beats it, CI-separated* |
| 🔻 `FUSE_BASE_GROUNDED_STRING` (**+ spelling**) | 🔻 `0.0431` | **WORSE THAN THE BAG ALONE** |
| `A5_STRINGCTRL` (honest spelling floor) | `0.0193` | *fusion beats it ~`4x`* |

➡️ **THE HUB-AND-SPOKE FUSION BEATS BOTH OF ITS OWN COMPONENTS CI-SEPARATED, AND BEATS THE HONEST
FLOOR BY ~`4x`.** *Control binds: `FUSE_RANDOM_GROUNDED` `0.0291` -- it is not "any second channel".*
⚠️ **AND THE `0.1125` "clears the floor's upper bound" HEADLINE IS THE **WEAKER** CLAIM, NOT THE
STRONGER ONE.** It uses the SPELLING channel scored on LEAKY gold -- morphology on both sides. **On
fair gold that same arm COLLAPSES to `0.0431`, below the bag alone: once the leakage is stripped the
spelling channel is ACTIVELY HARMFUL.** *The cell's own verdict is the conservative
`COMBINE_BEATS_EITHER_BUT_NOT_THE_FLOOR`, and the brain-faithful arm indeed does not clear the LEAKY
floor (`-0.0033`, CI includes 0). Quote the FAIR-gold row.*
🧠 **AND IT FITS THE NIGHT'S ONE FINDING RATHER THAN CONTRADICTING IT: fusion WORKS when the two
channels are COMPARABLE (distributional + grounded); it FAILS when one is a DOMINATING PRIOR (the
frequency prior swamps the same grounded channel, `0.4811` -> `0.1415`).** *Same missing organ: a
control that weights a source by how much it should be trusted HERE.*
🎯 **THIS IS `reader_meaning_channel`'s MISSING ADAPTER, MEASURED: z-score-fuse the distributional
cosine with the grounded sensorimotor cosine at read-out.** 🚫 **Do NOT add the spelling channel, and
score future c3-style gates against MORPHOLOGY-STRIPPED gold.**

🛑🛑 **AND A PRE-REGISTERED `STOP_IF` HAS ALREADY FIRED ON THIS WHOLE ROUTE -- `exp_corpus_capacity_
ppmi_svd_ceiling_v1` (08-18). READ THIS BEFORE PROPOSING ANY WRITE-RULE FIX.**
**`CORPUS_CAPACITY_CEILING__STOP_IF_iii_INFO_PRESENT_NO_UNSUPERVISED_FIRST_ORDER_TRANSFORM_REACHES_IT`**
*Every arm below is scored on the SAME dissociation instrument and the SAME 242-pair population:*

| arm | AUC | |
|---|---|---|
| **`C1_FITTED_ORACLE` (HELD-OUT CV, not in-sample)** | **`0.9606`** | ✅ **THE INFORMATION IS IN THE CORPUS** |
| `K1_KNOWN_ANSWER_WORDNET` | `0.9599` | *instrument works* |
| `N0_RANDOM_VECTOR_STORE` | `0.4862` | *chance* |
| **`A0_INCUMBENT` -- OUR write rule** | **`0.0710`** | `BELOW_0.5_COOCCURRENCE` |
| `B3_SECOND_ORDER_COSINE` | `0.0510` | below |
| `B2_PPMI_SVD` k=`50`/`100`/`300`/`500` | `0.0519`/`0.0285`/`0.0230`/`0.0278` | below |
| `B1_PPMI` | `0.0249` | below |

🔑 **THE INFORMATION IS PRESENT (a FITTED model reaches `0.9606` HELD-OUT) AND NO UNSUPERVISED
FIRST-ORDER TRANSFORM REACHES IT.** *PPMI, PPMI+SVD at four dimensionalities, second-order cosine,
and our own write rule ALL land in `0.02`-`0.07`, deep in the co-occurrence band.*
🔴 **THIS CORRECTS MY OWN FRAMING FROM EARLIER TONIGHT.** I wrote *"a plain distributional model over
this corpus extracts it CI-separated while ours does not."* **ON THIS INSTRUMENT NEITHER DOES -- and
OURS (`0.0710`) IS AHEAD OF `PPMI_SVD` (`0.0285`).** *P2's distributional win was on word-pair
SIMILARITY RATINGS, a different task and scorer, exactly the comparison I had already flagged as
non-transferable. Here is the direct evidence that it does not transfer.*
➡️ **SO THE PROBLEM IS NOT "OUR MECHANISM IS UNIQUELY BAD". IT IS THAT FIRST-ORDER CO-OCCURRENCE
TRANSFORMS AS A CLASS CANNOT PRODUCE SUBSTITUTABILITY FROM THIS CORPUS, WHILE THE INFORMATION IS
DEMONSTRABLY THERE.** 🚫 **DO NOT propose another unsupervised first-order transform of the
co-occurrence matrix -- that is the class the STOP_IF closed.**

🛑 **A SECOND `STOP_IF` CLOSED THE "TUNE IT HARDER" ESCAPE (`exp_tuned_count_unsupervised_
dissociation_v1`):** `TUNING_IMPROVES_ON_VANILLA_BUT_STAYS_BELOW_0.5__SUPERVISION_CONCLUSION_
SURVIVES_A_FAIRER_TEST`. *Shifted PPMI lifts `0.0519` -> `0.1144` on held-out selection and is still
nowhere near chance.* **Four tuning families tried; the ordering does not change.**

🧠 **AND THE GROUNDED CHANNEL WAS ALREADY SCORED ON THIS EXACT INSTRUMENT TOO
(`exp_sensorimotor_channel_discrimination_v1`) -- IT IS THE ONLY THING ON THE RIGHT SIDE OF CHANCE,
AND IT STILL DOES NOT CLEAR ITS OWN FLOOR:**

| arm | AUC | |
|---|---|---|
| 🔻 **`F_CONSTANT_PROTOTYPE__SM11` -- ONE VECTOR FOR EVERY WORD, ZERO word-specific information** | 🔻 **`0.6195`** | **its own floor, and the HIGHEST arm** |
| `SM11_RAW_NEG_EUCLID` | `0.6019` | above chance, **BELOW that floor** |
| `SM11_RAW_COSINE` | `0.5990` | above chance, **BELOW that floor** |
| `F_SCRAMBLE__SM11_*` | `0.4669` / `0.5000` | *chance -- controls bind* |
| `SM11_Z_COSINE` | `0.5358` | not separated |

**VERDICT `SENSORIMOTOR_DISCRIMINATION__B_AT_OR_NEAR_CONSTANT_PROTOTYPE_FLOOR`.** *A vector carrying
NO word identity beats the real grounded arms.* ➡️ **So the channel's above-chance reading is a
GENERAL property (a constant offset -- most plausibly concreteness), NOT word-specific meaning.**

## 🧱 **THE WALL -- 🔴 BROKEN 2026-08-24. READ THIS BANNER BEFORE THE SECTION BELOW IT.**
> **THE CLAIM BELOW ("NOTHING UNSUPERVISED CLEARS ITS OWN FLOOR") WAS TRUE WHEN WRITTEN AND IS NOW
> FALSE.** `where_does_a_meaning_signal_come_from_without_labels` came back SOLVED and re-verified:
> **cross-modal distillation reads `0.8388` CI `[0.8031,0.8720]`** on this exact instrument, beating
> its info-free twin's **MAXIMUM** over 200 draws (`0.7047`), with **no gold anywhere** -- the
> grounded hub TEACHES a direction over the distributional model, on `8,000` pairs whose vocabulary
> is disjoint from the instrument.
> ➡️ **SO THE SECTION BELOW IS THE STATE OF THE PROBLEM *BEFORE* THAT RESULT.** It is kept because
> every number in it still stands and is what the new arm had to beat -- but **do not quote its
> headline.**
> ⚠️ **AND THE LIMITS TRAVEL WITH THE FIX: LABEL-free but NOT RESOURCE-free (the teacher is the
> supplied Lancaster table), and TRANSDUCTIVE (orientation reads the candidate pairs' inputs).**
> 🚫 **THE SUBSTRATE ITSELF IS UNCHANGED -- stage 2 is still `BROKEN` and its write rule still reads
> `0.051`. This is a research result, not a capability, until it is wired.**

**As it stood BEFORE 2026-08-24 -- on one licensed instrument, one 242-pair population, chance
`0.4862`, known-answer `0.9599`:** **nothing unsupervised cleared its own floor.** Text transforms land at `0.02`-`0.13` (confidently
INVERTED -- they measure co-occurrence); the grounded channel lands at `0.599`-`0.602` but under a
`0.6195` no-information floor; **and the ONLY arms above `0.5` on merit are a FITTED SUPERVISED model
(`0.9606` held-out) and WordNet itself.** 🔑 **THE INFORMATION IS THERE AND EVERY UNSUPERVISED ROUTE
WE HAVE TRIED MISSES IT.** ⚠️ **THE NEXT MOVE IS NOT ANOTHER ARM ON THIS INSTRUMENT.** *Per the
owner's standing rule -- when the wheels spin, go back to brain foundationality and ask what
FUNCTION is missing -- the question is: **the brain acquires substitutability without a labelled
oracle. What does it use that a corpus does not contain?** That is a research question, not a
sweep.*

🧠🎯 **AND THE MECHANISTIC ANSWER WAS ALSO ALREADY ON DISK -- `exp_writerule_step_ladder_v1` (08-17)
AND `exp_writerule_maxpool_occurrence_v1` (08-18). THIS IS THE SYNTHESIS OF THE WHOLE NIGHT:**
**THE WRITE RULE BUILDS A CO-OCCURRENCE DETECTOR WHEN MEANING NEEDS SUBSTITUTABILITY.** On the
dissociation AUC (paradigmatic vs syntagmatic), where the WordNet known-answer arm reads `0.9599`
and every info-free floor sits at chance `~0.50`:

| arm | AUC | |
|---|---|---|
| `KNOWN_ANSWER_WORDNET_PATH_SIM` | `0.9599` | *the instrument works* |
| info-free floors (scramble / frequency / orthographic / random store) | `0.46`-`0.54` | *chance* |
| `S1_SINGLE_OCC` | `0.4173` | below |
| 🔻 **`A0_SUM` -- THE SUBSTRATE'S ACTUAL WRITE RULE** | 🔻 **`0.0510`** | **`BELOW_0.5_COOCCURRENCE`** |
| 🔻 `M1_MAXPOOL` (keep occurrences separate, best match) | `0.0299` | **WORSE** |
| 🔻 `M2_TOPK_MEAN` k=2/3/5 | `0.0264`/`0.0240`/`0.0217` | **worse still** |

🔑 **`AUC 0.051` IS NOT "AT CHANCE" -- CHANCE IS `0.50`. IT IS NEARLY PERFECTLY INVERTED.** *The
summed profile CONFIDENTLY ranks words that appear TOGETHER as similar, when the task asks which
words are INTERCHANGEABLE.* **It is not failing to learn; it is successfully learning the wrong
relation.** ➡️ **THAT EXPLAINS `TOP_COOCCURRENT` BEATING IT: the substrate is a WORSE
CO-OCCURRENCE DETECTOR THAN COUNTING CO-OCCURRENCE.**
⚠️ **AND THE OBVIOUS FIX IS ALREADY REFUTED TWICE: max-pool and top-k mean are WORSE than summing.**
🔻 **BUT THE INFORMATION IS THERE:** the ladder's decisive arm reads `BEST_SINGLE_ORACLE hit@1
0.3033` against `SUM_ALL 0.0100` and `RANDOM_SINGLE 0.0367` -- **summing is worse than picking ONE
occurrence AT RANDOM, and `30x` worse than picking the RIGHT one.** *So the gap is SELECTION, not
capacity -- and max-pool failing says we cannot yet select by best-match.*

✅ **GROUNDING IS NOT NOISE -- it beats the random floor on `2` of `3` seeds** (so my "at chance" was
wrong in that direction too). 🔻 **BUT A TRIVIAL "MOST CO-OCCURRING WORD" COUNT BEATS IT `2-3x` ON
`3` OF `3` SEEDS.** *The cell PRE-COMMITTED this reading: "(iii) ... ties TOP_COOCCURRENT -> what it
has learned is co-occurrence, this project's standing diagnosis arriving on a third instrument."*
**The observed case is WORSE than the tie it anticipated.** 🎯 **THE MECHANISM IS BEATEN, ON ITS OWN
TASK AND ITS OWN GOLD, BY THE SIMPLEST SUMMARY OF THE SAME TEXT -- and "read more" does not follow,
because these are already `10x` the reading volume of the underpowered arm.**
⚠️ **AND A LIMIT I CHECKED ON MYSELF: the distributional result is Spearman rho on word-pair
similarity; ours is anchor-assignment precision against ConceptNet. DIFFERENT TASKS, DIFFERENT
SCORERS -- the numbers may NOT be compared.** *Each is judged only against ITS OWN floor. I withdrew
"the gap IS the extraction mechanism" for resting on the forbidden verdict.*
*Witness: `test_grounding_correctness_has_never_been_measured_at_power.py`.*

### 🗄️ **08-22 (SUPERSEDED IN ITS PREMISE, KEPT FOR ITS SCOPING CORRECTION)**
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

- 🏗️ **OPERATING MODEL (OWNER 08-22): STRATEGY SESSION + SOLVER SESSIONS.** This session keeps the  10k view, writes briefs and INTEGRATES; solvers solve one bounded problem. **THE ORDER LIVES IN EACH  `notes/problems/<slug>/PROBLEM.md` FRONTMATTER (`priority:`) -- ENUMERATE, NEVER MIRROR.** *ENUMERATED FROM DISK 08-23 23:0x: `10` open (priorities `1`-`10`, contiguous), `8` solved+reviewed. **THE PREVIOUS TEXT HERE READ `11` open / `5` reviewed -- I MIRRORED A REMEMBERED COUNT ON THE VERY LINE THAT SAYS ENUMERATE.** Q111: solvers never write `hdlab/`.* `notes/problems/README.md`
- ✅ **TWO OF THE THREE ARE NOW REVIEWED (08-23 late). BOTH RE-VERIFIES PASS; I THEN AUDITED THE
  ARGUMENT, NOT THE ARITHMETIC, AND BOTH AUDITS PAID.**
  - 🥇 **P2 `does_learning_from_reading_deserve_to_continue` -- EXCELLENT.** *I attacked it with a
    comparator it did not use (it ran TWO supplied arms and quoted the weaker) and **it held**: the
    WordSim win survives against the stronger one CI-separated, and all three benchmarks clear the
    strongest floor's UPPER bound.* ➡️ **MY BRIEF'S PREMISE IS REFUTED -- the sixteen prior losses
    tested a WEAK implementation; the route is CORPUS-LIMITED, not exhausted (curve still climbing
    at `38M` tokens).** 🔻 *Gap: no scored population saved, so the coverage question needs a re-run.*
  - 🥈 **P1 `reader_meaning_channel` -- STRONG, and its FRAMING IS WRONG IN A WAY THAT MATTERS.**
    Headline stands (aggregate is honest, and it STRENGTHENED its own floor). **But `84%` of that
    aggregate is items where a frequency prior CANNOT lose. On the `53` words where the question is
    live: grounded channel ALONE `0.4811` (above chance `0.3854`), channel **+** prior `0.1415`
    (below chance), prior alone `0.0000` by construction.** ➡️ **THE PRIOR SWAMPS THE CHANNEL RATHER
    THAN REPLACING IT -- adding it costs `0.3396`, more than the channel's whole margin. "The channel
    adds nothing" and "our mixing rule destroys it" predict the SAME aggregate and imply OPPOSITE
    next steps.** **The mechanism under test is now the COMBINATION RULE (reliability-weighted cue
    combination), not the channel.** *Witness: `test_the_prior_swamps_the_grounded_channel_not_replaces_it.py`.*
  - 🥈 **P3 `the_bundle_destroys_meaning_but_replacing_it_hurts` -- STRONG. IT RETIRES A FLOOR.**
    **Its real finding: the string control beating us ~2:1 is `78%` MORPHOLOGY** (`0.0867` ->
    `0.0193` on stem-stripped gold, overlapping its own info-free twin). ➡️ **THAT IS Q117.**
    🔻 *But its headline "bundling is NOT the bottleneck" is contradicted by its own paired
    bootstrap: `RAW_COOC − A1_BASE = +0.0125 CI[+0.0057,+0.0195]`, CI-SEPARATED -- **deleting
    superposition BEATS the shipped flat bag by `26%` of its own score.** Both are true: removing
    the bundle HELPS and does not help ENOUGH. It grounded "not the bottleneck" on losing to the
    floor it then demolished.* 🎯 **BUILD TARGET HERE = MORE INDEPENDENT SOURCE DIMENSIONS (an
    11-dim signal cannot fill a 256-dim code); the count table that wins has no rank ceiling.**
    ⚠️ **NOTE THE TWO BRIEFS POINT OPPOSITE WAYS -- P1 says the COMBINATION RULE is the target, P3
    says it is NOT. Different organs, different faults. DO NOT MERGE THEM.**
    *Witness: `test_removing_the_bundle_helps_it_just_does_not_help_enough.py`.*
- 🚨 **THE THREE SUBMISSIONS LANDED 08-23 AND WERE FOUND BY ENUMERATING DISK, NOT BY ANY NOTIFICATION.**
  **Found by ENUMERATING `SOLVED.md` on disk, not from any notification.** Each has a `reverify:` line
  in its frontmatter; **run it before believing the headline, then write the `review:` /`review_text:`
  frontmatter into the matching `PROBLEM.md` (that is what the GUI renders).**
  | when | priority / slug | its own status | the claim, in short |
  |---|---|---|---|
  | 17:40 | **2** `does_learning_from_reading_deserve_to_continue` | **SOLVED** | **YES, and my brief's premise is REFUTED** -- surprise-weighted PPMI-SVD over 38.09M tokens clears the idf-count floor CI-separated on all three banks and is **STILL CLIMBING at the corpus ceiling**, so the route is corpus-limited, NOT exhausted. *Loses verbs to the supplied hub (`0.129` vs `0.266`).* |
  | 19:34 | **3** `the_bundle_destroys_meaning_but_replacing_it_hurts` | **SOLVED** | **The bundling is NOT the c3 bottleneck** -- removing superposition ENTIRELY scores BELOW the spelling floor. **And ~`78%` of that spelling floor is MORPHOLOGICAL LEAKAGE**: on stem-stripped gold it collapses `0.0867`->`0.0193` while the flat bag holds and BEATS it. |
  | 21:23 | **1** `reader_meaning_channel` | **REFUTED** | The meaning gap is **ARCHITECTURAL, not MODAL** -- the grounded hub plus the sense-frequency prior does NOT clear the most-frequent-sense floor (`0.4702` vs `0.4778`, not separated). *It also REPLACES that instrument's shipped uniform floor with a stronger one.* |
  ⚠️ **DO NOT PROPAGATE ANY NUMBER ABOVE UNTIL ITS `reverify:` HAS BEEN RUN HERE.** *Five submissions
  were verified this way today and BOTH failures found were in MY checker, never in a submission --
  so the review is real work, but the prior says start by suspecting the tool.*
- 🧠 **THE MEANING CHANNEL: SEVEN MEASUREMENTS 08-23, ALL IN
  `notes/problems/reader_meaning_channel/` WITH AN ORIENTATION MAP AND A REVERIFY PER FINDING.
  READ THE BRIEF, NOT THIS BULLET, BEFORE BUILDING.**
  🚨 **THE WALL: our channel reads `+0.0000` on verbs; the supplied sensorimotor one reads
  `+0.3107` on the same benchmark.** *Not a subtraction -- different coverage; "ours is ABSENT where
  this one is PRESENT".*
  🔻 **AND FOUR THINGS DO NOT WORK:** it **cannot gate links alone** (`66%` hit / `37%` false alarm,
  no threshold better than the one already set); **storage is fine but COMBINING destroys** (2
  distractors halve it); **sparsity** and **an addressed slot** both fail to rescue that.
  🔻🔻 **AND TWO LANDED CELLS ALREADY REFUTED THE OBVIOUS REMEDY -- I FOUND THEM AFTER
  MEASURING, BY CHECKING HOW THE READER CONSUMES THE VECTOR.** `exp_structured_code_vs_flat_bag_c3_v1`
  = **`STRUCTURE_HURTS`** (`-0.0113`, CI `[-0.0195,-0.0030]`, CI-separated BELOW);
  `exp_perirhinal_conjunctive_readout_c3_v1` = **`CONJUNCTIVE_HURTS`** (no conjunctive arm beat the
  flat bag). **`hdlab/perirhinal_conjunctive.py` already exists as a default-off drop-in, and its
  docstring states my finding better than I did.**
  ⚖️ **WHAT SURVIVES: a measured COST (`62%` per sentence) -- a property of representations.**
  🔻 **WHAT DOES NOT: "so replace the flat bag". That is exactly what both cells tested and both
  found WORSE.** *My test asks whether INDIVIDUAL WORD MEANING survives; task c3 may not need it --
  if similarity-by-shared-context-words is what it wants, blending is the FEATURE.*
  ➡️ **HONEST STATE: a measured cost with NO demonstrated benefit, against two landed refutations
  of the obvious remedy. A property of a representation is not a licence to change it.**
  🔑 **AND A BIGGER ALARM FROM THE SAME RECORD: `A5_STRINGCTRL 0.0870` vs `live base 0.0480` -- A
  STRING-MATCHING CONTROL BEATS THE LIVE SYSTEM ~2:1 ON THAT TASK. That outranks this thread.**
  🧠✅ **ONE THING DOES: SEGREGATION AT EQUAL BUDGET.** *Same `D=256` both ways.* **Segregation wins
  at every `k`: at `k=16`, a 16-dim isolated slot reads `+0.1949` vs a 256-dim superposed `+0.0479`.**
  📐 **`8` dims/slot is the practical floor** (`+0.1537`, over half full resolution); below that
  both schemes are losing. ⚠️ **SCOPE: ATTRIBUTE segregation, NOT per-item** -- addressing is free
  only when slots are TYPED. `32` attribute streams fit; per-item gives `2.56` dims at 100 items.
  🎯 **AND THE LIVE COST IS NOW MEASURED, NOT SWEPT: `context_vector` is a
  "bag-of-content-words bipolar bundle", so `k` = CONTENT WORDS/SENTENCE = median `6` over 3,998
  real sentences. At `k=6` the superposed vector retains `37.6%` of baseline (`+0.1095` vs
  `+0.2914`) -- **the reader throws away ~`62%` of the meaning signal PER SENTENCE, and a 42-dim
  isolated slot would carry MORE than the full 256 shared (`+0.2343`).**
  ⚠️ *Separate from the known `sign()` issue (`+0.0245`-`+0.0267` for dropping it) -- this is the
  BUNDLING, not the normalisation. Both are live.*
  ➡️ **THE BUILD LINE: meaning gets its OWN ATTRIBUTE-TYPED SLOT, separate from whatever else the
  reading loop accumulates. NOT a slot per word -- I nearly wrote that.**
  🧠 *Brain result: somatotopy holds at power (ACTION − PERCEPTUAL on verbs `+0.0651`
  `[+0.0306,+0.1005]`); the noun half is CLOSED AS UNANSWERABLE (~`20,800` pairs needed, we own
  `666`).* ⚠️ **STANDING PROHIBITION: do NOT raise `GROUNDED_CAP`** -- the `0.05` gap is what makes
  "contribute, do not decide" enforceable in code.
- ✅ **Q115 EXECUTED AND ITS TRIAGE CLOSED (08-23): new cells GATED at commit; backlog inventoried.**
  🔻 **COVERAGE `~21%` IS WITHDRAWN -- the truth is `71.2%`** (`3,495` of `4,908` re-runnable).
  Funnel: `1,413` replay -> `425` assert a result -> `135` cited -> `29` lack a floor -> `20` claim a
  capability -> `14` after 6 turned out to HAVE floors. **🔑 AND THE QUESTION WAS WRONG: a re-run
  verifies the ARITHMETIC, NOT THE ARGUMENT -- a result with no floor re-runs and still has no
  floor.** *Proven by running one: `132` of `132` fields identical, still `HARD_PASS` at `1.000` on
  `n=10`.* 🎯 **OUTCOME: one row acted on and ITS FLOOR TIES** (a dictionary scores
  `1.000/1.000/1.000` on the same 160 trials); **the OTHER no-floor row's criticism was WRONG AGAINST
  US** (*"the sweep never bit"* -- a random baseline breaks inside that range where it held `1.0000`).
  **ORGAN_MAP corrected at both citations.** ⚠️ *My detectors were wrong THREE times -- JSON `null`
  literals, floor-shaped key names, the substring "cited" test. Each caught by reading an actual row;
  the citing documents beat every regex I wrote.*
  *Full sequence: `notes/THE_Q115_TRIAGE_FOURTEEN_RESULTS_WANT_A_RERUN_2026-08-23.md`.*
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
- 🔧 **COORDINATION FIXED 08-23:** *`dispatch_queue.py announce` adds-and-claims in one step, so starting NEW work is announceable -- previously only pre-existing rows could be claimed.*
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
