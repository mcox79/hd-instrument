# Prereg: wave14_betV_kappa4_separation_v1

**Trigger**: Strategy x Research shore-up matrix 2026-05-23 Weakness #3 (MEDIUM-LOW). Bet V PARTIAL gap=0.424 at largeN cycle 103; stale 65 cap_map versions. Cycle 188 Task 2 honest framing: "self-reflective" claim implies gap of order epsilon; gap=0.424 is structurally inconsistent with the label. Per the matrix this is realistically a CLOSURE candidate, not a rescue candidate (P(rescue) <= 0.25), but kappa_4 is a substrate-novel direction (per v167 KAPPA_PROFILE_GROWS) that the original second-moment cycle-103 metric did not access — worth one cheap probe.

**Hypothesis**:
Excess kurtosis k_4 of the stored-probe confidence distribution differs from k_4 of the unstored-probe confidence distribution by >= 2 SD (5-seed pooled jackknife + across-seed SE) at largeN, providing a higher-cumulant separation signal where the second-moment gap is structurally inconsistent with the self-reflective framing.

**Operating point**: N=4096, num_entities=200, num_relations=20, num_facts=100, n_probes=200 per class (stored / unstored), 5 seeds. Pure CPU.

**Hard PASS** (`BETV_KAPPA4_RESCUE_PASS`):
- |k4_separation_sd| >= 2.0 SD (pooled jackknife + across-seed)
- k4_stored sign-consistent across all 5 seeds (positive OR negative for all 5).

**Hard FAIL** (`BETV_KAPPA4_RESCUE_FAIL`):
- |k4_separation_sd| < 1.0 SD.
  Closure: Bet V closes per PROT-004/006. Filed sketches: (a) re-axiomatize as downstream conformal calibration (subsumed by cap2_conformal_subsumption row); (b) absorb into v166 codeword-overlap KS-test row; (c) deprecate.

**PARTIAL**: 1.0 SD <= |k4_separation| < 2.0 SD, OR PASS magnitude but no sign consistency.

**Closure implication**:
- PASS → Bet V rescued via higher-cumulant signature; cap_map row updated to ✅ with kappa_4 separation as new metric. Substrate-novel finding aligns with v167 KAPPA_PROFILE_GROWS evidence that higher cumulants carry algebraic structure invisible to second moment.
- FAIL → Bet V closes; the row joins Cap 2's closure pattern as "metric was the issue but no rescue metric works either".

**Cost**: ~10 min CPU on remote_cpu_queue.

**Smoke result**: N=1024 1-seed returned k4_stored=-1.07 vs k4_unstored=-0.15, |sep|=1.61 SD with sign_consistent (single seed trivially). Directional signal present; FULL 5-seed at N=4096 is the discriminating run.

**Risks / caveats**:
- k_4 is sensitive to tail outliers; jackknife block-SE is the conservative choice.
- Per [[feedback-no-smoke]] honest reading: even a PASS verdict here is contingent — sign-consistent k_4 separation does not constitute a "self-reflective" claim in the strong sense the original Bet V framing implied. A PASS would be re-axiomatized to "substrate distinguishes stored vs unstored via higher-cumulant signature" not "substrate self-reflects".
- This is the FINAL probe; FAIL closes Bet V cleanly with full rescue-exhausted audit trail.

**Lit cross-check**: classical k_4 = mu_4/sigma^4 - 3 (Pearson 1905); jackknife SE (Efron 1979). Higher-cumulant separation in spin-glass order parameters (Mezard-Parisi-Virasoro 1987 Ch. 3) is the substrate-physics analog framing.
