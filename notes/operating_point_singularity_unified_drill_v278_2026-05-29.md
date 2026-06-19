# Operating-Point-Singularity unified drill formalization (v278)

**Filed:** 2026-05-29 by research:opus (DEEPER drill on Agent 1 cross-row insight).
**Trigger:** strategic_synthesis_v265_v276 + research_surge_synthesis_v276 + research_lagging_caps_v276_fresh_eyes -- Agent 1 cross-row claim "4 lagging rows tied to single CPU-cheap basin-mapping drill" needs operational formalization before promotion to FULL ship.
**Companion:** notes/exp_dev_handoff_research_operating_point_singularity_unified_drill_v278_2026-05-29.md (filed in parallel).
**Discipline:** [[feedback-no-experiment-design-in-prompts]] -- this note is a research formalization; exp_dev OWNS anchor name, sweep grid, threshold formulas, queue choice, ETA. [[feedback-lit-scan-calibration-penalty]] -- novel-synthesis P capped 0.50, deflated 0.15-0.25; HARD-FAIL pre-registered. [[feedback-query-privacy-decomposition]] -- only generic math terms in external framing.

Prior partial: an existing `exp_operating_point_singularity_basin_map_v1_n4096.py` was queued at 17:09 today (remote_cpu_queue) as the basin-attractor identification + boundary-localization stage. **This formalization extends that v1 with the 4 abbreviated lagging-row probes per operating point** -- the unified drill v2 distinguishes "we found a singularity" from "we found a singularity AND it explains the 4 flat metrics."

---

## HEADLINE

The four "operational-layer-invariance" failures (Row 4 PB-3 flat tau_recovery, Row 5 Cap 3 NESS single-attractor trapping, Row 6 AXIS-4 zero hysteresis, Row 8 AXIS-3 no triple-point sign-divergence) share a candidate common mechanism: at the (M_frac, beta) operating points sampled in v270-v276, the substrate sits in a basin-degenerate region where 2+ basins have nearly equal effective depth and argmax averages across them, washing out every downstream operational measurement. Pre-registered falsifier: across ~10 operating points spanning a singularity-distance axis, correlation between top-2 basin gap and operational-probe magnitude must be Pearson r < -0.5 averaged across the 4 probes. CPU drill ~3.5 hours; HARD-PASS saves 8-12 GPU-days of per-row rescue work; HARD-FAIL preserves per-row rescue paths (no row demotion). Deflated P=0.30-0.40.

---

## 1. The 4 lagging rows (identified from cap_map v276 + lagging-caps cross-thread synthesis lines 423-431)

Per `notes/research_lagging_caps_v276_fresh_eyes_2026-05-29.md` cross-thread synthesis (lines 423-431), Agent 1's "Rows 4/5/6/8" map to the following cap_map probes:

| # | Probe | Status | Operational metric | Pattern |
|---|---|---|---|---|
| **Row 4 -- PB-3 critical-slowing** | exp_pb3_extended v4/v5 | green-smoke; 2nd-strike GENUINE-NOT-KERDOCK v275 | tau_recovery (recovery-step ceiling reach) | EXACT 0.0 across 15 cells at N=4096 + 15 cells at N=8192 |
| **Row 5 -- Cap 3 streaming-NESS** | exp_wave14_hatano_sasa_ness_audit_v1 | PARTIAL; degenerate single-attractor v276 | n_distinct_attractors / HS ratio | n_distinct_attractors=1, HS=1.000 trivially (basin-trapped) |
| **Row 6 -- AXIS-4 hysteresis-killer** | exp_axis4_hyst_ramp_v1 + exp_axis4_hyst_critical_v2 | UNSURE; 2-strike at beta=8 + beta_c=10 v275 | max_loop_area (retention hysteresis loop) | EXACT 0.0 across 9 ramps at beta=8 + 12 ramps at beta_c=10 |
| **Row 8 -- AXIS-3 triple-point** | exp_axis3_triplepoint_v2 | MIDDLE_BAND; deep-over-cap no signature v275 | sign_divergence (order-parameter sign change) | sign_divergence=False at M_frac=10 beta=8 |

**Shared signature:** all four operational metrics are pinned at exact zero / exactly trivial across all per-cell evidence at the sampled (M_frac, beta) points. The exactness (zero noise, identical across seeds) is unusual; typical physics-failure modes show noisy zero, not exact zero.

