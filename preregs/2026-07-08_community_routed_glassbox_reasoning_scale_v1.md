# Pre-reg: community_routed_glassbox_reasoning_scale_v1

Date: 2026-07-08. Author: exp_dev (Opus 4.8 1M, agent-spawn). LOCAL smoke + hand-off for FULL.

Design source (brain-first drill, read + verified off-disk this cycle):
notes/research_community_routed_glassbox_reasoning_scale_invariant_brain_first_2026-07-08.md

Composes (both certified THIS session):
- hdlab/glass_box_loop.py -- the CHAIN_GRADE glass-box retrieve->gate->audit->requery loop
  (Merkle-chained per-hop audit; causal hand-edit; tamper-detect; deterministic replay).
- experiments/exp_community_bounded_retrieval_scale_invariance_v1.py -- MM-tier community-bounded
  two-stage route-then-restrict store (route to community via ~sqrt(V) gist codebook, resolve within).
- experiments/exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1.py -- the 80x-scale certified loop.

## WHAT / WHY (the innovation)
Swap the glass-box loop's FLAT per-hop store for the community-routed store, so multi-hop reasoning
over ingested knowledge scales past a flat-store crosstalk wall by routing EACH hop to its relevant
community first, then reasoning within that bounded neighborhood. MANDATORY mechanical fix (from the
drill): routing becomes its OWN logged, Merkle-chained audit step -- else it is a hidden un-editable
pre-filter and breaks the glass-box causal-editability guarantee.

## THE TEST -- arms
Store-capacity-in-chain (V-sweep, WITHIN-community depth-3 chains):
- ARM_A_FLAT (must-collapse control): each hop's retrieve/cleanup runs against the WHOLE per-hop store
  (global bundle over ALL V within-edges; argmax over all V). Reproduces the M<N/(2 ln V) crosstalk
  wall INSIDE the chain. Vacuous-smoke guard: if it does NOT collapse at V_max, the harness is not
  exercising the crosstalk regime -> void.
- ARM_B_ROUTED_WITHIN (treatment): route each hop to its community (coarse gist argmax over ~sqrt(V)
  pointers), unbind + cleanup within the community's ~sqrt(V) members. Routing logged as its own
  Merkle-chained step. Should stay FLAT vs total V.

Routing-error compounding (fixed V_C, DEPTH-sweep, CROSS-community chains + routing perturbation):
- ARM_C_FRESH (real mechanism -- independent coarse channel): per-hop routing cue is a FRESH coarse
  gist pointer (grid-cell/entorhinal reset), noise independent each hop. Governing principle
  (research_deep_chain_reasoning_bounded_compounding_error 2026-07-08): a decision drawn from an
  informationally-INDEPENDENT source does not compound. Predicted BOUNDED (flat conditional hazard).
- ARM_C_COMPOUND (positive control -- shared-noise channel): per-hop routing cue derived from the SAME
  accumulating fine residual (noise variance ~ hop index). Predicted RISING conditional hazard. This
  arm's job is the measurement-sensitivity guard: if it does NOT rise, the hazard-slope metric cannot
  detect compounding -> FRESH-flat is meaningless -> void (raise noise/depth).

Read the arm-C result JOINTLY with the in-flight chain-drift GPU FULL (same compounding-error class).

## Functional Requirements (Gate E)
- FR1 route a query hop to its community: community-gist argmax over ~sqrt(V) pointers (v1 primitive).
- FR2 resolve the answer within the routed community: unbind + argmax cleanup within community members
  (v1 peel/SIC / single-cue top1 primitive).
- FR3 chain hops: retrieved value becomes the next hop key (glass_box_loop WM-rebind / SCALE chain).
- FR4 audit EVERY step incl. routing: Merkle-chain + deterministic replay + tamper-detect
  (exp_reasoning_chain_replay_v1 primitives, transcribed in glass_box_loop.py).
- FR5 causal editability of the routing decision: hand-edit the logged routing community -> downstream
  recompute flips AND tamper flag fires (the deep-prize glass-box property, extended to routing).

## Positive-control arms (Gate D)
- ARM_ORACLE_ROUTE (route to TRUE community, no noise) -> within-community fine retrieval ceiling at
  each V; reproduces v1 TREATMENT clean regime (cited_prior: v1 treat_fid 0.996-1.000 at N=8192).
  tolerance 0.10; if oracle < 0.85 at any V the fine-retrieval machinery is broken -> downstream suspect.
