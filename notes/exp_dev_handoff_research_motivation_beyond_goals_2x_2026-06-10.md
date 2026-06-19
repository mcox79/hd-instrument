# exp_dev hand-off -- research: motivation beyond goals (2x)

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_motivation_beyond_goals_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist
(or confirm with orchestrator). Do not ship if paused.

---

## Context summary

An overclaim audit corrected the framing: PP-272 active inference implements the extrinsic-value
branch of FEP (goal-completion) but NOT the epistemic branch (information gain / genuine curiosity).
The five-part decomposition (Friston 2015):

  EFE(policy) = -[epistemic value] - [extrinsic value]

With a hard target in active_goals, the epistemic term is suppressed. The system is a goal-
completion engine only. Five engineering anchors bridge from current state to partial intrinsic
motivation using primitives already present in the substrate:

- Anomaly margin (PP-263): detection side of curiosity; partial; missing the drive side
- Schema consolidation (PP-282/284): passive skill consolidation; missing the improvement-rate signal
- Sleep-defrag (PP-141/142): maintenance cycle; missing mastery-signal extraction

Four anchors use CPU-only existing substrate operations. One anchor (EMPOWER-DRIVE-B1) requires
a pre-test before authorization (validate finite action-space assumption in binding space).

Research finding: this is not a substrate-physics gap; it is an architectural gap. No new substrate
physics is needed. The LP-signal path is bookkeeping over existing cleanup margin output.

---

## Anchor candidates (rank-ordered by P_actionable x cost x prerequisite order)

### 1. Anchor CURIOUS-DRIVE-A1 (HIGHEST PRIORITY)

Anchor pointer: CURIOUS-DRIVE-A1 (new; not yet queued)
Substrate-product reading: computes learning-progress (LP) signal from cleanup margin improvement
  rate per topic cluster. Uses Oudeyer LP formula: LP(cluster_i, t) = cleanup_margin(t) - cleanup_margin(t-delta).
  Biases topic-selection toward high-LP clusters. Tests whether an LP-derived curiosity signal
  improves topic coverage diversity vs random selection.
  This gates all product claims about partial intrinsic motivation (cheapest validation).
Tier hint: CPU-only; pure bookkeeping over existing PP-263 output; no new substrate physics.
Why-now: cheapest test; uses existing primitives; if it passes, legitimate product differentiation
  claim (no other VSA/HDC system has a published LP intrinsic motivation primitive).

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: LP-guided topic selection produces >= 20% more unique topic clusters with cleanup
             margin above threshold, vs random selection, in a 200-insertion benchmark.
  HARD-FAIL: < 5% delta between LP-guided and random (LP signal is noise; mechanism needs revision).
  MID-BAND: 5-20% improvement (weak signal; use as input to combined multi-factor score).

P_deflated: 0.35 (raw 0.50, deflated 0.15 per calibration penalty; LP from cleanup margin is a
proxy not a true compression-progress signal).

---

### 2. Anchor BORED-DRIVE-D1

Anchor pointer: BORED-DRIVE-D1 (new; not yet queued)
Substrate-product reading: implements boredom-as-saturation trigger. When a topic cluster has been
  queried >= N_sat times with high cleanup margin, flag as saturated and reduce sampling weight by
  factor F_bore. Routes exploration to adjacent unsaturated clusters.
  Tests the behavioral correlate of reduced intrinsic reward from mastered material (Berlyne 1960).
Tier hint: CPU-only; N_sat and F_bore are tunable hyperparameters; can run in parallel with A1.
Why-now: complements A1 (A1 = approach drive; D1 = avoidance drive for mastered topics); together
  they approximate the approach-avoidance balance in Berlyne's optimal arousal model.

Pre-reg bands:
  HARD-PASS: boredom-trigger reduces redundant re-queries of mastered topics by >= 30% while
             maintaining cleanup margin >= 0.85 on those topics (redirects, does not forget).
  HARD-FAIL: boredom-trigger causes retrieval quality degradation (cleanup margin drops > 10%
             on mastered topics) -- means saturation flag is causing forgetting, not redirecting.
  MID-BAND: redundant-query reduction 10-30%; no quality degradation (useful but not strong).

P_deflated: 0.40 (straightforward bookkeeping; failure mode is under-tuning of N_sat, not
mechanism failure).

---

### 3. Anchor LP-DRIVE-C1: schema-acquisition-rate-as-mastery-proxy

Anchor pointer: LP-DRIVE-C1 (new; not yet queued)
Substrate-product reading: tracks rate of new schema generation per unit of interaction time
  (PP-282/284). When schema generation rate drops (mastery plateau), increases exploration weight
  on adjacent topic clusters. Converts sleep-defrag cycle output (PP-141/142) into a
  motivation-relevant signal.
Tier hint: CPU-only; requires schema generation logging in the sleep-defrag output path; architectural
  addition to existing maintenance loop.
Why-now: second LP proxy orthogonal to A1; if both A1 and C1 show positive signal, the LP-from-
  substrate-statistics approach is robust. Run after A1 verdict.

