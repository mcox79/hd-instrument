# exp_dev hand-off -- research: continuous-truth biology 3x

Filed-by: research sub-agent (2026-06-09)
Trigger: notes/research_drill_continuous_truth_biology_3x_2026-06-09.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Biology handles continuous-truth and probabilistic inference via three layered mechanisms:
(1) population codes that implicitly represent probability distributions over continuous
variables, (2) energy-based attractor dynamics that provide continuous-valued stable states,
and (3) predictive coding hierarchies that encode surprise rather than raw input.

All three have direct analogs in substrate's existing FHRR complex-valued representation.
The cheapest path (rank 1) requires no new mechanism -- only exposing the FHRR complex
magnitude as a continuous truth value rather than thresholding it. This addresses the
HARD BLOCK on vague predicates and Sorites-class queries.

The C1-FACT fact-recall=0 issue (memorization without generalization) is addressed by
anchor rank 5 (ACTIVE-INFERENCE-SUBSTRATE): iterative hypothesis refinement converts
single-shot lookup into a verification loop that can chain across multiple substrate
retrievals before committing to an answer.

All rank 1-3 anchors are CPU-only and run on the local laptop runner. No cloud dispatch
needed for the pre-tests.

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. CONT-TRUTH-FHRR -- Highest priority

Anchor pointer: CONT-TRUTH-FHRR-T1 (new; not yet queued)
Substrate-product reading: FHRR complex magnitude varies monotonically with how well a
  stored entity satisfies a scalar predicate. Exposing this as a float rather than a
  Boolean threshold enables ranked retrieval of vague predicates ("tall", "old", "many").
  Directly addresses substrate HARD BLOCK on continuous-truth gradients (drill 8).
Tier hint: CPU laptop; ~30 min wall; no GPU needed
Why-now: Zero new mechanism. Change is in output consumption (float vs Boolean). Cheapest
  possible test. Should ship in the next exp_dev cycle.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: Spearman rho(retrieval cosine, scalar distance from threshold) > 0.70 on
             N=100 test instances spanning clearly-above / borderline / clearly-below
  HARD-FAIL: rho < 0.30 (cosine not monotone with truth value; FHRR magnitude
             encoding insufficient for continuous-truth; alternative mechanism required)
  MID-BAND: rho in [0.30, 0.70] -- partial monotonicity; investigate noise sources
             and whether fractional binding refinement improves separation

Setup guidance: encode N=100 entities with a scalar property; 20 "clearly above threshold",
  60 "borderline" at varying distances, 20 "clearly below threshold". Bind [ENTITY,
  PROPERTY, VALUE] using FHRR fractional binding. Query with threshold vector. Measure
  cosine vs scalar distance correlation.

### 2. POPULATION-SUBSTRATE -- Second priority

Anchor pointer: POPSUBSTRATE-T2 (new; not yet queued)
Substrate-product reading: N=10 stochastic perturbations of the same query produce an
  empirical distribution of retrieval results. The variance of cosine scores is a
  calibrated uncertainty metric: near-zero for unambiguous queries, high for ambiguous
  queries. This gives the system a principled confidence score without analytic integration.
Tier hint: CPU laptop; ~30 min wall
Why-now: Independent of T1. If T1 HARD-FAILs, T2 is still needed (uncertainty estimation
  is orthogonal to truth-gradient estimation). Can run in parallel with T1.

Pre-reg bands:
  HARD-PASS: mean variance(cosine) for ambiguous queries > 3x mean variance for
             unambiguous queries (N=10 samples, 10 queries per group)
  HARD-FAIL: variance ratio < 1.5x (stochastic perturbation does not differentiate
             query certainty; noise model insufficient)
  MID-BAND: ratio in [1.5x, 3x] -- some differentiation; test larger N or different
             noise model

Setup guidance: 10 "unambiguous" queries (single clear answer in KB), 10 "ambiguous"
  queries (2+ plausible answers). Add Gaussian noise epsilon ~ N(0, sigma^2) to query
  vector; sweep sigma in [0.01, 0.05, 0.10]. Run N=10 passes per query. Measure
  variance of cosine scores across passes. Report variance ratio at best sigma.

### 3. PREDICTIVE-CODING-SUBSTRATE -- Third priority

Anchor pointer: PREDCODE-SUBSTRATE-T3 (new; not yet queued)
Substrate-product reading: Storing prediction errors (deviations from category mean)
  rather than raw values encodes surprisingness. Atypical instances have larger deviation
  magnitude. This compresses storage for typical instances and preserves signal for
  atypical ones -- addressing the memorization-without-generalization issue.
Tier hint: CPU laptop; ~60 min wall (requires category mean precomputation)
Why-now: Prerequisite for active inference. If deviation encoding does not separate
  typical from atypical, the active-inference loop has no surprise signal to act on.