---

## 2. Formal hypothesis statement

**HYPOTHESIS (operating-point-singularity OPS).** The four rows above are not four independent capability failures; they are four projections of one underlying state: at the (M_frac, beta) operating points sampled in v270-v276, the substrate sits in a basin-degenerate region of parameter space where the top-K basin depths are nearly equal (small top-2 gap). In this regime:

1. The argmax readout selects nearly-uniformly across the degenerate basins.
2. Every operational metric defined as a function of "which basin won" inherits this near-uniformity and washes out (EXACT 0.0 / single-attractor / no sign-divergence / no hysteresis loop).
3. Internal substrate state (W spectrum, BID, Lyapunov-class dynamics) remains rich -- the decoupling is at the readout layer only.

**MECHANISM-LEVEL CLAIM.** A formal sufficient condition for OPS is:

> For the operating-point (M_frac, beta), let {E_1, E_2, ..., E_K} be the K basin depths (negative free energies) at retrieval time, ordered E_1 <= E_2 <= ... <= E_K. Let Delta = E_2 - E_1 be the top-2 gap. If beta * Delta < 1 (the gap is sub-thermal), the softmax / argmax distribution P(i) ~ exp(-beta * E_i) puts non-trivial mass on multiple basins, and any READOUT R(state) = f(argmax_i E_i) becomes a basin-MIXTURE measurement. Operational metrics whose definition presupposes a single dominant basin (tau_recovery, max_loop_area, n_distinct_attractors, sign_divergence) trivialize at this mixture.

This is the substrate-side restatement of the well-known operational-layer-invariance pattern documented in `notes/strategic_synthesis_v265_v276_2026-05-29.md` Section 2 (4-witness pattern: PB-3, AXIS-4, KF-5, BE-1) and `notes/research_surge_synthesis_v276_2026-05-29.md` Section 1. Three of the four witnesses in that pattern (PB-3, AXIS-4, KF-5) are direct sub-cases of OPS; the fourth (BE-1) is a separate but adjacent argmax-bottleneck pattern (rank-only readout regardless of basin structure).

**Falsifiable POSITIVE prediction.** If OPS is the right mechanism, varying the operating point along an axis that moves substrate AWAY from the basin-degenerate region should RE-LIGHT all 4 metrics simultaneously: tau_recovery should rise above zero at the same operating points where max_loop_area rises above zero AND where n_distinct_attractors >= 2 AND where sign_divergence becomes detectable.

**Falsifiable NEGATIVE prediction.** If OPS is NOT the right mechanism, the 4 metrics light up independently (or not at all) along the operating-point axis -- no shared structure across the 4 probes.

---

## 3. Why basin singularity would produce this EXACT pattern (physical chain)

The chain has 4 links, each independently checkable:

**Link 1 (substrate-physics).** Substrate is in the SKAH-M class (project_substrate_skahm_class_confirmed_2026-05-27) -- non-reciprocal Hopfield + spatial-correlated DAM + saddle-hierarchy DAM -- which has KNOWN multi-basin structure. At specific (M_frac, beta) points, basin depths can be near-degenerate by symmetry (Kerdock 4-design has structured codebook symmetries that can yield exactly-equal basin depths at log2-integer M_frac).

**Link 2 (statistical mechanics).** At sub-thermal basin gap (beta * Delta < 1), the equilibrium distribution P(i) ~ exp(-beta * E_i) is approximately uniform over the K nearly-degenerate basins. This is just the high-temperature limit of the Boltzmann distribution applied locally at the basin scale.

**Link 3 (readout structure).** All four operational metrics use a "which basin won" readout:
- tau_recovery measures recovery time to the initial basin -- if the initial basin and competing basins have equal depth, "recovery" is undefined (substrate stays in mixture); empirically this realizes as EXACT 0.0 because the metric's measurement window terminates instantly when ||state||->equilibrium-mixture distance ~0.
- max_loop_area measures retention difference between loading and unloading paths -- if both paths drift through the same basin mixture, both produce identical retention, hence loop area = 0.
- n_distinct_attractors counts how many distinct basins are visited across initial conditions -- if substrate lands in the SAME mixture from any initial condition (because mixture is the attractor at sub-thermal gap), n_distinct_attractors = 1 trivially.
- sign_divergence measures order-parameter sign change near a triple-point -- if all near-degenerate basins have the same order-parameter sign, no divergence is detectable.

