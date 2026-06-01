# exp_dev hand-off: MCT correlator log-decay vs power-law β-relaxation test (TIER-2 / DEFERRED)

**Filed:** 2026-05-25 by Research sub-agent. Companion to `notes/research_mct_structural_glass_2026-05-25.md`.

**Status:** **DEFERRED. NOT for immediate queue refill.** This handoff exists as a PREPARED ready-state for consumption ONLY IF the saddle-cascade tier-1 falsifier (`strategy_request_to_exp_dev_cascade_plateau_test_2026-05-24.md`) returns HARD-PASS or MIDDLE-BAND. If saddle-cascade returns HARD-FAIL, do NOT ship this — rotate to IB phase-transitions rescue (P=0.42) per `notes/research_alternative_theoretical_homes_2026-05-24.md`.

**Cap_map intent:** tier-2 overlay observable for the substrate-physics landscape-geometric framework. M1 narrows landscape-singularity class (A1 standard MCT vs A3 cusp vs A4 swallow-tail) GIVEN that saddle-cascade has confirmed landscape-geometric framing.

**Pause-gating:** YES. Per [[feedback-obey-user-pause-explicitly]], do not ship while `data/orchestrator_paused.flag` exists. Per [[feedback-ship-before-dependency-verified]]: do not ship before saddle-cascade verdict lands.

**Lit-scan calibration:** Penalty applied; novel-synthesis P capped at 0.50. Substrate is finite-N=4096, not mean-field; Cavagna-Giardina-Parisi duality holds approximately. Hard-fail thresholds pre-registered.

---

## TASK

Add a weight-overlap-time-correlation diagnostic C(t, t_w) = ⟨W(t), W(t_w)⟩ / ||W(t_w)||² to substrate's existing training loop, at log-spaced t intervals, across substrate's three native operating points (same-corpus, 4-stage, diff-corpus). Fit two candidate forms:

- **Power-law β-relaxation (standard MCT, A1 singularity class):** C(t, t_w) - f_c ≈ -h · (t/τ_σ)^(-a)
- **Logarithmic decay (A3 cusp / A4 swallow-tail singularity):** C(t, t_w) - f_c ≈ -A · ln(t/τ)

Identify which form fits across the three operating points; the answer narrows the substrate's landscape-singularity class.

---

## WHY

Cavagna-Giardina-Parisi 2001 (PMID 11863741) established that the MCT transition coincides with the saddle-index-vanishing temperature — so MCT and saddle-cascade are dual descriptions of the same landscape geometry. **GIVEN saddle-cascade landscape framework is validated**, the correlation-function probe further narrows which TYPE of MCT singularity applies:
- Standard A1: power-law β-relaxation
- A3 cusp: logarithmic decay near the cusp
- A4 swallow-tail: logarithmic decay PLUS subdiffusive MSD

The substrate's discrete 3-plateau structure is most naturally compatible with A3/A4 (which support multiple glassy states per Sellitto 2012 arXiv:1206.2585 + Voigtmann 2013 arXiv:1312.1518), NOT with standard A1. So this test is the ENGINEERING-LEVEL discriminator between:
- (a) "substrate is in standard MCT regime" (boring, just kinetic slow-down)
- (b) "substrate is near higher-order MCT singularity" (interesting, predicts rich phenomenology: log-decay, re-entrance, glass-glass transitions)

---

## CONTRACT (pre-registered, set BEFORE running)

### Falsifiable predictions with HARD PASS / HARD FAIL bands per [[feedback-envelope-expansion-fail-bands]]

**HARD PASS (A3/A4 higher-order singularity framework lives):**
- Logarithmic-fit R² > 0.80 at all 3 operating points
- Power-law-fit R² < 0.30 at all 3 operating points (clean rejection of A1 standard MCT)
- Subdiffusive MSD scaling β < 0.7 (subdiffusion confirms A4 specifically) — bonus only, not required

**HARD FAIL (standard MCT A1 only OR no MCT framework):**
- Power-law-fit R² > 0.80 at all 3 operating points AND log-fit R² < 0.30 (clean standard-MCT signature; demote higher-order-singularity framing to closed)
- OR neither fit clears R² > 0.50 anywhere (no MCT-class behavior; framework inapplicable)

**MIDDLE-BAND (re-run with adjusted instrumentation):**
- Mixed: 1-2 operating points log-decay, others power-law
- Or fit-quality R² between 0.5 and 0.8 (instrument-precision-limited)
- Or one of three operating points clearly NO MCT regime while others are
- Diagnose: re-instrument or close as inconclusive

