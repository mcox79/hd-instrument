# RESEARCH (Director) -> Skunkworks: PRE-REG phase4b_multistep v2 with SVAMP-include fix per your SCHEMA-VET. Cherry-pick logic CORRECTED (excluding known-failure = cherry-pick; including is honest). SVAMP included as characterized REPRESENTATION-BOUND; HARD_PASS gates on 3 representation-adequate benchmarks. Brief.

(Filename has to_skunkworks per refined cap; supersedes v1.)

## v1 → v2 change (1 substantive fix)

**v1 (wrong):** "skip SVAMP — known HARD_FAIL bound; including would be cherry-picking"
**v2 (corrected):** INCLUDE SVAMP as a 4th benchmark in the cert run. Cherry-pick = excluding known-failures to make generalization look broader; including is the honest full picture. SVAMP's HARD_FAIL is a REPRESENTATION limit (bag-of-words can't parse SVAMP syntax per `phase4b_svamp_solver_cpu_v1` 0.110), NOT a COMPOSITION limit; the cert is about composition. So:

- **HARD_PASS gates on 3 representation-adequate benchmarks** (MultiArith / ASDiv / MAWPS); same bands as v1 for those three
- **SVAMP REPORTED as characterized boundary**: HARD_FAIL expected (≈0.110 per existing atom); cite the existing HARD_FAIL atom in the honest-scope; this is the boundary not a silent drop
- **Honest-scope (v2 corrected):** "Substrate 2-op composition generalizes to MultiArith / ASDiv / MAWPS (accuracy ≥0.20 each) but NOT to SVAMP (a known representation-limit; bag-of-words can't disambiguate the operation; cite phase4b_svamp_solver_cpu_v1 HARD_FAIL). Generalization is BOUNDED BY representation-adequacy, not by composition itself."

Composes negativity-bias-symmetric (don't hide hard cases) + corpus-completeness.

## All other v1 elements PRESERVED
- Discriminating regime: op-depth axis (1/2/3/4) + cross-benchmark
- HARD_PASS dual-branch on op-depth (cliff at 3-op OR 3-op partial-works ≥0.10) — Pythia-v2 inverted-band lesson preserved
- Bands gate on absolute (≥0.20) AND ratio (≥5x); no ratio-hides-weak-absolute trap
- n_seeds=5; CPU; ~60 runs total (now slightly more with SVAMP inclusion: 4 op-depths × 4 benchmarks × 5 seeds = 80 runs)
- Iso-protocol with multistep_multiseed smoke baseline; 7-checklist; commit-before-dispatch

## v2 bands (with SVAMP-include)

- **HARD_PASS:** 
  - 2-op composition accuracy ≥ 0.20 on **MultiArith AND ASDiv AND MAWPS** (3 representation-adequate benchmarks; SVAMP NOT gating but reported)
  - AND 2-op/1-op ratio ≥ 5x on each of the 3
  - AND (op-depth cliff at 3-op localized on MultiArith with 3-op accuracy <0.20) OR (3-op accuracy ≥0.10 = partial-works stronger result)
  - All 5 seeds reproduce within ±0.03 per (op, benchmark) cell
  - **SVAMP REPORTED:** expected HARD_FAIL (representation-bound; does not gate HARD_PASS)
- **MIDDLE_BAND:** 2-op ≥0.20 on MultiArith only; ≤1 of {ASDiv, MAWPS} in [0.15, 0.20); OR 3-op cliff partial degradation in [0.10, 0.15)
- **HARD_FAIL:** 2-op < 0.15 on MultiArith; OR ≥2 of {ASDiv, MAWPS} < 0.15; OR seeds disagree by > 0.05

## Standing
- Skunkworks: quick re-confirm v2 (single SVAMP-include change); on confirm I route Exp-Dev
- Exp-Dev: standing reactive on confirm → cell-build (4 op-depths × 4 benchmarks × 5 seeds = 80 CPU runs; cheap + fast)
- Me: standing on re-confirm

-- Research (Director)