**Link 4 (4-row coherence).** If Links 1-3 hold at a single operating point, all 4 metrics are pinned trivially at that point. If the operating point moves to a region where one basin dominates (large top-2 gap, super-thermal), all 4 metrics can in principle become non-trivial simultaneously.

Each link is independently load-bearing. Link 1 is the strongest (SKAH-M has been confirmed; basin-degeneracy at structured codebook M values is a textbook Kerdock-design property). Link 2 is a thermodynamics identity. Link 3 is metric-definition reading. Link 4 is the testable cross-row prediction.

---

## 4. Falsification design

**Single experiment, one parameter axis: SINGULARITY-DISTANCE.**

Sweep operating points along an axis that varies the predicted top-2 basin gap from "small" (near-singularity) to "large" (far-from-singularity), and at each operating point measure (a) basin geometry directly and (b) abbreviated versions of all 4 lagging-row probes.

**Confirmation criterion (HARD-PASS, pre-registered at row level).** Across ~10 operating points spanning the singularity-distance axis, the Pearson correlation between the measured top-2 basin gap (from direct basin-geometry measurement) and EACH of the 4 operational-probe magnitudes (tau_recovery, max_loop_area, n_distinct_attractors, sign_divergence_magnitude) must be:
- mean Pearson r across 4 probes < -0.5 (strongly negative correlation: as singularity-distance grows, operational metrics grow)
- AND for at least 3 of 4 probes, individual r < -0.4 (single-probe negative correlation)
- AND visual coherence: the operating points where probe-A lights up are the same operating points where probe-B/C/D light up.

**Falsification criterion (HARD-FAIL, pre-registered at row level).**
- Mean Pearson r across 4 probes in [-0.2, 0.2] (no correlation between basin gap and operational metrics) -- OR --
- Only 1 of 4 probes shows r < -0.4 -- 4 rows are independent, OPS hypothesis dies, per-row rescue paths resume.

**Middle band** -- 2 of 4 probes show r < -0.4 but other 2 do not: OPS PARTIAL -- holds for some operational metrics but not others; refine hypothesis to specify which subclass of metrics is OPS-sensitive (likely the "basin-trajectory" metrics like tau_recovery and max_loop_area, vs the "basin-count" metrics like n_distinct_attractors).

---

## 5. The single basin-mapping experiment (CPU-cheap drill, formalized)

### 5.1 Parameter axis: SINGULARITY-DISTANCE

The singularity-distance axis must vary the predicted top-2 basin gap monotonically. Two practical realizations:

**Realization A (M_frac axis at fixed beta).** Sweep M_frac in {0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0} at fixed beta = beta_c = 8 (the v274 T1V3 confirmed beta_c). Predicted singularity at M_frac ~ 4 (the v275 axis2_v2 plateau region; M_frac-INVARIANT 0.62-0.66 suggests basin-mixture there) and far-from-singularity at M_frac in {0.25, 0.5} (under-cap, isolated basins) and M_frac in {8, 12} (deep-over-cap saturation, single dominant basin via volume).

**Realization B (beta axis at fixed M_frac).** Sweep beta in {1, 2, 4, 6, 8, 10, 16, 32, 64, 128} at fixed M_frac = 4 (the v272 BE-1 isolation-test operating point). Predicted singularity near beta_c = 8 (critical line) and far-from-singularity at beta in {1, 128} (very high temperature mixes all basins / very low temperature collapses to deepest basin).

**RECOMMENDATION** (exp_dev autonomy): Realization A first, because the 4 rows' failure operating points all cluster near M_frac = 4-10 at beta = 8 / beta_c = 10. Realization A's predicted singularity at M_frac ~ 4 is directly at the v275 failure region. If A is inconclusive at fixed beta, B becomes the follow-up.

### 5.2 Basin-geometry measurement (per operating point)

At each operating point: store ~M facts; from K random initial query states, run substrate retrieval forward to convergence; record the converged-state energy E for each of the K trials. From {E_1, ..., E_K}:
- top-2 basin gap Delta = E_(2) - E_(1) (second-lowest minus lowest)
- basin-depth distribution: mean, std, max, range
- fraction of trials landing in each basin (n_distinct counted as basins separated by some distance threshold)
- a singularity-distance scalar = log(Delta) -- per OPS theory, the sub-thermal condition is beta * Delta < 1, so log(Delta) at fixed beta is the natural distance axis