- ARM_A_FLAT reproduces v1 CONTROL collapse (cited_prior: v1 ctrl_fid 0.742@V580 -> ~0.0@V>=29000).
  Regime-extension audit: v1 tested SINGLE retrieval; this cell tests it inside a depth-3 CHAIN
  (SHAPE_DRIFT single-shot->chained; documented risk: chain multiplies per-hop error, so ARM_A may
  collapse EARLIER in V than v1's single-shot -- acceptable, still the must-collapse control).

## composition_edges (Gate C)
- community_gist_router -> within_community_cleanup: SHAPE_MATCH (router emits community id; cleanup
  restricts codebook to that community's member rows).
- within_community_cleanup -> next_hop_key: SHAPE_MATCH (retrieved id is the next hop's cue id; BSC
  bipolar self-inverse rebind, identical to glass_box_loop WM active-slot rebind).
- routing_decision -> merkle_audit_step: SHAPE_MATCH (routing id serialized as a step string, same
  hash-chain discipline as the existing hop steps).

## effective vs nominal params (Gate A)
swept_params: V (store-capacity arm), D (depth, compounding arm).
effective_params_per_primitive:
- flat_cleanup: effective candidate count = V (grows with sweep) -> ALIGNED (collapse is the point).
- routed_cleanup: effective candidate count = comm_size ~ sqrt(V) (grows only as sqrt) -> ALIGNED
  (bounded is the point; effective-V decoupled from total-V, the v1 result).
- gist_router: effective codebook = n_comm ~ sqrt(V) -> ALIGNED.
- compounding hazard: effective stressor = per-hop routing perturbation held FIXED across depth; the
  swept axis is depth D; ALIGNED (slope vs depth at fixed per-hop noise is the compounding measure).
sweep_alignment_verdict: ALIGNED

## bracket_includes_discriminating_band (Gate B)
- store arm: FLAT predicted 0.74@V580 -> ~0.0@V_max (spans full band); ROUTED predicted ~1.0 flat.
  Discriminating fraction of the JOINT (A collapses while B flat) is the design; >=0.30 by construction.
- compounding arm: per-hop routing hazard tuned into [0.05, 0.60] at hop 1 (STRESS band) so the
  slope-vs-depth is measurable (not saturated, not floor). Calibrated in smoke; params iterated if
  hop-1 hazard lands outside band OR COMPOUND fails to rise.

## Compute architecture
(c) mixed with justification. The chain is genuinely SEQUENTIAL across hops (hop k+1 key = hop k value);
per-trial Merkle/tamper/causal audit is scalar CPU. The codebook cleanup matvecs (the V-scaling cost)
are STAGE-BATCHED into single BLAS gemms across all chains (E @ Probes.T). numpy CPU only (the certified
base is numpy-only; no torch/GPU rewrite for no material win). Peak RAM ~1GB (V_max=30000 x N=8192 f32).
Storage strategy: MIXED -- each per-hop store is a single-hop BUNDLED associative memory (exemption (a):
single-hop read within a hop); cross-hop composition is SHARDED via key-rebind (retrieved id carried
forward, never fused into one global chain bundle). Matches glass_box_loop.py's declared mixed storage.

## progress_logging
print_flush_true (line-buffered stdout + flush=True per (seed,V) and per compounding-depth line).
FULL timeout_s 5400 (matrix_sweep floor). Each seed checkpoints (write_partial); kill/resume loses <=1 seed.

## Bands (strict per META_RULE_L)
Store-capacity (PRED-B), chain-success (all-D-hops-correct) V_min->V_max:
- FLAT_COLLAPSE_RD_MIN = 0.30    (ARM_A relative degradation >= this; discriminator/vacuous guard)
- ROUTED_FLAT_RD_MAX   = 0.10    (ARM_B relative degradation <= this)
- ROUTED_ABS_MIN       = 0.70    (ARM_B absolute chain-success at V_max)
- ROUTE_ACC_MIN        = 0.90    (ARM_B coarse-route accuracy at V_max)
- ORACLE_ROUTE_MIN     = 0.85    (ARM_ORACLE_ROUTE within-community ceiling at every V; Gate D)
- MODULARITY_MIN       = 0.30    (real community structure; generator guard)
Glass-box (PRED-A), at EVERY V:
- REPLAY == 1.0, MERKLE_VERIFY == 1.0, TAMPER_DETECT == 1.0
- ROUTING_CAUSAL_FLIP_MIN = 0.80   (hand-edit logged routing community flips downstream recompute)
- ROUTING_CAUSAL_TAMPER == 1.0     (edited routing step breaks the committed Merkle root)
Compounding (PRED-C), conditional routing hazard slope vs depth at V_C:
- FRESH_SLOPE_MAX    = 0.02   (ARM_C_FRESH slope <= this -> BOUNDED, HARD-PASS)
- COMPOUND_SLOPE_MIN = 0.04   (ARM_C_COMPOUND slope >= this -> measurement fires; vacuous guard)
- STRESS_H1_MIN = 0.05, STRESS_H1_MAX = 0.60  (hop-1 hazard in-band: injection active, not saturated)

## Verdict logic
- HARD_FAIL (audit) if any V has REPLAY<1 or MERKLE_VERIFY<1 or TAMPER_DETECT<1 or routing_causal_flip
  <0.80 or routing_causal_tamper<1.
- HARD_FAIL (generator) if modularity_min < 0.30.
- HARD_FAIL_CARDINALITY if observed units != expected.
- HARD_FAIL_DISCRIMINATOR_INERT (void) if ARM_A does NOT collapse (ctrl_rd < 0.30) OR ARM_C_COMPOUND
  does NOT rise (compound_slope < 0.04) OR hop-1 hazard out of [0.05,0.60].
- HARD_FAIL_ROUTING_COMPOUNDS (honest negative; couples Barrier #2) if ARM_C_FRESH slope > FRESH_SLOPE_MAX
  by a clear margin (fresh_slope >= COMPOUND_SLOPE_MIN) -- routing inherits the compounding problem;
  composition NOT trustworthy past a couple hops without an independent-channel fix.
- HARD_PASS if PRED-A holds at every V AND ARM_A collapse>=0.30 AND ARM_B flat<=0.10 AND ARM_B abs>=0.70
  AND route>=0.90 AND oracle>=0.85 AND modularity>=0.30 AND FRESH_slope<=0.02 AND COMPOUND_slope>=0.04.
- MIDDLE_BAND otherwise (e.g. ARM_B degrades slower than A but not flat; FRESH slope in (0.02,0.04)).

## Schema-vet template fields
- arms_differ_verified: true (SHA256 of per-arm chain-answer arrays; A/B/ORACLE diverge; FRESH/COMPOUND
  routing-decision arrays diverge)
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace) + per-seed partial checkpoint
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: accuracy-gap + hazard-slope discriminators; reachability by bundle-SNR feasibility
  (sqrt(N/M): flat SNR 3.76@V580 -> 0.52@V30000 collapse; routed SNR ~ sqrt(N/comm_size) stays >2).
- baseline_in_band: ARM_A spans 0.74->~0.0 (not saturated); ARM_C hop-1 hazard tuned into (0.05,0.60).
- discriminator survives scale: smoke runs the SAME V grid + N + store density as FULL (seed count only
  differs). ARM_A asserted to collapse at V_max; ARM_C_COMPOUND asserted to rise; both in smoke.
- HP_SCOPE: store gates (collapse/flat/route/oracle) apply to {ARM_A, ARM_B, ARM_ORACLE_ROUTE};
  compounding gates (slope) apply to {ARM_C_FRESH, ARM_C_COMPOUND}; audit gates apply to the ROUTED loop.
- cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(V_GRID) (vsweep) + len(SEEDS) (compound), verdict
  counts completed units.
- per-unit failure-class instrumentation: no bare except; per-seed crash diag.
- calibration_check: adaptive_with_discriminator_gate -- ROUTE_NOISE_STORE / ROUTE_NOISE_COMPOUND /
  P_INJECT chosen a-priori; smoke verifies discriminator still fires (A collapses, COMPOUND rises,
  hop-1 hazard in band); if not, params iterated (logged), not tuned-for-PASS.
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- cell_chunked: false (single cell, per-seed checkpoint; seeds independent, cheap).

## Numbers (tagged)
- v1 CONTROL fid 0.742@V580 -> 0.039@V2900 -> 0.000@V>=29000  CITED@experiments/exp_community_bounded_retrieval_scale_invariance_v1.py:44-49
- v1 TREATMENT fid 1.000 flat, route_acc 1.000  CITED@same
- bundle top1 reliable while M < N/(2 ln V)  THEORETICAL@ bundle-crosstalk gaussian max-order-statistic
- glass_box_loop 4 certified properties (discriminator/causal-edit/tamper/replay)  CITED@hdlab/glass_box_loop.py:50-56
- compounding governing principle (same-noise-source decisions compound; independent don't)
  CITED@notes/research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md
- all in-cell target numbers are HYPOTHESIZED@this prereg until smoke re-measures them.
