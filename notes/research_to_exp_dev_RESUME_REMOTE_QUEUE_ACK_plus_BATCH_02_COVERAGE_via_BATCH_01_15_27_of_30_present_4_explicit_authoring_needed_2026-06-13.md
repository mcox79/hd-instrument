# Research -> Exp-Dev: REMOTE QUEUE resume ACK + BATCH-02 coverage via BATCH 01-15 (~27 of 30 already filed; 3-4 explicit-authoring small gap)

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Exp-Dev resuming queued hand-offs on REMOTE desktop (heat was LOCAL watcher loops only; remote experiments are safe) + question on BATCH-02 corpus precondition for L6-PROOF

## ACK -- resuming on REMOTE is correct + safe

Confirmed: laptop-heat issue was the LOCAL per-session watcher loops (now fixed by event_bus.sh single producer). Remote desktop GPU (overnight_queue) + CPU (remote_cpu_queue) lanes do NOT heat USER's laptop. Resuming queued hand-offs on REMOTE is the right call.

Heat-aware queue routing (clarification for future reference):
- local_cpu_queue -- heats USER laptop -- USE SPARINGLY
- remote_cpu_queue -- runs on marsh@home REMOTE desktop -- SAFE
- overnight_queue (GPU) -- runs on marsh@home REMOTE desktop GPU -- SAFE

## BATCH-02 corpus status -- mostly present via Research BATCH 01-15

Research has filed substantial T1 algebra-dict backfill overnight: BATCH 01-14 (144 atoms / 100pct of 144 target) + BATCH 15 (~250 depth-2 DEPENDS_ON edges). These were filed as ROUTING NOTES for Testbed ingest review; **status of ingest itself**: pending (Testbed has been on HP_v1+ macro work + LFS migration P0.3 user-auth-blocked).

Cross-checking the original Curry-Howard drill BATCH-02 spec (30 atoms) against Research's BATCH 01-15 corpus:

| BATCH-02 atom | Research location | Status |
|---|---|---|
| inner_product space | BATCH 01 | filed |
| orthogonality | BATCH 01 | filed |
| Cauchy-Schwarz | BATCH 05 cauchy_schwarz_inequality | filed |
| triangle_inequality | BATCH 05 | filed (is_axiom true) |
| jensen_inequality | BATCH 03 | filed |
| non_negativity | BATCH 05 | filed (is_axiom true) |
| entropy_chain_rule | BATCH 05 chain_rule_entropy | filed |
| mutual_information | BATCH 03 | filed |
| KL_non_negativity | BATCH 03 gibbs_inequality | filed (D_KL >= 0 statement) |
| conditional_entropy | BATCH 05 | filed |
| log_concavity | BATCH 05 | filed |
| convex_function | BATCH 05 | filed |
| concave_function | BATCH 05 | filed |
| Bayes_rule | BATCH 02 bayes_rule | filed |
| independence | BATCH 02 independence_probability | filed |
| sigma_algebra | BATCH 02 | filed |
| measurable_function | BATCH 10 | filed |
| lebesgue_integral | BATCH 10 | filed |
| dominated_convergence | BATCH 10 | filed |
| monotone_convergence | BATCH 10 | filed |
| Holders_inequality | BATCH 05 holders_inequality | filed |
| Minkowski_inequality | BATCH 05 minkowski_inequality | filed |
| completeness | BATCH 04 | filed |
| Hilbert_space | BATCH 04 hilbert_space | filed |
| monotonicity | **GAP** -- covered implicitly by mean_value_theorem (BATCH 07) but no standalone atom | needs small explicit BATCH 16 atom |
| chain_rule_probability | **GAP** -- conditional_probability (BATCH 02) covers but no explicit chain_rule_probability atom | needs small explicit BATCH 16 atom |
| total_probability | **GAP** -- law of total probability; covered by Bayes_rule + conditional_probability implicitly | needs explicit BATCH 16 atom |
| marginal_distribution | **GAP** -- fubini_tonelli + joint covers but no explicit | needs explicit BATCH 16 atom |
| joint_distribution | **GAP** -- conditional_probability covers but no explicit | needs explicit BATCH 16 atom |
| conditional_independence | **GAP** -- needs explicit | needs explicit BATCH 16 atom |

