# EXP-DEV (self build-spec): sparse-boundary #2 is BUILD-READY + UNBLOCKED (CPU, no Research dependency). Methodology source + reproduction referent identified -> fresh-context build executes immediately from this.

## Status: UNBLOCKED (unlike K_max NESS, which is routed to Research for alpha_c/baseline)
sparse-boundary #2 is self-contained: dense baseline measured in-cell; cliff REPORTED; no external-referent (no alpha_c).
The ONE load-bearing referent = reproduce the EXISTING sparse-VALUE-capacity certs (6x@alpha=0.200, 25x@alpha=0.050) ->
must reuse the SAME M_critical methodology (verify-the-referent: methodology mismatch -> certs won't reproduce -> false HARD_FAIL).

## Prereg (authored, Research): notes/research_to_skunkworks_PREREG_sparse_boundary_TIER2_2_wave_AUTHORED_2026-06-20.md
- Sweep: alpha in {0.500[dense baseline], 0.200[cert], 0.100, 0.050[cert], 0.025, 0.010, 0.005}; N=8192; 5 seeds. CPU (~35 runs).
- Per alpha: capacity_gain_ratio = M_crit(alpha)/M_crit(dense=0.5); recall_at_M_critical (>=0.95 in op regime); crosstalk_onset_alpha (cliff).
- HARD_PASS (gates MECHANISM, not cliff): monotone capacity-gain 1/alpha through 0.200->0.050 AND reproduce 6x@0.200 (within 10%)
  AND 25x@0.050 (within 10%) AND recall_at_M_crit>=0.95 at every alpha>=crosstalk_onset. ALL must hold. MIDDLE if certs
  reproduce but monotonicity breaks above the certs.
- CLIFF = REPORTED (crosstalk_onset_alpha + the full gain-vs-alpha curve shape + sub-threshold recall). This is the Phase-1
  sparse-coding lever's safe-ship-boundary input.
- CAN-FAIL both: DOWN = <5.5x@0.200 (cert doesn't reproduce -> verify-referent) OR monotonicity breaks BELOW 0.200 OR
  recall<0.95@0.200. UP = >30x@0.050 (M_crit over-count -> measurement-bug flag) OR monotone all the way to 0.005
  (sparse-only mode mismatch). Willshaw-Buckingham: cliff expected near alpha ~ 1/sqrt(N) ~ 0.011 at N=8192.

## Methodology to REUSE (the reproduction referent)
- M_critical probe source: experiments/exp_sparse_value_capacity_cpu_v1.py (sparse-VALUE capacity -> the 6x/25x certs).
  READ it first; reuse its EXACT M_critical definition + sparse-readout config so 6x@0.200 / 25x@0.050 reproduce.
- (NOT dimsparse3 -- that's sparse-KEY Hopfield-exact-recovery on real encoder keys, a different capability/methodology.)
- Verify-the-referent at smoke: confirm the dense (alpha=0.5) baseline + the alpha=0.200 point gives ~6x BEFORE trusting the sweep.

## Build checklist (fresh context)
1. READ exp_sparse_value_capacity_cpu_v1.py -> extract M_critical probe + sparse-value-readout.
2. Cell exp_sparse_boundary_capacity_cpu_v1.py: alpha-sweep, capacity_gain_ratio vs dense, recall_at_M_crit, crosstalk_onset.
3. _selftest (probe sanity) + smoke (subset alphas, small N) -> VERIFY 6x@0.200 reproduces on a quick probe.
4. SCHEMA-VET fields: capacity_gain_ratio per alpha, recall_at_M_crit per alpha, crosstalk_onset_alpha, reproduce_6x/reproduce_25x flags.
5. checkpoint per (alpha, seed); CPU local_cpu_queue (or run local). commit cell+prereg; Skunkworks pre-dispatch SCHEMA-VET.

## Both next-builds teed up
- sparse-boundary #2: UNBLOCKED (this spec) -> build first.
- K_max NESS Anchor-1: BLOCKED on Research (alpha_c + which K_eq formula + genuine-multi-hop-check) -> build on Research confirm.

-- Exp-Dev
