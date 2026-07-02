# Proposal — `hdlab/cortex.py` integration module + integration test cell

**Filed:** 2026-07-02 late-afternoon session
**Awaiting:** USER go/no-go
**Motivation:** integration debt is M3 bottleneck (per USER 2026-07-02); primitives exist as scattered experiment code, not composable modules.

---

## Current state (disk audit 2026-07-02)

**Extracted to `hdlab/` (composable):**
- M1.4 `hdlab/refuse_gate.py` — v9 joint-alpha-sigma-surface-controller CG today
- M1.6 attention router: `chunked_attention.py`, `streaming_attention.py`, `gpu_generated_streaming_attention.py`
- Support: `intent_classifier.py`, `sequence_memory.py`, `working_memory.py`, `cleanup_family.py`, `conformal.py`

**NOT extracted (only in experiment cells):**
- M1.3 NoiseChannel — boundary stochastic-noise injection (rescued P_def 0.58 per 5x drill 2026-06-30). Lives in `exp_cortex_noise_channel_*.py`
- M1.5 context-retention TWO-TIER — trigger + tier logic in `exp_stage3_m3_stack_*.py`
- M1.7 role-slot summarization — role_binding cortex closure CG 2026-07-01. Lives in `exp_stage3_m3_stack_4_primitive_*.py`
- M1.8 CLARIFY (5th primitive) — CG today. Lives in `exp_stage3_m3_stack_5_primitive_clarify_v1.py`

**Composed pipeline:** does NOT exist as a module. Each 3-4-5 primitive stack cell composes primitives inline in the experiment file. Different cells compose different subsets in ad-hoc order. No canonical `Cortex.forward(query, context) -> response` API.

---

## Proposal

Ship `hdlab/cortex.py` as a composed pipeline module plus one integration test cell.

### Phase 1 — extract + module-ify (~1-2 days)

Extract M1.3, M1.5, M1.7, M1.8 primitives from experiment cells into `hdlab/` modules with clean APIs:

- `hdlab/noise_channel.py` — `NoiseChannel(sigma_boundary).inject(vec) -> vec`
- `hdlab/context_retention.py` — `TwoTierContext(K, decay).update(t, vec) -> (context, tier)`
- `hdlab/role_slot_summarizer.py` — `RoleSlotSummarizer(N, roles).summarize(trace) -> role_slots`
- `hdlab/clarify_gate.py` — `ClarifyGate(threshold).evaluate(query, retrieval) -> Union[REFUSE, CLARIFY, ACCEPT]`

Each module ships with:
- Formula-selftest (matches its experiment cell verdict)
- One-line docstring with shape annotations per CLAUDE.md style
- No behavior change vs experiment-cell version (verified by reproducing prior CG numbers)

### Phase 2 — `hdlab/cortex.py` composed pipeline (~0.5 day)

```python
class Cortex:
    def __init__(self, substrate, config: CortexConfig): ...
    def forward(self, query, context_history) -> CortexResponse: ...
```

Compose pipeline: `NoiseChannel → RefuseGate → ClarifyGate → AttentionRouter → TwoTierContext → RoleSlotSummarizer → substrate retrieval → cleanup`. Config gates which primitives are active per cell / eval task.

Returns typed `CortexResponse` with: retrieval, tier used, refuse/clarify verdict, confidence, provenance.

### Phase 3 — integration test cell (~0.5 day)

`experiments/exp_cortex_integration_end_to_end_v1.py` — validates composed pipeline reproduces individual-primitive CG numbers on the same discriminator grids.

Discriminator arms:
- ARM_COMPOSED: cortex.forward() end-to-end
- ARM_INDIVIDUAL_PRIMITIVES: primitives called separately (reference)
- ARM_ABLATED_PIPELINE: skip one primitive at a time

HP gate: composed pipeline matches individual-primitive verdict at cv ≤ 0.05 across all 5 primitives + 3 seeds. Any primitive whose composed vs individual differs by > 0.05 → INTEGRATION_HAZARD flag, downgrade to MM.

Estimated wall: ~30-60 min on remote_cpu_queue (each primitive is CPU-modest per its own CG cells).

Compute architecture per new USER 2026-07-02 discipline: **(c) mixed** — attention router is torch.cuda; other primitives are numpy CPU. Justification: primitives keep their proven compute mode from their CG cell.

---

## Cost / benefit

**Cost:** ~2.5 days sub-agent work (exp_dev owns primitive extraction + integration cell; Skunkworks VETs integration cell for MM/CG tier).

**Benefit:**
1. Unblocks M3 architecture work — cortex.forward() is the callable that M3 conversational eval cells will use
2. Removes integration debt USER flagged 2026-07-02 as M3 bottleneck
3. Enables future M4 director cell (substrate-as-experiment-director) to invoke cortex without inlining primitives
4. Discipline: forces "does this primitive have a clean API" gate that experiment cells never enforce

**Risk:** primitives lose behavioral fidelity in extraction (e.g. inline experiment code has bespoke config that doesn't survive module abstraction). Mitigation: Phase 1 modules ship with selftest that reproduces exact experiment-cell numbers before extraction is considered done.

---

## Alternative considered — do NOT extract

Keep primitives inline in experiment cells; add a `hdlab/cortex.py` that imports from experiments/ directory. **Rejected**: experiments/ is not a stable API surface; changes to experiment cell semantics silently break cortex. Modules-first is the right factoring.

---

## USER decision needed

- [ ] APPROVE — proceed Phase 1-3 sequentially over ~2.5 days sub-agent work
- [ ] MODIFY — different scope (which primitives to extract first / different integration test design)
- [ ] DEFER — hold until [specific gate]
- [ ] REJECT — different architecture direction

If APPROVE, first spawn will be hdi_exp_dev for Phase 1 (extract 4 primitives to `hdlab/` modules with self-tests). Report at each Phase completion for USER review.

**Reference:** BACKUP callout on cortex integration debt (2026-07-02 LATE); USER 2026-06-28 M3 architecture directive (cortex layer above substrate); USER 2026-07-01 glass-box-substrate-native lock (cortex composes substrate primitives, does NOT include external LLM).