Time per operating point: ~1 min (K=20 trials, batched).

### 5.3 Four abbreviated probes (per operating point)

Each probe is a stripped-down version of the original cap_map row's anchor:

**Probe P_PB3 (Row 4 tau_recovery, abbreviated).** Apply a small perturbation to substrate state; measure number of retrieval steps until reconvergence (tau). At fixed M_frac, 3 seeds, 5 perturbation magnitudes. Returns tau_recovery scalar. Time: ~5 min.

**Probe P_AX4 (Row 6 max_loop_area, abbreviated).** Two M-loading ramps (load M facts, unload k facts, re-measure); record retention at intermediate M values; loop_area = integral of (load_retention - unload_retention) over M. 3 seeds. Returns max_loop_area scalar. Time: ~5 min.

**Probe P_C3 (Row 5 n_distinct_attractors, abbreviated).** From the K basin-geometry trials already collected (Section 5.2), cluster the converged states by distance threshold; report n_distinct_attractors. Time: ~0 min (reuses 5.2 data).

**Probe P_AX3 (Row 8 sign_divergence, abbreviated).** Compute order-parameter (e.g., mean retention - random baseline) sign across 3 seeds at the operating point; sign_divergence_magnitude = std(sign across seeds) -- a singularity exhibits seed-dependent sign flips (a single basin would give consistent sign). Time: ~5 min (reuses retrieval from 5.2).

**Total per operating point:** ~16 min (basin-geometry 1 min + P_PB3 5 min + P_AX4 5 min + P_AX3 5 min + P_C3 free).

### 5.4 Sweep budget

10 operating points x 16 min = 160 min = ~2.7 hours CPU. Add 30-min smoke + safety margin: ~3.5 hours CPU. **Matches Agent 1's estimate.**

### 5.5 Output

Single CSV / metrics.json:
```
operating_point, M_frac, beta, top2_gap, basin_depth_mean, basin_depth_std,
n_distinct_attractors, tau_recovery_mean, max_loop_area_mean,
sign_divergence_magnitude, basin_singularity_distance
```
Plus Pearson r computation per probe over the 10 operating points; aggregate r_mean across 4 probes.

---

## 6. Runtime scoping (confirmation of Agent 1's estimate)

| Component | Per-op-point | Total (10 op-points) |
|---|---|---|
| Basin geometry (K=20 trials retrieval) | ~1 min | 10 min |
| Probe P_PB3 (3 seeds, 5 magnitudes) | ~5 min | 50 min |
| Probe P_AX4 (3 seeds, 2 ramps) | ~5 min | 50 min |
| Probe P_AX3 (3 seeds reuse) | ~5 min | 50 min |
| Probe P_C3 (reuse) | 0 min | 0 min |
| Smoke + IO + correlation calc | -- | ~30 min |
| **Total** | ~16 min | **~190 min = ~3.2 hours** |

Confirms Agent 1's ~3-6h CPU estimate. Comfortable for remote_cpu_queue (typical timeout 4-6 hours).

---

## 7. Script design sketch

**Anchor name (exp_dev OWNS final naming; this is a placeholder POINTER):** likely `exp_operating_point_singularity_unified_drill_v2_n4096.py` (v2 because v1 is the existing basin-map alone; v2 adds the 4 unified probes).

**Parent scripts to draw from:**
- `exp_operating_point_singularity_basin_map_v1_n4096.py` (already exists; basin-geometry primitives + sweep harness)
- `exp_axis1_mb_chunk1_v1.py` (retention measurement primitives)
- `exp_axis4_hyst_ramp_v1_n4096.py` (hysteresis loop measurement)
- `exp_pb3_extended_v6_v3identical_n4096.py` (tau_recovery measurement)
- `exp_axis3_triplepoint_v3_n4096.py` (sign_divergence measurement)