Pre-reg bands:
  HARD-PASS: mean deviation magnitude for atypical instances > 2.0x typical (N=50
             typical, N=10 atypical in same category)
  HARD-FAIL: ratio < 1.3x (deviation encoding not separable; predictive coding benefit
             not realizable in FHRR substrate)
  MID-BAND: ratio in [1.3x, 2.0x] -- partial separation; investigate whether larger
             category sample size improves ratio

Setup guidance: Define a category with 50 typical instances and 10 atypical instances.
  Compute category mean embedding. For each instance, compute deviation = instance_vec -
  category_mean_vec. Store deviation magnitude. Measure ratio of mean deviation magnitude
  for atypical vs typical groups.

### 4. BAYESIAN-SUBSTRATE-PRIORS -- Fourth priority (medium cost)

Anchor pointer: BAYESIAN-PRIORS-T4 (new; not yet queued)
Substrate-product reading: Store context-specific prior distributions as substrate
  bindings. Evaluate scalar predicates against the retrieved prior rather than a global
  threshold. Implements context-dependent truth ("tall for a basketball player" vs "tall
  for a child") using only existing substrate operations.
Tier hint: CPU laptop; ~45 min wall
Why-now: Depends on T1 showing that cosine encodes truth gradient. Only actionable
  if T1 MID-BAND or HARD-PASS. Do not dispatch if T1 HARD-FAIL.

Pre-reg bands:
  HARD-PASS: same height value rated as higher truth-score against basketball-player prior
             than general-adult prior; effect size > 0.15 cosine units
  HARD-FAIL: no significant difference in truth-score across contexts (< 0.05 units);
             context-dependent thresholds not achievable via prior binding

### 5. ACTIVE-INFERENCE-SUBSTRATE -- Fifth priority (highest ceiling, C1-FACT relevance)

Anchor pointer: ACTIVE-INF-T5 (new; not yet queued)
Substrate-product reading: Iterative hypothesis refinement loop: generate hypothesis h,
  retrieve nearest vector r, compute residual e = r - h, update h' = h + alpha*e. Iterate
  until convergence. Directly addresses C1-FACT fact-recall=0 by converting single-shot
  lookup into a multi-step verification loop.
Tier hint: CPU laptop; ~60-90 min wall; may need remote_cpu if iteration count is high
Why-now: Addresses the open C1-FACT issue. Also relevant to multi-hop revival (iterative
  retrieval for K-hop chains). Prerequisite: T3 should pass (deviation signal needed
  for convergence criterion). Can be tested independently if T3 is deferred.

Pre-reg bands:
  HARD-PASS: iterative refinement converges in <= 5 iterations for 2-hop chains AND
             final answer accuracy > single-shot accuracy by >= 0.10 F1
  HARD-FAIL: does not converge in 10 iterations (exponential blowup) OR no accuracy
             improvement over single-shot retrieval
  MID-BAND: converges in 5-10 iterations with modest accuracy improvement (< 0.10 F1);
             try larger alpha or different update rule

---

## Dispatch order

T1 and T2 in parallel (independent; both CPU; both 30 min).
T3 after T1 results are known (T3 is most useful if T1 MID-BAND or HARD-PASS).
T4 requires T1 HARD-PASS or MID-BAND; can be dispatched alongside T3.
T5 is highest ceiling; dispatch after T3 results are known. Do not defer indefinitely
  -- C1-FACT is an open issue and T5 is a direct gate on resolving it.

---

## Context pointers

- Research note (full analysis with all 9 levels + 19 citations):
  d:/AI/hd-instrument/notes/research_drill_continuous_truth_biology_3x_2026-06-09.md
- C1-FACT open issue (fact-recall=0, memorization without generalization):
  d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Prior dismissed-capabilities drill (defeasible logic, analogy, ToM):
  search notes/ for research_drill containing "dismissed" or "defeasible"
- Multi-hop revival priority:
  d:/AI/hd-instrument/memory/project_multihop_revive_priority.md
- FHRR fractional binding reference:
  d:/AI/hd-instrument/hdlab/ (fractional binding implementation)
- Substrate capability map:
  d:/AI/hd-instrument/data/substrate_capability_map.md

---

## Contract section

This hand-off is research-to-experiment. The 5 anchor specs (T1-T5) are provided as
pre-reg recommendations. exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if empirical baseline differs)
- Implementing test scripts (FHRR fractional binding test harness, noise injection,
  deviation encoding, iterative retrieval loop)
- Assigning to correct queue (T1-T4 are CPU laptop; T5 may need remote_cpu if iteration
  count is high)
- Writing verdict notes for each test per standard protocol
- Escalating T5 HARD-PASS to orchestrator for cap_map update on continuous-truth rows
  and C1-FACT resolution

## Autonomy declaration

exp_dev may dispatch T1, T2, and T3 independently without orchestrator approval (all
CPU pre-tests, low cost, low risk). T4 requires T1 non-HARD-FAIL. T5 dispatch requires
T3 results or explicit orchestrator authorization to skip T3 gate. A T5 HARD-PASS that
would resolve C1-FACT and update the continuous-truth cap_map row MUST be escalated to
orchestrator before any cap_map annotation is finalized.
