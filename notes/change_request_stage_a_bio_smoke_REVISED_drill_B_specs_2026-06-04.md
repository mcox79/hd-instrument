# Change Request -- Stage A bio-primitive smoke cells REVISED per Drill B specs + WHY-DRILL diagnostics

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04 (REVISION of change_request_stage_a_add_bio_primitive_smoke_cells_2026-06-04)
**Subject:** Earlier change-request used pre-Drill-B specs. Drill B (per-bio-primitive empirical test designs 3x) landed with engineering constraints + WHY-DRILL diagnostics. This REVISES the bio-primitive smoke cells to match.

---

## Why this revision

Earlier change-request (15:54-ish today) shipped 5 bio-primitive smoke cells with OUTDATED specs:
- B2 DG expansion: spec'd N_DG=20000 (1.6GB W storage; INFEASIBLE on laptop RAM)
- B5 STDP replay: spec'd M=20 at N=2048 (vacuously easy; M/N=0.0098 << alpha_c=0.14; no catastrophic forgetting to correct)
- B4 column ensemble: spec'd wall-time speedup HP (not achievable on single-CPU thread)

Drill B (per-bio-primitive empirical test designs 3x) landed with REVISED engineering specs + WHY-DRILL diagnostics per primitive. This change-request applies those revisions.

---

## Revised bio-primitive smoke cells (per Drill B spec)

### Cell B1: One-shot Hebbian write (unchanged)

- N=2048, V=70 bigram char-LM, K=5 classes, M_total=50 patterns
- Cell 1a: balanced random patterns
- Cell 1b: hard negatives (inter-class Hamming < N/4)
- Cell 1c: noisy patterns sigma=0.5
- HP: accuracy >= 80% AND speedup >= 100x vs Adam baseline
- WHY-DRILL on HF: measure per-class energy drop after each write; if > 30% per class added, capacity exceeded; fix: normalize patterns or switch to sparse encoding prerequisite
- Wall: ~15s; P_deflated 0.50

### Cell B2: DG-class sparse expansion (REVISED to RAM-feasible N_DG)

- Input N=1024 -> expand 4x to N_DG=4096 (NOT 20000; RAM constraint)
- 2a: dense f=0.5 at N=2048 baseline
- 2b: sparse f=0.02 expansion at 4x
- 2c: intermediate f=0.02 at 4x
- M=50 patterns; recall at 20% noise
- HP: M_crit(2b) >= 10x M_crit(2a) (revised from 100x; 4x expansion not 20x)
- WHY-DRILL on HF: compute E^T E; if off-diagonal > 0.1*N → orthogonality insufficient; fix: increase N_DG or use ReLU projection
- Wall: ~25s; P_deflated 0.42

### Cell B3: cf-RPE active gating (unchanged spec; revised metric)

- N=2048, V=70 char-LM
- 3a: write all examples (baseline)
- 3b: write at top-10% prediction error
- 3c: write at top-1% prediction error
- HP: Cell 3b/3c reaches BPC=2.0 target with <= 1/10 writes of 3a
- WHY-DRILL on HF: histogram prediction error distribution; if no bimodal structure → gate not selective; fix: use exponentially-smoothed surprise (running mean-subtracted error)
- Wall: ~30s; P_deflated 0.42

### Cell B4: Column ensemble (REVISED HP metric to parameter-efficiency)

- K=10 sub-substrates at N=2048 each
- 4a: disjoint training splits
- 4b: same data, different seeds (bagging)
- 4c: single N=20480 substrate at M=10 (smoke budget; not M=50)
- **REVISED HP:** ensemble within 0.05 BPC of single large substrate (PARAMETER-EFFICIENCY metric, NOT wall-time speedup -- parallel speedup needs hardware not available on single CPU thread)
- HF: > 0.2 BPC worse than single large
- WHY-DRILL on HF: pairwise W cos-similarity; if all > 0.9 → no ensemble diversity; fix: BAGGING with 50% subsets
- Wall: ~50s (Cell 4c N=20480 is bottleneck); P_deflated 0.32

### Cell B5: STDP-replay consolidation (REVISED M to near-alpha_c)

- N=2048; M=20 sequential patterns (smoke)
- 5a: no replay
- 5b: random replay 10% time budget
- 5c: temporally-ordered STDP replay 10% budget
- 5d: 50% budget replay
- HP: Cell 5c retains >= 1.5x more patterns than 5a
- **CRITICAL:** M=20 at N=2048 is M/N=0.0098 << alpha_c=0.14. No catastrophic forgetting to correct. WHY-DRILL on HF MUST first rerun at M = alpha_c * N = 287 before concluding replay ineffective.
- WHY-DRILL on HF: verify M/N ratio; if < 0.05 → rerun at M=287; if still HF → diagnose temporal-order encoding
- Wall: ~15s for 4 smoke cells; P_deflated 0.37

### NEW Cell B6: Energy-driven pruning (D-ECR) (from Drill B)

- N=512 (not 2048; 4x speedup; smoke budget)
- alpha_c at N=512 = 72 patterns
- M = {1.0 * alpha_c, 1.3 * alpha_c} = {72, 94}
- 4 sub-cells per loading: no-eviction / D-ECR / LRU / random
- HP: D-ECR >= 20% higher recall than no-eviction AND beats LRU at M=1.3*alpha_c
- MID: D-ECR beats no-eviction but not LRU
- HF: D-ECR <= LRU or <= random
- WHY-DRILL on HF: compute energy-interference correlation corr(E_i, I_i); if < 0.3 → energy not proxy for interference; fix: evict by direct interference score
- Wall: ~16s (8 cells at N=512); P_deflated 0.37

