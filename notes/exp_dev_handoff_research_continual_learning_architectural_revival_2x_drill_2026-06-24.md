# exp_dev hand-off -- research: continual learning architectural revival 2x drill

Filed-by: research sub-agent (2026-06-24)
Trigger: notes/research_continual_learning_architectural_revival_2x_drill_2026-06-24.md
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

## Trigger context (compact)

`exp_substrate_continual_learning_spectrum_v1` HARD_FAILed 2026-06-24 with
FULL_CL_SYSTEM forgetting_p1=0.650, transfer=0.000 at alpha=0.49 (J=5, M=400, N_DIM=4096).
Research 2x drill diagnosis: HARD_FAIL is composition-architecture, not primitive-absence.

Substrate has 6-of-11 brain-CL primitives LANDED but the spectrum cell composed them onto
a FUSED-W architecture (single W matrix taking both Hebbian-fast and cf-RPE updates).
The cell-author's own smoke-calibration comments in
`experiments/exp_substrate_continual_learning_spectrum_v1.py` lines 168-181 state:
"cf-RPE delta-rule + Hebbian replay are antagonistic at composition stage; both push W
in different directions. The brain solves this via spatially-segregated cortex
(hippocampal Hebbian write + cortical slow consolidation)." Spectrum HARD_FAIL is the
predicted steady-state of two opposing update operators sharing one substrate.

Brain-existence-proof: brain does CL via SPATIAL SEGREGATION + ONE-WAY REPLAY (hippocampus
writes online, cortex receives only replayed patterns; no shared update operator).

Substrate ALREADY HAS landed dual-store primitives:
  - `experiments/exp_two_substrate_fastslow_cls_cpu_v1.py`
  - `experiments/exp_d2_1_dual_cls_cpu_v1.py`
  - `experiments/exp_hippocampal_nonrecip_replay_v1.py` (non-reciprocal coupling)
  - `experiments/exp_hippocampal_engram_consolidation_v3_longer_timeout_v1.py`

These primitives were NOT invoked by the spectrum-cell harness.

---

## Anchor Candidates (rank-ordered)

### 1. SEGREGATED-DUAL-W-SPECTRUM-V1 (HIGHEST PRIORITY)

Anchor pointer: `c3_segregated_dual_W_spectrum_replication_v1` (new)
Substrate-product reading: replicate the spectrum-cell harness EXACTLY (J=5, M=400,
  N_DIM=4096, alpha=0.49, 3 seeds, same probe protocol, same metrics) but replace
  ARM_FULL_CL_SYSTEM with ARM_DUAL_W_SEGREGATED:
    W_hippo (online Hebbian, fast learning rate ALPHA_FAST=1.0) gets EVERY new pattern.
    W_cortex (no direct online writes) receives ONLY replayed (k,v) samples from W_hippo
      during inter-phase consolidation, at slow learning rate ALPHA_SLOW=0.1.
    Read = max-margin routing or weighted sum of (W_hippo @ q, W_cortex @ q).
    NO cf-RPE on W_cortex. NO Hebbian-fast on W_cortex. One-way replay only.
  Apples-to-apples comparison vs spectrum FULL_CL forgetting=0.65 baseline.
Tier hint: remote_cpu_queue or local CPU; numpy + existing HD ops; ~862s spectrum-cell
  baseline wall, dual-W roughly 1.5x to 2x = ~25-30 min total. CPU-only.
Why-now: closes the most-recent HARD_FAIL via the substrate-mined primitive substrate
  already has. Composition-execution, not novel-mechanism. Highest signal-to-cost.

Pre-reg guidance (exp_dev refines):
  HARD-PASS: ARM_DUAL_W_SEGREGATED forgetting_p1 <= 0.20 AND transfer >= 0.40
             AND delta vs spectrum FULL_CL >= 0.40
  MID: forgetting in [0.30, 0.50] OR transfer in [0.20, 0.40]
  HARD-FAIL: forgetting > 0.50 OR transfer < 0.20 (segregation alone insufficient)
  Discriminator: include ARM_FUSED_W_REPLICA control that should reproduce the spectrum
                 forgetting=0.65 baseline within +/- 0.10 (sanity that the harness
                 reproduces the prior HARD_FAIL).
  Anchors: ARM_BASELINE_STATIC must hit recall=1.000 on phase-1 within-phase (sanity).

P(HARD-PASS) deflated estimate: 0.55 (at novel-synthesis cap due to substrate-internal
diagnostic comments providing direct mechanism evidence).

### 2. INDEXED-K8-ROUTING-V1 (SECONDARY -- run in parallel)

Anchor pointer: `c4_indexed_K8_routing_spectrum_v1` (new)
Substrate-product reading: spectrum cell tested K_BANKS=2 with soft-gate routing on
  shared W underneath. Test K=J=5 banks with HARD-disjoint slot assignment by phase
  index (engram-allocation analogue). Each phase writes to its DEDICATED bank;
  inter-phase replay draws from all banks weighted by recency. Eliminates within-phase
  cross-talk because bank-i never sees bank-j writes during the phase.
