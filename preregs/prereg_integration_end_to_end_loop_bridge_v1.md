# PRE-REG: end-to-end substrate loop (perceive -> store -> reason -> BRIDGE -> generate) v1

Anchor: `integration_end_to_end_loop_bridge_v1`
Cell: `experiments/exp_integration_end_to_end_loop_bridge_v1.py`
Owner: exp_dev. Date: 2026-07-05.
Drill: `notes/research_integration_end_to_end_substrate_loop_2026-07-05.md` (3-arm decisive spec).

## Question (goal-level)
Does the substrate compose into ONE working glass-box loop? Encode an SVO fact -> store -> query
(subject, relation, ?) + reason 1-hop -> GENERATE the answer as ordered tokens; measure END-TO-END
round-trip accuracy (spoken tokens == stored fact), per-arm. Constructive (no vs-LLM).

## Reused proven components (2 of 3 hand-offs already clean; only the seam is new)
- encoder->store: CLEAN (exp_regime_switch_encoder_instore_integration_verify_v1 HARD_PASS smoke). CITED.
- store->reason: CHAIN_GRADE, SAME algebra -- real `hdlab.binding` HRR circular-conv over real BGE atoms
  (exp_deep_reasoning_hub_robustness_v1). REUSED directly for STORE + REASON.
- generate: roles-known bipolar-BSC decoder (exp_generation_decoder_roundtrip_v1, real_rolesknown_hi
  exact_ordered=1.000 MEASURED@data/exp_generation_decoder_roundtrip_v1/metrics.json). REUSED for GENERATE.

## ALGEBRA-GAP finding (refines the drill)
The reasoning primitive AS IMPLEMENTED is HRR circular-conv on real BGE fillers at N_R=1024 (NOT
bipolar-BSC as the drill framed it). The generation decoder is bipolar-BSC at N_G=8192. The seam is a
genuine CROSS-ALGEBRA + CROSS-DIMENSION gap: there is NO zero-transform hand-off; a bridge transform is
MANDATORY. This is the ONLY new component in the loop.

## Arms (5; paired trials; per-arm reported separately per Fix#28)
The BRIDGE maps the reasoning-recovered object HV (N_R=1024 HRR-BGE) to a bipolar generation filler
code (N_G=8192). All arms share the SAME store/reason/generate machinery; the bridge is the only variable.
1. `cotrained_linear` (DELIVERABLE) -- learned ridge map W (fit ONLY on a train concept pool DISJOINT from
   the test vocab; held-out). code_est = sign(r_hv @ W). The Director's "co-trained bridge."
2. `naive_symbolic` -- argmax r_hv into nearest test concept then look up its clean gen code (the drill's
   "cheapest bridge"; symbolic-identity hand-off). Answers "does the matched/symbolic bridge suffice."
3. `naive_randproj` -- fixed random projection + sign, does NOT know the target geometry (pure bolt-on
   floor / negative reference for "naive analytic bridge").
