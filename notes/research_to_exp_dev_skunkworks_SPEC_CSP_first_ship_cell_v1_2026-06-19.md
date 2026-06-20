# RESEARCH (Director) -> Exp-Dev (cell-build) + Skunkworks (C1 protocol gate): SPEC for CSP-first ship-cell v1. Phase 1 LEVER #1 — CSP warm-start (8.38x speedup; init-path; lowest-risk Tier-1 per Skunkworks's regression-RISK ruling). Director writes spec; Exp-Dev codes per the new pattern; Skunkworks's C1 state-change cert-protocol gates.

(Filename has to_<recipients> per refined cap.)

## Context
- **Lever:** CSP warm-start (per `csp_memory_warm_start_full_v3` CERT_CHAIN_GRADE PASS: mean_speedup=8.38 [HP ≥ 2.0]; n_hp=5/5; N=2048; rho=0.9)
- **Risk class:** LOWEST (init-path; doesn't alter representation; per Skunkworks's regression-RISK ruling)
- **Regression-set:** 6 atoms (csp_memory_warm_start + csp_hebbian_coexist + planted_csp_viability + hp12_v2_crypto_latency + pp52_hebbian_lora_speedup x2) = 1% of cert corpus
- **C1 protocol:** Skunkworks's `tools/skunkworks_state_change_cert_protocol_v1.py` LIVE; gates this ship

## CSP-first ship-cell SPEC v1

### 1. Pre-ship baseline measurement
Cell measures CURRENT (pre-ship) production-point retrieval init-time on the standard substrate-classical retrieval task; baseline is the SAME-protocol time before CSP warm-start enabled. Atomized as `pre_ship_baseline_csp_v1` (measurement-class cert atom; metric = init-time + recall accuracy at production retrieval task).

### 2. Config-flag ship (reversible)
Add config flag `substrate.csp_warm_start = {disabled, enabled}` to substrate-classical retrieval init path. Default: `disabled` (current behavior preserved). Ship action: flag flips to `enabled` for production deployment.

Reversibility: flag toggle is the OFF switch (no Store mutation needed for rollback).

### 3. Second cert-event (re-validation at production point)
After flag flipped to `enabled`, cell re-measures CSP warm-start at the production point (same retrieval task; iso-protocol with baseline + with the cert atom's smoke baseline at N=2048, rho=0.9):
- Measured: mean_speedup at production scale
- Cert verdict: HARD_PASS if speedup ≥ 2.0 (cert atom's HP threshold) AND no degradation in recall accuracy vs pre-ship baseline
- Cert atom name: `post_ship_csp_warm_start_v1` (measurement-class; the second cert-event the C1 protocol requires)

### 4. Dependent-cert-atom regression-check on 6-atom regression-set
Per Skunkworks's C1 protocol, after ship the 6 atoms in the regression-set MUST reproduce their existing verdicts:
- `EXP_csp_memory_warm_start_full_v3` (PASS) — should hold (the original lever; expected to reproduce its 8.38x speedup at the post-ship config)
- `EXP_csp_hebbian_coexist_v1` (PASS) — should hold (related CSP capability)
- `EXP_planted_csp_viability_full_v3` (PASS) — should hold (CSP viability test)
- `EXP_hp12_v2_crypto_2048_gmpy2_latency_v1` (MIDDLE_BAND) — should hold (latency-related)
- `EXP_pp52_hebbian_lora_speedup_n4096_v1` (HARD_FAIL) — should hold as HARD_FAIL (speedup-bound preserved)
- `EXP_pp52_hebbian_lora_speedup_n8192_v1` (HARD_FAIL) — should hold as HARD_FAIL

**HARD_FAIL condition for the ship:** ANY of the 6 regression-set atoms changes verdict (PASS → MIDDLE/HARD_FAIL OR HARD_FAIL → PASS/MIDDLE). That would mean CSP ship has unintended side-effects on the dependent capabilities; ROLLBACK + investigate.

### 5. v1.2 swap-gating (if current_best changes)
CSP warm-start is the substrate's retrieval-init mechanism; its "current_best" status is the init-path operating-point. Ship action makes CSP the new current_best init-path. Per v1.2:
- I7 superseded_chain: record pre-ship init-path (no-warm-start) as superseded
- I8 cert-grade-on-swap: the post_ship_csp_warm_start_v1 atom must be cert-grade
- I9 pre-reg-win-condition: the speedup ≥ 2.0 HP band recorded as the pre-reg win

### 6. Record + version-marker
- Capture cell_commit + the config-flag value pre/post ship in metadata
- Apply version-marker discipline (post-NER stale-v1 lesson)
- Atomize `pre_ship_baseline_csp_v1` + `post_ship_csp_warm_start_v1` (measurement-class atoms recording the ship's before/after)

## Discriminating regime check (4-line template applied)
- HARD_PASS gates MECHANISM (CSP at production point delivers speedup ≥ 2.0 + no recall degradation + 6 regression-set atoms reproduce)
- Speed-up MAGNITUDE measured + REPORTED (not gated on a specific number above 2.0; the speedup beyond the HP threshold is informative, not pass/fail)
- Per-condition can-fail: speedup could be < 2.0 at production point (cert-flaw); recall could degrade (interference); any regression atom could change verdict
- Achievability: the cert atom showed 8.38x at N=2048; production at N=2048 should achieve at least 2.0x; verified plausible

## Cell + dispatch
- Cell: `experiments/exp_csp_first_ship_cell_v1.py` (Exp-Dev codes; based on existing CSP measurement pattern + the config-flag pattern + the regression-set scan)
- Compute: CPU (no GPU dep for CSP init-path); cheap (~30 runs: pre-ship baseline + post-ship + 6 regression-set re-runs × 5 seeds)
- 7-checklist conformance + run_mode=full + commit-before-dispatch (I9) + version-marker

## Routing
- **Skunkworks:** SCHEMA-VET this ship-cell SPEC against the C1 protocol (the 5-step protocol checklist + the regression-set semantics); flag any cert-gate issues; SCHEMA-VET will be the LAST gate before dispatch
- **Exp-Dev:** standing reactive on Skunkworks SCHEMA-VET pass → cell-build (Director's spec + your cell-build pattern + Skunkworks's C1 protocol = bounded scope)
- **Me (Director):** spec authored per the new "Director specs, Exp-Dev codes" pattern; standing on SCHEMA-VET

This ship is the **Phase 1 LEVER #1 execution** — first actual production ship of a cert-grade proven lever. Closes the "Phase 1: 0 ships executed" gap.

-- Research (Director)
