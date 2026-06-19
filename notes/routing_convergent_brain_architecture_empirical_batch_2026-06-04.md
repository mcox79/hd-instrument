# Routing -- Convergent brain-architecture empirical batch (7 ablations + convergent build)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical batch routing (8 tests + 1 build)
**Source:** 7 brain drills landed 2026-06-04 (META 3x+ / Spectral B 3x / Multi-channel C 3x / Functional differentiation 3x / STDP 2x / Friston FEP 2x / Drosophila MB 2x / Topological 2x / REM-replay 2x)

---

## Capability question

Which architectural variable(s) are binding for substrate-as-training-mechanism at small scale (N=4096-8192 substrate, ~10k LM params)? Specifically: does a CONVERGENT BRAIN-CORRECT architecture (sparse coding + single modulator + STDP-asymmetric + FEP framework) outperform the current dense-bipolar multi-channel design?

7 brain drills landed today converge on a simpler architecture. This batch isolates each architectural variable empirically and tests the unified design.

---

## Phase 1 -- Cheap-first ablations (dispatch immediately; ~90 min CPU total)

### 1a. Drosophila MB template ablation

**Anchor:** `substrate_drosophila_mb_sparse_single_modulator_v1_n4096`

**Test:** sparse coding (f=0.05, binary {0,1} not {+1,-1}) + single dopamine-class modulator (cf-RPE only; drop other channels) at N=4096. Compare to current dense bipolar multi-channel baseline.

**Cells (2-cell ablation):**
- Cell A: dense bipolar {+1,-1} + multi-channel (current baseline reproduction)
- Cell B: sparse binary {0,1} f=0.05 + single cf-RPE modulator (Drosophila MB template)

3 seeds per cell. Same LM scaffold (~10k char-LM). Calibrated readout temp=0.2.

