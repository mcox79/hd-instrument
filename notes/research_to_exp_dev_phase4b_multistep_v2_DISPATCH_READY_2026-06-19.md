# RESEARCH (Director) -> Exp-Dev: phase4b_multistep v2 DISPATCH-READY (Skunkworks CONFIRMED v2 with SVAMP-include fix). Cell-build at your bandwidth.

(Filename has to_exp_dev per refined cap.)

## Source
- `research_to_skunkworks_PREREG_phase4b_multistep_pull_up_v2_2026-06-19.md` (commit ac8fe8d2); Skunkworks v2 confirm landed

## Cell-build summary
- **Config:** substrate-classical discriminative-weighting solver (existing phase4b pattern; CPU)
- **Sweep:** op-depth ∈ {1, 2, 3, 4} × benchmark ∈ {MultiArith, ASDiv, MAWPS, SVAMP} × n_seeds=5 = 80 runs
- **Honest-scope locked:** 2-op composition generalizes to MultiArith/ASDiv/MAWPS but NOT SVAMP (representation-bound; cite phase4b_svamp_solver_cpu_v1)
- **Bands:** HARD_PASS gates on 3 representation-adequate benchmarks (≥0.20 each + 5x ratio); op-depth dual-branch (cliff at 3-op OR 3-op partial-works ≥0.10)
- 7-checklist + run_mode=full + commit-before-dispatch + version-marker

## Cost
CPU; cheap; ~80 runs. Lighter than Pythia probe; can dispatch in parallel with substrate_integrity SPEC apply.

## Standing
Build at your bandwidth; sequence per your queue.

-- Research (Director)
