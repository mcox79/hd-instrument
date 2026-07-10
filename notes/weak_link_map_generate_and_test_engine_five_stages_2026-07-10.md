# Weak-Link Map — Generate-and-Test Inference Engine, 5 Stages (SCOUR, 2026-07-10)

**Purpose:** off-disk mining of ALL prior "make relational real" failures, mapped onto the 5 stages of the generate-and-test engine we are building, so the PREDICTED weak links are known in advance and instrumented per stage. Read-only scour; every number below traces to a cert_ledger row (`data/substrate_index/meta/cert_ledger.jsonl`) or a cell metrics.json. Companion: `notes/relational_capability_track_record_scour_2026-07-10.md` (the full relational tier map). Engine design: `notes/next_arc_density_plus_generate_and_test_unified_design_2026-07-10.md`.

**The single most load-bearing prior:** `gt_induction_fb15k237_dense_v1` (commit 7529b6c02, 3-seed FULL, 2026-07-10) — this IS the generate-and-test engine (AMIE L1/L2 path-rule PROPOSE + support-confidence VERIFY) run on a dense KG. Its landed verdict is the clearest per-stage evidence we have, so it anchors multiple stages below.

---

## STAGE 1 — PROPOSE / candidate generation

**Failure mode A — generator REACH ceiling caps the whole engine.** On dense FB15k-237 the L1/L2 path-rule generator's REACH ceiling is **0.514** — the fraction of held-out edges for which the true candidate is proposed AT ALL. Even a PERFECT verifier downstream cannot exceed this. (gt_induction_fb15k237_dense_v1: reach ceiling 0.514, barely above frequency prior 0.487, margin 0.027.)

**Failure mode B — substrate-native (oracle-free) proposal by composing primitives = no signal at depth.** Proposing candidates by chaining CG primitives without an oracle collapses: `partition_oracle_substrate_derived_hint` route acc @ chance; `partition_oracle_brain_composition_hint` arm_c 0.01; `brain_faithful_4_primitive_multihop_chain_composition` HARD_FAIL at depth 15 (2x drill). Root cause (META_RULE_AP/AQ): signal-shape / operating-regime mismatch between a primitive's validated regime and the chained downstream regime.

**Failure mode C — density gates proposal.** On a fair degree-downsampled sparse graph (avgdeg 3.0, same nodes/rels/code) the generator's h@10 = **0.000 (all 3 seeds)** — below the density floor there is no true candidate to propose. Our canonical graphs are ALL sub-floor: ConceptNet 2.68, science 2.91, bio-trio ~3.3 vs FB15k-237's ~37.

**Predicted severity: MEDIUM-HIGH.** Hard cap on end-to-end recall (0.514 dense; ~0 sparse). Not the #1 wall because it is measurable and improvable (richer rule templates, more knowledge), but it silently bounds everything downstream.

**Diagnostic that localizes it:** measure the generator REACH ceiling (is the true candidate in the proposed SET?) SEPARATELY from verify/rank, on EVERY run. Decouples "never proposed" from "proposed but mis-ranked". gt_induction shows this catches the 0.514 cap before any verifier tuning is wasted.

---

## STAGE 2 — COMPOSE (bind/unbind VSA operator)

**This stage is the PROVEN floor — but has two named hazards.**

- The bind/unbind PRIMITIVE is CG: parietal unbind 0.995; analogy completion r1 0.8613 (`MATH_VSA_CELL1`); cross-modal bind to 2/3/4/5 modalities CG. The operator itself preserves signal.
- **Hazard A — cleanup-AFTER-bind destroys the composite.** `pfc_goal_conditioned_gate_v2`: BIND_CLEAN **0.000 @depth6** — cleanup snaps to a single codebook entry and loses the composite. Never clean up the whole composite mid-chain.
- **Hazard B — crosstalk at load, not the op.** Capacity is set by N and load α, NOT the bind op: `substrate_binding_op_x_capacity_v1` K-cliff 750 identical across all ops; involutive-HRR systematic generalization = null **0.0067 (chance)**. Choosing a fancier bind op buys nothing.
- **The mitigation is already CG:** regenerative hard-snap cleanup BEATS analog soft-carry above Hebbian crosstalk M/N>1 (`digital_repeater_regenerative_hard_snap_cleanup`); per-step fidelity ~0.985 stable across a 4x depth range; d*(recall=0.50) ≈ 50-55 hops — **but only WITH partition-oracle routing.**

**Predicted severity: LOW (for the op) / MEDIUM (for cleanup-at-load).** Compose is safe IF: per-step regenerative hard-snap cleanup, load kept below the crosstalk threshold, and no full-composite cleanup mid-chain.

**Diagnostic:** BIND_CLEAN recovery probe at depth (recover the composite AFTER cleanup); track crosstalk load M/N and per-step argmax fidelity; regenerative-vs-soft-carry A/B at the operating depth.

