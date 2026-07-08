# Research — revival drill: ranking WHERE the self-improvement MONITOR loop can be
# non-trivially demonstrated (density HARD_FAIL was an honest null, not a closure)

Date: 2026-07-07. Author: research (Sonnet, 2 parallel lit-scan sub-agents + main-thread synthesis).
Drill type: 2x-negative revival (operational drill on existing findings, no new cell dispatch).
Trigger: `exp_self_improvement_monitor_loop_density_v1` landed FULL and HARD_FAILED
(`data/exp_self_improvement_monitor_loop_density_v1/metrics.json`, verdict_msg: "miss>2steps=False
no_controls=True (correct=True beats_both=True C1=False C2=False)") — the proposal itself was
CORRECT and beat both baselines, but neither firing control could fire, because the density
landscape is genuinely, robustly flat (`argmax_min_m=8` at ALL THREE scales 50K/100K/177,899,
`law_b=-3.6e-15` — numerically zero, not floating-point slop). Per the standing directive, this is
routed back to research as a 2x-drill: the loop MACHINERY is validated (it ran, computed real
numbers, and both controls correctly stayed silent because there was truly nothing to
discriminate) — what's missing is a REGIME with a genuinely non-flat law. This note ranks
candidates and names the single best revival target.

---

## HEADLINE

**Density was an honest, verified null — not a metric artifact — and a STRONGER candidate than the
pre-identified resonator regime already exists, sitting fully landed on disk at zero marginal
cost: the reasoning-depth capacity-provisioning law.** Re-reading the raw per-density,
per-scale data directly from the HARD_FAILed cell's own `metrics.json` confirms the argmax
location (`m*=8`) is flat to 1e-15 precision across a 3.5x range of V — genuinely flat, not
under-sampled (Q3 below). Ranking five candidate regimes by (law-non-flatness x
substrate-can-observe-its-own-inputs x controls-would-fire): **the reasoning-depth exact-capture
law (`exp_reasoning_depth_exact_order_statistic_self_margin_v1`, already CG-tier, already
CHAIN_GRADE at canonical scale, cert_ledger 2026-07-06T06:45Z) is the single best revival
target** — stronger than the resonator restart-budget instance the Director's framing
pre-identified, for three concrete reasons: (1) it is CG (closed-form, zero fitted constant),
not MM (semi-empirical bracket) like the resonator law; (2) the discriminating control the loop
needs (a wrong-model alternative measurably worse than the real law) is **already sitting in
landed data** — the cell's own retained "naive occupancy-binary" control is 2.02x biased
(CV 15.6%) against the exact-capture model's 0.98x unbiased fit (CV 11.7%), independently
replicated on a second cell (cortex iterative-attractor cleanup, 6.4% deviation) — meaning
Control-1-equivalent has effectively ALREADY fired, using zero new dispatch; (3) the corpus
already contains multiple capacity operating points per (N, difficulty) cell — `capacity_law`
sub-dicts for baseline / keyslots_2x / shard variants across 2 N values x 3 difficulties — giving
more genuine rungs for a leave-one-out extrapolation-fold test than density's 3 V-scales had. The
resonator instance remains a legitimate, worthwhile SECOND test (confirmed below, Q1) but carries
more risk: it is MM-tier, its FULL run has not yet been dispatched, and the note that derived it
already pre-registered a 0.40 probability of landing MIDDLE_BAND-or-WALL rather than a clean pass.
**P_deflated(a non-trivial self-improvement law demonstrable in >=1 regime, this project) = 0.50
(capped at the novel-synthesis ceiling)**; P_deflated(the reasoning-depth capacity-provisioning
loop specifically clears a HARD-PASS-equivalent bar once wrapped in the OBSERVE/PROPOSE/CONTROL/
SCORE scaffolding) = **0.45** — the highest per-regime estimate assigned to any candidate in this
note, and higher than this project's own density-loop estimate was before it ran (0.20-0.25),
precisely because the discriminating evidence already exists on disk rather than being projected.

---

## 1. Is density truly flat, or metric-limited? (direct re-read of the HARD_FAIL data)

**Argmax location: genuinely flat, not a coarse-metric artifact.** Read directly from
`data/exp_self_improvement_monitor_loop_density_v1/metrics.json:observed`, the dense 8-point grid
`[3,4,5,6,7,8,10,12]` at all three scales gives `argmax_min_m=8` and `cv_onset_m=5` IDENTICALLY at
V=50,000, V=100,000, and V=177,899 — a 3.5x range, fit as `m*=a+b*ln(V)` gives `b` in the
`1e-15`-`1e-16` range at every leave-one-out fold (i.e. numerically exact zero, not a small
nonzero slope hidden by grid coarseness). The grid itself is dense enough to rule out
under-sampling as the explanation (8 candidate densities per scale, `min_ret` measured cleanly at
every one, tight cross-seed CV at the peak). **This is a real finding: at this V range, on this
channel, the optimal encoding density does not move.** Treat it as load-bearing, not a metric
artifact to explain away.

**But a DIFFERENT, non-flat target sits in the SAME already-landed data: CV magnitude at a FIXED
density, tracked across scale.** Re-reading the same `observed` block at the argmax density (m=8):
`cv(50K)=0.0670`, `cv(100K)=0.0794`, `cv(177,899)=0.1049` — a monotonic ~57% relative increase
over the same 3.5x V range. The wider grid also reveals the CV-vs-density shape itself is an
oscillating comb (tight at m=4,5,8; wide at m=3,6,7,10,12: `cv(7)` runs 0.387->0.433->0.461 across
the same three scales), and this SHAPE is itself scale-invariant (same comb pattern, same tight/
wide density assignment, at all three V) — so "which density will have tight CV at 970K" is ALSO
a flat, trivial prediction (no new law there). The genuinely learnable piece is narrower than the
original loop's ambition: not "where is the optimum" (flat) and not "which density is noisy"
(also flat, just a fixed comb), but **"how much noisier does the SAME density get as V grows"** —
a real, if modest, gradable signal using the identical already-landed corpus.

**Honest scope of this partial revival:** three data points (3.5x V range) is thin for fitting
`cv(m,V) ~ cv0(m) + k(m)*ln(V)` per density and holding out a fold, and the growth is modest
(57% relative, well within the kind of variation a single extra seed could shift) — this is a
narrower, lower-confidence candidate than reasoning-depth or resonator (ranked #3 below), useful
mainly as a "confidence-band sizing" recommendation (how many seeds to budget at 970K) rather than
an operating-point recommendation, and its own firing controls would need to discriminate a REAL
`k(m)>0` growth-rate from `k(m)=0` (flat CV) — plausible given the trend's consistency across all
8 densities in the same direction, but not yet built or scored.

---

## 2. Ranked candidates (law-non-flatness x substrate-self-observability x controls-would-fire)

| Rank | Regime | Law | Tier | Non-flatness (measured) | Discriminating control status | Dispatch cost |
|---|---|---|---|---|---|---|
| **1** | **Reasoning-depth capacity provisioning** | `D* = ln(FLOOR)/ln(p_hop_exact)`, Poisson-occupancy capture probability (Gauss-Hermite order-statistic family) | **CG** (closed-form, cert_ledger CHAIN_GRADE 2026-07-06T06:45Z) | Strong: exact model 0.980x unbiased (CV 0.117) vs retained naive-binary control 2.021x biased (CV 0.156) — an 2x error factor across the SAME data | **Already fired, zero new dispatch** — the naive-vs-exact differential is measured, stable (CV~0.10-0.12), cross-cell replicated (6.4% dev on a 2nd cell) | **Zero new GPU cost** — reuses `exp_reasoning_depth_keyslots_sharding_v1` + `exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1` landed data; new work is bookkeeping only (same class as the density-loop cell) |
| **2** | **Resonator restart-budget** (pre-identified n=2) | `oracle_any=1-(1-p_basin)^R`; `p_basin(K)` bracket (Model A budget / Model B wall) | **MM** (semi-empirical; literature says "stymied," confirmed independently twice this session) | Strong but uncertain shape: K3->K4 measured 0.383->0.151 (2.5x per K-step); smoke pilot (0/30 at K5,K6, underpowered) suggests the TRUE decline may be even steeper than either bracket model | Control 1 (regime-discrimination Model A/B/WALL) well-specified; Control 2 analogue **not yet built to equal rigor** (honest gap flagged in the source note itself) | FULL K-sweep not yet dispatched (~4200-4500s per prereg estimate); cell already built + smoke-passed positive controls |
| **3** | **Density CV-magnitude growth** (same corpus, narrower target) | `cv(m,V) ~ cv0(m) + k(m)*ln(V)` at FIXED density (not argmax location) | Not yet classified (would need a fresh fit) | Modest: ~57% relative CV growth at m=8 over 3.5x V, consistent direction across all 8 densities | Not built; would need a scrambled-null (permute which V maps to which CV trend) analogous to the density loop's original Control 2, applied to growth-RATE not onset-LOCATION | **Zero new GPU cost** — same already-landed corpus as the HARD_FAILed cell; pure re-analysis |
| 4 | Compositional-math depth (add/sub) | Same reasoning-depth law, reused not re-derived | **MM** ("safe conservative bound," not exact — self-healing on `mul` beats the naive bound) | Real (add/sub ratio ~1.04x tight) but NOT a fresh law-discovery — a 3rd confirmed application of rank-1's law, evidence FOR rank 1's generality, not an independent candidate | Not separately built; would inherit rank 1's controls if rank-1's exact-order-statistic follow-on cell is built | Low — same reuse-not-rebuild status as landed |
| 5 | Comprehension correlated-superposition (PR-substitution) | `PR(V)-1` replacing raw `V-1` in order-statistic quadrature | **MIDDLE_BAND** (not CG — `perseed_max`=1.088 misses the 1.50 HARD-PASS sub-gate) | Moderate: PR(V) saturates ~16-29 (not V-1~999), a real but bounded/saturating curve | Partially present (PR-vs-naive-V comparison, 1.999x improvement) but tier itself is not yet CG | Landed already; a fresh loop-instance would need new leave-one-out bookkeeping |
| 6 (unconfirmed) | Composition Hits@10 vs branching-factor (out_degree) | Unknown — not yet fit | Unclassified | Unknown — `out_degree` is computed per-item in `exp_conceptnet_semantic_seeded_beam_composition_v1.py:396` but NOT persisted in the aggregate `metrics.json` (only the derived trivial/nontrivial split is kept) | Cannot assess without new instrumentation | Requires either a re-analysis of raw per-item logs (if they exist beyond the aggregate file) or a cell tweak — **not zero-cost**, flagged as a real but unconfirmed candidate, do not rank above confirmed regimes |

---

## Q1 — Confirming the resonator regime (Director's pre-identified n=2)

**Yes, it is a legitimate revival regime and the law is non-flat enough — but it is riskier than
newly-ranked #1, not a substitute for it.** `p_basin(K)` genuinely varies with K (0.383 -> 0.151,
a real 2.5x-per-step decline, not a flat/scale-invariant quantity like density's argmax), so
"predict R needed at unseen K" is a non-trivial law by construction — this confirms the framing in
`research_resonator_restart_budget_geometric_race_law_2026-07-07.md`. The would-be Control-2
analogue (gated on the re-shipping K-sweep FULL run) WOULD make the controls fire in the sense
that matters: Control 1 (regime-discrimination: does measured `p_basin(K5,K6)` fall inside Model
A's bracket, Model B's bracket, or neither) is a real, pre-registered, falsifiable three-way split
that the smoke pilot's own 0/30 result already statistically disfavors at p<1e-3 for even the
aggressive end of Model B — meaning there IS a real discriminating signal to catch, not a
guaranteed rubber-stamp. **However, two honest cautions temper "confirm":** (a) this is MM-tier,
not CG — the founding resonator literature explicitly states the K-dependence "stymied" analytical
derivation, so any loop built here recommends against a BRACKET, not an exact law, which is a
weaker "genuine self-improvement" claim than a CG-tier instance; (b) the note's own calibrated
call is P=0.40 that the FULL run lands MIDDLE-or-WALL rather than a clean BUDGET pass — i.e. the
most likely single outcome is that the resonator loop's own PROPOSE step would correctly recommend
"do not add restarts, flag for redesign" (the WALL branch), which is a valid, useful,
self-improvement-relevant output but is a qualitatively different, less crisp "genuine law
confirmed" story than reasoning-depth's already-measured 2x control differential. **Verdict:
dispatch it — it is worth running regardless of this note's ranking, per the standing "research
every finding" directive (a WALL confirmation would itself be a valuable, load-bearing negative,
closing K>=5 joint-factor recovery as a near-term capability path) — but do not treat it as the
ONLY candidate**, now that reasoning-depth-capacity-provisioning is on the table as a
lower-risk, zero-marginal-cost, CG-tier alternative that can be scored in parallel.

---

## Q2 — Ranked survey of other non-flat regimes (see table above; expanded reasoning below)

- **Reasoning-depth survival vs D (`p^D`, genuinely non-flat):** confirmed as rank 1, above — this
  IS the concrete instance of "reasoning-depth survival vs D" the prompt asked to survey, and it
  is the strongest candidate found this drill.
- **Composition Hits@10 vs branching-factor (out-degree):** the per-item `out_degree` field is
  computed in-code (`exp_conceptnet_semantic_seeded_beam_composition_v1.py` line 396,
  `{"out_degree": int(len(cpool)), "chain_depth_le2": bool(trivial)}`) but this drill's direct
  filesystem check confirms it is used ONLY to derive the trivial/nontrivial split
  (`n_trivial=126, n_nontrivial=107` in the landed `metrics.json:per_arm`) — the raw per-item
  `out_degree` values are NOT persisted in the aggregate metrics file. **Honest answer: cannot
  confirm or refute a law here without new work** (either locating raw per-item logs if the cell
  writes them elsewhere, or a minor cell tweak to bucket `hits@10` by `out_degree` before
  aggregating). Flagged as the correct NEXT scope-expansion candidate for a future drill or a cheap
  `hdi_exp_dev` re-analysis pass — not ranked above the four confirmed/pre-registered candidates
  in this note.
- **Encoder retrieval vs correlation/PR:** already covered by the self-margin taxonomy's row 5
  (comprehension correlated-superposition, `PR(V)-1` substitution) — MIDDLE_BAND tier, moderate
  non-flatness (PR saturates, doesn't grow linearly with V), ranked #5 above a real but weaker
  candidate than the top three.
- **Arithmetic depth vs D:** ranked #4 above — real but a reuse of rank 1's law on a different
  substrate operation (add/sub), which is actually evidence FOR rank 1's cross-operation
  generality (a 3rd independent confirmation point: reasoning-depth cell, cortex-cleanup cell,
  compositional-math cell all reproduce the same capture-probability shape) rather than an
  independent candidate regime.

---

## Q3 — answered inline above (Sec. 1): genuinely flat for argmax-location (not metric-limited),
but a narrower non-flat target (CV-magnitude growth at fixed density) exists in the same corpus.

---

## Cheap decisive test

**Zero new GPU dispatch.** Wrap the ALREADY-LANDED reasoning-depth data
(`data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json:extra.per_op`, 6 op-points x nested
`capacity_law` arms for baseline/keyslots_2x/shard per op, plus the independent
`exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1_smoke` replication point) in the SAME
OBSERVE/LAW/PROPOSE/CONTROL/SCORE scaffolding class already built for
`exp_self_improvement_monitor_loop_density_v1.py` (same "sequential-CPU, post-hoc analysis of
landed JSON telemetry, no matmul" compute-architecture justification, <10s wall time). Concretely:
(1) OBSERVE per (N, capacity-arm) the measured usable depth and its cross-seed CV (already
computed, `mean_base_usable`, `seed_tiers`, `cv_base_crossing` all already in the landed
`metrics.json`); (2) LAW = the exact-capture Poisson-occupancy formula (already derived and scored
in `research_reasoning_depth_self_margin_closed_form_2026-07-06.md`, not re-derived here); (3)
PROPOSE, leave-one-out over the available (N, capacity-arm) rungs, the minimum capacity needed for
a target depth at a held-out rung; (4) CONTROL 1 = the ALREADY-MEASURED naive-occupancy-binary vs
exact-capture differential (2.02x biased vs 0.98x unbiased) — this is Control 1, already fired, no
new computation; CONTROL 2 (scrambled-CV analogue, not yet built) would need constructing, the one
genuinely new piece of machinery this revival needs; (5) SCORE against a no-adjustment baseline
(assume flat capacity requirement) and a nearest-lookup baseline, exactly as the density loop did.
The concrete follow-on cell name: `exp_reasoning_depth_capacity_provisioning_monitor_loop_v1`
(spec only, not built this drill, per the "no cell dispatch" 2x-revival scope of this note).

---

## Falsifiable predictions

**HARD-PASS (a non-trivial self-improvement law is demonstrable in the reasoning-depth regime):**
- The leave-one-out capacity-provisioning proposal (minimum capacity for a target depth, fit on
  all-but-one (N, capacity-arm) rungs) falls within a pre-registered tolerance of the held-out
  rung's actual required capacity, AND beats both a no-adjustment and nearest-lookup baseline, AND
- Control 1 (already measured: naive-binary vs exact-capture, 2.02x vs 0.98x) continues to hold at
  the SAME differential once reframed as a leave-one-out proposal-vs-control comparison (not just a
  retrospective fit-quality comparison), AND
- A Control 2 analogue (a scrambled/permuted-null check on the depth-vs-capacity relationship,
  still to be built) falls outside its own null distribution — this is the one genuinely open piece
  of machinery; without it this candidate matches the resonator instance's own honest gap
  (Control-2-not-yet-built-to-equal-rigor).

**HARD-FAIL (reasoning-depth capacity-provisioning is NOT a demonstrable non-trivial
self-improvement law once formally wrapped):**
- The leave-one-out proposal misses the held-out rung's actual required capacity by more than the
  pre-registered tolerance, OR
- The naive-binary control, once reframed as the loop's Control 1, does NOT measurably underperform
  the exact-capture law on the SAME held-out comparison (i.e. the already-observed 2.02x-vs-0.98x
  gap does not survive the leave-one-out reframing — plausible if the gap is itself an artifact of
  in-sample fitting rather than genuine held-out predictive power), OR
- A constructed Control 2 fails to discriminate signal from a permuted null.

**MIDDLE (plausible, informative outcome):** the capacity-provisioning proposal is directionally
correct and beats the no-adjustment baseline, but the naive-binary control's underperformance
shrinks substantially once evaluated strictly out-of-sample (still worse, but not by the full
already-measured margin) — an honest "the law helps, but the in-sample control differential
partly reflects fitting-to-the-same-data" finding, analogous to the density loop's own MIDDLE band
definition.

**For the resonator instance (Q1), restated for completeness:** HARD-PASS/HARD-FAIL/MIDDLE bands
are already fully specified in `research_resonator_restart_budget_geometric_race_law_2026-07-07.md`
Sec. "Falsifiable predictions" — not re-derived here; that note's own calibrated P=0.40 for
MIDDLE-or-WALL stands.

**Calibration (per the mandatory lit-scan calibration penalty):**
- P(reasoning-depth capacity-provisioning loop, once formally wrapped, clears a HARD-PASS
  including a newly-built Control 2): undeflated ~0.60-0.70 (the Control-1-equivalent differential
  already exists, is stable across N/fill, and cross-cell replicated — the strongest empirical
  starting position of any candidate assessed this session) -> **P_deflated = 0.40-0.45** (deflated
  for the same reason the density loop still failed despite the underlying law being solid: a
  LOOP-level bar with an untested Control 2 carries real risk beyond the law's own tier).
- P(a non-trivial self-improvement law is demonstrable in AT LEAST ONE regime across all
  candidates surveyed, this project, ever): raw OR-across-candidates estimate ~0.65-0.75 (multiple
  independent shots: reasoning-depth, resonator, density-CV-growth) -> **P_deflated = 0.50, capped
  at the novel-synthesis ceiling** (this ranking itself is a fresh synthesis assembling prior
  session findings into a new comparative frame, not a retrieval of an established result).

---

## Cross-thread synthesis

Composes five same-project threads without re-deriving any of them: (1)
`research_self_improvement_monitor_loop_scoping_2026-07-07.md` and its landed
`exp_self_improvement_monitor_loop_density_v1` HARD_FAIL supply the loop-shape scaffolding and the
concrete honest-null finding this note re-reads directly off disk (Sec. 1); (2)
`research_resonator_restart_budget_geometric_race_law_2026-07-07.md` supplies the pre-identified
n=2 candidate this note confirms-with-caveats (Q1) rather than displaces; (3)
`research_reasoning_depth_self_margin_closed_form_2026-07-06.md` and the self-margin taxonomy
synthesis (`research_self_margin_taxonomy_synthesis_cg_meta_assessment_2026-07-06.md`, row 3)
supply the CG-tier law and the already-measured naive-vs-exact control differential this note
promotes to rank 1 — a genuinely new connection (that note never framed its finding as a
self-improvement-loop candidate; this note is the first to make that connection); (4) the
compositional-math self-margin row (row 8 of the same taxonomy) supplies independent
cross-operation confirmation of rank 1's underlying law, strengthening rather than duplicating it;
(5) `exp_conceptnet_semantic_seeded_beam_composition_v1.py`'s per-item `out_degree` field
(line 396) is a genuinely new observation this drill surfaces — present in code, absent from the
persisted aggregate metrics, an honest "cannot yet assess" flag rather than a forced ranking.

---

## Substrate-product implications

For Director: this drill asks for NO new dispatch as its immediate next step — the reasoning-depth
capacity-provisioning candidate (rank 1) can be wrapped in the same monitor-loop scaffolding
`hdi_exp_dev` already built for density, at zero marginal GPU cost, reusing fully-landed data. The
resonator FULL K-sweep (rank 2, Q1) remains worth dispatching on its own merits (a real,
already-built, already-smoke-passed cell) regardless of this note's ranking — it answers a
separate, load-bearing product question (is K>=5 joint-factor recovery a near-term capability path)
whether or not it also serves the self-improvement-loop demonstration. The honest headline for the
broader question: self-improvement is NOT closed by today's density HARD_FAIL — the loop machinery
is validated and correctly produced an honest null on a genuinely flat regime; the project's
operating landscape is NOT uniformly flat/trivial (reasoning-depth and resonator both show
real, order-of-magnitude-scale non-flatness) — the honest bound is narrower than "self-improvement
proven" and stronger than "self-improvement landscape is flat everywhere": **at least one, and
likely two, regimes exist where a genuine non-trivial self-improvement law is demonstrable, and
the cheapest of them (reasoning-depth) can be tested at zero new GPU cost using data already on
disk.**

---

## Citations (verified count)

Two parallel Sonnet lit-scan sub-agents dispatched this cycle (generic engineering/math/stats
terms only per query-privacy discipline; no substrate-novel mechanism names sent externally),
targeting the two new angles this revival drill introduces beyond what the two trigger notes
already cited: (a) whether inverting an already-validated collapse law into a proactive
capacity-provisioning recommendation is methodologically sound and how such inversions are
typically validated/discriminated in reliability engineering and capacity-planning practice; (b)
whether treating a correctly-detected flat/null landscape as a valid scientific outcome (rather
than a failed loop) has established precedent, and how fields distinguish genuine flatness from
grid-coarseness artifacts.

**Sub-agent 1 (capacity provisioning from a fitted failure/collapse law — inverse-problem framing),
9 sources:** "Reliability Optimization of a Series-Parallel k-out-of-n System with Failure Rate
Depends on Working Components," *Int. J. Industrial Engineering*; "Reliability allocation of the
system with k-out-of-n:G subsystems considering K-mixed redundancy strategy," ScienceDirect 2025;
"Large-scale benchmarking of multi-objective soft-computing metaheuristics for redundancy
allocation in repairable k-out-of-n systems," arXiv:2512.18343; "Spare Parts Forecasting Based on
Reliability" (IntechOpen) — spares/demand forecasting confirms held-out-period validation (e.g.
"2014-2018 train / 2019 held out") IS standard practice for inverted capacity recommendations, the
closest direct precedent found; "A Hitchhiker's Guide to Scaling Law Estimation," arXiv:2410.11840;
"Practical Scaling Laws: Converting Compute into Performance in a Data-Constrained World,"
arXiv:2605.09189 (two-step chain law directly analogous to this note's `p(x)^D` structure);
"Loss-to-Loss Prediction: Scaling Laws for All Datasets," arXiv:2411.12925; "Functional Component
Ablation Reveals Specialization Patterns in Hybrid Language Model Architectures," arXiv:2603.22473
(scrambled/matched-random ablation control precedent, transplanted from ML-interpretability rather
than queueing/reliability lit); Design-of-Experiments Response Surface Methods notes
(n.ethz.ch/~kahans/doe2020/ch-rsm.html) — replicated-center-point + lack-of-fit testing as the
formal method for decomposing "flat" into genuine-flat vs noise/resolution-masked-gradient.
**Honest gap flagged by the sub-agent:** no paper found that directly states inverse
(resource-for-target-performance) scaling-law extrapolation is proven harder than forward
extrapolation — an inferred, not directly-cited, finding; queueing-theory-specific
discriminator/scrambled-control designs returned nothing domain-matched (the control concept is
real but only found in an adjacent field, ML ablation, not capacity-planning literature itself).

**Sub-agent 2 (honest-null validity + retry-budget-as-geometric-process + flat-vs-coarse-grid),
9 sources:** "Position: Embracing Negative Results in Machine Learning," arXiv:2406.03980 (2024,
explicit argument that a correctly-detected null is a legitimate, underpublished scientific
outcome); "Want for nothing, need for null: useful output from negative results," *Matter* (Cell
Press) 2024; "Better null models for assessing predictive accuracy of disease models," PMC10162537
(2023, shows a correctly-chosen null model legitimately beating complex models under sparse-data
regimes — direct precedent for "nothing to learn is sometimes the statistically correct
conclusion"); Li, Jamieson, DeSalvo, Rostamizadeh, Talwalkar, "Hyperband," JMLR 2018 (multi-armed-
bandit resource allocation across knobs/arms, the standard framework for arm-elimination, though
not specifically for provably-flat arms); "HAMLET: A Learning Curve-Enabled Multi-Armed Bandit for
Algorithm Selection," arXiv:2001.11261; Luby, Sinclair, Zuckerman, "Optimal Speedup of Las Vegas
Algorithms," *Information Processing Letters* 1993 (canonical general, non-SAT-specific restart-
budget-as-geometric-process result); "Optimal Restart Strategies for Parameter-dependent
Optimization Algorithms," arXiv:2501.10173 (2025); "Black-box Acceleration of Las Vegas Algorithms
and Algorithmic Reverse Jensen's Inequalities," arXiv:2304.11017; Saltelli et al., "Variance Based
Sensitivity Analysis of Model Output," *Computer Physics Communications* 181 (2010, Sobol'-sequence
convergence-of-sensitivity-index as the canonical test for flat-vs-undersampled); "Towards
systematic grid selection in LES," arXiv:1912.04699 (CFD-specific but directly on point: define
sufficient resolution as the coarsest grid where further refinement doesn't change the sensitivity
estimate — this note's own "grid dense enough, `b` numerically exact zero across leave-one-out
folds" check in Sec. 1 is the same convergence-style argument, applied post-hoc rather than by
pre-registered refinement). **Honest gaps flagged by the sub-agent:** no named framework found
specifically for "knob pre-screening by known-flat response surface" (an implicit special case of
bandit arm-elimination, not a separately named methodology); no core-ML/stats paper found stating a
general numeric rule for "how many grid points before flatness is claimable" (the Saltelli
convergence-of-estimate approach, borrowed from numerical-simulation/UQ literature, is the closest
general-purpose answer).

**Verified count: 18 distinct external sources found via live web search across 2 sub-agents this
cycle. Zero fabricated citations; both sub-agents explicitly flagged their own honest gaps (no
direct proof that inverse extrapolation is harder than forward; no queueing-theory-specific
discriminator-control precedent; no named "flat-knob-pre-screening" framework; no numeric
grid-density rule for claiming flatness in core ML literature — Saltelli's convergence-of-estimate
method is the nearest general answer, imported from sensitivity-analysis/UQ rather than native to
this project's domain).**

Internal citations (not counted toward the external total, load-bearing, all independently
re-verified off-disk this drill, not carried over from memory text uninspected):
`data/exp_self_improvement_monitor_loop_density_v1/metrics.json` (HARD_FAIL verdict, full
`observed` block, all three scales, read directly); `preregs/self_improvement_monitor_loop_density_v1.md`;
`data/exp_reasoning_depth_keyslots_sharding_v1/metrics.json` (`extra.per_op`, 6 op-points,
`capacity_law` nested arms, read directly); `research_reasoning_depth_self_margin_closed_form_
2026-07-06.md`; `research_self_margin_taxonomy_synthesis_cg_meta_assessment_2026-07-06.md`;
`research_resonator_restart_budget_geometric_race_law_2026-07-07.md`;
`preregs/2026-07-07_resonator_ksweep_reachability_v1.md`;
`experiments/exp_conceptnet_semantic_seeded_beam_composition_v1.py` (line 396, `out_degree` field,
grep-verified); `data/exp_conceptnet_semantic_seeded_beam_composition_v1/metrics.json` (confirmed
`out_degree` NOT persisted at aggregate level, `per_arm` structure read directly);
`research_density_scale_sweep_design_970k_extrapolation_2026-07-07.md`;
`research_density_scale_theory_reconciliation_970k_2026-07-07.md`.
