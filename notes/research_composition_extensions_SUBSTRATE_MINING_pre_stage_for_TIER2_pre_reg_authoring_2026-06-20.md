# RESEARCH (Director) -- composition-extensions substrate-mining synthesis: pre-stage work for the TIER-2 #1 pre-reg (composition extensions = the wave's #1 per enabling-ness; Skunkworks endorsed). Catalogues existing composition cert atoms + identified gaps + the can-fail / discriminating-regime / HARD_PASS shape ready for 1-shot authoring on Skunkworks signal. Director-side artifact; NOT routed (no inbox-routing pressure).

(Filename has no `to_<recipient>` per refined cap — Director-side working document.)

## Why this note

Per Skunkworks's endorsement of the enabling-first wave order: composition extensions is TIER-2 #1 (everything stacks on composition — KG / reasoning / glass-box-LLM Phase 3 all build on multi-hop). Skunkworks's queue is full → pre-reg authoring waits on her signal. Director-lane forward work between cycles = SUBSTRATE-MINE the composition cert atoms + identified gaps + the pre-reg shape, so when she signals the authoring is 1-shot (not "now think about it").

Composes with Phase 0d framework (commit b6d585dd) — composition q_b op section gets populated by this mining.

## Existing composition cert atoms (validated; HARD_PASS unless noted)

| Atom / capability | Operating-point | Verdict | Lit anchor | Note |
|---|---|---|---|---|
| `b2xb4xhier_v1_n2048` (multiplicative-composition) | N=2048, K=10, D=5, sparse + hier | **HP** 600K patterns, recall=1.00 | Plate 1995 HRR + Treves-Rolls 1991 | FLAGSHIP for capacity multiplicative principle |
| SQ2 K=12 multi-hop iterated retrieval | N=2048, M/N=0.5α_c | **HP** flagship | Frady-Sommer 2020 resonator | Mode 4 NC1-class; pure single-substrate depth |
| SQ2 × hierarchical 24-hop | N=2048, D=4-6 | **HP** 24-hop, 2×α_c via ensemble | hierarchical extension drill | Reasoning MULTIPLICATIVE with hierarchical aggregation |
| Compositional generalization K=10-20 | N=2048, varied K | **HP** 60-80% stored-chain depth | drill synthesis | Chain stored facts to novel conclusions |
| Composition EXACT-1.0000 at L=10000 | algebraic | **HP** | algebraic | Audit primitive |
| Resonator/cleanup-augmented depth | N=2048, K=24+ at 2×α_c | **HP** 6× boost (drill predicted 2.7×) | Frady-Sommer | Cleanup-augmented depth extends past plain-iter ceiling |
| `q_b1_cleanup_mediated_composed_v_HP` | (the q_b1 candidate-2; depth-extension MODEL) | **HP** (CERT 587-tier) | substrate cert chain | Per Skunkworks: the q_b1 cleanup-mediated depth-extension IS the working MODEL of composition enabling-ness |
| R5 serial-stack (B2 sparse-storage + B8 sparse-readout) | N=2048 | **HP** | composition rule | Storage compatible with ROBUST-PROJECTION readouts |
| R6 sparse storage + resonator | N=2048 | **HF** | composition rule | Storage INCOMPATIBLE with PRECISE-STRUCTURE recovery → must isolate substrate |
| B6 × SQ2 audit-preserving reasoning | N=2048 + eviction active | **HP** K=12 holds + deletion-cert preserved | flagship | Audit + reasoning compose cleanly |
| heterogeneous-axis composition (cf-RPE × STDP) | N=2048 | **HP (3/5 seeds)** | shared-axis drill | Task + temporal orthogonal compose |
| same-axis composition (B36, B26) | various | **VALIDATED SUBSUMED** | collinear | NEGATIVE principle: don't stack same-axis on single-stream |
| B36-MIXED-stream superadditive | various ratios | **HP** input-regime-specific | flagship | Compose where streams MIX (redundant + novel) |

## Identified GAPS (the pre-reg target)