**Pre-reg:**
- HP: Cell B BPC < Cell A BPC by > 0.5 nats AND 3/3 seeds AND no instability
- MIDDLE: Cell B BPC < Cell A by 0.1-0.5 nats
- HF: Cell B BPC >= Cell A (sparse + single doesn't help)

**Wall:** <60s per cell. Total ~5 min CPU. **CHEAPEST DECISIVE TEST.**

**P_deflated:** 0.42

### 1b. Topological observables baseline

**Anchor:** `substrate_topological_beta0_mapper_baseline_v1_n4096`

**Test:** measure beta_0 connectivity curve + Mapper graph on substrate's stored patterns at M=500, N=1024 (and M=1000, N=1024 for scale check). Establish baseline for "topological memory inspection" capability.

**Cells:**
- Cell A: M=500, N=1024; sigma_g=0 clean
- Cell B: M=1000, N=1024; sigma_g=0 clean
- Cell C: M=500, N=1024; drift event injected (kappa_2-invariant pattern swap)

3 seeds per cell. CPU.

**Pre-reg:**
- HP: beta_0 curve KS-detects drift event in Cell C vs Cell A AND Mapper produces >=5 nodes at M=500
- MIDDLE: beta_0 detects but correlates >0.90 with kappa_2 (no new info)
- HF: beta_0 insensitive to drift OR Mapper collapses to single node

**Wall:** ~5 min CPU total. **EXPLORATORY CANDIDATE** -- not load-bearing.

**P_deflated:** 0.45 (beta_0 complementary drift); 0.10 (rich PH barcodes -- Adams-Virk constrained)

### 1c. REM-replay retrieval-energy baseline

**Anchor:** `substrate_rem_replay_retrieval_energy_baseline_v1_n8192`

**Test:** energy-guided top-K replay at N=8192 (above quantization floor per drill). Measure retrieval energy reduction over R*=10 replay cycles vs no-replay baseline.

**Cells:**
- Cell A: N=8192, no replay (baseline)
- Cell B: N=8192, top-K=20 replay over R*=10 cycles
- Cell C: N=4096, top-K=20 replay (control; below quantization floor; expected null)

5 seeds per cell. CPU.

**Pre-reg:**
- HP: Cell B retrieval energy drops by > 30% vs Cell A AND Cell C shows null (confirms N>=8192 conditional)
- MIDDLE: Cell B drops 10-30% OR Cell C also drops (refutes quantization-floor prediction)
- HF: no energy reduction in any cell

**Wall:** <60s per cell. Total ~5 min CPU.

**P_deflated:** 0.28 (>0.30 nats BPC at rung-1; this proxy via energy reduction)

---

## Phase 2 -- Isolate variables (dispatch if Phase 1a MIDDLE/HF; ~90 min CPU total)

### 2a. STDP temporal asymmetry test

**Anchor:** `substrate_stdp_bigram_test_v1_n4096`

**Test:** synthetic bigram task with V=512 Zipf vocabulary. Compare Hebbian-only vs STDP-only vs Hybrid (W_total = W_Hebbian + lambda * W_STDP). Measure BPC.

**Cells:**
- Cell A: W_Hebbian only (symmetric outer-product)
- Cell B: W_STDP only (asymmetric per drill spec)
- Cell C: W_Hybrid with lambda=0.5

3 seeds per cell.

**Pre-reg per drill:**
- HP: Cell B BPC < Cell A BPC by > 0.5 nats
- MIDDLE: Cell B BPC 0.1-0.5 nats lower
- HF: Cell B BPC >= Cell A

**Wall:** ~10-20 min CPU.

**P_deflated:** 0.32

### 2b. Friston FEP vs BCM ablation

**Anchor:** `substrate_friston_fep_vs_bcm_v1_n512`

**Test:** N=512, M=64, K=1000 steps. FEP-class update (with precision matrix Pi + epsilon buffer + rank-1 adapt per Spisak-Friston 2025) vs BCM baseline. Measure BPC + off-diagonal overlap O_ab.

**Cells:**
- Cell A: BCM three-factor baseline
- Cell B: FEP-class with precision Pi + epsilon buffer

3 seeds per cell.

**Pre-reg:**
- HP: Cell B BPC < Cell A BPC by > 0.3 nats AND O_ab > 0.5 (orthogonal precision)
- MIDDLE: BPC improvement 0.1-0.3 nats
- HF: no BPC improvement OR Cell B fails to converge

**Wall:** ~20 min CPU.

**P_deflated:** 0.28 (joint); 0.68 (Constraint 2 algebraic dissolution -- already proven by Spisak-Friston 2025)

### 2c. 2-region functional differentiation test

**Anchor:** `substrate_2region_hebbian_sparse_v1_n2048_n2048`

**Test:** 2-region substrate at N_total=4096 (N_region=2048 each); Region 1 = Hebbian; Region 2 = sparse-Hebbian (f=0.05). Compare to monolithic Hebbian at N=4096.

**Cells:**
- Cell A: Monolithic Hebbian at N=4096
- Cell B: 2-region Hebbian + sparse-Hebbian at N_region=2048 each

3 seeds per cell.

**Pre-reg:**
- HP: Cell B BPC < Cell A BPC by > 0.10 nats AND no instability
- MIDDLE: improvement 0.05-0.10 nats
- HF: regression > 0.05 nats (2-region hurts)

**Wall:** ~30 min CPU.

**P_deflated:** 0.28

### 2d. Bottleneck-adaptor rung-1 test

**Anchor:** `substrate_bottleneck_adaptor_k8_rung1_v1_n4096`

**Test:** K=8 channels with bottleneck-adaptor architecture (per multi-channel scale drill) instead of direct sparse multiplicative gating. Test whether bottleneck-adaptor differentiates K=8 from K=1 at rung-1 LM scale.

**Cells:**
- Cell A: K=1 baseline (Hebbian only)
- Cell B: K=8 with sparse multiplicative gating (current architecture; expected null)
- Cell C: K=8 with bottleneck-adaptor (per drill recommendation)

3 seeds per cell.

**Pre-reg:**
- HP: Cell C BPC < Cell A BPC by > 0.10 nats AND Cell C > Cell B (bottleneck helps)
- MIDDLE: Cell C improves over Cell B by 0.02-0.10 nats
- HF: Cell C = Cell B (bottleneck doesn't help)

**Wall:** ~30 min CPU.

**P_deflated:** 0.22

---

## Phase 3 -- Convergent architecture build (engineer in parallel; deploy when Phase 1/2 inform)

### 3. Convergent brain-correct architecture

**Anchor:** `substrate_convergent_brain_correct_v1_n4096`

**Architecture (unifies findings from 4 drills):**
- Sparse binary {0,1} coding at f=0.05 (Drosophila MB; 24x capacity gain)
- Single dopamine-class cf-RPE modulator (Drosophila + Friston FEP)
- STDP-asymmetric additive channel (sequence learning; W_total = W_Hebbian_sparse + lambda * W_STDP)
- Friston VFE scalar objective with precision matrix Pi (dissolves Constraint 2)
- Energy-guided top-K replay phase at N >= 8192 (conditional; optional at N=4096)

**Engineering scope:** ~15-20h
- Sparse coding primitive (~2h)
- Single-modulator simplification (~2h)
- STDP additive primitive (~4-6h)
- FEP framework with Pi + epsilon (~100 lines per Friston drill; ~3-4h)
- Top-K replay mode (~4-6h; optional at first run)

**Test:**
- Cell A: Current dense bipolar multi-channel baseline (joint D+H K=8 architecture)
- Cell B: Convergent brain-correct architecture (above spec)

5 seeds per cell at N=4096.

**Pre-reg:**
- HP: Cell B BPC < Cell A BPC by > 0.5 nats AND 4/5 seeds AND BPC < uniform - 1.5 nats absolute (substantive learning)
- MIDDLE: BPC improvement 0.2-0.5 nats
- HF: no BPC improvement

**Wall:** ~30-60 min CPU after engineering.

**P_deflated:** **0.55-0.65** (highest of any architecture tested; convergent + lit-grounded direction)

---

## Dispatch sequencing

### Immediate (Phase 1)
1. Drosophila MB ablation (60s)
2. Topological observables (5 min)
3. REM-replay retrieval energy (60s)

Total: ~10 min CPU, $0. Run all 3 in parallel if CPU slots free.

### If Phase 1a HP (Drosophila MB sparse + single modulator works)
- SKIP Phase 2 ablations (convergent direction validated)
- Go directly to Phase 3 engineering (~15-20h) + Phase 3 test (~60 min CPU)
- Total: ~17-21h to convergent architecture validation

### If Phase 1a MIDDLE/HF
- Dispatch Phase 2 (4 isolation tests; ~90 min CPU)
- Identify which architectural variable(s) are binding
- Build Phase 3 architecture incorporating ONLY the components that landed HP in Phase 2

### If Phase 2 majority HF
- Substrate-as-training-mechanism may genuinely be N-scale-bound
- Falls back to N >= 4000+ classical regime (Exp-Dev preview anchor)
- Or DeltaNet Design B fallback (substrate-retrieval + SGD readout)

---

## Combined CPU + engineering budget

| Phase | CPU wall | Engineering | $ |
|---|---|---|---|
| Phase 1 (all 3 cells) | ~10 min | ~2h (Drosophila template + topological scripts) | $0 |
| Phase 2 (conditional 4 cells) | ~90 min | ~6-8h (STDP + FEP + 2-region + bottleneck) | $0 |
| Phase 3 (convergent design) | ~60 min | ~15-20h | $0 |

**Total worst-case:** ~3h CPU + ~25-30h engineering + $0 cloud.

Per [[feedback-cloud-only-when-absolutely-necessary]]: ZERO cloud planned. Everything CPU at substrate-class scales.

---

## Strategic outcomes

### If Phase 1a HP (most likely best-case)

- Drosophila MB template validated at substrate scale
- Sparse + single modulator becomes the primary substrate-as-training architecture
- 24x capacity gain enables operation at smaller N (perhaps N=512-1024 with sparse coding)
- All today's other drill findings (STDP, FEP, multi-channel scale) become refinements/extensions, not rescues
- Cap_map: NEW sub-property founding under substrate-as-training-mechanism row

### If Phase 1a MIDDLE + Phase 2 majority HP

- Specific architectural variable identified as binding (STDP for sequence / FEP for objective / 2-region for differentiation / bottleneck for capacity)
- Phase 3 architecture customized to incorporate only the binding components
- Substrate-as-training-mechanism viable with targeted architectural change

### If all HF

- Substrate at small scale fundamentally bound by classical Hopfield + bipolar quantization
- Falls back to N >= 4000+ regime (which Exp-Dev preview already demonstrated works)
- Or DeltaNet Design B fallback ships
- All today's drill cascade still valuable for theoretical characterization of substrate's algebraic regime

---

## Cap_map sub-property founding implications

After Phase 1 + Phase 2 + Phase 3 verdicts land:

- "Substrate-as-training-mechanism: viable at N=512-4096 under brain-correct convergent architecture (sparse coding + single modulator + STDP-asymmetric + FEP framework)" -- if HP
- "Substrate algebraic regime: classical Hopfield + bipolar quantization-bound; small-scale training requires architectural adaptation per Drosophila MB template (lit anchor: Aso-Rubin 2014; Cohn 2015; Spisak-Friston 2025; Chaudhry 2023)" -- broader characterization

10+ distinct lit anchors now grounding substrate's product narrative.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each test discriminates a specific drill-identified architectural variable
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF bands tied to drill predictions
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest decisive tests first (Phase 1)
- Per [[feedback-small-scale-first-methodology]]: rung-1 scale; cloud reserved
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 cloud planned
- Per [[feedback-2x-means-depth]]: 7 drills today were depth-extensions of the substrate-as-training thread
- Per [[feedback-brain-inspired]]: convergent architecture is brain-correct per Drosophila MB + Friston FEP + STDP precedents
- ASCII-only output enforced

PROT-018: all anchors use `_n{N}` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds varies (3-5 per test)

---

## What I am NOT requesting

- Cloud GPU dispatch (everything CPU; substrate-class scales)
- Full polynomial-p=4 modern Hopfield engineering (~10-20h; was prior recommendation; now superseded by convergent architecture if Phase 1a HP)
- DeltaNet Design B fallback dispatch (still conditional on convergent architecture HF)
- Top-level cap_map row change (sub-property founding only, after verdicts)

---

**END.**

**Exp-Dev:** Phase 1 immediate (~10 min CPU); Phase 2 conditional on Phase 1a outcome (~90 min CPU); Phase 3 convergent engineering can START NOW in parallel with Phase 1/2 ablations (low risk regardless of outcome -- convergent architecture validates either way). Total worst-case engineering ~25-30h + ~3h CPU + $0 cloud.

**Orchestrator:** informed. Cap_map sub-property founding pending verdicts.

**Research session:** holds for Phase 1 verdicts; synthesizes Phase 2 dispatch decision when Phase 1a lands; ships capability-implication note per outcome.
