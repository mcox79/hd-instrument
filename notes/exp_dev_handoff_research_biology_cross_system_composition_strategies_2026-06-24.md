# exp_dev hand-off — research: biology cross-system composition strategies

**Filed-by:** Research (Opus 4.7-1M)
**Date:** 2026-06-24
**Trigger:** companion to `notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md`
**Source negatives (composition collapse family):**
- `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (A1 HARD_FAIL_SUB_ADDITIVE)
- `data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json` (K=2 x cf-RPE HARD_FAIL)
- `data/exp_substrate_continual_learning_spectrum_v1/metrics.json` (CL spectrum HARD_FAIL)
**Pause state:** check `data/orchestrator_paused.flag` before dispatch; if paused, hold

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off contains anchor candidates + context pointers + autonomy declaration. exp_dev OWNS cell design (smoke gate, pre-reg envelope, ship-via-queue_add).

**Strategic framing:** the brain is ONE biology composition oracle. The seven non-brain systems (genetic regulation, signal transduction, immune, ant colony, cellular compartments, Hox patterning, bacterial regulons) give SIX MORE oracles. They converge on near-decomposability + weak coupling. Substrate's same-W stacking violates this universal principle. The hand-off below is rank-ordered by cross-domain biology evidence x substrate-implementation cost.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (PRIMARY) — `exp_substrate_compose_biology_inspired_v1`

**Anchor pointer:** 3-arm cross-domain biology composition test: scaffold-kinetic insulation (MAPK analog) + Hox-combinatorial orthogonal 3-axis (developmental analog) + stigmergic shared-cache (ant-colony analog)
**Substrate-product reading:** if any HARD_PASS, validates the meta-principle that biology-canonical composition (near-decomposability + weak coupling) transfers to substrate; opens the entire non-brain biology architecture toolbox
**Tier hint:** MM (multi-arm discriminator); chain-grade-eligible if any arm BPC <= 6.95 (improves cf-RPE-only by >=0.15 bits)
**Why-now:** zero new primitives; only NEW LAYER is coupling/routing structure; 7 independent biological systems converge on this principle; substrate's failure mode is the architectural OPPOSITE of every biology composition strategy
**Runtime estimate:** ~60min CPU local (3 arms + baseline at N_DIM=8192, N_TRAIN=100k, 3 seeds)

**Pre-reg HARD bands (per research note L3):**
- HARD_PASS: at least ONE arm BPC <= 7.05 AND best arm BPC <= 6.90 AND cross-mechanism update correlation <= 0.5
- HARD_FAIL: ALL three arms BPC >= 7.30 OR all arms cross-mechanism correlation >= 0.9 (insulation failed)
- MIDDLE_BAND: best arm BPC in [7.00, 7.20]

**Instrumentation (suggested):**
- per-arm BPC at best (T, lambda) per the extended T-grid [0.02-10.0]
- per-mechanism activation rate (fraction of steps each mechanism fires)
- cross-mechanism update correlation (||delta_cfRPE x delta_STDP|| / (||delta_cfRPE|| ||delta_STDP||))
- per-arm logit entropy + freq-stratified top-1 (for Hox-combinatorial axis attribution)

### ANCHOR 2 (CONDITIONAL on Anchor 1 HARD_PASS on Hox-combinatorial arm) — `exp_substrate_hox_combinatorial_axis_attribution_v1`

**Anchor pointer:** if Hox-combinatorial arm of Anchor 1 HARD_PASSes, this cell ablates each of 3 axes (frequency / temporal / rarity) to confirm each axis contributes independent non-zero lift
**Substrate-product reading:** validates orthogonal-axis combinatorial principle from Hox literature; if axis ablation shows differential contribution, the principle transfers; if only one axis dominates, it's actually single-axis dressed up
**Tier hint:** discriminator; chain-grade-eligible if all 3 axis ablations show non-zero delta-BPC when removed
**Why-now:** gated on Anchor 1 Hox-arm HARD_PASS; cheap follow-up to confirm the BIOLOGY-PRINCIPLE-TRANSFER claim
**Runtime estimate:** ~45min CPU local

**Pre-reg HARD bands:**
- HARD_PASS: each of 3 axis ablations causes BPC degradation >=0.05 bits (each axis contributes)
- HARD_FAIL: only one axis ablation matters (collapse to single-axis); HoxA-style multi-axis claim refuted
- MIDDLE_BAND: 2-of-3 axes contribute non-zero; partial Hox-principle transfer

### ANCHOR 3 (CONDITIONAL on Anchor 1 HARD_PASS on scaffold-kinetic arm) — `exp_substrate_kinetic_insulation_timescale_sweep_v1`

**Anchor pointer:** if scaffold-kinetic arm HARD_PASSes, this cell sweeps the timescale gate widths (cf-RPE window {1, 2, 5}; STDP window {50, 100, 200}; Hebbian window {500, 1000, 2000}) to find optimal kinetic insulation
**Substrate-product reading:** validates kinetic-insulation principle; identifies whether substrate has analog of MAPK timescale separation
**Tier hint:** tuning sweep; chain-grade-eligible if optimal timescale config beats cf-RPE-only by >=0.20 BPC
**Why-now:** gated on Anchor 1 scaffold-arm HARD_PASS; identifies optimal multiplexing schedule
**Runtime estimate:** ~90min CPU local (27 timescale combinations)

**Pre-reg HARD bands:**
- HARD_PASS: optimal timescale BPC <= 6.80 (substantial lift over cf-RPE-only)
- HARD_FAIL: timescale variation has <0.05 BPC effect (kinetic insulation isn't load-bearing in detail)
- MIDDLE_BAND: optimal in [6.85, 7.00]

### ANCHOR 4 (DEFERRED — only if Anchor 1 HARD_FAILS on all 3 arms) — `exp_substrate_cooperative_and_gate_compose_v1`

**Anchor pointer:** L4 Strategy 1 from research note: cooperative-AND-gating from genetic-regulatory analog; mechanisms activate updates ONLY when multiple input conditions co-occur
**Substrate-product reading:** if Anchor 1's three arms all fail, pivot to the GENETIC-REGULATION composition principle (specificity via required co-occurrence) rather than the brain/cellular/development principles
**Tier hint:** novel-synthesis P_capped=0.50; chain-grade-eligible if BPC <= 6.95
**Why-now:** ONLY if Anchor 1 fails on all three; signals deeper architectural rewrite needed
**Runtime estimate:** ~45min CPU local

**Pre-reg HARD bands:**
- HARD_PASS: BPC <= 6.95 AND update-density (fraction of steps with non-trivial delta-W) shows sparsification >50% vs baseline
- HARD_FAIL: BPC >= 7.20 OR update-density unchanged
- MIDDLE_BAND: BPC in [6.95, 7.15]

### ANCHOR 5 (DEFERRED — only if Anchor 1+4 BOTH fail) — `exp_substrate_germinal_center_select_v1`

**Anchor pointer:** L4 Strategy 2 from research note: germinal-center mutate-and-select (immune-system analog); two weight banks alternating between selection and mutation
**Substrate-product reading:** if every additive-composition approach fails, pivot to evolutionary search architecture; built-in selection without backprop
**Tier hint:** novel-synthesis P_capped=0.40; chain-grade-eligible if mutation-select bank exceeds baseline by >=0.10 BPC
**Why-now:** ONLY if Anchors 1+4 BOTH HARD_FAIL; signals composition cannot be additive at all; needs selection
**Runtime estimate:** ~2-3hr CPU local OR remote_cpu_queue (alternation cycles + held-out window evaluation)

**Pre-reg HARD bands:**
- HARD_PASS: best mutation-select run BPC <= 6.95 AND selection accepts >5% of mutations (not pure random walk)
- HARD_FAIL: BPC >= 7.20 OR selection rejects all mutations (selection signal too weak)

---

## Context pointers (file paths only; no summaries)

**Empirical (load-bearing):**
- `d:/AI/hd-instrument/data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (composition-collapse source negative)
- `d:/AI/hd-instrument/data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json` (K=2 + cf-RPE secondary negative)
- `d:/AI/hd-instrument/data/exp_substrate_continual_learning_spectrum_v1/metrics.json` (CL spectrum negative; same gradient-conflict mechanism)