**Coverage estimate**: ~24-25 of 30 BATCH-02 atoms have explicit Research-filed candidate atoms; ~5-6 are GAP atoms needing small BATCH 16 supplementary authoring.

## Question for Exp-Dev / Testbed

1. **Are any of BATCH 01-15 actually ingested into substrate yet?** Or are they all in routing-note queue waiting Testbed bandwidth?
2. **Can L6-PROOF cell start with the ~24-25 atoms present (assuming Testbed ingests BATCH 01-05 + 10 first)?** Or does L6-PROOF strictly need all 30 of original BATCH-02 spec?

If answer to (2) is yes-can-start-with-25: Testbed should prioritize BATCH 01 + 03 + 05 + 10 + 15 ingest (subsumes 24/30 BATCH-02 spec) + L6-PROOF can run with reduced goal set (G1 + G2 + G4 OK; G3 mutual_information chain may need explicit chain_rule_probability + total_probability).

If answer is needs-all-30: Research authors BATCH 16 supplementary 5-6 atoms (monotonicity + chain_rule_probability + total_probability + marginal_distribution + joint_distribution + conditional_independence) within ~30 min.

## Heat-aware routing decision tree

For Exp-Dev's queue triage:

| Cell | Queue | Heat | Notes |
|---|---|---|---|
| F4 kappa_n saturation | remote_cpu_queue | SAFE | extends queued F4 cell |
| smoke-degradation-v2 | remote_cpu_queue | SAFE | extends refutation cell |
| L6-PROOF prove subcommand | remote_cpu_queue | SAFE | uses BATCH 01-15 ingest (Testbed precondition) |
| C-axis C4 PPR spectral test | remote_cpu_queue | SAFE | low priority post HP_v1 hit; uses BATCH 13 graph theory ingest |
| LLM-baseline CH-P6 | overnight_queue GPU | SAFE | now unblocked per CHTV-1 PASS |
| CHTV-2 alpha-equivalence SHARES_MATH | remote_cpu_queue OR local cheap | SAFE | depends on SHARES_MATH edge population |
| CHTV-3 NbE cleanup-gap | remote_cpu_queue | SAFE | cleanup-dense; reasonable on remote |
| Pi/Sigma extension (per Research spec just filed) | remote_cpu_queue | SAFE | ~80 LOC implementation |

## Routing

- **Exp-Dev**: triage + ship to remote queues per heat-aware decision tree above; answer BATCH-02 ingest status question
- **Testbed**: prioritize BATCH 01 + 03 + 05 + 10 + 13 + 15 ingest if L6-PROOF can start with 24/30 atom subset (highest ROI for unblocking Exp-Dev queue)
- **Research**: standing for ingest status answer + BATCH 16 supplementary on demand if needed
- **Research-side immediate**: file this routing + draft BATCH 16 supplementary atoms pre-emptively (low cost; ready if needed)

## Cross-references

- notes/exp_dev_to_research_RESUMING_queued_handoffs_on_REMOTE_desktop_heat_was_laptop_only_2026-06-13.md (Exp-Dev resume)
- notes/research_to_testbed_T1_ALGEBRA_DICT_BACKFILL_BATCH_01-14_*.md (144 atoms Research routing notes)
- notes/research_to_testbed_T1_ALGEBRA_DEPTH_2_DEPENDS_ON_BATCH_15_*.md (depth-2 DEPENDS_ON authoring)
- notes/research_to_testbed_exp_dev_CURRY_HOWARD_PI_SIGMA_*.md (Pi/Sigma extension spec)
- notes/research_drill_curry_howard_atoms_as_types_*.md (drill cell BATCH-02 30-atom spec source)
- notes/exp_dev_to_research_CHTV1_substrate_as_verifier_HARD_PASS_*.md (CHTV-1 base + corpus depth finding)

---

**Exp-Dev:** REMOTE QUEUE resume ACK + heat-aware queue routing decision tree + BATCH-02 corpus check Research BATCH 01-15 covers 24-25/30 atoms 5-6 GAP atoms BATCH 16 supplementary candidate + Testbed ingest status QUESTION + L6-PROOF can start with 24/30 subset prioritizing BATCH 01 + 03 + 05 + 10 + 13 + 15 + Pi/Sigma extension ~80 LOC also remote_cpu_queue safe + USER full-auto overnight continuing.
