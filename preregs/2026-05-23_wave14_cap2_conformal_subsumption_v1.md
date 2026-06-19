# Prereg: wave14_cap2_conformal_subsumption_v1

**Trigger**: Strategy x Research shore-up matrix 2026-05-23 Weakness #1 (HIGH priority). Cap 2 PROVISIONAL ❌ at v160 is the only open PROVISIONAL ❌ closure in v168 portfolio; Rescue 5 (Gap C conformal subsumption Pattern 1) was sketched at v160 but never operationalized.

**Hypothesis (re-axiomatization, not substrate-level claim)**:
Cap 2's customer-facing self-monitoring claim — "the substrate knows when it does not know" — can be delivered as DOWNSTREAM conformal calibration over the existing Bet G / cleanup confidence stream, WITHOUT any substrate-level intrinsic margin signal. Pattern 1 (metric re-axiomatization) per research_meta_map_and_adjacencies_2026-05-23.md says this is the highest-leverage cheap intervention.

**Operating point**: N=8192, M=200 (above-but-near capacity per Bet G calibration), 5 seeds, n_queries=800/seed, noise grid p in {0.0, 0.05, 0.10, 0.15, 0.20}. 50/50 calibration/test split per seed. Alpha sweep over {0.30, 0.20, 0.10, 0.05} to trace Pareto front.

**Hard PASS thresholds** (any ONE of the following at FULL config):
1. >= 3/5 seeds achieve committed-set accuracy >= 0.90 at abstention rate <= 0.20 at some alpha.
2. Pareto front is monotone (as alpha decreases, abstain decreases AND committed_acc decreases; tolerate 0.05 noise).
Both must hold simultaneously for `CAP2_CONFORMAL_RESCUE_PASS`.

**Hard FAIL thresholds**:
- 0/5 seeds reach committed_acc >= 0.90 at abstain <= 0.20 at ANY alpha → `CAP2_CONFORMAL_RESCUE_FAIL`.
  Cap 2 closure stands; re-axiomatization does not deliver.

**PARTIAL**: in between (some seeds satisfy gate but not the 3/5 floor, OR all satisfy but Pareto non-monotone).

**Closure implication**:
- PASS → Cap 2 returns to portfolio as a rescued ✅ via Gap C subsumption; cap_map row updated to "calibrated abstention over Bet G stream". Zero substrate change.
- FAIL → Cap 2 closure at PROVISIONAL ❌ holds; Rescue 5 exhausted (along with the 4 prior unrun rescue sketches). Per [[feedback-rehabilitation-after-rejection]] the next move is either Rescue 2 (VAMP posterior variance) or final closure with audit trail.

**Cost**: pure CPU; ~30 min on remote_cpu_queue at FULL.

**Risks / caveats**:
- Margin distribution is sensitive to the noise stratification choice; the noise grid is fixed to match the prior cap2_confidence_margin_probe_v1 design for direct comparability.
- The split conformal coverage guarantee assumes exchangeability across the 800 queries; we stratify noise within calibration AND test to satisfy this.
- Smoke at N=1024 M=30 returned PARTIAL with monotone trade-off and acc=1.0 across all alphas (small-N is below capacity; this is structural validation only).

**Lit cross-check**: split conformal prediction (Vovk-Shafer 2005; Lei-Wasserman 2014). Venn-Abers calibration (Vovk-Petej 2014). Both are textbook; this is post-hoc wrapper not novel theory. The novelty is the substrate-portfolio re-axiomatization, not the math.