4. `stored_direct` (POSITIVE CONTROL) -- cotrained bridge on the CLEAN object BGE (no reasoning crosstalk).
   Isolates the bridge ceiling from reasoning tax (the drill's Arm C).
5. `broken_reasoning` (DISCRIMINATOR) -- cotrained bridge on r_hv from a role NOT in the trace (identity
   severed). MUST collapse to chance -- proves end-to-end accuracy is attributable to genuine reasoning.

## Metric
END-TO-END exact-ordered = spoken (subj, rel, obj) == stored (S, rel_q, obj_q). subj/rel codes are clean,
so the metric gates on the bridged object slot. Object-slot accuracy + bridge bit-agreement also reported.

## Pre-registered bands (HYPOTHESIZED@this-prereg; verified against smoke + full-V preview before dispatch)
- HARD_PASS (substrate composes now): `cotrained_linear` end2end >= 0.70 AND discriminator gap
  (best_bridge - broken) >= 0.40 AND posctrl(stored_direct) >= 0.70. (Also HARD_PASS if the symbolic/matched
  bridge clears 0.70 + gap even when the learned-vector bridge is only MIDDLE -- reported which bridge.)
- HARD_FAIL (seam is the wall): best bridge < 0.40 while posctrl >= 0.70 (degradation is the HAND-OFF, not
  any single component). Next step per drill: co-train the bridge on reasoning-RECOVERED HVs.
- MIDDLE_BAND: best bridge in [0.40, 0.70).
- Band feasibility (META_RULE_L): band_width = 0.70-0.40 = 0.30; +5pct = 0.415; HP=0.70 strictly above.

## Discriminator-fires gates (META_RULE_K; apply in all modes; smoke must satisfy)
- WIRING: posctrl(stored_direct) >= 0.70 else DISCRIMINATOR_DID_NOT_FIRE (bridge/generation broken; can't
  attribute a loop failure to the seam).
- IDENTITY: broken_reasoning <= 0.10 else IDENTITY_DISCRIMINATOR_DID_NOT_FIRE (answer leakage).
- SMOKE verified (V=256, full N): posctrl=1.000, broken=0.000, naive_randproj=0.000, arms differ.
  MEASURED@data/exp_integration_end_to_end_loop_bridge_v1/metrics.json (smoke run).

## SCHEMA-VET checklist
- `arms_differ_verified`: True (W vs R_naive matrices distinct; broken recovery != cotrained recovery).
  arms_differ_exempted: [(cotrained_linear, naive_symbolic), (cotrained_linear, stored_direct)] -- these
  legitimately share TRUTH-token output when both fully recover; the differ-check compares mechanism
  artifacts (bridge matrices) + the severed-identity discriminator, not perfect-recovery outputs.
- `final_metrics_atomicity`: tmp_replace.
- `cardinality_ok`: EXPECTED_N_UNITS = n_seeds * n_arms (5). Verdict does not sweep an axis; simple count.
- `except SystemExit: raise` BEFORE `except Exception`; no bare/BaseException (grep-gated, clean).
- `crlb_floor_computed`: chance object acc = 1/V = 1/1024 = 0.00098 THEORETICAL (broken lands here).
  `crlb_n_a` for the bridge itself (learned linear map has no closed-form noise floor; posctrl empirically
  bounds the reachable ceiling). `discriminator_reachability`: True (HP=0.70 below posctrl ceiling 1.000).
- `baseline_in_band`: broken (discriminator) collapses to chance; posctrl recovers high; deliverable in the
  measurable band by full-V preview.
- `calibration_check`: default_ok_for_this_regime (substrate primitives used directly; ridge lambda=1.0 is a
  fixed label-free regularizer; bridge trained on a DISJOINT concept pool -- no test leakage).
- `discriminator survives scale`: measured AT full N_R=1024 / N_G=8192 in ALL modes; smoke reduces V/trials/
  seeds only. Full-V=1024 single-seed PREVIEW (option C): cotrained=1.000, posctrl=1.000, broken=0.000,
  naive_randproj=0.000, gap=1.000. MEASURED (preview log).
- `progress_logging`: line_buffered_stdout + print_flush_true (per-seed print + per-seed _heartbeat.jsonl).
  Full run < 2min so per-seed cadence is adequate (60s-cadence rule targets 15min+ cells).

## §15 composition/sweep gates
- `sweep_alignment_verdict`: ALIGNED (no nominal-vs-effective sweep; single anchor regime).
- `discriminating_fraction`: n/a (no parameter sweep). The discriminator is the broken/posctrl contrast,
  which fires by construction and is verified in smoke + preview.
- `composition_edges`:
  - store->reason: SHAPE_MATCH (both HRR circular-conv, N_R=1024, real BGE; the proven CHAIN_GRADE joint).
  - reason->bridge->generate: SHAPE_MISMATCH_adapter_bridge (the NEW seam; adapter = the bridge arm; this
    cell EXISTS to measure that adapter -- the mismatch is the subject of the test, not an unhandled gap).
- `positive_control_arms`: stored_direct reproduces the bridge ceiling on clean fillers (posctrl); the
  generation machinery reproduces the roles-known decoder (exact-ordered ~1.000 at anchor, CITED prior).
- `functional_requirements`:
  - perceive+store real correlated fact -> HRR bundle of role-bound BGE fillers (store/reason primitive).
  - reason 1-hop -> HRR unbind by relation role (store/reason primitive).
  - cross-algebra hand-off -> the bridge (NEW; the arms under test).
  - generate ordered tokens -> bipolar-BSC roles-known decode (generation primitive).

## Compute architecture
Class: (b) sequential-CPU with justification. Per-trial loop has a genuine sequential dependency
(store -> reason -> bridge -> generate) and wall time is < 2min total; not a batching candidate. HRR via
FFT (N=1024) + argmax cleanups (V x N_G) are cheap. No GPU. Storage strategy: no persistent substrate
store mutation (read-only; in-memory HRR trace per trial). Real correlated fillers from a compact BGE
subset cache (data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz, ~47MB; SCP to remote --
untracked npz not auto-shipped by queue_add).

## Dispatch
- Smoke: local (V=256, full N). PASS (elapsed 8.3s). Self-test PASS (5.9s, exit 0).
- FULL: remote_cpu_queue (V=1024, 60 trials, 3 seeds). timeout 900s (>=10x margin over ~30-90s expected).
  SCP the BGE subset cache to the remote before dispatch (untracked npz). CPU-only.
