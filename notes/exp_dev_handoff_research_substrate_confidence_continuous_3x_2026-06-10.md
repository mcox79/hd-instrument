# exp_dev hand-off -- research: substrate per-sample confidence continuous 3x drill

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_confidence_continuous_3x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY +
CONTRACT + AUTONOMY. Exp_dev designs anchors, sweep parameters, thresholds, and queue
placement. NOT this file.

---

## WHY NOW

Cycles 216-217 established a hard empirical boundary:
  - PP-277: aggregate ECE=0.018 (excellent calibration over the distribution)
  - LAP4-3: per-sample correlation corr=0.000 (margin carries zero per-sample signal)
  - PP-263: binary know-accuracy=0.992 (binary threshold per-sample works)
  - PP-281: binary-threshold AUC=0.998 (binary is near-ceiling)

Three independent lines confirm the binary structure. The 3x drill identifies FIVE
mechanisms that can produce genuine per-sample continuous confidence without changing
the core substrate architecture. These are ordered by cost and expected impact.

The cheapest decisive test (CONF-MULTI-PROBE, 2 hrs CPU) will either (a) find a quick
win via margin_ratio as novel feature, or (b) confirm the impossibility applies at
feature level and direct resources to sampling-based approaches. Either outcome is
high-value.

The conformal prediction wrapper (CONF-CONFORMAL-BUILD, 1 day CPU) is recommended
regardless of CONF-MULTI-PROBE outcome -- it provides a formal statistical guarantee
(95% coverage) that is immediately usable in product and that no competitor provides
alongside audit trails and GDPR erasure.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- CONF-MULTI-PROBE (CPU, ~2 hrs)

Pointer: research note Level 9 (Multi-feature ensemble confidence) and Level 12 Rank 2
Substrate-product reading: using the existing calibration dataset from PP-277 / LAP4-3,
compute multi-feature confidence vector [margin, margin_ratio, iter_count, neighbor_density]
for each query. margin_ratio = top1_margin / top2_margin is the novel feature. Train a
logistic regression on 500 queries, evaluate AUC on 200 held-out. Compare against
margin-alone baseline (AUC from LAP4-3).
Tier hint: laptop CPU, no API, no GPU; existing calibration data reused
Why now: cheapest gate. If margin_ratio carries signal (two nearly-equal top patterns =
ambiguous query), AUC improvement is immediate and costs nothing architecturally.

HARD-PASS: AUC >= 0.75 per-sample (meaningful improvement over margin-alone baseline)
MIDDLE-BAND: 0.60 <= AUC < 0.75 (weak improvement; proceed to Anchor 2)
HARD-FAIL: AUC <= 0.60 (no signal in any feature combination; confirms impossibility
           at feature level; pivot directly to Anchors 3 and 4)

### Anchor 2 -- CONF-LANGEVIN-SMOKE (CPU, ~2-3 hrs)

Pointer: research note Level 6 (Sampling-based posterior)
Substrate-product reading: modify the cleanup loop to add Gaussian noise
eps~N(0,sigma^2) at each iteration. Run T=20 stochastic cleanup samples from the same
cue. Measure fraction agreeing on the top-1 retrieved pattern. Compute spearman rho
between this fraction and per-sample correctness. Test three sigma values (small,
medium, large). This tests whether Langevin sampling provides a genuine per-sample
posterior beyond what the deterministic margin gives.
Tier hint: laptop CPU, existing KB; T=20 runs per query at ~5ms each = 100ms/query total
Why now: strongest theoretical grounding (Boltzmann stationary distribution). The key
unknown is the sigma calibration -- testing three values in a smoke is the decisive gate.

HARD-PASS: spearman rho >= 0.30 for at least one sigma value
MIDDLE-BAND: 0.10 <= rho < 0.30 for best sigma
HARD-FAIL: rho <= 0.10 for all three sigma values (stochastic cleanup adds no signal;
           the basin structure is too rigid for Langevin mixing to help)

### Anchor 3 -- CONF-CONFORMAL-BUILD (CPU, ~1 day)

Pointer: research note Level 5 (Conformal prediction over substrate retrieval)
Substrate-product reading: implement the conformal wrapper on the existing cleanup
margin. Use calibration set of n=1000 queries with known correct answers. Define
nonconformity score A(q, xi_mu) = 1 - margin(q, xi_mu). Compute tau as the
(1001*0.05)/1000-th quantile of calibration scores. Evaluate on held-out 200 queries:
(a) empirical coverage (fraction where correct pattern in prediction set),
(b) median prediction set size, (c) fraction with set size 1 (unambiguous queries).
Tier hint: laptop CPU; existing substrate; no new training; n=1000 calibration set
Why now: recommended regardless of Anchors 1-2 outcome. Provides a formal coverage
guarantee that upgrades the product confidence story immediately. The set size is itself
a per-query uncertainty signal (size 1 = confident; size 4 = ambiguous).

HARD-PASS: empirical coverage >= 0.94 AND median set size <= 2 (tight and accurate)
MIDDLE-BAND: coverage >= 0.94 but median set size > 3 (accurate but uninformative)
HARD-FAIL: empirical coverage < 0.90 (calibration-test data mismatch; investigate
           query distribution shift between calibration and test sets)

### Anchor 4 -- CONF-ENSEMBLE-DISAGREE (CPU, ~2-3 hrs)