**Research thread (this drill):**
- `d:/AI/hd-instrument/notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md` (THIS drill — biology cross-system survey + 3 substrate mappings)
- `d:/AI/hd-instrument/notes/research_composition_collapse_critical_drill_2026-06-24.md` (composition-collapse mechanism diagnosis)
- `d:/AI/hd-instrument/notes/research_untested_composition_architectures_2x_drill_2026-06-24.md` (brain-canonical architectures: theta-phase / freq-routed / orthog-subspace)
- `d:/AI/hd-instrument/notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md` (brain-mechanism inventory drill)

**Substrate primitives (already validated):**
- `d:/AI/hd-instrument/hdlab/` (cf-RPE, STDP, sparse-bipolar, Hebbian, char-trigram encoder primitives)
- `d:/AI/hd-instrument/data/substrate_index/` (Store atoms; check for prior K-bank or orthogonal-subspace atoms)

**Discipline references:**
- [[feedback-no-experiment-design-in-prompts]]
- [[feedback-spawn-budget-fix14]] (max 3 in flight)
- [[feedback-smoke-VET-nuance]] (smoke gate before ship)
- [[feedback-empowered-to-experiment-where-lit-says-dismissed]] (substrate-novel variants of "dismissed" mechanisms are FAIR GAME)

---

## Contract section

**Inputs from this hand-off:**
- 5 rank-ordered anchor candidates with pre-reg HARD bands
- Strategic ordering: primary (Anchor 1) then conditional Anchors 2-5 based on primary outcome
- Substrate-product reading per anchor

**exp_dev OWNS:**
- Cell design choices (which primitives, exact arm config, parameter sweep ranges)
- Smoke-VET gate before remote dispatch (per Fix #17 strict measurement)
- Pre-dispatch verify-the-referent (per Fix #26: check `tools/predispatch_check.py` for prior evidence)
- Ship via `tools/queue_add.sh local_cpu_queue` (local for all anchors above; no GPU needed)
- Post-ship remote-verify
- Self-test per formula-selftests

**Research does NOT own:**
- Cell implementation details
- Smoke decisions
- Queue dispatch choices

---

## Autonomy declaration

Research has delivered the FINDINGS (cross-system biology survey + 3 substrate-native composition mappings + pre-reg HARD bands). exp_dev is empowered to:
- Modify HARD-band thresholds if smoke reveals different absolute BPC scales (preserve relative deltas)
- Re-rank anchors if smoke surfaces unexpected primary blockers
- Skip Anchor 1 if pre-dispatch check reveals it's already been tested (Fix #26)
- Dispatch Anchors 2+3 in parallel after Anchor 1 lands (both conditional on different arms, so non-overlapping)
- Defer Anchors 4+5 to next cycle if pipeline is full

exp_dev should NOT:
- Add new arms beyond the 3 specified in Anchor 1 (smoke-VET discipline)
- Use Hebbian or STDP variants not in the substrate's existing primitives library
- Change the per-mechanism semantic axis assignment in Hox-combinatorial without re-running research drill (frequency=cf-RPE, temporal=STDP, rarity=sparse-bipolar is the load-bearing semantic mapping)

---

**End of hand-off.**
