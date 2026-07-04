# Pre-registration: exp_cortex_2_phase_2_apply_probe_v1_s7

**Filed:** 2026-07-04 (hdi_exp_dev sub-agent, task `aedb533a91fba532c`)
**Anchor:** `cortex_2_phase_2_apply_probe_v1_s7`
**Cell:** `experiments/exp_cortex_2_phase_2_apply_probe_v1_core.py`
**Wrapper:** `experiments/exp_cortex_2_phase_2_apply_probe_v1_s7.py`
**Parent atom:** math atom #54 `MM_TENTATIVE_ADVISORY` (Phase 1 v1.1 warmup-fix
landed HARD_PASS 2026-07-03)
**Research drill:** `notes/research_drill_cortex_2_phase_2_advisory_to_enforcement_architecture_2026-07-04.md`
**Meta parent:** meta atom #48 (ADD_AXIS discipline; empirical grounding required)

---

## Strategic context

Phase 1 (advisory-only, `applied=False`) landed math atom #54
MM_TENTATIVE_ADVISORY 2026-07-03. Retrieval discriminator
`match_and_honored_over_all = 0.80` MEASURED@`d:/AI/hd-instrument/data/exp_cortex2_atom_consultation_smoke_v1_1_warmup_fix_s7_smoke/metrics.json:match_and_honored_over_all`
(Phase 1 v1.1). Wall_p95 <= 5ms (v1.1 warmup fix). Zero silent contradictions.

Phase 2 = transition from advisory to enforcement WITH anti-silent-enforcement
discipline. Load-bearing design elements (per drill sections 3-4):

1. **Two-part nonce discriminator** (mechanical read-proof): every enforce()
   call writes a fresh 16-byte hex nonce alongside the recommendation value.
   Downstream reads via `read_and_ack_nonce()` and emits the nonce ack;
   audit compares written vs acked to prove mechanical read.
2. **Null-arm A/B discriminator** (distributional effect-proof): interleaved
   null-arm calls where enforce() writes the PRE-value (identity) but with
   fresh nonce. Downstream KS test on real-arm vs null-arm output
   distributions detects distributional effect.
3. **Per-atom SHADOW/WARN/LIVE flag** (OPA/Gatekeeper pattern):
   - SHADOW: no write; log-only
   - WARN: write value + nonce + audit log
   - LIVE: write + refractoriness enforcement (post-first-probe)
4. First probe promotes the 5 curated CG_META/FIX28 atoms to WARN so
   measurements can fire. LIVE promotion is post-HARD_PASS Skunkworks
   decision, NOT this probe.

## Framing

- **MM_TENTATIVE_ADVISORY_APPLIED** at SMOKE (per drill section 7).
- **arc-continuation** of Phase 1 v1.1 (not arc-closure).
- Prior-work concept-query 2026-07-04 for "phase 2 apply nonce discriminator
  null arm enforcement cortex": NONE at cosine > 0.30. Novel synthesis.

## Source signature (per USER-locked MM_STANDARD 2026-07-03)

**Phase 2 apply-probe v1, cortex-2 arc, 5 cases x 100 real-arm + 100
null-arm = 1000 consultations at FULL (50 at SMOKE), WARN mode for 5
curated atoms (SHADOW default for uncurated), atom store 2026-07-04
106-atom corpus (curated subset of 7 covering 5 ground-truth cases),
5 op-classes, char-trigram encoder N=1024, downstream stub
N(mu(value), sigma=1) scalar draw.**

## Delta from Phase 1 v1.1

- ADD: `AtomMatch.nonce` (16-byte hex; fresh per enforce() call)
- ADD: `ConsultationResult.applied_flag / null_arm / nonce_written /
  pre_value / post_value / enforcement_wrote` (Phase 1 defaults preserved)
- ADD: `_AtomRecord.enforcement_mode` (default SHADOW; per-atom promotion)
- ADD: `AtomConsultant.enforce()` -- Phase 2 apply wrapper around consult()
- ADD: `read_and_ack_nonce()` -- downstream instrumentation contract
- ADD: `EnforcementDecision` + `EnforcementDecisionLogger` (JSONL append,
  atomic tmp+rename)
- ADD: 6 Phase 2 selftests (SHADOW no-write, WARN write+nonce, null-arm
  identity+nonce, nonce uniqueness, read_and_ack roundtrip, logger flush)
- IDENTICAL: curated atom corpus, 5 op-classes, 5 ground-truth cases
- Phase 1 `_selftest_applied_always_false_v1` PRESERVED (consult() still
  returns applied=False; enforce() is the Phase 2 code path)

## PRE-COMMITTED predictions (locked BEFORE run)