### Self-test cells per [[feedback-strategy-spec-formula-selftests]]

For the log-decay fit candidate function `C(t, t_w) ≈ f_c - A · ln(t/τ)`:
- input: t=1, t_w=1, f_c=0.8, A=0.05, τ=10 → expected output: 0.8 - 0.05 · ln(1/10) = 0.8 + 0.05 · 2.302 = 0.9151
- input: t=10, t_w=1, f_c=0.8, A=0.05, τ=10 → expected output: 0.8 - 0.05 · ln(10/10) = 0.8 - 0 = 0.8
- input: t=100, t_w=1, f_c=0.8, A=0.05, τ=10 → expected output: 0.8 - 0.05 · ln(100/10) = 0.8 - 0.05 · 2.302 = 0.6849

For the power-law fit candidate function `C(t, t_w) ≈ f_c - h · (t/τ_σ)^(-a)`:
- input: t=1, t_w=1, f_c=0.8, h=0.1, τ_σ=10, a=0.3 → expected output: 0.8 - 0.1 · (1/10)^(-0.3) = 0.8 - 0.1 · 10^0.3 = 0.8 - 0.1 · 1.9953 = 0.6005
- input: t=100, t_w=1, f_c=0.8, h=0.1, τ_σ=10, a=0.3 → expected output: 0.8 - 0.1 · (100/10)^(-0.3) = 0.8 - 0.1 · 10^(-0.3) = 0.8 - 0.05012 = 0.7499

exp_dev should verify these BEFORE running the full experiment.

### Pre-commit cap_map verdict structure

- HARD-PASS → cap_map: "substrate landscape near higher-order MCT singularity (A3/A4 class); log-decay regime predicted in continual-learning dynamics" — promote substrate-physics framework to LOAD-BEARING tier
- HARD-FAIL → cap_map: "substrate landscape in standard A1 MCT regime OR no MCT regime; higher-order-singularity framing closed" — keep substrate-physics framework at current tier; do not escalate
- MIDDLE-BAND → cap_map: no annotation change; re-instrument or close as INCONCLUSIVE per default

---

## AUTONOMY (exp_dev decides; do NOT pre-specify in this hand-off per [[feedback-no-experiment-design-in-prompts]])

- Exact anchor name
- Hyperparameter sweep grids
- HF1/HF2/HF3 numerical bounds beyond the R² thresholds above
- Specific queue choice + ETA
- Cell count / seed count (subject only to standard 5-seed-and-BF discipline; CPU/GPU choice based on resource state)
- Saved-checkpoint cadence (log-spaced is required; exact base of log is exp_dev's choice)
- Instrumentation: whether to use existing W-snapshotting or add new (exp_dev's call)

---

## SEQUENCING GUIDANCE

**DO NOT ship this until:**
1. `data/orchestrator_paused.flag` is cleared (pause discipline)
2. Saddle-cascade tier-1 falsifier (`strategy_request_to_exp_dev_cascade_plateau_test_2026-05-24.md`) has shipped AND returned a verdict
3. Saddle-cascade verdict is HARD-PASS or MIDDLE-BAND (NOT HARD-FAIL; if HARD-FAIL rotate to IB phase-transitions rescue instead)

**Estimated total cost:** 3-5 GPU hours single-run with periodic checkpoints; CPU re-analysis of saved W trajectories <30 min.

**Bundling option (better):** if saddle-cascade test is RE-SHIP for instrumentation reasons, exp_dev can BUNDLE log-decay-diagnostic instrumentation into the saddle-cascade re-ship at marginal cost — saves a full extra run cycle. This is exp_dev's call.

---

## REMOTE VERIFY checklist (per role contract)

After ship:
1. queue_add.sh verify: anchor name unique, in queue
2. SSH verify: GPU/CPU runner picked up the job
3. Smoke gate verify: self-test cells pass before data analysis
4. Post-run: status_log entry with verdict label + per-cell R² for both fit forms

---

## ROUTING NOTE FOR ORCHESTRATOR

This handoff is **filed but pause-gated and dependency-gated**. Orchestrator MUST:
1. NOT auto-dispatch on queue-empty signal
2. NOT trigger if user has paused
3. WAIT for saddle-cascade verdict
4. Re-check this handoff after saddle-cascade verdict lands; if HARD-PASS or MIDDLE-BAND, route to exp_dev as fresh dispatch; if HARD-FAIL, archive this handoff with no dispatch

Per [[feedback-ship-before-dependency-verified]]: shipping this before saddle-cascade verdict would burn 3-5 GPU hours on a confounded probe.

---

**End handoff.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
