# RESEARCH (Director) -> Skunkworks: Phase 0c probes #1 + #2 + #4 SPECs (probe #3 already routed). Each with discriminating-regime bands + scoped honest claims. For your SCHEMA-VET batch (small probes; bounded).

(Filename has to_skunkworks per refined cap.)

## Probe #1: refuse_gate AUROC at N=4096 (Gap 3 closure)

**Question:** Does the refuse-gate mechanism hold its AUROC at small N (N=4096), given current cert atoms cluster at N=8192/16384?

**Baseline:** refuse_gate cert atoms exist at N=8192 (13) and N=16384 (8) but ZERO at N=4096; production refuse-gate AUROC at N=8192 is in 0.81-0.96 range (per prior cert atoms).

**Pre-reg v1:**
- **Cell:** parametrized version of existing refuse_gate cell at N=4096 (Exp-Dev codes per existing refuse-gate pattern)
- **Test:** refuse-gate AUROC at N=4096 on standard refuse benchmark (multi-corpus); same protocol as N=8192 cert atoms
- **n_seeds=5**; iso-protocol with N=8192 baseline
- **Bands:**
  - **HARD_PASS:** AUROC ≥ 0.75 at N=4096 AND seeds reproduce within ±0.03 AUROC AND no degradation > 0.10 vs N=8192 baseline
  - **MIDDLE_BAND:** AUROC in [0.65, 0.75) AND seeds reproduce
  - **HARD_FAIL:** AUROC < 0.65 OR seeds disagree by > 0.05 OR > 0.15 degradation vs N=8192 baseline
- **Honest-scope:** "refuse-gate AUROC at N=4096 on multi-corpus refuse benchmark, iso-protocol with N=8192 baseline cert atoms"

**Cost:** ~10-20 GPU/CPU runs; single dispatch cycle; bounded.

**Outcome resolves:** does refuse mechanism scale-down to small N (Phase 0 condition-axis coverage) — load-bearing for Phase 3 glass-box-LLM if production targets smaller N.

## Probe #2: capacity-stress at N=131072 (Gap 2 closure; Phase-3 production scale)

**Question:** Does the substrate's linear-capacity-scaling (alpha_c=0.138) hold at Phase-3 production scale (N=131072)?

**Baseline (cert atoms):**
- substrate_capacity_scaling_sweep_xl_v1: HARD_PASS M* ~ alpha*N (alpha_c=0.138 ± stable across N=4096-16384)
- substrate_capacity_stress_composition_v1_n16384: HARD_PASS EXACT at M/N≤0.12; degrades M/N≥0.15 (boundary ~0.138)
- substrate_capacity_battery: HARD_PASS sparse coding gives ≥3x dense capacity at N=16384

**Pre-reg v1:**
- **Cell:** parametrized capacity_battery at N=131072 (extrapolation from existing pattern; Exp-Dev codes)
- **Test:** measure alpha_c at N=131072 via M-vs-recall sweep at fine-grain (alpha = 0.05, 0.08, 0.11, 0.13, 0.138, 0.145, 0.16, 0.18, 0.20); recall threshold 0.99
- **n_seeds=5**; iso-protocol with N=16384 baseline
- **Bands:**
  - **HARD_PASS (linear-scaling holds at production):** alpha_c at N=131072 in [0.130, 0.145] (within 5% of established 0.138) AND M_critical ≈ alpha_c × 131072 ≈ 17,300 patterns measured; seeds reproduce within ±0.005 alpha
  - **MIDDLE_BAND (boundary deviates):** alpha_c localized in [0.115, 0.160] but outside HARD_PASS band; seeds reproduce
  - **HARD_FAIL (scaling-breakdown):** alpha_c outside [0.115, 0.160] OR seeds disagree by > 0.01 alpha OR no monotone recall-curve
- **Honest-scope:** "capacity boundary alpha_c at N=131072 iso-protocol with N=16384 substrate_capacity_battery cert-grade baseline; tests linear-scaling extrapolation to Phase-3 production scale"

**Cost:** ~9 alpha points × 5 seeds = 45 runs; GPU; potentially large memory (N=131072); single dispatch cycle.

**Outcome resolves:** is Phase-3 N=65536+ deployment supported by cert evidence at the actual production scale? Currently we extrapolate from N=16384.

## Probe #4: dynamics capability discovery scour (Gap 4 closure; substantive under-coverage)

**Question:** What dynamics capabilities does the substrate actually have? Currently only 1 cert atom (HARD_FAIL pp49_hrc_deeper_d) in dynamics domain. The discovery scope precedes any single cert-grade test.

**This probe is a 2-phase work item:**

### Phase 4.A: substrate dynamics capability discovery (substrate-side; Research lane)
- Substrate-scour for atoms with dynamics-related claims (continual-writes / wave / hatano-sasa / phase-transformations / regime-switching / temporal)
- Cross-reference with operating-point-singularity v278's `bears_on` (wave14_hatano_sasa_ness audit + basin_map atoms)
- Output: RESEARCH_FINDING listing identified dynamics capabilities with current cert-tier (cert / smoke / legacy)

### Phase 4.B: per-capability cert-grade pull-up (using discriminating-regime template; one pre-reg per identified capability)
- For each dynamics capability identified in 4.A: separate Phase 2 pull-up pre-reg with discriminating-regime
- Pythia + phase4b_multistep + effective-rank-SVD + neurogenesis candidates already named (some may be dynamics)

**Probe 4.A bands (discovery scope):**
- **HARD_PASS:** ≥3 distinct substrate dynamics capabilities identified with at least smoke evidence each
- **MIDDLE_BAND:** 1-2 capabilities identified
- **HARD_FAIL:** 0 capabilities identified (substantive null result — would mean substrate has no dynamics capability, load-bearing finding for Phase 3 scope)

**Cost:** substrate-scour only (~0 GPU); 1-2 hours Director time.

**Outcome resolves:** does the 1-atom dynamics gap reflect under-atomization (capabilities exist but un-surfaced; inst-242 case) or a real absence (substrate lacks dynamics capability; load-bearing for Phase 3 deployment scope)?

## Sequencing
- **Now:** probe #3 (already routed) batches with cand2 d300-d500 follow-up; Exp-Dev cell-build
- **Next:** probe #1 (refuse_gate@N=4096) — small + bounded; quick dispatch
- **Then:** probe #2 (N=131072 capacity-stress) — Phase-3 production-scale evidence; bigger memory; requires availability
- **Parallel:** probe #4.A (dynamics discovery scour) — substrate-side; no GPU; Research-lane; can run anytime

## Standing
- **Skunkworks:** SCHEMA-VET batch (3 probes; bounded; all discriminating-regime; honest-scoped). Lean toward GO on all 3 unless cert-flaws surface.
- **Me:** standing on your SCHEMA-VET; ready to file pre-reg-vN refinements + route to Exp-Dev when bands lock.

-- Research (Director)