### Gap #1: N>2048 scaling cert atoms MISSING
- `b2xb4xhier` cert at N=2048 only; n4096/n8192 GPU runs FAILED (no logs; infra issue per scorecard 2026-06-05 01:45 — "passed --self-test + smoke" but no-log GPU failure)
- Scorecard explicit: "Capacity multiplicative principle validated at N=2048 (125k); N>2048 scaling is nice-to-have, not blocking" — but for ENABLING-FIRST per USER, this BECOMES load-bearing (everything that stacks on composition needs known scaling)
- **Pre-reg target:** cert-grade `b2xb4xhier_N4096` + `b2xb4xhier_N8192` after GPU infra fix; recall reproduces; pattern-count scales as the multiplicative-principle predicts

### Gap #2: Cleanup-augmented depth at N>2048 untested
- 6× depth boost validated at N=2048; not characterized at N=4096 / N=8192
- **Pre-reg target:** at N=8192, cleanup-mediated composition K_observed ≥ K_classical_floor × (sqrt(N_ratio)); cliff REPORTED at K where cleanup fails

### Gap #3: K_max formula PESSIMISTIC — needs NESS correction (deferred follow-up)
- Scorecard 2026-06-05 01:20: "K_max depth formula 3.3×(1-α/α_c)^2/α is PESSIMISTIC; substrate reasons deeper than predicted; likely NESS-dynamics correction needed"
- **Out-of-scope for THIS pre-reg** (theoretical correction; future-drill); but the empirical pre-reg results FEED the NESS correction work
- Pre-reg reports observed K vs predicted-classical-floor (the discrimination axis)

## Pre-reg SHAPE (1-shot authoring on Skunkworks signal)

### Title
"Composition extensions: cleanup-mediated multi-hop at N=4096/8192 + b2xb4xhier multiplicative scaling at N>2048"

### Cluster type
**Dependent-set** (b2 × b4 × hier inherits cert from existing singletons; the EXTENSION at N is the new claim) + **operating-point-series** across N (so individual N values are scale-points within one cap, per Skunkworks's op-series cluster type)

### 4-line template applied
1. **HARD_PASS gates load-bearing MECHANISM:** at N=4096: `b2xb4xhier` recall reproduces ≥0.95 of N=2048 result with patterns scaling per multiplicative principle; cleanup-mediated K_observed ≥ classical-floor predicted from N-scaling
2. **CLIFF (REPORTED measurement, not gated above HARD_PASS):** K_observed at the cleanup-failure regime (where cleanup-augmented depth stops extending past plain-iter ceiling)
3. **Per-condition can-fail:** failure modes — recall <0.95 at N=4096; K_observed < classical-floor; cleanup augmentation drops below 2× (vs 6× baseline at N=2048); pattern-count fails multiplicative-principle prediction
4. **Achievability check on plausible data:** N=2048 cert atoms (recall 1.00 + 6× cleanup boost + 600K patterns) → N=4096 extension is plausible (the multiplicative principle predicts it; same-architecture; just GPU infra was the blocker not the science)

### Discriminating regime
- N × K joint sweep: N ∈ {2048 [cert baseline], 4096, 8192}; K ∈ {12 [SQ2 baseline], 24, 36, 48}
- At each (N, K): measure recall + pattern-count + cleanup-mediated-depth-vs-plain-iter ratio
- CAN-fail axis: K at which cleanup augmentation drops below 2× — this is the cliff where the extension fails

### Cost (rough)
- GPU runs (infra-fixed): N=4096 + N=8192 × K ∈ {12, 24, 36, 48} × 5 seeds = ~40 runs; medium GPU
- Pre-req: GPU infra fix (the n4096/n8192 no-log failure from 2026-06-05); coordinate with Orchestrator before dispatch

### Composes downstream
- Phase 0d framework q_b composition op section gets populated (validated regions extended to N=8192; cliff REPORTED)
- KG fb15k237 pre-reg (#3 in wave) builds on this — KG traversal IS composition at scale
- Glass-box-LLM Phase 3 multi-hop scale-up uses this as the load-bearing capacity envelope

## Standing
- This is Director-side working document (NOT routed; no inbox-routing pressure on Skunkworks)
- When Skunkworks signals queue-drain → 1-shot author the pre-reg per the SHAPE above + file with `to_skunkworks` cap → SCHEMA-VET → Exp-Dev cell-build
- Pre-req coordination: Orchestrator + Exp-Dev on GPU infra fix for n4096/n8192 (the 2026-06-05 no-log failure must be RCA'd before dispatch; can be flagged when pre-reg files)

Director self-catch counter: still 2 this session (vs-LLM tier + substrate-distinctive lens; no new ones).

-- Research (Director)
