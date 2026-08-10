# Pre-registration: exp_propara_decisive_inference_arm1_v3_stateful_verb_v1

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator brain-foundational-fix follow-up
to v1 (HARD_FAIL: order-invariant priors) + v2 decomposition (HARD_FAIL_PRIOR_CONFOUNDED). Drill
note (pre-registered mechanism): `notes/research_propara_content_driven_order_dependent_state_
update_2026-08-10.md`.

## Prior-work check (SUBSTRATE-KB)
Same arc as v1/v2 (top hit cosine 0.3096 FrameNet, no prior arc cell > 0.30). Direct
brain-foundational-fix follow-up on v2's own landed decomposition; novelty inherited.

## Diagnosis being fixed (from the drill)
v1/v2 RETRIEVE = memoryless per-step BoW classifier (== ProPara's WEAKER ProLocal baseline);
VALIDATE = content-blind index-window monotonicity (survives scramble by construction). Neither
does `state_t = f(state_{t-1}, content_t)`. The brain's homologous mechanisms (SEM event-
segmentation, Kintsch C-I, Zwaan Event-Indexing) are ALL sequential state-conditioned recurrences,
which is what makes content-use order-dependent (scramble-clean). ProGlobal's
`c_i = softmax(W[mu_i; c_{i-1}])` already validated this direction on ProPara itself.