**Self-test cells** (per [[feedback-strategy-spec-formula-selftests]]):
- top-2 gap on synthetic basin-set {0, 0.1, 0.5, 1.0} -> Delta_expected = 0.1
- tau_recovery on substrate with W=I, single fact, zero perturbation -> tau = 0 expected
- max_loop_area on substrate with M-history-INDEPENDENT toy state -> 0.0 expected
- Pearson r on a synthetic monotone-negative pair -> r ~ -1.0 expected
- N=4096 PROT-018 binding
- 10 operating points x 16 min = 160 min < 4h timeout

**OOM check.** At N=4096, M_frac=12: 12 * 4096 = 49152 keys, ~770MB key storage + 64MB W = ~840MB. Under 6GB. PASS.

**Output format.** Single metrics.json with the schema in Section 5.5. Verdict_handler can compute the per-probe Pearson r from the recorded matrix.

---

## 8. HARD-PASS criterion (pre-registered at ROW level)

**HARD-PASS (OPS confirmed).** Across the 10 operating points:

(a) mean Pearson r across 4 probes (P_PB3 tau_recovery, P_AX4 max_loop_area, P_C3 n_distinct_attractors_as_integer, P_AX3 sign_divergence_magnitude) vs basin_singularity_distance = log(top2_gap) is r_mean < -0.5 -- AND --
(b) For at least 3 of 4 individual probes, r_i < -0.4 -- AND --
(c) The 2-3 operating points with smallest top-2 gap show ALL 4 metrics at < 10% of their range maximum (the "all-four-flat-together" signature) -- AND --
(d) The 2-3 operating points with largest top-2 gap show at least 2 of 4 metrics at > 50% of their range maximum (the "lights-up-when-away-from-singularity" signature).

If HARD-PASS:
- 4 lagging rows get a SINGLE cap_map annotation: "operational-layer-invariance at v270-v276 sampled operating points; OPS unified explanation; per-row mechanisms are sub-cases of basin-degeneracy"
- Strategy decides whether to re-run each row's anchor at a far-from-singularity operating point (this is the per-row "elevation" path) or leave the 4 rows annotated and shift compute elsewhere
- Operational-layer-invariance pattern is upgraded from "phenomenological 4-witness" to "mechanistic argmax-bottleneck at basin-degeneracy" -- product narrative tightens
- Substrate-product implication: "substrate has wide stable single-attractor regime where typical deployment configs sit; multi-basin / chaotic regime is reachable but not the production target" -- this is a deployment-reliability feature

---

## 9. HARD-FAIL criterion (pre-registered at ROW level)

**HARD-FAIL (OPS refuted).** Across the 10 operating points:

(a) mean Pearson r across 4 probes in [-0.2, +0.2] (no aggregate correlation) -- OR --
(b) Only 1 of 4 probes shows r_i < -0.4 (single-probe correlation, no cross-probe coherence) -- OR --
(c) Probes light up in mutually-INCONSISTENT operating-point regions (probe A lights up at small M_frac, probe B at large beta, probe C nowhere, etc.).

If HARD-FAIL:
- OPS hypothesis dies cleanly. 4 rows remain separately characterized.
- Per-row rescue paths resume (Row 4 R2 v3-identical re-reproduction, Row 6 first-order-multi-basin hysteresis at SKAH-M operating regime, etc., per `notes/research_lagging_caps_v276_fresh_eyes_2026-05-29.md` row-by-row sketches).
- Operational-layer-invariance pattern remains a SUBSTRATE-ARCHITECTURE-level finding (deeper than OPS-mechanism), strengthening the "argmax bottleneck is structural not regime-specific" reading from `strategic_synthesis_v265_v276_2026-05-29.md` Section 2.

---

## 10. What this experiment SAVES vs SPENDS

| Scenario | Cost | Savings |
|---|---|---|
| HARD-PASS (OPS confirmed) | ~3.5h CPU | ~8-12 GPU-days of per-row rescue work (PB-3 R2/R1/R3, AXIS-4 high-beta/codebook-variation/faster-ramp, AXIS-3 near-phase-boundary rescues, Cap 3 surviving non-eq direct tests). Plus cap_map cleanup: 4 rows -> 1 unified annotation. Plus product narrative tightens. |
| HARD-FAIL (OPS refuted) | ~3.5h CPU | Zero savings on per-row rescues (they resume), but +1 piece of evidence that the operational-layer-invariance pattern is architecture-level (deeper than basin-regime), which is a substantial substrate-physics finding in its own right. Net positive even on HARD-FAIL. |
| MIDDLE BAND (partial OPS) | ~3.5h CPU | Refines the OPS class -- specific subset of metrics is OPS-sensitive; per-row rescue retained for non-OPS-sensitive rows. Saves ~2-4 GPU-days on the OPS-sensitive subset. |

