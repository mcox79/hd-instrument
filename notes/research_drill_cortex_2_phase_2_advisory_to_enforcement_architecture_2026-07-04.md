# Research drill: Cortex-2 Phase 2 advisory-to-enforcement architecture (2026-07-04)

## 1. HEADLINE

Phase 2 apply-mode is feasible ONLY with a two-part discriminator (write-nonce + null-arm A/B) and a per-atom `SHADOW/WARN/LIVE` graduation flag (OPA/Gatekeeper pattern), NOT a global mode switch; MM_TENTATIVE_ADVISORY_APPLIED tier (not CG) after first-probe lands; **P_deflated = 0.42** (novel-synthesis cap 0.50 applied); HARD-FAIL if nonce-consumption < 50% OR match-and-honored-and-effect < 20% (decorative enforcement -> revert to advisory).

## 2. Lit-scan (advisory -> enforcement in production rule engines / policy-as-code / expert-systems)

- **OPA / Open Policy Agent Gatekeeper** (P=0.55, highest transfer): per-constraint `enforcementAction` flag `dryrun`/`warn`/`deny`; decisions computed and logged 100% of time regardless of enforcement state, so audit trail predates enforcement flip. Per-rule graduation, not global switch. Source: openpolicyagent.org/docs/management-decision-logs; Gatekeeper violations docs.
- **Rete-family (Drools/CLIPS/Jess)** (P=0.45): conflict resolution swappable (LEX/MEA/salience/agenda-groups); the load-bearing safety primitive is **refractoriness** -- each rule instantiation fires at most once per fact-set, preventing oscillation when a rule's applied-write re-triggers its own condition. Direct transfer: every enforcement decision must be refractory against re-firing on the same (op_class, params) tuple within one consultation window. Source: en.wikipedia.org/wiki/Rete_algorithm; CLIPS conflict-resolution strategies.
- **Microsoft Conditional Access Report-Only -> Enforced** (P=0.50): ring-based rollout (report-only >=1wk on real traffic -> pilot -> full), side-by-side dashboards compare would-block vs actual-block. Close-monitoring 48h window post-enforcement. Source: MS Learn concept-conditional-access-report-only.
- **HITL clinical decision support (CDSS)** override literature (P=0.40): measured override rates 62-93%; only 3-7% of alerts judged clinically appropriate. **Load-bearing warning: a high override rate is diagnostic of low-value rule content**, and blindly auto-applying encodes false-positive rate into behavior. For Cortex-2: advisory Phase 1 override telemetry (match-and-honored=0.80) is the analog and above the 0.70 pass floor, giving cover to promote curated 5-case atom set to LIVE; the ~90 non-curated Stage-1 atoms remain SHADOW. Source: PMC9579928.
- **Cedar / AWS Verified Permissions** (P=0.40): sync fast-path decision + async centralized audit-trail write; scales to high-throughput per-decision auditing. Directly maps to per-consultation nonce + async EnforcementDecisionLogger.
- **NOT transferable**: SMT/Z3 "verify-before-apply" (P=0.20) -- symbolic UNSAT-proof gate doesn't apply to numeric-weight adjustments under noise.

## 3. Anti-silent-enforcement discriminator taxonomy

The core question: after `AtomConsultant.consult()` returns `recommendation="SHARDED"` and Phase 2 `apply_recommendation()` sets a downstream storage-strategy parameter, did the DOWNSTREAM ROUTINE actually READ the modified value, or did it use the pre-modification value silently?

**Discriminator A -- Write-nonce + read-ack (mechanical proof of read).**
- On enforcement, `apply_recommendation()` writes both the value AND a fresh per-decision nonce token to the parameter slot.
- Downstream primitive is instrumented with `read_and_ack_nonce(param) -> (value, nonce)`; the last-read nonce is emitted to the audit log alongside its output.
- Discriminator: `nonce_written == nonce_ack_at_effect_boundary` for the same operation.
- **False-positive**: downstream reads the nonce but doesn't use `value` in arithmetic (e.g. reads then clamps to identity). Caught by Discriminator B.
- **False-negative**: downstream reads-and-uses but the ack-emission path is broken (missing instrumentation). Caught by nonce-consumption-rate rolling-window monitor (see 5).
- Prior work analog: eBPF uprobe argument-capture (Brendan Gregg toolset) + Chaos Mesh probe-vs-injection status split. Novel here is the causal versioning: nonce binds the write and the read into one event pair.

