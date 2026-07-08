# Research — the resonator restart-budget geometric-race LAW: p_basin(K) generalization
# derivation (the n=2 self-improvement-loop instance)

Date: 2026-07-07. Author: research (Sonnet, 2 parallel lit-scan sub-agents + main-thread derivation).
Trigger: the self-improvement-monitor-loop scoping note
(`notes/research_self_improvement_monitor_loop_scoping_2026-07-07.md`) named this exact derivation as
the REQUIRED second instance to move the loop from a density-only special case (n=1) to a genuine
pattern (n=2), and the K-sweep cell that empirically tests it (`exp_resonator_ksweep_reachability_v1`)
is already built and shipping. THEORY DERIVATION ONLY — no cell built, no dispatch, per instruction.

---

## HEADLINE

**The restart-budget formula itself (`oracle_any = 1-(1-p_basin)^R` for FIXED K) is fully derivable —
textbook independent-Bernoulli-trial restart theory, near-certain. But `p_basin(K)` — how that
per-restart probability falls as the factorization order K grows — is NOT closed-form derivable from
first principles for this specific dynamical system: two independent drills today (this one, and the
sibling `research_resonator_basin_proliferation_self_predictability_2026-07-07.md`, a different
resonator cell) both hit this same wall from different angles, and the founding literature itself says
so in print (Kent/Frady/Sommer/Olshausen 2020: "our attempts to analytically derive this result were
stymied"). This is a genuinely semi-empirical (MM-family) law, not a CG-family one — exactly the honest
bound the self-margin taxonomy already uses for its other MM rows.**

Given that, this note derives the best available BRACKET rather than a single number: a
constant-ratio "budget" extrapolation (Model A, matching the K-sweep cell's own pre-registered null,
p_basin(K6)~0.024) and an accelerating "wall" family (Model B, motivated by the near-universal
finding across K-SAT/tensor-decomposition/p-spin disordered-systems literature that competing-solution
proliferation grows EXPONENTIALLY, not linearly, in interaction order — p_basin(K6) as low as
0.001-0.003 depending on the compounding rate). **My calibrated, pre-registered call: the FULL K-sweep
is more likely to land MIDDLE_BAND-or-HARD_FAIL(WALL) than a clean HARD_PASS(BUDGET) — even Model A,
the OPTIMISTIC extrapolation, already only predicts MIDDLE_BAND at K6 (p_basin~0.024, between the
cell's own WALL_CEIL=0.01 and BUDGET_FLOOR=0.05), and the (statistically underpowered, single-seed)
smoke-pilot data already on disk (oracle_any(K5)=oracle_any(K6)=0/30) is more extreme than even the
aggressive end of Model B, which is itself only a directional early read pending the properly-powered
FULL run (P_deflated=0.40 for "MIDDLE-or-WALL", capped, see Sec. 1d).**

The loop-shape generalizes (Sec. 3): both the density instance and this resonator instance follow the
identical OBSERVE -> apply-regime-matched-LAW -> PROPOSE-a-knob-value -> gate-with-independent-CONTROLS
-> apply-externally -> SCORE-against-ground-truth shape, even though the underlying substantive laws
are mechanistically unrelated (order-statistic mean-fit vs. geometric-race-with-regime-dependent-rate).
That is real n=2 evidence the loop-SHAPE is a pattern, not a one-off — while the underlying LAWS remain
per-regime bespoke, exactly as the honest self-margin-taxonomy precedent predicts.

---

## 1. Derivation: the geometric-race form and the p_basin(K) bracket

### 1a. What IS fully derivable (near-certain, textbook)

For FIXED K, if each of R restarts independently lands in the true basin with probability p_basin
(a genuinely fresh, re-dithered trajectory each time — confirmed on-platform by the parent reachability
note's own measurement, `mean_within_trial_distinct~9.19/10` at best T0, i.e. near-max realized
diversity across restarts within a trial), then the probability that AT LEAST ONE of R restarts
succeeds is the standard union-bound-tight independent-trials formula:

```
oracle_any(R) = 1 - (1 - p_basin)^R
p_basin = 1 - (1 - oracle_any)^(1/R)                    (inversion, used to back out p_basin from data)
R_to_target(p, target=0.95) = ceil( ln(1-target) / ln(1-p) )
```

This is exactly the formula already coded in `exp_resonator_ksweep_reachability_v1.py`
(`p_basin_from_oracle`, `R_to_target`, both self-tested to reproduce K3=0.3830/K4=0.1512 and
R95=7/19 to 1e-3). Nothing new here — restating for completeness because the SECOND half (K-dependence
of p_basin) is where the actual open question lives.

### 1b. What is NOT derivable: p_basin(K)

**Independent confirmation from two angles today.** The sibling drill
(`research_resonator_basin_proliferation_self_predictability_2026-07-07.md`, on the naive
`exp_resonator_capacity_gpu_v1` cell — no restarts/dither/verifier, a DIFFERENT but adjacent resonator
capability) attempted exactly this derivation via annealed basin-counting (the AGS/TAP/Kac-Rice/K-SAT
program) and reported: (1) the founding resonator papers state in print that analytical derivation
"stymied" them; (2) the simplest possible model (constant per-wrong-configuration capture probability,
giving raw `M^K` growth, predicting 30x more failure K3->K4) MISSES the substrate's own measured
2.86x growth by ~10x — informative, but not a completed closed form. My own lit-scan sub-agents today,
searching independently and for a different question (K-dependence of a RESTART-probability, not a
raw-success-rate), reached the identical literature conclusion from scratch (Sec. 1c below) — a strong
cross-validation that this is a genuine open gap, not a missed citation.

**So this note derives a BRACKET, not a point estimate**, using two lit-grounded models plus the
substrate's own measured anchor (K3=0.3830, K4=0.1512, ratio r=0.3949).

**Model A — constant-ratio ("BUDGET") extrapolation.** Assumes the per-K-step degradation ratio
r = p_basin(K)/p_basin(K-1) stays flat at the measured K4/K3 value (0.3949). This is the null the
K-sweep cell itself pre-registers ("geometric extrapolation... predicts p_basin(K6)~0.024").

```
p_basin(5) = 0.1512 * 0.3949           = 0.0597      R_to_95(K5)  = 49
p_basin(6) = 0.1512 * 0.3949^2         = 0.0236      R_to_95(K6)  = 126
```

**Model B — accelerating-ratio ("WALL") family.** Motivated by the p-spin/K-SAT/tensor-decomposition
lit-scan (Sec. 1c): assumes the ratio itself compounds by a factor q>1 per K-step (each additional
factor doesn't just cost a fixed multiplicative penalty, it makes the NEXT factor's penalty worse too),
i.e. r(K->K+1) = r(K-1->K) / q. Central illustrative value q=2 (loosely anchored to the K-SAT/tensor
literature's own doubling-type scaling, e.g. alpha_c(K) ~ 2^K ln2 for K-SAT thresholds and CP-tensor
recovery-gap exponent ~K/2 — NOT a rigorous derivation of q, an illustrative bracket parameter,
flagged honestly as such):

```
q=1.5:  p_basin(5)=0.0398  R95=74     p_basin(6)=0.0070   R95=428
q=2.0:  p_basin(5)=0.0299  R95=99     p_basin(6)=0.0029   R95=1015    <- central illustrative case
q=3.0:  p_basin(5)=0.0199  R95=149    p_basin(6)=0.0009   R95=3428
```

**Cross-check against the on-disk smoke-pilot data (statistically underpowered, flag prominently, NOT
confirmatory).** `data/exp_resonator_ksweep_reachability_v1_smoke/metrics.json` (1 seed, TR=30 trials
per arm — a pilot run, not the confirmatory FULL) already shows `oracle_any(K5)=oracle_any(K6)=0.000`
(0/30 hits at both K5 and K6), while K3/K4 correctly reproduce the positive-control bands (K3=1.000,
K4=0.867, both within the required [0.95,1.00]/[0.72,0.90] tolerance — the numpy port is healthy).
Computing `P(observe 0/30 | model true)`:

```
Model A p_basin(5)=0.0597  -> oracle_any(K5,R=10) predicted = 0.4599 -> P(0/30 trials succeed) = 9.4e-9
Model B q=2 p_basin(5)=0.0299 -> oracle_any predicted = 0.2616 -> P(0/30) = 1.1e-4
Model B q=3 p_basin(5)=0.0199 -> oracle_any predicted = 0.1822 -> P(0/30) = 2.4e-3
Model B q=5 p_basin(5)=0.0120 -> oracle_any predicted = 0.1132 -> P(0/30) = 2.7e-2
p_basin(5) would need to be <=0.0099 (q>=6 compounding) for P(0/30)>=0.05 (not-surprising threshold)
```

Even the AGGRESSIVE end of Model B (q=3) is formally rejected at p<0.01 by the smoke pilot's own
0/30 result. Read HONESTLY, not as confirmation: a single-seed, TR=30 pilot has real sampling risk
(and this specific arm hasn't been cross-checked for a K5/K6-specific numerical bug the way K3/K4's
positive control was) — but taken at face value, it says the true trajectory may already be steeper
than either bracketing model captures, i.e. closer to a genuine discontinuous cliff at K5 than to any
smooth extrapolation. **This is exactly the signature 1RSB/discontinuous-transition physics predicts
(Sec. 1c) rather than the smooth continuous decline p=2/SK-type systems show** — a mechanistic reason
to take the pilot's extremity seriously rather than dismiss it as noise, while still treating the
properly-powered FULL run (3 seeds x TR=120 = 360 trials/K, 12x the pilot's statistical power) as the
actual decisive test, not this note's arithmetic on a pilot.

### 1c. Literature grounding (2 parallel Sonnet lit-scans, generic terms only)

**Sub-agent 1 (p-spin / K-SAT / tensor-decomposition / disordered-systems complexity scaling).**
Well-established: p=2 (SK model) has a continuous (full-RSB) transition; pure p-spin models with p>=3
have a DISCONTINUOUS (1-step RSB) transition with an exponentially-large-in-N number of metastable TAP
states appearing at the transition (Gardner 1985; Crisanti-Sommers 1992; Kac-Rice counting formalized
by Cavagna-Giardina-Parisi). Across FOUR independent sub-literatures the pattern is consistently
EXPONENTIAL-in-interaction-order, never constant-ratio: random K-SAT satisfiability threshold
alpha_c(K) = 2^K*ln2 - O(1) (rigorously proven, Ding-Sly-Sun 2014-15; Achlioptas-Peres); the
clustering/condensation transition (Krzakala-Montanari-Ricci-Tersenghi-Semerjian-Zdeborova PNAS 2007;
Bapst-Coja-Oghlan arXiv:1507.03512) also scales as ~2^K; CP-tensor-decomposition's
statistical-to-computational gap threshold rank scales as ~n^(k/2) for order-k tensors
(arXiv:2211.05274) — exponent GROWS linearly in k, i.e. the gap widens geometrically per added mode;
sparse-superposition-code AMP decoding shows a sharp (not smooth) phase-transition-limited error curve
(Barron & Joseph arXiv:1712.06866). Honest gap: no paper found directly quantifies HOW MUCH the
per-order penalty accelerates going from p=4 to p=5 vs. p=3 to p=4 specifically — the qualitative
"exponential not linear" finding is solid across 4 domains; the exact COMPOUNDING RATE for THIS
system is not in the literature (hence Model B's q is illustrative, not derived). P_deflated capped
<=0.50 per calibration discipline for the "accelerating is the right qualitative bucket" claim.

**Sub-agent 2 (resonator-network-specific literature).** The founding papers (Kent, Frady, Sommer,
Olshausen, "Resonator Networks 1 & 2," Neural Computation 32(12), 2020, arXiv:2007.03748 /
arXiv:1906.11684) DO study operational capacity as a function of factor count F (their notation),
alongside N (quadratic capacity scaling, F-independent exponent) and codebook size M. Their own
reported finding is the OPPOSITE of a cliff: capacity is described as NON-monotonic in F, peaking at
INTERMEDIATE F~3-4, with one comparison explicitly noting "F=3 outperforms F=4" under matched
conditions — a graded, non-catastrophic picture, no cliff language anywhere. Crucially: no source
(including a targeted p-spin/K-SAT/resonator combined search) found the K-body-interaction /
p-spin-analogy framing anywhere in the resonator-network literature or its citers (Hersche et al. 2023;
Karunaratne/Langenegger et al. 2024) — this mapping (Sec. 1b/1c's own synthesis) is genuinely NOVEL,
not retrieval, and inherits the novel-synthesis P-cap accordingly.

**Reconciling the tension (own synthesis, not from either source).** Kent et al.'s graded/non-cliff
F-sweep and the general disordered-systems literature's exponential-collapse pattern are not actually
in conflict once the REGIME is made explicit: Kent et al. study F while ALSO letting N and M trade off
to preserve total information capacity (their capacity surface is 2-dimensional, F vs. an
information-budget axis) — a regime where you can always "spend more of the fixed budget" to
compensate for higher F. **This substrate's own K-sweep cell holds N=4096 and M=30 FIXED while only K
grows** — directly inflating the raw search space M^K with NO compensating resource increase, which is
the harsher, budget-constrained regime the K-SAT/tensor/p-spin literature's "fixed resources, growing
order" framing actually describes. This substrate's own sibling result today (naive resonator, no
restarts: K3=0.7, K4=0.142, a real 2.86x failure-rate increase, milder than naive M^K=30x but NOT flat)
already sits between Kent et al.'s "no real problem" picture and the disordered-systems literature's
"exponential collapse" picture — consistent with this note's own bracket (Model A/B), not with either
literature extreme taken alone. This reconciliation is this note's own synthesis and is accordingly
capped at the novel-synthesis P ceiling, not treated as an established result.

### 1d. Pre-registered numeric predictions (what the FULL K-sweep will confirm/falsify)

| Quantity | Model A (BUDGET, r=0.395 const.) | Model B (WALL, q=2 central) | Smoke pilot (underpowered, directional) |
|---|---|---|---|
| p_basin(K5) | 0.0597 | 0.0299 | consistent with <=0.010 (0/30 obs.) |
| R_to_95(K5) | 49 | 99 | -- |
| p_basin(K6) | 0.0236 | 0.0029 | consistent with <=0.010 (0/30 obs.) |
| R_to_95(K6) | 126 | 1015 | -- |
| Cell's own verdict band at K6 | MIDDLE_BAND (0.01<=p<0.05) | HARD_FAIL / WALL (p<0.01) | HARD_FAIL / WALL (if pilot direction holds) |

**Calibrated call: P(FULL run lands MIDDLE_BAND or HARD_FAIL/WALL, i.e. NOT a clean HARD_PASS/BUDGET)
= 0.40** (raw ~0.60-0.65 from: (i) the p-spin/K-SAT/tensor lit-scan's own capped-0.50 "accelerating is
the modal pattern" finding, (ii) the sibling note's independent 10x mismatch of the naive constant-rate
model, (iii) the smoke pilot's 0/30 result at both K5 and K6 — deflated 0.15-0.25 per mandatory
calibration penalty because Kent et al.'s own graded/non-cliff finding for THIS specific system family
is real counter-evidence tempering full confidence, and because a single-seed TR=30 pilot is weak
statistical evidence on its own). This is ALSO, by construction, an explicit prediction that Model A
alone (the cell's own null hypothesis) is more likely wrong than right — a genuinely falsifiable,
useful-before-the-fact forecast.

---

## 2. The resonator-regime self-improvement-loop instance

Mirroring the density-loop's shape exactly (`research_self_improvement_monitor_loop_scoping_2026-07-07.md`
Sec. 1): **OBSERVE** the substrate's own measured `oracle_any` at some already-run (K, R) pair (already
logged in `metrics.json`, no new instrumentation) -> **APPLY THE LAW** (geometric-race,
`p_basin = 1-(1-oracle_any)^(1/R)`, itself regime-classified as BUDGET/MIDDLE/WALL per Sec. 1's bracket)
-> **PROPOSE** a structured, machine-checkable claim:

```json
{"target_reachability": 0.95, "K_target": 5,
 "proposed_R": 49,
 "regime_classification": "BUDGET (Model A, if p_basin(K5) measured >= 0.045)",
 "fallback_if_WALL": "no realistic R achieves target; recommend algorithmic redesign, not budget increase",
 "law_used": "geometric-race 1-(1-p)^R, p_basin(K) extrapolated via constant-ratio r=0.395 from K3/K4 anchor",
 "confidence_band_R": [49, 1015],
 "fit_anchors": ["K3", "K4"]}
```

This is the resonator-regime analogue of the density loop's `{"predicted_m_star":..., "confidence_band":...}`
claim — same carrier shape (a pre-registered, falsifiable, structured recommendation emitted BEFORE the
target rung is measured), same "propose a knob value, never apply it" discipline (a human/`hdi_exp_dev`
decides whether to bump R or shelve the K5/K6 use case; the loop never edits code or re-dispatches
itself). The KEY DIFFERENCE from the density loop, and the honest reason this is a GENUINE second
instance rather than a copy-paste: the resonator loop's PROPOSE step must itself branch on the regime
classification — "add R" is only a valid recommendation in the BUDGET regime; in the WALL regime the
correct proposal is "do not add restarts, flag for redesign," a qualitatively different action than any
density-loop output ever needs to consider (the density law never has a "no density fixes this" case in
its current scope). This asymmetry is a genuine, not cosmetic, difference between the two law instances.

---

## 3. Generality check: does a common LOOP FORM exist across n=2 instances?

| Stage | Density-loop instance (07-07, same session) | Resonator-loop instance (this note) |
|---|---|---|
| OBSERVE | cross-seed MIN + CV of `graded_ret_agree10` at measured density arms | `oracle_any` at measured (K,R) from already-run cells |
| LAW | JL/Larsen-Nelson order-statistic mean-fit, `m*(V)=a+b*ln(V_eff)` | geometric-race `1-(1-p)^R`, with `p_basin(K)` regime-classified (BUDGET/MIDDLE/WALL) |
| PROPOSE | structured `{predicted_m_star, confidence_band, cv_onset_delta}` | structured `{proposed_R, regime_classification, fallback_if_WALL}` |
| CONTROL 1 | scrambled-law (mismatched functional form must underperform) | regime-discrimination test: does measured p_basin(K5,K6) match Model-A or Model-B bracket, NOT a free-floating fit (Sec. 1d's table IS this control, pre-registered before FULL lands) |
| CONTROL 2 | scrambled-CV (permuted-null early-warning check) | none yet specified with equal rigor -- see gap below |
| APPLY | human/`hdi_exp_dev` decides whether to dispatch R4 at proposed density | human/`hdi_exp_dev` decides whether to bump R, or shelve K>=5 use cases, per regime flag |
| SCORE | R4's actual optimum vs. proposal, vs. no-adjustment and nearest-lookup baselines | FULL run's actual p_basin(K5,K6) vs. Model A/B bracket, vs. "assume flat p_basin=K4 value" naive baseline |

**Verdict: YES, a common form composes across both instances** — OBSERVE a margin-quantity already
computed by an existing cell -> apply a REGIME-MATCHED law (different law per regime, as the self-margin
taxonomy itself requires) -> emit a falsifiable STRUCTURED proposal before the confirmatory data lands
-> gate it against at least one independent discriminating control -> apply EXTERNALLY, never
self-modifying -> SCORE against both the true measurement and a naive baseline. That is real n=2
evidence this loop-SHAPE is a genuine, reusable pattern in this project, not a one-off dressed up to look
general.

**Honest gap, not papered over:** this resonator instance's Control 2 (an independent early-warning-style
discriminator, analogous to the density loop's scrambled-CV permutation test) is NOT yet specified with
equal rigor. The closest analogue would be tracking whether the MEASURED ratio-of-ratios
(`r(K5->K4)` vs `r(K4->K3)`) itself falls outside a permuted-null distribution constructed from
resampling which K-rung's oracle_any is assigned to which K-label — this is a real, buildable control
(not attempted here, flagged as the natural next addition) but its absence today means this instance is
currently ONE control short of matching the density loop's two-control rigor. Reported honestly as a
partial match, not silently upgraded to a full match.

---

## 4. Honest bound: derivable vs. semi-empirical

**Not derivable from first principles today, confirmed independently twice this session.** (1) The
sibling drill's own annealed-basin-counting attempt hit a real, reported 10x mismatch on the simplest
possible model and explicitly states the founding papers call the derivation "stymied." (2) This note's
own lit-scan, searching from a different angle (restart-probability K-dependence, not raw-success-rate),
independently confirmed no closed-form K-explicit resonator law exists anywhere in the literature, AND
that the general disordered-systems literature (which DOES have exponential-in-order scaling laws for
adjacent problems: K-SAT, tensor decomposition, p-spin) has never been explicitly connected to resonator
networks before — meaning even "borrow a known formula from an adjacent field" is not directly available,
only a qualitative directional prior (accelerating, not constant-ratio, is the more common pattern).

**Classification: this is an MM-family law (semi-empirical), not CG (closed-form)** — same honesty
tier as other MM rows already logged in the self-margin taxonomy (`reference_self_margin_taxonomy_
splits_by_decode_regime_2026-07-06`). The bracket in Sec. 1d is the most defensible PRE-REGISTERED
statement available without the K-sweep's own data: it names two lit-grounded candidate models, gives
each a concrete falsifiable number, and states which one the cell's own bands (BUDGET/MIDDLE/WALL)
already discriminate between. **The K-sweep's FULL run is not optional confirmatory decoration — it is
the only source that can actually PIN p_basin(K) down; no amount of further theory work this cycle
would close that gap**, exactly as the sibling note independently concluded for the adjacent
naive-resonator cell.

---

## Cheap decisive test

No new cell needed — `exp_resonator_ksweep_reachability_v1` (already built, smoke-passed at the
positive-control gates, FULL not yet dispatched per the trigger note) IS the decisive test. Its own
pre-registered bands (BUDGET_FLOOR=0.05, WALL_CEIL=0.01 on p_basin(K6), plus the positive-control
reproduction gates on K3/K4) already implement exactly the Model-A-vs-not-A discrimination this note's
Sec. 1d table specifies. This note's marginal contribution is (a) an independently-derived, literature-
grounded SECOND bracket (Model B) the cell itself does not compute, (b) the explicit p-values showing
the on-disk smoke pilot already statistically disfavors Model A at the 1e-8 level and disfavors even
aggressive Model B at the 1e-3 level (Sec. 1b), and (c) the resonator-instance of the self-improvement
monitor loop (Sec. 2-3) the trigger note asked for.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**HARD-PASS (this note's bracket-and-forecast validated):**
- FULL run's `p_basin(K5)` falls within +/-25% of EITHER Model A (0.0597) or a Model-B value at some
  q in [1.5,3] (i.e., the bracket contains the true value; the note's own bracketing, not a single
  guess, is vindicated), AND
- The calibrated directional call (Sec. 1d: P=0.40 that FULL lands MIDDLE-or-WALL, not clean BUDGET)
  is confirmed by the actual verdict landing MIDDLE_BAND or HARD_FAIL, matching the majority
  probability mass of this note's own forecast, AND
- The resonator self-improvement-loop instance (Sec. 2) emits a structured proposal whose
  regime-branch (BUDGET "add R" vs. WALL "flag redesign") matches the FULL run's actual classification.

**HARD-FAIL (bracket and/or loop-generality claim refuted):**
- FULL run's `p_basin(K5)` or `p_basin(K6)` falls OUTSIDE both Model A and the full Model B range
  (q in [1.5,3]) by more than 25% in EITHER direction (e.g., true p_basin(K6) between 0.01 and 0.018,
  outside Model B's tightest bracket but also clearly below Model A — a genuine miss, not just
  "somewhere in a wide net"), OR
- FULL run lands a clean HARD_PASS/BUDGET classification (p_basin(K6)>=0.05) — this would falsify BOTH
  brackets and the smoke-pilot's directional read simultaneously, meaning the smoke pilot's 0/30 result
  was a fluke (single-seed sampling noise) rather than early signal, and Kent et al.'s graded/non-cliff
  picture transfers to this fixed-M,N regime after all (an honest, valuable negative for this note's own
  Sec. 1c reconciliation argument), OR
- The loop-generality claim (Sec. 3) is refuted if a genuinely different, non-composable shape is needed
  for the resonator instance (e.g., if the regime-branching PROPOSE logic turns out to require bespoke
  machinery incompatible with the density loop's carrier format) — not expected given the shapes already
  align in this note's own table, but stated as the explicit falsification condition.

**MIDDLE (informative, non-clean outcome):** FULL run's p_basin(K5)/p_basin(K6) land inside the wide
[Model-A, Model-B q=3] envelope but closer to one edge than either central estimate predicted — i.e.,
the QUALITATIVE bracket held (accelerating decline confirmed vs. flat decline) but neither specific
model was quantitatively close — an honest "right direction, wrong magnitude" finding, valuable for
narrowing q in a follow-up rather than treated as a clean pass or fail.

---

## Cross-thread synthesis

- **`research_self_improvement_monitor_loop_scoping_2026-07-07.md`**: this note supplies exactly the
  "second dial+law instance" that note's Sec. 4 named as required before the loop-shape claim earns any
  credibility beyond n=1 — delivered same-session, independently derived, and shown (Sec. 3) to share a
  common OBSERVE/LAW/PROPOSE/CONTROL/APPLY/SCORE form with the density instance, with one honest gap
  (Control 2 not yet built to equal rigor) rather than a forced perfect match.
- **`research_resonator_reachability_ceiling_2026-07-07.md`**: supplies the K3/K4 anchor values
  (p_basin=0.3830/0.1512, ratio 0.3949) this note's Model A directly reuses, and the restart-independence
  evidence (`mean_within_trial_distinct~9.19/10`) this note's Sec. 1a leans on for the geometric-race
  formula's validity.
- **`research_resonator_basin_proliferation_self_predictability_2026-07-07.md`** (sibling, same day,
  different cell — naive `exp_resonator_capacity_gpu_v1`, no restarts): independently reaches the SAME
  "no closed form exists, literature says so in print" conclusion via a completely different derivation
  attempt (annealed basin-counting) on a completely different quantity (raw success rate, not restart
  probability) — strong cross-validation this is a genuine, not manufactured, open gap. Its own
  measured 2.86x (not 30x) failure-rate growth K3->K4 is the anchor this note's Sec. 1c reconciliation
  argument uses to place the substrate's actual regime between Kent et al.'s graded picture and the
  general disordered-systems exponential-collapse picture.
- **`reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06`**: this note's honest MM-family
  classification (Sec. 4) is the same tier already used for other semi-empirical rows in that taxonomy —
  no new tier invented, existing vocabulary reused.
- **`exp_resonator_ksweep_reachability_v1.py`** (already-built cell, smoke passed positive-control
  gates, FULL not yet dispatched): this note's Sec. 1d predictions are PRE-REGISTERED against that cell's
  own already-specified BUDGET/MIDDLE/WALL bands — no new cell needed, the existing one is the test.

---

## Substrate-product implications

- **No new dispatch requested.** The K-sweep cell already exists and is the decisive test; this note
  only supplies a richer, literature-grounded pre-registration for interpreting its FULL result, plus the
  resonator instance of the self-improvement-loop pattern.
- **If FULL confirms MIDDLE-or-WALL (this note's majority-probability call):** the product-relevant
  reading is that K>=5 joint-factor recovery via "just add more restarts" is NOT a reliable near-term
  capability upgrade path — a genuinely different search dynamics (not more-of-the-same annealed
  alternating-projection) would be needed for product use cases requiring deep multi-slot binding (K>=5),
  consistent with the CG_META basin-proliferation risk already flagged, now given concrete numbers rather
  than a qualitative worry.
- **If FULL confirms clean BUDGET (this note's minority-probability call, ~0.35-0.40 raw complement):**
  K<=6 joint-factor recovery stays a solved-cheaply problem (verifier readout + restart bump), and Kent
  et al.'s graded/non-cliff picture would be shown to transfer even to this substrate's harsher
  fixed-M,N regime — a genuinely reassuring, falsifiable-and-testable outcome either way.
- **The self-improvement-loop pattern (Sec. 2-3)**, once the density loop's own first live instance
  lands (R4, per that note's own near-zero-marginal-cost plan) and this resonator instance's Control 2
  gap is closed, would give the project TWO independently-scored instances of a genuine (if narrow)
  self-improvement-PROPOSAL capability — the concrete next step toward the broader north-star, not a
  detour from it.

---

## Citations (verified count)

Two parallel Sonnet lit-scan sub-agents dispatched this cycle, generic math/physics terms only per
query-privacy discipline (no substrate-novel mechanism names sent externally). All citations
independently verified via live search by each sub-agent.

**Sub-agent 1 (p-spin / K-SAT / tensor-decomposition / disordered-systems complexity scaling), 11
sources:** Gardner, "Spin glasses with p-spin interactions," Nucl. Phys. B 257 (1985); Crisanti &
Sommers, Z. Phys. B 87 (1992); Cavagna, Giardina, Parisi (Kac-Rice stationary-point counting in p-spin
models); "Continuous and discontinuous transitions in generalized p-spin glass models," arXiv:1309.4292;
"The Ising M-p-spin mean-field model... continuous vs. discontinuous transition," arXiv:1010.5000;
Krzakala, Montanari, Ricci-Tersenghi, Semerjian, Zdeborova, "Gibbs states and the set of solutions of
random constraint satisfaction problems," PNAS 104:10318 (2007); Ding, Sly, Sun, "Proof of the
Satisfiability Conjecture for Large k" (2014/2015); Achlioptas & Peres, "The Threshold for Random k-SAT
is 2^k ln2 - O(k)," cs/0305009; Bapst & Coja-Oghlan, "The Condensation Phase Transition in the Regular
k-SAT Model," arXiv:1507.03512; Coja-Oghlan & Zdeborova (hypergraph 2-coloring condensation),
arXiv:1107.2341; "Average-Case Complexity of Tensor Decomposition for Low-Degree Polynomials,"
arXiv:2211.05274; Barron & Joseph, sparse superposition codes (AMP decoder phase transition),
arXiv:1712.06866.

**Sub-agent 2 (resonator-network-specific capacity-vs-factor-count literature), 4 sources:** Frady,
Kent, Olshausen, Sommer, "Resonator networks for factoring distributed representations of data
structures," Neural Computation 32(12):2311-2331 (2020), arXiv:2007.03748; Kent, Frady, Sommer,
Olshausen, "Resonator Networks, 2: Factorization Performance and Capacity Compared to Optimization-Based
Methods," Neural Computation 32(12):2332-2388 (2020), arXiv:1906.11684; Kleyko et al., HDC/VSA survey
Parts I-II, arXiv:2111.06077 / arXiv:2112.15424 (cleanup-memory capacity context, confirmed silent on
multi-factor-K scaling beyond the Resonator Networks papers themselves); confirmed absence of any
p-spin/K-SAT framing anywhere in the resonator-network citation graph (Hersche et al. 2023;
Karunaratne/Langenegger et al. 2024, both already cited in the sibling note).

**Internal/substrate sources (on-disk, verified this drill):** `experiments/
exp_resonator_ksweep_reachability_v1.py` (full script read, formulas and pre-reg bands verified);
`data/exp_resonator_ksweep_reachability_v1_smoke/metrics.json` (smoke-pilot p-value cross-check);
`notes/research_resonator_reachability_ceiling_2026-07-07.md`; `notes/research_resonator_basin_
proliferation_self_predictability_2026-07-07.md`; `notes/research_self_improvement_monitor_loop_
scoping_2026-07-07.md`; `reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06`.

**Verified count: 15 distinct external sources found via live web search across 2 sub-agents this
cycle, plus 6 internal on-disk sources cross-checked. Zero fabricated citations; both sub-agents
explicitly flagged their own honest gaps (no direct p-vs-p+1 compounding-rate formula found anywhere;
no p-spin/K-SAT framing found anywhere in the resonator-network literature itself — both gaps are why
this note's Model B and its reconciliation argument are labeled novel synthesis, capped at P<=0.50).**