---

## STAGE 3 — VERIFY (separate true from false candidates)

**Failure mode A — the verifier IS load-bearing and does separate (good news), proven by ablation.** Random/broken verifier halves ranking on dense FB15k-237: MRR **0.212 -> 0.102**, h@1 **0.171 -> 0.072**. So a real support-confidence verifier is genuinely doing work — this is the piece every passive/smoothing method lacked.

**Failure mode B — thin, seed-fragile separating margin.** The broken-verifier control passes its gate THIN at **0.481 of 0.50** (3.8% margin). Grounding verifiers clear their bars by razor margins: concreteness gap A 0.0589 clears 0.05 by **0.0089** (cv 0.69, only 2/5 seeds clear); fusion-beats-single knife-edge **+0.0206 clears 0.02 by 0.0006**, seed23 goes **-0.0199**. A verifier separating at these margins flips verdict on one seed.

**Failure mode C — degenerate controls that can't carry a negative.** `grounding_additive_geometric_inductive_v1`: the DISTMULT specificity control landed **0.012, BELOW the random floor 0.014** — a control that never cleared its own expected floor cannot prove additive-specificity. (Now a locked META rule: a control must clear its OWN floor before its failure is evidence.) Cross-cutting hazard: telemetry-INSENSITIVE discriminators auto-pass and fake robustness.

**Predicted severity: MEDIUM.** The verifier works in principle but its margin is thin and confound-prone; false-pass risk is real.

**Diagnostic:** (1) broken/random-verifier ablation must HALVE reach (load-bearing check); (2) every control must clear its OWN expected floor before its failure counts; (3) telemetry-sensitivity check (perturb the data, confirm the metric moves) before tiering.

---

## STAGE 4 — RANK / AGGREGATE (scoring, noisy-OR)  ← **THE #1 PREDICTED WEAK LINK**

**Failure mode A — the true candidate LOSES to the frequency/degree prior even when proposed AND verified.** This is the through-line of the entire arc. On dense FB15k-237 the full generate-and-test loop LOSES to the per-relation FREQUENCY prior on ALL THREE metrics: h@1 **0.171 vs POP_RELFREQ 0.262**, h@10 **0.288 vs 0.487**, MRR **0.212 vs 0.338**. And the generator ceiling 0.514 barely clears frequency 0.487 (margin 0.027) — even PERFECT verification beats frequency by only 2.7 pts h@10. The engine's fate is decided HERE.

**Failure mode B — degree confound silently inflates AND reverses results (recurs across 4+ cells).**
- `grounding_additive_geometric_degree_control_v1` (HARD_FAIL, d67bf19d7): TransE-over-discrete advantage is degree-CONCENTRATED and REVERSES on the tail — HIGH **+0.264**, MID **+0.085**, LOW **-0.040** (3/3 seeds negative in LOW). Degree-invariant lever hypothesis CLOSED.
- `graph_inductive_ceiling_v1` (MM): headline **+0.062 collapses to -0.132** under degree control (PA 0.755 sparse -> 0.622 dense); classic CN/AA/RA/JC predictors LOSE to codes; smoke->FULL "inversion" was a PA-degree artifact.
- `grounding_learned_sr_heldout_reasoning_v1` (HARD_FAIL, 5ab793d1): held-out reach@2 **0.115 vs random-code 0.104, Δ0.011 < margin 0.05**, codes_necessary=False — ranking is no better than random on held-out (memorized search, not reasoning).

**Failure mode C — multi-channel aggregation (noisy-OR / fusion) is knife-edge.** `grounding_multiview_fusion_v2` (6-attribute reliability-weighted late fusion): fusion-beats-single **+0.0206**, cv **0.265** (far above 0.15 promotion bar), NEGATIVE on seed23, only **3/6 channels** carry real weight (visual/haptic/interoceptive; aoa 0.018, olfactory 0.007 marginal). Aggregating more channels did NOT robustly help.

**Predicted severity: HIGHEST — this is the most-likely stage to break.** The construction-proof already showed a clean propose+verify loop on a DENSE graph loses to frequency; every passive-code arc died the same degree/frequency death. Whatever the engine proposes and verifies, it must OUT-RANK a frequency prior on the low-degree tail — the exact place all prior evidence says it fails.

**Diagnostic:** MANDATORY degree/frequency-STRATIFIED scoring (LOW/MID/HIGH strata) + BOTH a degree-only AND a per-relation-frequency-only baseline arm the engine must BEAT (locked META rule: beating only degree or a broken verifier is construction-proof, not capability). Report per-stratum survival margin, not just aggregate.

---

## STAGE 5 — KNOWLEDGE / density floor