## The fix (ProGlobal/NCET/ProStruct-precedented)
- **Verb-class content signal** (`verb_classes`): a curated CREATE/DESTROY/MOVE-class predicate
  lexicon replaces raw BoW (Gupta&Durrett 2019: verb tokens are the dominant content signal on
  this task, -5.5pts on ablation). Coverage on ProPara's actual vocabulary is MEASURED
  (`verb_coverage_frac`), not assumed (drill's predicted single point of failure = sparsity).
- **Sequential + state-conditioned firing** (`_assign_verb_stateful`): walk sentences in the order
  PRESENTED (natural for the natural arm; SCRAMBLED for the scramble arm -- the loop does NOT
  secretly re-sort by true index), maintaining an existence-state + a pointer into the canonical
  event sequence [CREATE?, MOVE*m, DESTROY?] (from the oracle event-COUNT multiset -- same grant as
  v1/v2). Fire the next expected event iff the presented sentence carries the matching verb class
  AND the state allows it (CREATE only if not-yet-created; MOVE/DESTROY only if exists). Firing
  advances the pointer + updates state; the event is assigned to that sentence's TRUE step. Unfired
  events (sparse coverage) fall back to random unused true steps (content-free, same as the
  prior-lesion) so `content_delta` isolates the verb-driven timing benefit. Under scramble a verb
  encountered at the wrong point in the state trajectory mis-fires or is skipped -> the content
  contribution degrades = emergent order-dependence.
- All arms wired through the same per-paragraph `AccumulateRegister` decode path (parity, organ
  load-bearing).

## Controls (dual, both mandatory per the drill)
- **PRIOR-LESION / content-lesion** (`_assign_prior_lesion`): TRUE order, full oracle multiset,
  canonical sequence placed at random INCREASING true steps (monotonicity-respecting, ZERO
  content). Isolates the content contribution orthogonally to scramble (scramble alone is
  insufficient -- monotonicity is order-invariant). content_delta = reasoning - prior_lesion.
- **8 scramble seeds** (7,17,29,41,53,71,83,97) on TEST -- the content-delta must collapse.

## Metric scope (per the decomposition + coordinator)
- **PRIMARY / claim axis = LOCALIZATION official F1 = mean(moves.f1, conversions.f1)** -- the
  categories that REQUIRE step localization (the coordinator's stated HARD-PASS gate: "beats the
  prior-lesion control on the localization subset"; v2 per-category evidence: content lives in
  moves/conversions).
- **EXISTENCE official F1 = mean(inputs.f1, outputs.f1)** -- prior-solvable by the oracle count
  grant (prior_lesion scores ~1.0 here). Reported SEPARATELY, NEVER inside the comprehension claim.
- **FOCUS unmentioned macro-F1** -- reported as a SECONDARY diagnostic. NOT a gate (see DEV
  finding below): on the hardest unmentioned subset the verb content genuinely cannot beat random
  scatter (Gupta&Durrett ceiling: content caps near baseline on unmentioned entities that need
  cross-step propagation / world-knowledge, not local verb cues), AND the focus macro-F1 has a
  perverse property (rewards the random-scatter lesion for occasionally landing a rare implicit
  event on an unmentioned step; penalizes the verb mechanism for correctly ABSTAINING where there
  is no evidence). Gating on focus would penalize the mechanism for being right.

## HARD-PASS / HARD-FAIL bands (reframed per drill: the prize is SCRAMBLE-ROBUSTNESS, not magnitude)
- `CONTENT_DELTA_LOC_MIN_POSITIVE = 0.02`: reasoning localization F1 must beat the prior-lesion by
  >= this (natural order). DEV MEASURED: +0.026.
- `SCRAMBLE_CLEAN_MEDIAN_HARD_PASS = 0.30`: median `retained_frac_loc` (= (scramble_loc -
  lesion_loc)/(reasoning_loc - lesion_loc)) across the seeds must be < 0.30 -- the localization
  content-delta collapses scramble-clean (per the drill's tightened all-seed target).
- `SCRAMBLE_FRAGILE_MEDIAN_HARD_FAIL = 0.55`: median retained_frac_loc > this = the win did not
  meaningfully depend on order -> HARD_FAIL.
- **HARD-PASS** iff content_delta_loc >= 0.02 AND median retained_frac_loc < 0.30 -> the FIRST
  genuinely ORDER-DEPENDENT, scramble-clean content-driven localization signal of the program.
- **HARD-FAIL** iff content_delta_loc < 0.02 (verb content decorative) OR median retained_frac_loc
  > 0.55 (still fragile -- lexicon-sparsity localized).
- **MIDDLE_BAND** = partial fix (positive content but scramble collapse inconsistent, median in
  [0.30, 0.55]).
- Infra gates (HARD_FAIL_INFRA): arms_differ, decode_fidelity >= 0.99 both arms.

## HP_SCOPE
`{content_delta: [content_delta_loc_positive_over_prior_lesion, content_delta_loc_scramble_clean_median]}`.
Baselines + prior_lesion are decomposition references, not claims under a HARD-PASS gate.

## Cell-template mandates
arms_differ (META_RULE_AF; asserted self-test + recorded); final_metrics_atomicity tmp_replace;
except SystemExit before except Exception (grep-verified, only comment hits `except:`);
crlb_n/a; calibration_check default_ok (DEV-calibrated, pinned before TEST); deterministic_seeding
(hashlib.sha256-seeded rng + scramble perms, no Python hash()/list(set())); progress_logging
print_flush_true.

## Compute architecture
Sequential-CPU, justified: curated-lexicon lookup + discrete state-machine assignment + FHRR
decode at d=512 over <=16-event registers; no batching opportunity. MEASURED smoke 3.2s (dev, 2
seeds); TEST + 8 seeds expected ~15-25s. Run INLINE/LOCALLY foreground, not queued.

## Smoke findings (DEV, 2 scramble seeds) -- DEV-calibration, decision pinned before TEST
**MEASURED@data/exp_propara_decisive_inference_arm1_v3_stateful_verb_v1_smoke/metrics.json (dev,
43 paragraphs, 3.2s):**
- verb_coverage_frac = 0.612 (61% of sentences carry a verb-class hit -- NOT the sparsity failure
  the drill flagged as the likely single point of failure).
- **LOCALIZATION (primary claim axis):** prior_lesion loc 0.4195 (moves 0.300 / conversions 0.539),
  reasoning loc **0.4455** (moves **0.357** / conversions 0.534) -> **content_delta_loc = +0.026,
  driven entirely by MOVES (+0.057)**. Scramble: both seeds drop loc back to ~lesion (scr_loc
  0.4140 / 0.4225 vs lesion 0.4195) -> **median retained_frac_loc = -0.048** (collapses
  scramble-clean). -> DEV HARD_PASS on the localization axis.
- **FOCUS (secondary, reported):** content_delta_focus = **-0.027** (reasoning 0.320 < prior_lesion
  0.347). On the unmentioned subset verb content does NOT beat random scatter -- the honest ceiling
  + the focus-macro-F1 perverse-reward property described above. This is why the focus axis is
  NOT a HARD-PASS gate (documented decision, made on DEV before TEST -- the coordinator's own
  HARD-PASS spec is on the localization subset).
- **EXISTENCE (separate, never in claim):** prior_lesion 1.000, reasoning 0.966 (verb-firing
  slightly mis-times some CREATE/DESTROY vs the count-grant's trivial-perfect existence answer).
- Infra: arms_differ True, decode_fidelity 1.0 both arms.

**Decision pinned before TEST (calibrate-on-dev protocol):** claim on the LOCALIZATION axis;
report FOCUS + EXISTENCE separately and transparently. Bands above frozen. The TEST run (8 seeds)
is the decisive check of whether the +0.026 localization content-delta (a) holds on held-out data
and (b) collapses scramble-clean across MANY seeds (n=2 on dev is too thin: per-seed
retained_frac_loc was [-0.21, +0.115], noisy because the +0.026 denominator is small).

## Full findings (TEST, 8 scramble seeds) -- HARD_PASS (genuine, modest, moves-specific)
**MEASURED@data/exp_propara_decisive_inference_arm1_v3_stateful_verb_v1/metrics.json (test split,
54 paragraphs, 8 scramble seeds; run_mode=full, no crash, arms_differ=True, decode_fidelity=1.0
both arms, verb_coverage=0.581).**

**LOCALIZATION (primary claim axis):** prior_lesion loc 0.3445 (moves 0.347 / conv 0.342),
reasoning loc **0.3715** (moves **0.429** / conv 0.314) -> **content_delta_loc = +0.027**, which
REPLICATES the DEV +0.026 on held-out TEST (not a dev-overfit metric choice). The signal is
**MOVES-specific: moves delta = +0.082** (0.347 -> 0.429; reasoning also beats every baseline's
moves, best baseline bow_singlestep=0.380); conversions delta = -0.028 (the verb mechanism
slightly HURTS the paired create+destroy conversions category). Honest scope: the content gain is
concentrated in MOVE localization, where the verb-class signal (flow/move/enter/fall/rise...) is
cleanest.

**SCRAMBLE control (the load-bearing test), retained_frac_loc across 8 seeds =
[0.111, 0.204, 0.167, 0.778, 0.278, 0.815, 0.111, 0.167], median 0.185, mean 0.329.** 6/8 seeds
collapse (< 0.30); every scramble arm regresses toward the content-lesion (scramble loc all in
0.347-0.367 vs reasoning 0.3715, lesion 0.3445). **Median 0.185 < 0.30 -> scramble-clean by the
pre-registered band -> HARD_PASS.** Honest caveat: 2/8 permutations (seeds 41, 71) do NOT collapse
(retained 0.778, 0.815) -- some random reorderings happen to preserve local move-verb ordering, so
the collapse is by MEDIAN, not unanimous. The distribution is bimodal (6 tight in 0.11-0.28, 2
outliers ~0.8); the median is the robust statistic and it is cleanly in the collapse zone.

**FOCUS (secondary, reported not gated):** content_delta_focus = +0.010 (reasoning 0.376 vs
prior_lesion 0.366) -- essentially flat / at ceiling on the hardest unmentioned subset, consistent
with Gupta&Durrett (content caps near baseline on unmentioned entities). Not a gate (see metric-
scope decision above). On DEV it was -0.027; the sign is noise around ~0 -- the honest read is
"content cannot crack the unmentioned subset," unchanged from v2.

**EXISTENCE (separate, never in claim):** prior_lesion 1.000 (count grant trivially perfect),
reasoning 0.980 (verb-firing slightly mis-times some CREATE/DESTROY). Correctly excluded from the
comprehension claim.

**VERDICT: HARD_PASS_ORDER_DEPENDENT_LOCALIZATION_SIGNAL.** The brain-foundational fix (sequential,
state-conditioned, verb-class-gated firing = state_t = f(state_{t-1}, content_t)) produces the
FIRST genuinely ORDER-DEPENDENT, scramble-clean, content-driven localization signal of the
program: a +0.027 localization-F1 content-delta over the content-lesion (driven by +0.082 on
MOVES), replicated held-out DEV->TEST, that collapses toward the lesion under scramble in 6/8
permutations (median retained 0.185). Per the drill's honest reframing, the PRIZE is scramble-
robustness, NOT magnitude -- and the magnitude is genuinely small and moves-specific, exactly as
the Gupta&Durrett ceiling predicted. This is NOT a large comprehension win and does NOT crack the
unmentioned subset (still at ceiling). It IS the first evidence in the program that the substrate's
inference organs, given a state-conditioned content signal, use content in a genuinely order-
dependent way on real prose -- the qualitative thing v1/v2 lacked. Recommended next step: this
localization/MOVES signal is the genuine thread to pull into ARM 2 (extracted structure), where the
verb signal must be extracted rather than oracle-gated; and to strengthen the collapse consistency
(2/8 non-collapsing seeds) by tightening the verb->state gating (e.g. participant-mention-weighted
verb evidence) before scaling.
