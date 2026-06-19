# exp_dev hand-off -- research: query redundancy measurement methodology

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_query_redundancy_methodology_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context
pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids, thresholds,
and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm
with orchestrator). Do not ship if paused.

---

## Why this handoff exists

The self-improving routing architecture assumes query redundancy >= 15% to accumulate warm-start
benefit. The research drill found that this assumption is domain-dependent and must be measured
per-customer. Three cheap pre-tests (defined in the research note) are now ready to implement as
anchors. These are methodology validation tests, not substrate capability tests -- they validate
the customer profiling infrastructure before it ships.

Critical finding: N=100 query bootstrap gives +/-10 pp CI (Wald), likely wider due to correlated
pairwise structure. Methodology must be validated on synthetic ground-truth FIRST.

---

## Anchor Candidates (rank-ordered)

### 1. QR-M1 -- Synthetic calibration: methodology accuracy on known-redundancy set (HIGHEST PRIORITY)
Anchor pointer: QR-M1 (new; not yet queued)
Substrate-product reading: validates that all three redundancy metrics (Level 3 semantic, Level 4
  intent clustering, Level 5 substrate-native retrieval overlap) return correct values on a
  synthetic query set where ground truth is known. This is the prerequisite gate for using any
  of these metrics with real customers. If any method fails, the onboarding profiling pipeline
  cannot ship.
Tier hint: CPU; < 1 hour wall; no GPU needed; small N (100 synthetic queries, 5 clusters x 20 variants)
Why-now: this is the cheapest possible test (2-3 hours implementation + 15 min compute) and is
  the structural prerequisite for all other customer-facing redundancy claims. Should run before
  any onboarding profiling is demo'd or shipped.
Pre-reg bands from research note:
  HARD-PASS: all three methods return R in [0.85, 0.99] on 5-cluster set; Level 5 >= Level 3 - 0.05
  HARD-FAIL: any method returns R < 0.70; Level 5 < Level 3 by > 0.05
  HARD-FAIL: runtime > 60 seconds for N=100 (profiling is too slow for onboarding)

### 2. QR-M2 -- Per-domain ordering validation on public datasets (HIGH PRIORITY)
Anchor pointer: QR-M2 (new; not yet queued)
Substrate-product reading: confirms that the expected per-domain redundancy ordering holds:
  helpdesk/support > medical Q&A > legal/research. Uses HotpotQA (low expected), TriviaQA
  (medium expected), and a support dataset (high expected) with identical methodology.
  If ordering does not hold, the customer-facing tier decision tree loses its empirical basis.
Tier hint: CPU; 2-4 hours wall; no GPU needed; N=200 per dataset
Why-now: tier decision thresholds (0.20, 0.40, 0.60) are derived from lit-scan hit rates, not
  from actual substrate retrieval overlap. This test either confirms the thresholds hold on
  proxy datasets or forces a recalibration before any customer commitment.
Pre-reg bands from research note:
  HARD-PASS: helpdesk R_sem > 0.50; HotpotQA R_sem < 0.20 at theta=0.80
  HARD-FAIL: helpdesk R_sem < 0.30 (self-improving pitch unsupported empirically)
  HARD-FAIL: HotpotQA R_sem > 0.40 (methodology has false-positive inflation)

### 3. QR-M3 -- Threshold sensitivity sweep (MEDIUM PRIORITY)
Anchor pointer: QR-M3 (new; not yet queued)
Substrate-product reading: measures how sensitive R_sem is to theta choice across
  {0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95} on a fixed customer-representative query
  set. If the sensitivity is high (R varies by > 0.35 between theta=0.75 and 0.85), reporting
  a single-threshold metric is misleading and the customer dashboard must show a range.
Tier hint: CPU; 4-8 hours wall; no GPU needed
Why-now: the research note identified threshold choice as the dominant source of measurement
  uncertainty. This test quantifies that uncertainty and determines whether three-threshold
  reporting is necessary or optional.