### NEW Cell B7: Theta-gamma temporal binding (from Drill B; lower P)

- N=2048, K=5 sequence
- 7a: explicit position vectors (Bundle E E1 baseline)
- 7b: phase modulation x_phase_k = sign(x_k * cos(2*pi*k/5)) -- no position vectors
- 7c: Cell 7b with sigma=0.2 phase noise
- HP: Cell 7b achieves >= 80% order recovery AND 50% parameter saving (no position vectors stored)
- HF: < 50% order recovery
- WHY-DRILL on HF: compute pairwise dot products of x_phase_k; if > 0.1*N → not orthogonal; fix: increase to N=8192 (4x reduction in overlap error) or reduce K from 5 to 3
- Wall: ~25s (100 noise draws); P_deflated 0.20 (novel-synthesis cap; substrate-novel)

### NEW Cell B8: Predictive-coding residual encoding (from Drill B; algebraically MID)

- N=2048, V=70 char-LM
- Base predictor: bigram frequency model from first 1000 chars Wikitext-2
- 8a: store full pattern x_full
- 8b: store x_residual = x_full - bigram_projection
- 8c: two-level hierarchical residual
- **REVISED HP:** Cell 8b achieves r = ||x_res|| / ||x_full|| <= 0.32 (algebraically required for 10x M_crit; bigram base only captures ~50% entropy so r ~ 0.5-0.7 expected)
- **MID is the ALGEBRAICALLY PREDICTED outcome** (2-4x capacity gain at r in [0.32, 0.71]); NOT HP (which requires 160M+ LLM as base predictor)
- HF: r > 0.71 (< 2x gain)
- WHY-DRILL on HF: measure r directly; if > 0.7 → base predictor too weak; fix: replace bigram with first-PC PCA projection
- Wall: ~20s; P_deflated 0.37

---

## Aggregate smoke sweep (existing N-crossover + revised bio cells)

Combined sweep:
- Existing N-crossover sweep (S1-S10; 10 cells): ~10-15 min
- REVISED bio-primitive cells (B1-B8; 8 cells, 29 sub-cells): ~3.3 min CPU
- **Total: 18 cells / ~39 sub-cells; ~15-20 min CPU; $0**

## P_deflated per cell (corrected per Drill B)

| Cell | P_algebraic | P_implementation | P_joint HP |
|---|---|---|---|
| B1 one-shot Hebbian | 0.80 | 0.62 | 0.50 |
| B2 DG sparse (N=4096) | 0.70 | 0.60 | 0.42 |
| B3 cf-RPE active gating | 0.70 | 0.60 | 0.42 |
| B4 column ensemble (param-eff) | 0.65 | 0.49 | 0.32 |
| B5 STDP replay (with M=287 fallback) | 0.65 | 0.57 | 0.37 |
| B6 D-ECR pruning | 0.62 | 0.60 | 0.37 |
| B7 theta-gamma (novel synthesis) | 0.40 | 0.50 | 0.20 |
| B8 residual encoding (MID expected) | 0.65 | 0.57 | 0.37 |

**P_all_8_HP = 0.17 (honest; product under independence).**
**Realistic outcome: 3-5 of 8 HP; 2-3 MID; 0-2 HF with specific WHY-DRILL fix paths.**

---

## Tier roadmap context (per Drill C bio-tier-scaling)

This smoke sweep tests Tier 1 (Drosophila MB-class) + first Tier 2 (Hippocampal) primitives:
- **Tier 1 primitives empirically validated today:** sparse f=0.05, cf-RPE (DA-Hebbian), one-shot via algebra
- **Tier 2 primitives in smoke:** DG separation (B2), STDP replay (B5), column ensemble (B4)
- **Future Tier 2 to add at Pythia-160M:** CA3 completion + 4-modulator system (DA + ACh + NA + 5HT)

Per bio-scaling law: primitives ~ N^0.34. Each tier-up adds ~6 new primitives.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per cell
- Per [[feedback-no-preframe-batch-all-pass]]: no implicit PASS expectation; P_all_8=0.17 realistic
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL diagnostics per HF with specific fixes
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-change-request-protocol]]: REVISION of earlier change-request
- ASCII-only

PROT-018: anchors use `_bio_smoke_REVISED_v1` suffix
PROT-021: source=local CPU, run_mode=smoke, n_seeds=3-5 per sub-cell

---

**END.**

**Exp-Dev:** REPLACES earlier `change_request_stage_a_add_bio_primitive_smoke_cells`. Use these revised specs. ~3-4h engineering total (similar to earlier; just revised cell parameters). ~3.3 min CPU for full bio sweep + ~10-15 min for N-crossover sweep = ~15-20 min combined.

Each cell has explicit HP/MID/HF + WHY-DRILL diagnostic on HF with specific fix path. Per [[feedback-pressure-test-negative-findings]]: HF triggers WHY-DRILL before iterating; don't abandon a primitive on first HF.

Realistic outcome: 3-5 of 8 HP; identify working bio-primitive set for Stage A full run + Stage B tier-up.

**Research session:** holds for combined smoke sweep verdict; next priority drill is sparse-coding-compressed-sensing (DG-expansion algebraic phase transition; converged across multiple drill landings as next-priority Tier-1b unmined topic).