- `match_and_honored_and_effect_rate` in [0.60, 0.80] (per task spec
  anti-drift). Expected ~0.80 by construction: 4/5 cases matched-and-honored
  from Phase 1 v1 corpus, all 4 should also KS-detect at n=100 real vs
  n=100 null with sigma=1 and mean gap >=2.0.
- `nonce_consumption_rate = 1.0 +/- 0.0` (by construction if downstream
  ack path correct; every WARN-mode enforce writes a nonce, downstream
  reads it back immediately).
- `n_cases_ks_pass >= 3/5` at FULL (real-arm value distribution mean
  diverges from null-arm value distribution mean by >=2.0 sigma).
- `n_silent_contradictions == 0` (bucket-ii flagged per_call).
- FAIL branches:
  - `match_and_honored_and_effect < 0.20` -> decorative enforcement; revert
    to advisory-only + file negative-result 2x drill.
  - `nonce_consumption < 0.50` -> instrumentation broken; ack path broken
    or bypassed. Diagnostic cell to isolate cause.

## Envelope + PRE-COMMITTED bands

### HARD_PASS

- `match_and_honored_and_effect_rate >= 0.60` AND
- `nonce_consumption_rate >= 0.90` AND
- `n_cases_ks_pass >= 3` (KS p<0.01 on real-arm vs null-arm per case) AND
- `n_silent_contradictions == 0`

### MIDDLE_BAND

- `match_and_honored_and_effect_rate in [0.20, 0.60)` OR other conditions
  in the HP conjunction fail without triggering HARD_FAIL.

### HARD_FAIL_DECORATIVE

- `match_and_honored_and_effect_rate < 0.20`

### HARD_FAIL_NONCE_INSTRUMENTATION_BROKEN

- `nonce_consumption_rate < 0.50`

### HARD_FAIL_CARDINALITY_BREACH (META_RULE_H)

- `len(per_call) < 2 * 5 * n_per_arm` (real + null per case).

## Post-SMOKE outcomes

- **HARD_PASS:** candidate atom
  `EMPIRICAL_CORTEX_2_PHASE_2_APPLY_ADVISORY_SHADOW_MODE_v1_MM_TENTATIVE_ADVISORY_APPLIED`
  filed by Skunkworks landed-VET; cortex-2 arc advances to Phase 2 (WARN
  mode promoted for 5 curated atoms; LIVE promotion pending Skunkworks
  ring-based rollout per drill section 4).
- **MIDDLE_BAND:** deeper analysis needed; likely nonce-implementation or
  null-arm-design fix; iterate.
- **HARD_FAIL:** honest-negative atom filed; escalate to research 2x drill
  (mechanism-mismatch or architecture-mismatch).

## Compute architecture (mandatory field)

- **Class:** (b) sequential-CPU with justification.
- **Justification:** cell IS the substrate-primitive being validated
  (atom_consultation enforce() path). No GPU-batchable work; per-consult
  wall ~1ms; 1000 total ~1-30s.
- **Storage strategy declaration:** NO_STORAGE (in-memory curated atom
  table + per-call fresh target dict; EnforcementDecisionLogger writes
  JSONL to output_dir).

## SCHEMA-VET pre-dispatch checklist

- `cardinality_ok`: True at EXPECTED_N_UNITS = 2 * 5 * n_per_arm (200
  SMOKE / 1000 FULL).
- `arms_differ_verified`: True (real-arm writes recommendation, null-arm
  writes pre_value; distinct values by construction across all cases).
- `final_metrics_atomicity`: `tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception`: verified.
- `crlb_n_a`: retrieval-correctness + KS + nonce fractions; no analytical
  noise floor; chance-baseline for match_and_honored = 0.20 (5 op-classes).
- `baseline_in_band`: chance = 0.20 in (0.05, 0.95).
- HP strictly above floor + 5% band-width: 0.60 vs 0.20 + 0.05 * 0.80 =
  0.24. HP >> band-floor + margin.
- `HP_SCOPE`: `{match_and_honored_and_effect: [REAL_ARM],
  nonce_consumption_rate: [REAL_ARM], ks_pvalue: [REAL_ARM vs NULL_ARM]}`.
- `discriminator_reachability`: True (selftest at n=5 per arm measured
  match_and_honored=0.80, nonce_consumption=1.0, 4/5 cases KS p<0.01).
- `discriminating_fraction`: 4/5 cases predicted in the HARD_PASS band
  (0.60, 1.00) at FULL; 1/5 (case 3) predicted at 0.0 by Phase 1 corpus.
- `composition_edges`: enforce() -> downstream stub via read_and_ack_nonce.
  Shape verdict: SHAPE_MATCH.
- `positive_control_arms`: Phase 1 v1.1 IS the positive control at same
  regime (identical curated corpus + 5 cases). Reproduction:
  match_and_honored fraction preserved at 0.80 +/- 0.05 in real-arm.