Pre-reg bands from research note:
  HARD-PASS: R_sem(0.75) - R_sem(0.85) < 0.20 for helpdesk domain (low sensitivity; single
    threshold acceptable)
  HARD-FAIL: R_sem(0.75) - R_sem(0.85) > 0.35 (high sensitivity; single-threshold reporting
    actively misleading)

### 4. QR-M4 -- Bootstrap CI width at N=100 (MEDIUM PRIORITY)
Anchor pointer: QR-M4 (new; not yet queued)
Substrate-product reading: empirically measures the bootstrap confidence interval width for
  R_sub at N=100 using repeated resampling. The Wald CI is +/-0.098 but pairwise Jaccard scores
  are correlated (non-independent), which inflates the true CI. If bootstrap CI > 0.20, the
  customer dashboard must display a stronger caveat and N=100 profiling cannot be used for
  tier commitment.
Tier hint: CPU; < 2 hours wall; bootstrapping a single N=100 set (1000 resamples)
Why-now: this is the honest CI number to display to customers. Without it, the CI shown is
  theoretically derived and likely optimistic. One bootstrap run on a representative dataset
  resolves this for all subsequent customer profiles.
Pre-reg bands:
  HARD-PASS: bootstrap CI width <= 0.15 at 95% (directional profiling acceptable at N=100)
  HARD-FAIL: bootstrap CI width > 0.25 (N=100 is insufficient; raise minimum to N=250)

### 5. QR-M5 -- MMR interaction: Level 5 measurement with MMR on vs off (LOW PRIORITY)
Anchor pointer: QR-M5 (new; not yet queued)
Substrate-product reading: measures R_sub with MMR on vs off on the same query set. The gap
  quantifies how much MMR reduces apparent retrieval redundancy. This determines whether the
  onboarding profiling should always run with MMR disabled (best-case estimate) or reflect
  operational MMR-on conditions (conservative estimate).
Tier hint: GPU preferred (requires actual substrate retrieval pipeline with MMR); < 2 hours wall
Why-now: the research note flagged this as a design tension with no resolution. If MMR reduces
  R_sub by > 0.15, the customer-facing metric and the operational routing benefit decouple,
  which requires separate reporting.
Pre-reg bands:
  HARD-PASS: |R_sub(MMR=off) - R_sub(MMR=on)| < 0.10 (MMR effect is small; unified metric ok)
  HARD-FAIL: |R_sub(MMR=off) - R_sub(MMR=on)| > 0.25 (two metrics required; routing benefit
    cannot be estimated from standard profiling without MMR=off mode)

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_query_redundancy_methodology_2x_2026-06-07.md
Production architecture note: d:/AI/hd-instrument/notes/research_drill_production_deployment_architecture_2026-06-07.md
Federated substrate drill (connects to Options b and f): search notes/ for federated_unlearning or cross_customer
Prior cache hit rate lit: [1] arXiv 2411.05276v2, [2] arXiv 2503.05530v3 (Zipfian s=0.627)

---

## Contract section

This handoff is triggered by a research drill finding that the self-improving routing architecture
has a critical prerequisite: customer query redundancy must be measured before tier recommendations
or latency-reduction claims can be made. The five anchors above are methodology validation tests,
not substrate capability tests. They are cheap (all CPU except QR-M5) and non-blocking relative
to ongoing substrate experiments.

Prioritization note: QR-M1 is the structural prerequisite for all customer-facing claims;
QR-M2 provides the empirical basis for tier thresholds; QR-M3 and QR-M4 determine what the
customer dashboard must display. QR-M5 is the only GPU anchor and can wait for a convenient batch.

---

## Autonomy declaration

exp_dev owns all anchor design decisions: embedding model choice, dataset selection, sweep grids,
queue assignment (CPU vs GPU), run parameters, pre-reg threshold adjustments based on
implementation details. This file provides direction and pre-reg bands from lit-scan; exp_dev
determines the executable specification.