Pre-reg bands:
  HARD-PASS: schema-rate-guided exploration produces >= 15% more unique schema types in a 1-hour
             run vs non-guided baseline.
  HARD-FAIL: schema acquisition rate is not predictive (< 5% difference from frequency-matched
             random baseline; schema rate is input-driven not substrate-state-driven).
  MID-BAND: 5-15% improvement (weak mastery signal; useful but insufficient for strong claims).

P_deflated: 0.30 (depends on whether schema rate has enough variance to serve as a drive signal;
pre-test needed to check schema rate variance in a standard run).

---

### 4. Anchor SELF-MODEL-E1: self-state-tracking-shard (ARCHITECTURAL PREREQUISITE)

Anchor pointer: SELF-MODEL-E1 (new; not yet queued)
Substrate-product reading: instantiates a dedicated memory shard storing topic-cluster competence
  scores, goal history, and knowledge gap estimates. No new substrate physics; purely a curated
  memory partition with structured keys. Required by SDT autonomy condition and by long-term
  "autonomous knowledge worker" framing.
  This is the architectural prerequisite for identity-driven goal formation.
Tier hint: CPU-only; schema encoding; architectural. Should run after A1 and D1 validate the
  LP-signal path (otherwise the self-model has no valid signal to store).
Why-now: lower priority than A1/D1 but blocks all stronger autonomy claims. Route to exp_dev
  once A1 verdict is available.

Pre-reg bands:
  HARD-PASS: self-state shard produces consistent competence scores across two independent test
             sessions (Pearson r >= 0.70 on topic-level scores).
  HARD-FAIL: competence scores uncorrelated across sessions (r < 0.20); shard is not capturing
             stable substrate state.
  MID-BAND: r in [0.20, 0.70]; weak consistency; shard needs a more stable input signal.

P_deflated: 0.45 (score consistency is mostly an implementation question once LP signal exists).

---

### 5. Anchor EMPOWER-DRIVE-B1: miniaturized-empowerment-signal (PRE-TEST REQUIRED)

Anchor pointer: EMPOWER-DRIVE-B1 (new; not yet queued)
Substrate-product reading: estimates I(A_{t+1}; O_{t+1} | s_t) by running K sampled probe actions
  and measuring variance of resulting observation vectors. Uses this as an action-selection bias.
  Tests whether a tractable empowerment proxy is computable in the substrate's binding space.
Tier hint: CPU; requires K probe actions per evaluation step. Pre-test REQUIRED before authorizing
  this anchor: validate that the binding-space action set can be represented as a discrete finite
  sample (if the action space is continuous/infinite, K-sample approximation may be noise-dominated).
Why-now: lowest priority; requires pre-test gate; queue only after A1 and D1 return verdicts.

Pre-reg bands:
  HARD-PASS: empowerment proxy Spearman >= 0.4 vs human state-utility ratings (N=50 states).
  HARD-FAIL: Spearman < 0.10 (proxy is noise; close empowerment line and redirect to LP-only).
  MID-BAND: Spearman 0.10-0.40 (weak proxy; usable as secondary signal only).

P_deflated: 0.25 (depends on pre-test result; if action space is not tractably discrete, P drops
to < 0.15).

---

## Prerequisite order

A1 and D1 can run in parallel (both CPU-only; no dependencies between them).
C1 depends on no strict prerequisite but is more informative after A1 verdict.
E1 should run after A1 verdict (needs a valid LP signal to store).
B1 requires pre-test gate before authorization (check action-space discreteness first).

Recommended dispatch order: [A1 || D1] -> C1 -> E1 -> [pre-test B1 -> B1]

---

## Context pointers (file paths only)

- Research note: d:/AI/hd-instrument/notes/research_drill_motivation_beyond_goals_2x_2026-06-10.md
- Aesthetic theory note (linked gap: LP signal absent explains aesthetic quality gap too):
  d:/AI/hd-instrument/notes/research_drill_aesthetic_theory_substrate_2x_2026-06-10.md
- Concept formation note (linked gap: curiosity-drive step 2-5 missing):
  d:/AI/hd-instrument/notes/research_drill_substrate_novel_concept_formation_2x_2026-06-10.md
- PP-272 active inference implementation: search hdlab/ for pp272 or active_goals
- PP-263 anomaly margin: search hdlab/ for anomaly_margin or cleanup_margin
- PP-282/284 schema: search hdlab/ for pp282 or schema
- PP-141/142 sleep-defrag: search hdlab/ for sleep_defrag or pp141

---

## Contract section

Research has completed its scope: overclaim identification, literature audit, mechanism decomposition,
gap analysis, pre-reg thresholds. exp_dev owns all of:
- Anchor design (sweep grids, exact implementation, parameter choices for N_sat, F_bore, K)
- Queue routing decision (CPU/GPU/laptop)
- Smoke gate definition
- Verdict classification

exp_dev should NOT receive inline experiment designs. This file is structural intent only.

---

## Autonomy declaration

exp_dev is autonomous within the envelope defined by the pre-reg bands above.
Do not request orchestrator approval for individual queue decisions within Anchors A1 and D1.
Escalate only if:
(1) A1 or D1 returns HARD-FAIL (triggers an honest product-claim revision, not just a cap_map row)
(2) E1 implementation touches substrate memory shard architecture in a way that could affect
    existing shard integrity (coordinate with orchestrator before dispatch)
(3) B1 pre-test shows action space is not tractably discrete (close that line, do not force it)