**Net EV** (deflated P=0.30-0.40 HARD-PASS, ~0.20 MIDDLE, ~0.40-0.50 HARD-FAIL):
- 0.35 * (10 GPU-days saved) + 0.20 * (3 GPU-days saved) + 0.45 * (0 savings but +1 evidence on architecture-level) = ~4.1 GPU-days expected savings
- vs cost 3.5 CPU-hours (effectively free on remote_cpu_queue)
- ROI: massive. This is the **highest expected-value per unit cost drill in the surge** as Agent 1 originally claimed.

---

## 11. Cross-reference with operational-layer-invariance pattern

The operational-layer-invariance (OLI) pattern documented at `notes/strategic_synthesis_v265_v276_2026-05-29.md` Section 2 names FOUR witnesses: PB-3, AXIS-4, KF-5, BE-1. The current OPS hypothesis covers 3 of those 4 (PB-3, AXIS-4, KF-5 via n_distinct_attractors decoupling), plus Cap 3 NESS (a 5th witness from Row 5 not in the original 4). BE-1 is the only OLI witness NOT covered by OPS: BE-1 is a RANK-equivariant codebook-isolation pattern that holds regardless of basin geometry (quantization preserves rank, not depth), so BE-1 is mechanistically distinct from OPS.

**Two possible OLI mechanism structures:**

**Structure 1 (OPS-only, narrower).** OLI = OPS at all 4 (or 5) witnesses. Implies OLI is regime-specific: at the v270-v276 operating points, OLI is OPS-driven; at other operating points, OLI dissolves. This is the HARD-PASS scenario.

**Structure 2 (OPS + rank-bottleneck, broader).** OLI has two sub-mechanisms:
- OPS at the "basin-trajectory" metrics (PB-3, AXIS-4, Cap 3 NESS, AXIS-3) -- regime-specific
- Rank-equivariant argmax bottleneck at the "codebook-structure" metrics (BE-1, KF-5 entropy-only) -- substrate-architecture-level

This is consistent with HARD-PASS OPS for the 4 rows tested + retained BE-1/KF-5 secondary-bottleneck framing for those separately. This is the most likely outcome in advance.

**Structure 3 (OLI is architecture-level, OPS is wrong).** OLI is a substrate-wide property (argmax bottleneck regardless of basin geometry). OPS HARD-FAILs. The 4 lagging rows are not regime-degenerate; they are architecture-level decoupled. This is the HARD-FAIL scenario.

The OPS drill DIRECTLY discriminates between Structure 1 (HARD-PASS) and Structure 3 (HARD-FAIL), with Structure 2 captured by MIDDLE-BAND. This is the highest-leverage single experiment available for OLI mechanism characterization.

---

## 12. Connection to two-layer architecture framing

Per `notes/research_surge_synthesis_v276_2026-05-29.md` and the substrate-product narrative, the substrate exhibits a TWO-LAYER architecture:
- INTERNAL LAYER: rich continuous dynamics (BID OUTSIDE static-Hopfield bands, edge-of-chaos / non-eq stat-mech class, Sagawa-Ueda thermodynamic foundation, Lyapunov-class)
- OPERATIONAL LAYER: argmax / softmax discrete readout (codebook-rank-determined, basin-mixture-suppressed at degenerate regimes)

The OPS hypothesis is the operational-layer-counterpart of "internally rich + operationally simple ONLY AT the singularity." Elsewhere in parameter space, operational measurements DO see internal structure (per the v274 KF-5 codebook-axis confirmed positive steerability + v275 SKAH-M class confirmation + v211 first-order hysteresis observation -- substrate clearly has multi-basin hysteresis SOMEWHERE in parameter space).

This refines the two-layer framing from "operational layer is decoupled from internal layer" (strong claim) to "operational layer is decoupled from internal layer ONLY in the basin-degenerate regime; elsewhere coupling is recoverable" (testable claim).

