# exp_dev hand-off -- research: federated substrate routing intelligence

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_federated_substrate_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Federated routing statistics architecture is theoretically sound. The core finding is
that routing histogram statistics have L2 sensitivity of O(1/N_queries), which makes
them low-sensitivity DP targets. At N >= 500 queries per customer and epsilon = 1.0,
Gaussian noise introduces < 5% MAE on histogram bins. This is materially more favorable
than gradient DP (used in federated model training). The architecture extends HIPAA
Option B without re-engineering the per-customer substrate.

Three cheap pre-tests (PT1, PT2, PT3) gate the empirical claims before any product
commitment or roadmap scheduling of v2.0.

P_theoretical = 0.72, P_empirical = 0.38 (calibration penalty applied; warm-start lift
and inference-attack robustness are the two unvalidated empirical claims).

---

## Anchor Candidates (rank-ordered by P_actionable x cost)

### 1. PT1 -- DP utility simulation on synthetic routing histograms (HIGHEST PRIORITY)

Anchor pointer: FED-DP-PT1 (new; not yet queued)
Substrate-product reading: Validates the core DP claim. If Gaussian mechanism at epsilon=1.0
  introduces < 5% MAE on routing histograms with N=500 queries, the federated architecture
  can be quoted to customers as "epsilon=1.0 differential privacy" without utility sacrifice.
  If MAE > 15%, the epsilon must be relaxed to 3-5, weakening the compliance posture.
Tier hint: CPU laptop; ~30-60 min wall; pure numpy simulation, no substrate code
Why-now: Cheapest possible gate. 30 minutes of code settles the core DP claim.
         Should run before any product spec or roadmap commitment.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: MAE < 5% at epsilon=1.0, delta=1e-5, N=500, 50 histogram bins
  HARD-FAIL: MAE > 15% at epsilon=1.0 for any N >= 500 (requires relaxing to epsilon=3+)
  MID-BAND: MAE in [5%, 15%] at epsilon=1.0 (still usable; customer communication must
             note that epsilon=1.0 introduces measurable noise at small customer scale)

Implementation sketch (exp_dev designs actual script):
  - Generate M=20 synthetic customer routing histograms (50 bins, Dirichlet distribution)
  - Vary N_queries from 100 to 5000
  - Apply Gaussian mechanism: noise ~ N(0, sigma^2) per bin where sigma = sqrt(2 * ln(1.25/1e-5)) / (N * 1.0)
  - Aggregate across M customers (weighted mean)
  - Measure MAE between noisy aggregate and true aggregate
  - Sweep epsilon in [0.1, 0.5, 1.0, 3.0]; report MAE per (epsilon, N) cell

### 2. PT2 -- Cross-domain routing correlation measurement (SECOND PRIORITY)

Anchor pointer: FED-CORR-PT2 (new; not yet queued)
Substrate-product reading: Determines whether the warm-start claim is defensible.
  If routing statistics are correlated across domains (cosine similarity >= 0.50),
  the warm-start lift of 10-20pp on Day 1 fast-path fraction is plausible.
  If correlation < 0.20, domain-clustered federation is required from v2.0 (not an option).
Tier hint: CPU laptop; ~1 hour wall; synthetic or real substrate routing logs if available
Why-now: Gates the customer pitch claim about warm-start lift. Must be resolved before
         any external communication about federated warm-start benefits.

Pre-reg bands:
  HARD-PASS: Mean cosine similarity across domain pairs >= 0.50
  HARD-FAIL: Mean cosine similarity < 0.20 (cross-domain aggregation adds noise not signal)
  MID-BAND: Cosine similarity in [0.20, 0.50] (domain clustering required; base federation
             may still work within domain clusters)

Note: if real substrate routing logs exist from any test runs, use those for realism.
If not, simulate two domain types (e.g. "entity-heavy" vs "procedural" query profiles)
with distinct histogram shapes and measure similarity.

### 3. PT3 -- Inference attack robustness at minimum N threshold (THIRD PRIORITY)