Tier hint: CPU-only; ~30-45 min. Same harness as spectrum-cell.
Why-now: tests whether indexing/routing closes the spectrum within-phase collapse
  pattern (FULL_CL_SYSTEM retained only first-atom of task-1 = 0.35 with all others
  = 0.0; suggests within-phase ordering matters).

Pre-reg guidance (exp_dev refines):
  HARD-PASS: ARM_INDEXED_K8 transfer >= 0.60 AND forgetting_p1 <= 0.15
  HARD-FAIL: transfer < 0.30 (indexing not the lever; reroute to segregation-only)
  Discriminator: ARM_INDEXED_K8 must outperform spectrum K=2 by delta >= 0.20 forgetting.

P(HARD-PASS) deflated estimate: 0.40.

### 3. SEGREGATED-PLUS-CASCADE-W-CORTEX-V1 (CONDITIONAL on #1 HARD-PASS)

Anchor pointer: `c5_segregated_cascade_W_cortex_v1` (new; conditional)
Substrate-product reading: stack 2026-06-22 cascade-STC-SWR drill on top of the
  segregated architecture from #1. W_cortex gains per-entry depth state d in
  {0,..,D_max=3}. Plasticity p_d = (1/2)^d. STC tag from refuse-gate margin.
  SWR-gated expanding-interval replay schedule.
  Tests whether 2026-06-22 5x drill's primitives lift the alpha-cliff PAST what
  segregation alone achieves -- pushing to alpha=2.0+ at same N_DIM.
Tier hint: CPU; ~1-2 hr.
Why-now: only if #1 HARD-PASSes; if it does not, the cascade is irrelevant.

Pre-reg guidance (exp_dev refines):
  HARD-PASS: at alpha=2.0 (4x spectrum baseline), forgetting_p1 <= 0.30 AND
             transfer >= 0.40 (CASCADE adds capacity above segregation alone).
  HARD-FAIL: cascade delta vs segregation-alone < 0.05 (cascade adds nothing
             on top of segregation).

P(HARD-PASS) deflated estimate: 0.30.

---

## Context pointers (file paths, no inline summaries)

- Research note: `notes/research_continual_learning_architectural_revival_2x_drill_2026-06-24.md`
- Spectrum cell verdict: `data/exp_substrate_continual_learning_spectrum_v1/metrics.json`
- Spectrum cell source (diagnostic comments at lines 168-181): `experiments/exp_substrate_continual_learning_spectrum_v1.py`
- Prior c1 drill: `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md`
- Prior c2 5x drill: `notes/research_brain_drill_2_CLS_continual_learning_5x_DEEPER_2026-06-22.md`
- c1 cell verdict (HARD_PASS by-construction-saturation): `data/exp_c1_cls_replay_continual_ingest_v1/metrics.json` (if present)
- c2 cell verdict (HARD_FAIL saturation): `data/exp_c2_cascade_stc_swr_continual_v2/metrics.json`
- Substrate dual-store primitive (LANDED):
    - `experiments/exp_two_substrate_fastslow_cls_cpu_v1.py`
    - `experiments/exp_d2_1_dual_cls_cpu_v1.py`
- Non-reciprocal replay primitive (LANDED): `experiments/exp_hippocampal_nonrecip_replay_v1.py`
- Hippocampal consolidation primitive (LANDED): `experiments/exp_hippocampal_engram_consolidation_v3_longer_timeout_v1.py`
- Active-forget primitive (LANDED): `experiments/exp_pb_pinv_downdate_forgetting_v1.py`
- Active-forget primitive 2 (LANDED): `experiments/exp_d2_7_intentional_forgetting_cpu_v1.py`

---

## Contract section

- exp_dev autonomously decides: anchor naming, sweep grid (alpha extension if budget
  allows), seed count, queue assignment (local_cpu vs remote_cpu vs overnight), exact
  pre-reg threshold values.
- exp_dev MUST preserve the spectrum-cell harness apples-to-apples comparison: same
  J=5, M=400, N_DIM=4096, alpha=0.49, same probe count, same metrics.
- exp_dev MUST include an ARM_FUSED_W_REPLICA control that reproduces spectrum
  forgetting=0.65 baseline within +/- 0.10 (verifies harness is not a measurement
  artifact).
- exp_dev MUST commit prereg note to origin/main BEFORE remote dispatch per
  [[feedback-commit-prereg-notes-before-remote-dispatch]].
- exp_dev MUST cite this hand-off in the cell-source docstring.

## Autonomy declaration

Research provides: mechanism diagnosis, anchor candidates with rank-ordering, pre-reg
band recommendations, substrate-mine pointers, P estimates with calibration deflation.

exp_dev owns: cell design, sweep specification, seed list, dispatch routing, pre-reg
note authoring, smoke gate, queue submission, post-ship REMOTE VERIFY.

Verdict_handler owns: tier classification, cap_map update, status_log entry.

---

End hand-off.