Pointer: research note Level 4 (Population codes, N=20-30 ensemble)
Substrate-product reading: extending the PP-249 / LAP4-4 population ensemble work.
Use N=20 independent substrate copies (different codebook seeds). For each query:
  - Record which pattern each copy retrieves
  - Compute disagreement fraction (1 - fraction agreeing on top-1)
  - Compute spearman rho(disagreement, per-query correctness)
This is the ensemble disagreement path recommended by arXiv:2509.14386 as the viable
workaround to the binary-supervision impossibility.
Tier hint: laptop CPU; N=20 copies at N=4096 each = feasible; existing KB reused
Why now: most empirically grounded mechanism after the impossibility confirmation.
PP-249 showed N=10 gives +12pp accuracy; the extension to disagreement-as-confidence
is a small step from validated infrastructure.

HARD-PASS: spearman rho(disagreement, correctness) >= 0.40 (strong signal)
MIDDLE-BAND: 0.20 <= rho < 0.40 (moderate signal; useful for calibration but not routing)
HARD-FAIL: rho <= 0.20 (ensemble disagreement adds nothing; accept binary + conformal)

### Anchor 5 -- CONF-BLL-HEAD (CPU, ~1 day)

Pointer: research note Level 3.2 (Bayesian last layer on cleanup features)
Substrate-product reading: implement the Bayesian last layer (arXiv:2302.10975) on
top of cleanup vectors. The feature extractor is the existing cleanup dynamics (fixed);
the Bayesian output layer is trained on a labeled confidence set. The posterior is
closed-form (no MCMC). Per-sample predictive variance is phi_i^T Sigma_post phi_i.
This gives: (a) per-sample confidence as posterior mean, (b) per-sample uncertainty
as posterior variance, (c) automatic identification of out-of-distribution queries
(high variance from low-density feature space regions).
Tier hint: laptop CPU; standard scipy/numpy for Bayesian linear regression; no GPU
Why now: gates on Anchor 1 outcome. If Anchor 1 HARD-FAIL confirms no feature-level
signal, Bayesian last layer likely hits the same ceiling (features have no signal).
If Anchor 1 MIDDLE-BAND or HARD-PASS, Bayesian last layer is the rigorous version
of the same feature signal. Run after Anchor 1 verdict.

HARD-PASS: per-sample NLL < log(2) = 0.693 (informative posterior, better than random)
MIDDLE-BAND: log(2) <= NLL < log(3) (weakly informative)
HARD-FAIL: NLL >= log(3) (uninformative posterior; feature space has no confidence signal)

---

## DEPENDENCY ORDERING

Run Anchor 1 first (cheapest gate).
  If Anchor 1 HARD-FAIL: skip Anchor 5, run Anchors 2+3+4 in parallel.
  If Anchor 1 HARD-PASS or MIDDLE-BAND: run Anchors 2+3+4+5 in parallel.
  Anchor 3 (conformal build) is recommended regardless of Anchor 1 outcome.

---

## CONTEXT POINTERS

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_confidence_continuous_3x_2026-06-10.md
- Prior calibration experiment: PP-277 (ECE=0.018 aggregate) in notes/substrate_capability_map.md
- Prior correlation failure: LAP4-3 (corr=0.000) in notes/substrate_capability_map.md
- Binary mechanism: PP-263 (know-acc=0.992), PP-281 (AUC=0.998) in cap_map
- Population ensemble: PP-249 (N=10 +12pp), LAP4-4 (N=100 +20pp) in cap_map
- Impossibility reference: arXiv:2509.14386 (binary supervision cannot learn
  nuanced per-sample calibration; ensemble disagreement recommended workaround)
- Langevin/sampling theory: PMC11888369 (sampling + attractor dynamics = Bayesian
  posterior via Boltzmann stationary distribution)

---

## CONTRACT

If Anchor 1 HARD-PASS: per-sample confidence improvement is achievable via cheap
multi-feature probe; authorize CONF-BLL-HEAD and conformal wrapper for product.

If Anchor 1 HARD-FAIL AND Anchor 2 HARD-PASS: Langevin sampling is the correct
mechanism; authorize T=20 sampling as standard confidence mode; route to exp_dev
for full-scale validation.

If Anchor 1 HARD-FAIL AND Anchor 2 HARD-FAIL: per-sample continuous confidence is
structurally inaccessible via feature-level or dynamics-level approaches; accept binary
+ conformal as the product confidence story; this is sufficient for all core use cases
(routing, audit, GDPR); no further per-sample rescue engineering warranted until
v2.0 LLM-distillation path is prioritized.

If Anchor 3 HARD-PASS (independent of above): conformal wrapper ships to product
immediately; framing is "95%-coverage prediction sets" not "per-sample probability."

If Anchor 4 HARD-PASS: ensemble disagreement is the practical confidence signal for
planning chains and Bayesian fusion (Level 11 use cases); authorize N=20 ensemble
as standard deployment for v2.0 hybrid applications.

---

## AUTONOMY DECLARATION

Exp_dev owns: exact kernel parameters, dataset size, stopping criteria, queue
assignment, anchor sequencing within the dependency ordering above.

This file provides: mechanism descriptions, pre-registered thresholds, dependency
ordering, and context pointers.

Exp_dev does NOT need to re-derive the theoretical basis -- read the research note
for the theory. The anchors above are ready-to-implement as described.