Anchor pointer: FED-ATTACK-PT3 (new; not yet queued)
Substrate-product reading: Determines the minimum N_queries threshold before a customer's
  contribution is safe to include in the federated aggregate. Operationalizes the rare-
  customer inference attack risk identified in DeSIA (2025).
Tier hint: CPU laptop; ~2-4 hours; implements a simple reconstruction attack
Why-now: Required before setting the N_queries threshold in the product spec. A threshold
         that is too low creates a compliance risk; too high delays warm-start benefit.

Pre-reg bands:
  HARD-PASS: At N >= 500, attacker reconstruction MSE exceeds DP noise floor at epsilon=1.0
             (attacker cannot distinguish signal from noise at better than chance)
  HARD-FAIL: At N = 2000, attack still succeeds (MSE below noise floor). Would require
             N > 2000 threshold, significantly delaying warm-start contribution for small
             customers.
  MID-BAND: Attack succeeds at N=500 but fails at N=1000 (set threshold at 1000)

Attack implementation sketch (exp_dev designs actual script):
  - Simulate M=50 customers with known routing histograms
  - Add one "target" customer with a distinctive histogram
  - Apply DP noise (epsilon=1.0) to all contributions
  - Aggregate
  - Attack: subtract aggregate-without-target from aggregate-with-target; measure if
    target histogram is recoverable
  - Sweep N_queries for target customer from 50 to 2000
  - Report: minimum N where reconstruction fails (MSE > 2x noise floor)

---

## Sequencing note

PT1 is independent and cheapest; run first. PT2 is independent; can run in parallel with
PT1. PT3 depends on knowing epsilon from PT1 (use PT1's best epsilon in PT3's attack
simulation). Run PT3 after PT1 result is known.

If PT1 HARD-FAIL: escalate to orchestrator before continuing. The DP claim is the
foundation of the compliance posture; if it fails, the v2.0 roadmap changes.

If PT2 HARD-FAIL: domain clustering (option d) becomes a REQUIRED component of v2.0,
not an optional enhancement. Note in exp_dev return for orchestrator awareness.

If PT3 HARD-FAIL (attack succeeds at N=2000): the minimum query threshold is too high
for small customers to contribute in any reasonable timeframe. Federation may only be
viable for enterprise customers with high query volume. Note in exp_dev return.

---

## Context pointers

- Research note (full analysis with DP mechanics, crazy options, compliance posture):
  d:/AI/hd-instrument/notes/research_drill_federated_substrate_2x_2026-06-07.md
- HIPAA Option B prior analysis:
  d:/AI/hd-instrument/notes/ (search for privacy drills 2026-06-07)
- Self-improving routing prior drill (context for what "routing statistics" means):
  d:/AI/hd-instrument/data/substrate_capability_map.md (routing rows)
- ZKL privacy work (orthogonal but related compliance context):
  d:/AI/hd-instrument/notes/research_drill_zkl_alternatives_crazy_ideas_3x_2026-06-07.md

---

## Contract section

This hand-off is research-to-experiment. The 3 pre-test specs (PT1-PT3) are provided as
pre-reg recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if synthetic data assumptions differ)
- Implementing the test scripts (Gaussian mechanism simulation, correlation measurement,
  reconstruction attack stub)
- Assigning to correct queue (all PT1-PT3 are CPU laptop tier; no cloud needed)
- Writing verdict notes for each test per standard protocol
- Escalating PT1 HARD-FAIL to orchestrator immediately (gates product roadmap)
- Noting PT2/PT3 outcomes in return for orchestrator strategic awareness

## Autonomy declaration

Exp_dev may dispatch PT1 and PT2 independently without orchestrator approval (CPU pre-tests,
low cost, no substrate modification). PT3 should run after PT1 to use confirmed epsilon.

PT1 HARD-FAIL is the only result that requires immediate orchestrator escalation before
continuing. All other results inform strategy but do not block exp_dev from completing
the full PT1-PT3 sequence.

No substrate code changes are required for any of PT1-PT3. These are pure simulation
tests using synthetic data to validate the mathematical claims in the research note.
