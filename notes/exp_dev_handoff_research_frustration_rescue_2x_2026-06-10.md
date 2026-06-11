# exp_dev hand-off -- research: frustration-rescue-2x

**Filed-by:** research sub-agent, 2026-06-10
**Trigger:** 2x operational drill on Frustration_BG_analog_diagnostic MIDDLE_BAND verdict (irreducible=0.960, BG-analog=0.040). BG lateral inhibition is not the rescue path. Drill identified four substrate-native mechanisms that can address the 96% irreducible component.
**Research note path:** d:/AI/hd-instrument/notes/research_drill_frustration_rescue_2x_2026-06-10.md

**Pause state:** Check data/orchestrator_paused.flag before dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off WHAT and WHY.
exp_dev owns all anchor names, sweep grids, threshold formulas, queue routing, and timing.

---

## Anchor candidates (rank-ordered)

### Rank 1: TEMPORAL_RESOLUTION_REGISTER -- highest P_deflated, lowest implementation cost

**Anchor pointer:** Add a partial-satisfaction register (one scalar per drive, updated after each retrieval) to the drive-arbitration path. When two drives produce co-equal cosine scores, the register provides a tie-breaking signal: the drive with lower accumulated satisfaction wins. This is a deferred-resolution mechanism, not a competition sharpener.

**Substrate-product reading:** Biological analog is neural landscape diffusion (PMC10651489): need-states diffuse noisily across a time-shifting energy landscape; co-equal drives are resolved by drift as one drive accumulates partial satisfaction, not by inhibition. The substrate-native implementation is a small modification to the existing arbitration step. The register scalar is alpha * (1 - satisfied_fraction). No new training required.

**P_deflated:** 0.50
**HP:** More than 60% of previously irreducible conflict cases resolved within timestep budget N (N pre-registered before test run)
**MID:** 30-60% rescue rate
**HF:** No improvement over BG-alone baseline at 2x timestep budget; rescue rate below 15%
**Tier hint:** CPU-only. No GPU. No LLM. Runs on existing substrate without new training. Under 2 hours.
**Why now:** The MIDDLE_BAND verdict established that the 96% irreducible share cannot be addressed by sharpening lateral inhibition further. This is the cheapest substrate-native path with the highest biological precedent. It requires only adding a scalar accumulator and a one-line modification to the arbitration comparison.

---

### Rank 2: META_COGNITIVE_DECOMPOSITION -- medium cost, highest principled coverage

**Anchor pointer:** When the conflict-detection signal exceeds a threshold theta for T consecutive steps, trigger a decomposition pass: unpack each conflicted drive bundle into 2-3 sub-drives using the substrate's unbinding operation. Test pairwise orthogonality between sub-drives from bundle A and sub-drives from bundle B. Route any orthogonal pair to the BG selection step. Repeat up to depth 3.

**Substrate-product reading:** The substrate's compositional operations (bind/unbind/superpose) directly implement this: a bundled drive representation can be unbound into components, and orthogonality between two components can be tested via cosine threshold. This is not a novel mechanism -- it uses existing substrate math in a new control loop. The biological analog is prefrontal cortex triggering problem decomposition when the ACC reports persistent conflict (Yeung/Summerfield 2012).

**P_deflated:** 0.45
**HP:** Decomposition reduces conflict signal below theta in more than 70% of previously irreducible cases; depth 1-2 sufficient in more than 60% of successes
**MID:** 40-70% rescue rate; depth 1-3 sufficient
**HF:** More than 50% of cases require depth greater than 3 with no orthogonal sub-drive found (indicates the conflict is not decomposable in the current representation space)
**Tier hint:** CPU-eligible for small drive sets. GPU-advisable for large bundled representations.
**Why now:** This is the most principled mechanism from classical multi-drive arbitration theory. The RSB framing (Section 3.1 of the research note) predicts that the 96% irreducible share reflects conflicts that are structural at the bundle level but may be separable at the component level.

---

### Rank 3: STOCHASTIC_TUNNELING_NOISE_INJECTION -- low-medium cost, validated in materials science