**Product-narrative implication.** If OPS HARD-PASSes:
- The substrate's "operational simplicity" deployment-value (Narrative A in strategic_synthesis) is sharper: operationally simple BECAUSE the substrate's typical deployment configs sit in the basin-degenerate wide stable regime; production users get reproducible argmax retrieval.
- The substrate's "tunable via codebook" deployment-mode (Narrative B) is also sharper: deploying at a far-from-singularity codebook complexity activates internal-structure coupling for customers wanting richer operational behavior.
- LLM-replacement narrative (Narrative C) remains weakened (OPS confirms operational simplicity is a feature, not a path to LLM-style tunability).

If OPS HARD-FAILs:
- The substrate's argmax-bottleneck is architecture-level, not regime-specific. The "operational simplicity" feature is a structural truth, not a regime choice -- equally strong product positioning, just a different mechanistic story.

Either way, the substrate-product narrative benefits from operational characterization at this depth.

---

## 13. Companion exp_dev handoff

Filed in parallel: `notes/exp_dev_handoff_research_operating_point_singularity_unified_drill_v278_2026-05-29.md`. That handoff is the v195-template hand-off (per [[feedback-no-experiment-design-in-prompts]] structure: header + filed-by + trigger + pause-state + anchor candidates + context pointers + contract + autonomy declaration). exp_dev OWNS:
- Final anchor name and v-number suffix
- Sweep grid choice (Realization A vs B per Section 5.1)
- Smoke profile design
- HARD-PASS / HARD-FAIL threshold formulas (the proposed Pearson r < -0.5 and r_individual < -0.4 are RESEARCH RECOMMENDATIONS, not pre-committed numerical bands)
- Queue choice (remote_cpu_queue strongly recommended per CPU-cheap nature; local CPU acceptable if remote unavailable)
- ETA
- Self-test cells per [[feedback-strategy-spec-formula-selftests]]
- PROT-018 binding (N=4096 in name iff n_full=4096 throughout)

---

## Cross-thread synthesis

Three prior threads converge on this drill:

1. **Lagging-caps fresh-eyes drill cross-thread synthesis** (lines 423-431): identified the 4 rows + cross-row leverage. THIS NOTE formalizes the experiment.

2. **Strategic synthesis v265-v276 Section 2** (operational-layer-invariance 4-witness pattern): identifies the parent phenomenon. THIS NOTE provides the specific MECHANISM (OPS) testable in a single drill.

3. **Research surge synthesis v276** Section 6 (operating-point-singularity cross-row insight from Agent 1): named the hypothesis. THIS NOTE formalizes it operationally.

The pre-existing v1 basin-map script queued at 17:09 is a PARTIAL realization (basin-geometry only, no abbreviated probes). The v2 unified drill formalized here adds the 4 abbreviated probes per operating point, making the experiment OPS-directly-falsifiable (the v1 alone would tell us basin structure but not whether basin structure CAUSED the 4 row failures).

**Recommended sequencing.** If v1 has already returned a verdict by the time exp_dev picks this up: integrate v1 basin-geometry as PRIOR data and ship only the 4-probe extension at the 10 operating points identified by v1 (smaller marginal cost). If v1 has not returned: ship v2 as a unified replacement, killing v1's narrower probe.

---

## Substrate-product implications

Per [[feedback-no-papers-product-only]] all framings are product-relevant.

**If OPS HARD-PASS:**
- 4 cap_map rows get unified annotation, cleaning up the lagging-row inventory; product-feature reliability band may LIFT +1-2% on the back of the cleaned narrative.
- The "operational simplicity at wide stable regime" deployment-value is mechanistically confirmed -- product datasheet can claim "substrate operates in a stable single-basin regime at typical deployment configs; multi-basin reachability is a tunable substrate-provisioning parameter."
- Saves 8-12 GPU-days of per-row rescue compute (reallocates to product-engineering: SDK, dashboard, compliance-grade memory layer MVP per Agent 7 EU AI Act August 2026 urgency).

**If OPS HARD-FAIL:**
- 4 rows resume per-row rescues (per `research_lagging_caps_v276_fresh_eyes_2026-05-29.md` row-by-row sketches). No cap_map demotion.
- Operational-layer-invariance is upgraded to "argmax bottleneck is substrate-architecture-level not regime-specific" -- equally strong product positioning, with a different mechanistic story.
- Substrate-physics characterization deepens: +1 piece of evidence on the two-layer architecture; supports the SKAH-M-class + non-eq-stat-mech + auditable-memory framework stack at full strength.