- `functional_requirements`: (1) mechanical read proof via nonce;
  (2) distributional effect proof via null-arm KS; (3) per-atom
  graduation flag semantics respected.
- `cell_chunked`: False (single-seed by design; stateless).
- `start_marker_written`: True.
- `crash_diagnostic_present`: True (`_write_crash_metrics` on Exception).
- `heartbeat_present`: N/A (elapsed_s < 30s).
- `defensive_error_checking`: `passed_all_4_patterns`.
- `progress_logging`: `line_buffered_stdout` + `print(..., flush=True)`
  on per-case audit line. timeout_s < 1800 so pre-reg field not mandatory
  but declared.

## Sweep-alignment audit (META_RULE_15 gate A)

- `swept_params`: 5 cases x (100 real + 100 null) = 1000 measured calls.
- `effective_params_per_primitive`: enforce() sees exact (op_class, params,
  query_hint, target, param_name, null_arm) tuple.
- `sweep_alignment_verdict`: ALIGNED.

## Discriminating-band audit (META_RULE_15 gate B)

- Predicted match_and_honored_and_effect = 4/5 = 0.80 (cases 1,2,4,5).
- `discriminating_fraction`: 4/5 = 0.80 in HP band (0.60, 1.00) >= 0.30 gate.

## Signal-shape compatibility (META_RULE_15 gate C)

- Only composition edge: `enforce()` -> `read_and_ack_nonce()` -> downstream
  stub. Shape: target dict `{param_name: value, param_name+'__nonce': str}`.
- Verdict: SHAPE_MATCH.

## Reproduce-prior-chain-grade (META_RULE_15 gate D)

- Parent = Phase 1 v1.1 (not yet CG; MM_TENTATIVE_ADVISORY at math #54).
- Positive control: real-arm match_and_honored preserves 0.80 +/- 0.05
  at MATCHED REGIME (identical corpus + 5 cases).
- If deviates > 0.05: enforce() code path changed retrieval semantics
  unintentionally. Cell FAIL flagged.

## Anti-drift signature

- 5 curated atoms locked in cell + prereg BEFORE running.
- WARN promotion list `_ATOMS_TO_WARN` FIXED in cell (no cherry-pick).
- Downstream `_VALUE_MU_MAP` mean values LOCKED before running.
- `_DOWNSTREAM_SEED_BASE = 20260704` LOCKED (deterministic RNG stream).
- KS threshold 0.01 LOCKED for FULL; selftest uses 0.10 (small-sample
  proxy) per META_RULE_AC transparency.
- Prediction match_and_honored_and_effect_rate in [0.60, 0.80] LOCKED.

## Dispatch

- Queue: `local_cpu_queue` (SMOKE only; per USER-LOCKED 2026-07-01
  smoke-only-on-laptop).
- Timeout: 120s (probe wall << 30s at FULL; 120s is queue-runner floor).
- SELFTEST_OK: verified via `--self-test` on `.venv` before queue_add.
- **NOTE:** local_cpu_queue currently paused (`data/local_cpu_queue_paused.flag`
  exists from 2026-07-01). exp_dev may direct-run SMOKE inline via python
  invocation (~1s wall) since queue-runner won't consume paused queue.
  This preserves USER-LOCKED "SMOKE-only on local" while surfacing the
  SMOKE landing under the same anchor. Orchestrator to arbitrate whether
  to unpause runner or acknowledge inline result.

## Independence

Independent of batch VET (task `a4016caa842325471`), encoder Step 1
running, and all other work in flight (different files + no shared
state).

---

## Discipline signature

- Prior-work concept-query: NONE at cosine>0.30.
- Mechanism-abstraction-lossy citation: source_signature declared in
  cell metrics + this pre-reg (Phase 2 v1 first probe, 1000 consults).
- Regime-mismatch: N/A (identical corpus + cases to Phase 1 v1.1; added
  enforcement instrumentation only).
- Anti-drift: 5 atoms + WARN promotion + downstream mu-map + seed +
  prediction band ALL locked BEFORE running.
- No hallucinated numbers:
  - Phase 1 v1.1 landed match_and_honored_over_all = 0.80 MEASURED@`d:/AI/hd-instrument/data/exp_cortex2_atom_consultation_smoke_v1_1_warmup_fix_s7_smoke/metrics.json:match_and_honored_over_all`
  - Selftest at SMOKE (n_per_arm=5) confirms 4/5 cases KS p<0.01 and
    nonce_consumption=1.0 MEASURED@self-test run 2026-07-04.
  - HP threshold 0.60 HYPOTHESIZED@this prereg (per task-spec drill
    section 8).
  - Predicted mhe rate 0.80 HYPOTHESIZED@this prereg (Phase 1 corpus
    reproduction).