**Anchor pointer:** When the conflict-detection signal remains above threshold for T steps and temporal deferral has not converged, inject calibrated noise into the arbitration state vector. Apply a guided acceptance criterion: accept the new state if it has a lower conflict signal; reject otherwise (no unconditional random walk). Calibrate noise level to estimated frustration-basin height (not global random exploration).

**Substrate-product reading:** The mechanism is stochastic tunneling (Wenzel/Hamacher 1999): in a frustrated state space, the acceptance criterion biases noise-driven moves toward lower-conflict basins, allowing the system to escape the current basin without destroying prior solutions. The substrate analog: the arbitration state vector is the spin configuration; the conflict signal is the energy function; the noise injection is the temperature perturbation; the acceptance criterion is the Metropolis criterion with conflict as the energy.

**P_deflated:** 0.40
**HP:** Noise injection reduces irreducible fraction by more than 40 percentage points (from 0.96 to below 0.56) at calibrated noise level; BG-solvable fraction not degraded by more than 5pp
**MID:** 20-40pp reduction in irreducible fraction; BG-solvable fraction degraded by less than 15pp
**HF:** Noise injection degrades BG-solvable (4%) fraction by more than 20pp (noise is too large and destroys existing solutions); OR irreducible fraction unchanged after 3x noise-level sweeps
**Tier hint:** CPU-eligible. Implementation cost low-medium (noise generation exists; acceptance criterion is a small modification).
**Why now:** This is the closest analog to how materials science resolves structurally frustrated systems. It provides a mathematically grounded fallback when temporal deferral and decomposition both fail. The HARD-FAIL guard (do not degrade BG-solvable fraction) is critical for safe deployment.

---

### Rank 4: CULTURAL_CONVENTION_LOOKUP -- lowest cost, limited coverage

**Anchor pointer:** Store a conflict-resolution priority table in the substrate's associative memory: key = binding of drive_A_hash with drive_B_hash, value = priority direction (A wins or B wins). At conflict time, compute the binding key and perform associative lookup. If the pair is in the table, enforce the pre-registered priority. If not, fall through to Rank 1.

**Substrate-product reading:** This is a constitutional AI analog: priority ordering is pre-established externally and bypasses competitive dynamics entirely. The substrate's associative memory implements the lookup natively -- it is key-value retrieval, not a new operation. Coverage is limited to enumerable conflict pairs, but for known frequent conflicts this is the lowest-latency resolution mechanism.

**P_deflated:** 0.38
**HP:** Lookup table covers more than 80% of observed co-equal conflict pairs; resolution latency under 1ms per lookup
**MID:** 50-80% coverage of observed pairs
**HF:** Circular priority dependency (A>B>C>A) found in more than 20% of conflict triple cases (indicates the priority table is inconsistent and cannot be deployed)
**Tier hint:** CPU-only. Near-zero cost once table is populated. Table population is the main design task.
**Why now:** This is the cheapest fallback for enumerable conflict pairs. It complements Rank 1-3 and handles the cases where temporal deferral is too slow (latency-sensitive applications).

---

## Context pointers

- Research note (full analysis, all P estimates, citations): d:/AI/hd-instrument/notes/research_drill_frustration_rescue_2x_2026-06-10.md
- MIDDLE_BAND verdict source: Frustration_BG_analog_diagnostic -- data/exp_Frustration_BG_analog_diagnostic/metrics.json (or equivalent per exp_ prefix convention)
- Substrate cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Post-compaction brief (most recent): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md

---

## Contract

This file hands off WHAT (mechanism descriptions, P estimates, HP/MID/HF thresholds) and WHY (biological and materials science precedents, substrate-native implementation paths). It does NOT specify:
- Anchor names (exp_dev assigns these)
- Sweep grids or hyperparameter ranges (exp_dev owns these)
- Queue routing or timing (exp_dev owns these)
- Cell structure or self-test formulas (exp_dev owns these)

## Autonomy declaration

exp_dev has full autonomy to:
- Select which rank(s) to dispatch first based on current queue state
- Combine multiple mechanisms into a single cell if queue efficiency warrants it
- Demote any rank if a prior verdict has already tested equivalent functionality
- Add or modify the acceptance-criterion parameters for Rank 3 based on current substrate state