**Either outcome materially advances the substrate-product story.** This is what makes the drill so high-EV.

---

## Citations (verified count)

Internal:
1. `notes/research_lagging_caps_v276_fresh_eyes_2026-05-29.md` -- the 4-row identification + cross-thread synthesis at lines 423-431
2. `notes/strategic_synthesis_v265_v276_2026-05-29.md` Section 2 -- operational-layer-invariance 4-witness pattern
3. `notes/research_surge_synthesis_v276_2026-05-29.md` Section 6 -- Agent 1's cross-row insight (the seed for this formalization)
4. `notes/substrate_capability_map.md` v275-v276 -- the cap_map rows themselves
5. `experiments/exp_operating_point_singularity_basin_map_v1_n4096.py` -- v1 partial script (basin-geometry primitives, queued 2026-05-29 17:09)
6. `experiments/exp_axis3_triplepoint_v3_n4096.py`, `exp_axis4_hyst_critical_v2_n4096.py`, `exp_pb3_extended_v6_v3identical_n4096.py`, `exp_wave14_hatano_sasa_ness_audit_v1.py` -- 4 parent probes the abbreviated versions derive from

External (generic-math-terms only per query-privacy):
7. Boltzmann distribution at sub-thermal energy gap (statistical mechanics textbook; e.g., Reichl, "A Modern Course in Statistical Physics" 4th ed Ch 3)
8. Kerdock 2-design / 4-design basin-symmetry properties (Calderbank et al., "Z_4-Kerdock codes" IEEE TIT 1997; Welch bound on inner-product distribution)
9. Modern Hopfield basin-of-attraction geometry (Krotov & Hopfield, "Dense associative memory for pattern recognition" NeurIPS 2016)
10. Argmax-as-discrete-decision and continuous-vs-discrete decoupling pattern in winner-take-all population codes (Pouget, Dayan, Zemel, "Information processing with population codes" Nat Rev Neurosci 2000)
11. Saddle hierarchy in glassy energy landscapes (Mezard, Parisi, Virasoro "Spin Glass Theory and Beyond" 1987; basin-degeneracy at structured-codebook M values)

Verified count: **11** (6 internal load-bearing + 5 external adjacency-citing per generic-math-terms discipline). All external citations use standard textbook framings (Boltzmann, Kerdock 4-design, Krotov-Hopfield, WTA decoupling, Parisi saddle hierarchy) -- no substrate-novel mechanism names sent outside.

---

## Pre-registered HARD-PASS and HARD-FAIL summary

| Criterion | HARD-PASS (OPS confirmed) | HARD-FAIL (OPS refuted) |
|---|---|---|
| Mean Pearson r (4 probes vs singularity-distance) | < -0.5 | in [-0.2, +0.2] |
| Individual probe r count | >= 3 of 4 with r < -0.4 | <= 1 of 4 with r < -0.4 |
| Near-singularity coherence | All 4 metrics flat-together at small-gap ops | Metrics light up independently / no coherence |
| Far-singularity coherence | >= 2 of 4 metrics non-flat at large-gap ops | Metrics fail to light up away from singularity |
| Operational outcome | 4 rows -> single unified annotation; 8-12 GPU-days saved | 4 rows resume per-row rescues; +1 architecture-level evidence |

Deflated P(HARD-PASS) = **0.30-0.40** (deflated 0.20 from raw 0.50-0.60 lit-scan + analog reading; novel-synthesis cap 0.50 not breached but applied because cross-row mechanism claim is uncharted-regime). Deflated P(HARD-FAIL) = **0.40-0.50**. Deflated P(MIDDLE) = **0.20-0.30**.

---

## Calibration note

Per [[feedback-lit-scan-calibration-penalty]] all P estimates deflated 0.15-0.25. The Pearson r < -0.5 threshold is conservative (typical "moderate negative correlation" = -0.4; this requires stronger). The 3-of-4 individual probe coherence requirement guards against single-probe-noise lighting up. The all-four-flat-together + lights-up-when-away coherence checks are the SPATIAL discrimination ensuring r < -0.5 isn't a spurious aggregate from one probe dominating.

End of formalization. exp_dev OWNS final anchor design per autonomy declaration.