**Discriminator B -- Null-arm A/B (distributional proof of effect).**
- Interleave "null recommendation" trials where `apply_recommendation()` writes the currently-active parameter value (identity, no-op) with fresh nonce.
- Distribution of downstream outputs on null-arm vs real-arm must differ measurably (KS p < 0.01 across >=50 trials/arm) else the modification is silent at the effect level.
- **False-positive**: high variance downstream swamps a real-but-weak effect (underpowered), reports no-difference-detected. Mitigation: pre-registered N=100 per arm minimum + effect-size (Cliff's delta) reporting alongside p.
- **False-negative**: confounds unrelated to the parameter drive a spurious null/real difference. Mitigation: nonce-consumption-rate must also be >=90% (both discriminators must fire).
- Prior work: standard A/B with null-treatment (Statsig lit; Alex Deng causal-inference text).

**Combined gate**: (Discriminator A >=90% consumption) AND (Discriminator B KS p < 0.01) is the required conjunction for match-and-honored-and-effect count. Either alone is insufficient.

## 4. Audit-gate architecture proposal

**Two-tier record shape** (from ML-monitoring pattern, P=0.50 the strongest single transfer):

```python
@dataclass
class EnforcementDecision:
    decision_id: str        # UUID
    op_class: str
    atom_id: Optional[str]  # None if no atom above floor
    recommendation: Optional[str]
    pre_value: Optional[Any]
    post_value: Optional[Any]
    applied: bool
    enforcement_mode: str   # "SHADOW" | "WARN" | "LIVE" (per-atom flag)
    nonce: str              # cheap tier
    wall_ms: float
    timestamp: str
    # RICH TIER (populated only on sampled events):
    downstream_nonce_ack: Optional[str] = None
    downstream_output_snap: Optional[Any] = None
    null_arm: bool = False
```

**Sampling discipline** (adaptive, not fixed-rate; from Fiddler/Arize ML-monitoring lit):
- Baseline: uniform 5% rich-tier sample of LIVE events.
- **100% rich-tier for null-arm events** (they're pre-registered and cheap).
- **Anomaly-triggered rate boost** to 25% rich-tier when nonce-consumption-rate rolling-window (last 100 events) drops >2sigma from baseline.
- Cheap tier logged 100% of decisions regardless of enforcement mode (dryrun/warn/live).

**Flagging rules**:
- `nonce_consumption_rate` < 80% over rolling 100 events -> WARN sink.
- `nonce_consumption_rate` < 50% OR match-and-honored-and-effect < 20% over rolling 200 -> **kill-switch: enforcement_mode flips LIVE -> WARN globally for that atom_id**; requires manual re-promote.
- Per-atom LIVE promotion criterion (from Conditional Access ring-based pattern): SHADOW >=100 events with match-and-honored >= 0.80 AND zero silent contradictions -> WARN >=50 events -> LIVE.

## 5. Anti-drift discriminators specifically for silent-enforcement detection

- **Rolling nonce-consumption rate** on 100-call window; expected ~100% for correctly-instrumented consumer.
- **Rolling KS-test p-value on null-arm vs real-arm output distributions**; alarm if p rises above 0.05 (distributions indistinguishable = silent enforcement).
- **Wall-time delta on downstream primitive** between advisory and enforce modes: if wall doesn't change on enforce, primitive isn't doing extra work with the applied value.
- **Skunkworks-analog symbolic oracle recompute**: for the 5 ground-truth cases, auditor computes `expected_post_state` from `pre_state + recommendation` using a symbolic oracle (`verification/theory.py`-style closed-form) and compares to observed `post_state`. Divergence -> silent-enforcement or bug flagged.

## 6. Concrete extension to `hdlab/atom_consultation.py`

Additive-only (Phase 1 advisory contract preserved: `consult()` still returns `applied=False` when called stand-alone; `enforce()` is the new Phase 2 entry point):

- Add field `enforcement_mode: str = "SHADOW"` to `_AtomRecord`; per-atom graduation flag. Default SHADOW; hand-promoted per-atom.
- Add class `EnforcementDecision` (dataclass above) and `EnforcementDecisionLogger` (two-tier sampled sink; JSONL append; atomic .tmp+rename per flush).
- Add method `AtomConsultant.enforce(operation_class, params, target, param_name, *, null_arm=False, k=3) -> EnforcementDecision`:
  1. Calls `self.consult(...)` internally (Phase 1 code path unchanged).
  2. Reads atom's `enforcement_mode`.
  3. If SHADOW: logs cheap-tier decision, does NOT write to `target`; returns `applied=False`.
  4. If WARN: writes `target[param_name] = post_value` AND emits warning to sink but does NOT block downstream override.
  5. If LIVE: writes value + nonce to `target[param_name]`; enforces refractoriness (rejects identical (op_class, params) tuple re-fired within same operation window).
  6. If `null_arm=True`: overrides post_value to pre_value (identity); nonce still fresh.
- Add helper `read_and_ack_nonce(target, param_name) -> (value, nonce)` for downstream instrumentation contract; downstream primitives call this instead of raw attribute read.
- Add selftests: `_selftest_shadow_mode_no_write`, `_selftest_nonce_written_on_live`, `_selftest_refractoriness_blocks_reapply`, `_selftest_null_arm_writes_identity_with_fresh_nonce`, `_selftest_kill_switch_on_low_consumption_rate`.
- Phase 1 selftest `_selftest_applied_always_false_v1` **REPLACE** with `_selftest_advisory_default_when_enforce_not_called` (contract renamed but same guarantee for Phase 1 code paths).

## 7. Composition with cortex-1 CG + cortex-2 v1

- Cortex-1 CG atoms: mechanism-proof that a composed-pipeline can invoke a primitive.
- Cortex-2 v1: mechanism-proof that advisory-mode consultation predicts downstream choice (match-and-honored = 0.80, above 0.70 floor, zero silent contradictions).
- **Cortex-2 Phase 2 CG-claim after landing**: **NOT CG-grade** -- tier is MM_TENTATIVE_ADVISORY_APPLIED. To reach CG-grade composition-claim ("consultation -> enforcement -> observed downstream behavior change"), all three must hold empirically:
  (a) nonce-consumption rate >=90% across all 5 cases (mechanical read proof), AND
  (b) null-arm vs real-arm KS p<0.01 for >=3 of 5 cases (distributional effect proof), AND
  (c) at least one case shows monotone dose-response over a swept recommendation (rare-op canary; e.g. sweep K/N through Amit-Gutfreund wall and verify SHARDED-preferred region shift).
- **Per USER-locked "mechanism analog is not task analog" (2026-07-02)**: this arc must NOT be framed as CG until (a)+(b)+(c) all fire; formal-analogy-only is insufficient.

## 8. First-probe cell design (Phase 2 first-probe)

- **Cell**: `experiments/cortex_2_phase_2_apply_probe.py` -- extends `cortex_2_advisory_probe.py`.
- **Ground truth**: same 5 hand-built cases as Phase 1 + null-arm variants.
- **Storage**: NO_STORAGE (stateless), with EnforcementDecisionLogger writing to `data/enforcement_decisions_<seed>.jsonl` (atomic).
- **Trial design**: for each of 5 cases, 100 real-arm + 100 null-arm consultations = 1000 total. Seeded (torch.Generator seed=42). CPU local; est. wall ~5s total.
- **Discriminator (primary)**: `match_and_honored_and_effect_rate = (matched AND nonce_ack_matches AND (null-KS-passes for this case)) / n_matched`.
- **Pre-registered fail bands**:
  - HARD-PASS: match-and-honored-and-effect >= 0.60 AND per-case nonce-consumption >= 0.90 AND >=3/5 cases show null-arm KS p<0.01 AND zero silent contradictions AND p95 wall <=5ms.
  - MIDDLE-BAND: 0.20-0.60 -> Phase 2 lands as WARN-only (no LIVE promotion); document as MM_TENTATIVE.
  - HARD-FAIL: < 0.20 OR nonce-consumption < 0.50 OR fewer than 2 cases show null-arm delta -> decorative enforcement, revert to advisory-only, file negative-result 2x drill.
- **CARDINALITY_OK**: `{n_atoms: 7, n_op_classes: 5, n_ground_truth_cases: 5, n_real_arm_per_case: 100, n_null_arm_per_case: 100, seed: 42}`.
- **SMOKE=FULL parity**: smoke = same code path with n_per_arm=5 (50 total consults); exercises `enforce()`, nonce write+ack, EnforcementDecisionLogger, null-arm identity path, refractoriness check, kill-switch simulation (inject fake consumption drop).
- **Cheap decisive test**: FULL run <= 30s CPU wall; no GPU needed. Checkpoint/resume trivial (JSONL append is idempotent per-decision by decision_id).
- **Error checking**: every trial's decision_id UUID-checked for uniqueness pre-log; refractoriness violation raises; nonce collision raises.

## 9. Falsifiable predictions

1. Nonce-consumption rate >= 0.90 for all 5 cases (else instrumentation broken; hard-fail).
2. Null-arm vs real-arm output-distribution KS p < 0.01 for >=3/5 cases (measurable downstream sensitivity).
3. Applied enforcement of Case 1 (SHARDED) shifts downstream `selected_storage` from BUNDLED to SHARDED in >=95% of trials.
4. p95 wall budget remains <=5ms with nonce+audit instrumentation overhead.
5. Refractoriness: same (op_class, params, nonce) tuple re-fired within one operation window raises OR returns cached decision (no double-write).
6. HARD-FAIL: match-and-honored-and-effect < 0.20 -> Phase 2 shipped BUT does NOT promote atoms SHADOW->LIVE; MM_TENTATIVE only.

## 10. Substrate-product implications (no papers)

- Product surface: this IS the "Auditable AI Memory Subsystem" MVP mechanism. The nonce-versioned decision + null-arm A/B proof-of-effect is the auditable primitive that differentiates from "LLM took action" black-box competitors. Marketable slogan-safe framing: "every symbolic constraint that modifies a numeric weight leaves a cryptographic receipt of consumption AND a distributional witness of effect."
- Generalization: nonce-parameter discriminator generalizes to any product surface where a symbolic recommendation modifies continuous computation. Downstream customer use: model-monitoring vendors could adopt the write-nonce/read-ack contract as a plug-in observability primitive.
- Risk: nonce+ack instrumentation is INVASIVE to downstream consumers -- requires cooperation. For internal substrate this is fine; for external LLM integrations the contract must be adapter-based (nonce wrapped in a metadata channel that adapters passthrough).

## 11. Citations (verified count = 15)

Lit-scan 1 (rule engines / policy-as-code):
- Drools 8.38 rule-engine docs; Huihoo Drools 4.0 (salience/agenda-groups/LIFO conflict resolution).
- Rete algorithm (Wikipedia); CLIPS LEX/MEA/refractoriness docs (csie.ntu.edu.tw).
- OPA decision logs (openpolicyagent.org/docs/management-decision-logs); OPA issue #520 dry-run.
- Gatekeeper enforcementAction docs (open-policy-agent.github.io/gatekeeper).
- MS Conditional Access report-only concept (learn.microsoft.com); welkasworld.com transition guide.
- CDSS override retrospective (PMC9579928; PMC7673981; PMC10484150).
- Peakflo / VerifyWise HITL safeguards.

Lit-scan 2 (silent-enforcement discriminators):
- Eiffel Design by Contract; jContractor bytecode instrumentation.
- Spacelift IaC drift detection; Harness config-drift.
- deepflow eBPF; Brendan Gregg eBPF tracing; OpenTelemetry eBPF profiler.
- Chaos Mesh inspect-chaos-experiments docs (probe-vs-injection status).
- Statsig / Alex Deng A/B null-hypothesis lit.

Lit-scan 3 (audit-gate architecture):
- OPA decision logs; Envoy ext_authz filter.
- AWS Verified Permissions / Cedar (aws.amazon.com; docs.aws.amazon.com prescriptive-guidance).
- IBM ODM Decision Warehouse; PCAOB AS 2315 audit sampling.
- Fiddler ML model monitoring; Arize AI drift detection.
- SR 11-7 model-risk-management guidance; ModelOp SR 11-7.
- HyperLTL k-safety monitoring (arXiv 1807.00758; 2101.07109).

**Calibration note (mandatory per lit-scan discipline)**: raw sub-agent P estimates deflated 0.15-0.25; novel-synthesis cap 0.50 applied; HEADLINE P_deflated = 0.42. HARD-FAIL thresholds explicit above (section 8).