**Failure mode A — below the density floor, the signal is not present for ANY method.** DENSITY is NECESSARY (causally isolated, fair downsample): dense h@10 **0.288 vs sparse avgdeg-3.0 h@10 0.000** (all 3 seeds, same vocab/code). Our canonical graphs are all 10-14x BELOW the inference floor (ConceptNet 2.68, science 2.91, bio ~3.3 vs ~37). Every prior relational-inference negative was measured where held-out edges were NOT latently inferable.

**Failure mode B — density ALONE is not the lever (necessary, not sufficient).** `grounding_density_payoff_relational_reasoning_v1` (HARD_FAIL): rel_gain sparse 0.084 -> dense 0.022, rise **-0.062** (branchiness confound). Richness flat (0.673, slope 0.002); structure-aware encoder ΔM5 **-0.0175**. Graph inductive predictability CEILING is AUC **0.76** (0.85 FALSE) — signal exists but capped; knowledge is thin.

**Predicted severity: HIGH as a GATE.** If the operating graph is sub-floor the engine is structurally ~0 (Stage-1 mode C). But clearing the floor is necessary-not-sufficient: even ABOVE the floor the engine loses to frequency (Stage 4). Density opens the door; it does not walk through it.

**Diagnostic:** compute the info-ceiling / latent-determinability at each density BEFORE iterating (achieved/ceiling discipline); avg-degree floor check vs the ~37 benchmark; report achieved/ceiling ratio so a sub-ceiling score is read as a TEST/knowledge limit, not a substrate wall.

---

## PREDICTED WEAK-LINK SEVERITY RANKING (for THIS engine)

1. **RANK / AGGREGATE (Stage 4)** — frequency/degree prior dominance. The construction-proof shows the whole loop loses to frequency on all 3 metrics even on a dense graph; the degree confound has silently inflated or reversed 4+ prior cells. **This is where the engine will break.**
2. **KNOWLEDGE / density (Stage 5)** — a hard GATE: our canonical graphs are all sub-floor (h@10 0.000 sparse). Must run on a dense testbed (FB15k-237) or the result is structurally 0 and uninterpretable.
3. **PROPOSE (Stage 1)** — generator reach ceiling 0.514 caps end-to-end recall; oracle-free primitive-composition proposal is at chance at depth.
4. **VERIFY (Stage 3)** — works and is load-bearing, but the separating margin is thin (0.481-of-0.50; 0.0006 knife-edges) and control-degeneracy-prone.
5. **COMPOSE (Stage 2)** — proven CG; safe with regenerative hard-snap cleanup, sub-threshold load, and no mid-chain full-composite cleanup.

## CROSS-CELL / CROSS-AGENT RECURRING PATTERNS (broke repeatedly, watch everywhere)

- **Degree/frequency confound — the single most recurring failure.** Inflated `graph_inductive_ceiling` +0.062->-0.132, reversed additive-geometric on the LOW tail (-0.040), and is why classic predictors "beat" codes for free (high-degree true tails beat uniform-random negatives). LOCKED META rule now requires degree-stratified + degree-only + frequency-only baselines.
- **Construction-proof ≠ capability.** gt_induction PASS exercises ZERO substrate primitives (pure AMIE hash-join) — a regime-map, not a substrate win; its follow-up bar is set to the frequency baseline it LOST to.
- **Thin-margin / single-seed-leverage passes.** 0.0089, 0.0206->0.0006, 0.481-of-0.50; dropping one seed (seed23/seed29) flips the verdict (cv 0.69, 0.265). Aggregate PASS is fragile above a hidden single-seed lift.
- **Degenerate / saturation-vacuous controls.** DISTMULT 0.012 below random floor 0.014 cannot carry a negative; must-fail controls must FIRE at scale (assert_discriminator_fires).
- **Oracle-dependence of every proven traversal.** All depth/routing CG rides on a partition-ORACLE; every learned/typed/native router collapses — `routing_geometry_family` router_SNR_sqrt_N_over_M **0.358**, typed routing HURTS **0.44 vs 0.998**, learned routers stuck at 0.66 centroid floor. Root cause: router SNR ~ sqrt(N/M) degrades under memory load M.

## THE SINGLE MOST-LIKELY WEAK LINK

**Stage 4 (RANK/AGGREGATE) losing to the frequency/degree prior.** The generate-and-test loop, run cleanly on a DENSE graph with a proven load-bearing verifier, already LOST to the per-relation frequency prior on h@1/h@10/MRR (0.171<0.262, 0.288<0.487, 0.212<0.338), and the generator ceiling (0.514) barely clears frequency (0.487). Propose, compose, and verify can all succeed and the engine still fails at ranking against frequency on the low-degree tail — the exact seam where the whole prior arc broke. The engine must be built and judged with degree/frequency-stratified scoring against BOTH a degree-only AND a frequency-only baseline from day one.
