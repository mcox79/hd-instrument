# M3 Architecture Readiness Assessment — Session Synthesis 2026-07-01/02

**Filed:** 2026-07-02 late-night full-night push session
**Purpose:** aggregate today's CG landings into a coherent M3 Phase 1 architecture readiness picture

## Session Cert Trajectory

- Session start: CERT 662 (post-post-compaction)
- Session current: **CERT 697** (session +35 atoms; 26 CG-tier)
- Session projected: 700-710 pending overnight + CPU queue drains

## M3 Phase 1 Architecture Layer Status

### Cortex Primitives (4/5 CG + M1.8 smoke HP pending FULL)

| Primitive | Status | Evidence |
|---|---|---|
| M1.3 NoiseChannel | CG (prior) | inherited |
| M1.4 refuse-gate | CG (Atom 15 v8) | conformal cal-source variation |
| M1.5 context-retention | CG (Atom 18) | TWO-TIER K=100 STM + K=4096 LTM |
| M1.6 attention-router | CG (Atom D v2) | 4-class + chain_signal at n_test=20 |
| M1.7 role-slot summarization | CG (batch 4) | ROLE 0.79/0.83/0.79 cv=0.024 |
| M1.8 CLARIFY | smoke HP 2-seed (pending FULL) | CM lift +0.375 over 4-primitive baseline |

**M3 4-primitive stack meta atom: CHAIN_GRADE** (batch 4). Composition-depth characterization MM (batch 9; smooth 5→100 depth curves).

**Predicted 5-primitive: CG-eligible per Sonnet Dim P drill** — primitives operate on disjoint substrate bands (refuse=cosine, context=STM banks, router=class-HV, summarize=LTM bundle, clarify=confidence-band); NO multiplicative decay with n (P_def 0.60).

### Substrate Physics (large CG portfolio)

**Foundational (Hebbian + argmax cleanup mechanism):**
- AGS-SNR raw bit_match empirical curve CG (v2c 3-seed; matches Amit 1985 theory to <0.003 across 3 orders of magnitude in α)
- Cleanup-augmented CAM capacity CG (drops to 0.87 at α=100 N=1024; still 1.000 at N=8192 α=30 — cleanup wall grows with N)
- Hebbian+argmax-cleanup capacity boost MM (batch 8; at N=8192 wall would require α > ~1000, infeasible)
- Substrate memory decouples META MM_TENTATIVE (raw Hebbian follows AGS; cleanup provides orders-of-magnitude capacity boost)

**Capacity boundaries:**
- Löwe correlated-key α_c(ρ)≈0.138(1-ρ²) CG (substrate physics law tier; first empirical Löwe 1998 confirmation on our substrate)
- Sparsity 2-regime META CG (PC axis v4b + WM axis v5 both CG; sparsity is CG-controllable substrate axis)
- Cross-axis (M,N,K) factorization at β=4 CG (batch 7 MM→CG expansion textbook)
- Cross-axis β=5 bridging smoke HP (β=8 saturating; discriminating regime β ∈ [4, 8])

**Precision Pareto:**
- INT8 zero-gap at noise cliff CG (batch 8; 3-seed; extends E v5 CG into noise regime)
- INT4 breaks hypothesis FALSIFIED CG (empirical negative; drop 0.006-0.009 vs 0.20 threshold)
- INT2_ASYM Pareto extension CG (16× compression at 0.097 gap)
- Zero-erasure mechanism CG (symmetric ternary catastrophic; asymmetric fixes; recovery fraction 0.787)
- INT2_ASYM ≈ BINARY AGS 1985 asymptotic equivalence CG

**Robustness:**
- Encoder cocktail HF_PROVEN_NEGATIVE CG (M3 architectural rule: NO encoder-family mixing without bridge)
- Encoder bridge HF_PROVEN_NEGATIVE (TRUE-bridge scope) CG (Procrustes + shared-intermediate both dead; tag-routing is separator not bridge)
- Adversarial gap crossing MM (single seed; Sonnet drill CS-bound constants ~50× off; substrate needs 70-80% L2 not 1.1%; encoder is SOLE attack surface)
- Dim S v3 top-K rescue CG (cliff at σ ∈ (0.05, 0.10]; sparse-Hopfield NeurIPS 2023 prediction confirmed)
- Dim T joint-surface interaction smoke HP (sigma_crit at α=0.10 vs α=0.45 delta 0.069; 2.3× margin)

**Commercial scale:**
- Hippo v5 M=1M CHAIN_GRADE_COMMERCIAL_SCALE (all 3 seeds HP; kernel_active 99% at M=1M; wall 6.9-13.5s)
- kernel_active_fraction ground-truth CUDA-event META CG (durable observability discipline)
- cleanup latency operating curve CG (O(N²) constant w.r.t. M/α; N=8192 p50=19.6ms)

**Falsifications (mechanism-class bounded):**
- Dim H shape HF_PROVEN_NEGATIVE (dense-Hopfield too robust for default-regime discriminators)
- Dim S metrics HF_PROVEN_NEGATIVE (metric-axis flat in underloaded regime)
- Dim H v3 dual MM + META MM_TENTATIVE (Willshaw two-tier prediction falsified across 3 mechanism classes)
- Sonnet drill Regime Table lines 118-133 DEMOTE_PARTIAL (theory intact for raw-bit-match; wrong for cleanup-augmented deployment)

### Sonnet Drills This Session (8 hidden dims exhausted)

| Dim | P_def start | P_def end | M3 architecture implication |
|---|---|---|---|
| A temporal | 0.32 | 0.08 | Cortex owns temporal (M1.5 TWO-TIER already CG); write order irrelevant by construction |
| C latency | (via cells) | — | O(N²) cleanup M-invariant; N=8192 p50=19.6ms numpy; batching viable |
| E adversarial | 0.48 | 0.52 | Encoder is SOLE attack surface; substrate direct-key attack closed by O(sqrt N) |
| F throughput | 0.18 | 0.28 | Sequential 590 QPS at M=500k; B=64 batching predicts 19k QPS; 100-user shard viable with batching |
| L learned encoding | — | (in flight) | v2 incremental_checkpoint dispatched; below-wall MB expected; discriminator at M=12000 |
| P n-primitive | (via cells) | 0.60 (5-prim) | Composition depth REGIME-limited not primitive-count-limited; disjoint substrate bands |
| R failure taxonomy | 0.36 | — | Rich substrate self-signaling (882 verdict strings; 41% HP, 18% LOUD_FAIL); recall extraction limited |
| T regime transitions | 0.28 | 0.32 | Transitions compose as JOINT hypersurface; M1.4 needs upgrade to (α, σ) joint controller |

## M3 Phase 1 Architecture Constraints (LOAD-BEARING)

From today's aggregation:

1. **Cortex primitive stack:** 4-primitive base is CG. 5th primitive (CLARIFY) smoke-validated; FULL-VET pending. n=5-6 is Sonnet-predicted "free zone" before infrastructure changes.

2. **Encoder architecture:** MUST use single unified encoder family across substrate. Universal cross-encoder bridge (Procrustes / shared-intermediate) empirically dead — tag-routing separates, doesn't bridge.

3. **Memory budget (Pareto):** INT8 is FREE (zero-gap noise cliff CG); INT2_ASYM extension gives 16× compression; BINARY sign() 32× compression viable but slightly worse than INT2_ASYM. Symmetric ternary INT2 catastrophic — do NOT deploy.

4. **Capacity budget:** substrate holds recall=1.000 to α ~ 30-100 (cleanup wall N-dependent, grows with N). Hebbian raw AGS wall at α_c=0.138. Sonnet dense-HF theory: substrate is Hebbian+argmax-cleanup, not raw Ramsauer. Deploy well below α_c.

5. **Timing/SLA budget:**
   - Cleanup p50 = 19.6ms at N=8192 (numpy CPU)
   - Cleanup torch.cuda at M=500k = 2ms p50 (M3 real-time viable)
   - Batched QPS at B=64 predicted ~19k on GPU (100-user shard viable)
   - M=1M SLA verdict PENDING commercial_M v2 landing

6. **Refuse-gate:** M1.4 v8 CG at 1D-on-sigma. Dim T joint-surface finding: **needs upgrade to 2D (α, σ) surface controller** — sigma_crit at α=0.45 is 0.069 lower than at α=0.10 (2.3× HP margin).

7. **Adversarial defense:** cortex-boundary stochastic-noise mandate (2026-06-30) is CONVERGENT (not strictly needed for direct-key defense per Dim E; needed for encoder-mediated attacks + refuse-gate adaptivity + brain literature).

8. **Substrate axes independence:** cross-axis M×N×K factorizes at β=4 (CG batch 7); β=5 bridging pending FULL. Cortex can treat as independent design knobs below saturating β regime.

## M3 Deployment Engineering Readiness

- **Small-scale (1-user, demo)**: READY. Sequential 590 QPS at M=500k > 3-30 QPS need.
- **Medium-scale (10-user shard)**: MARGINAL. Sequential 590 QPS ≈ 300 QPS demand; needs light queuing.
- **Production-scale (100-user shard)**: BLOCKED without batching. B=32-64 batched dispatch is deployment engineering item (Dim F batched QPS cell dispatched to validate).
- **M=1M**: PENDING commercial_M v2 landing for definitive SLA verdict.

## Prioritized Gap Closure for M3 Phase 1 CG

Missing from CG portfolio:
1. **M1.8 CLARIFY FULL** — 3-seed pending remote_cpu queue drain
2. **M3 5-primitive META lift** — depends on M1.8 CG + composition test
3. **Dim T joint-surface FULL** — seed_13/19 queued remote_cpu
4. **Commercial_M v2 M=1M torch.cuda SLA verdict** — queued overnight
5. **Dim F batched QPS validation** — queued overnight
6. **M1.4 joint-controller upgrade cell** — pending Dim T CG (next-arc work)

## Session Meta-Findings

**Discipline candidates flagged for Testbed durability:**
- Bash-tool 40-min inner timeout (Dim I A2 pattern)
- PROT-018 delegated-N gate false-positive (learned_encoder v1)
- PROT-021 multi-line _seed_checkpoint import false-positive (4× this session)
- SH-2 variant: _substrate_*_core.py Pattern 4 auto-SCP misses
- META_RULE_U smoke-vs-full framing (INT2 v1 confusion)
- META_RULE_T mandatory dual-readout for Hebbian+cleanup cells
- SH-9 sync-lag SCP-recovery discipline
- SH-10 reporting-side sync-lag (Orchestrator remote-read without SCP-pull)
- commercial_M timeout misestimation pattern (v1 3600s → v2 7200s → still tight)
- Dim L timeout pattern (v1 7200s → v2 14400s + incremental checkpoints)
- Smoke MUST exercise all production-scale code paths (cross_axis K > M bug)

**Substantive M3 architecture insights (session synthesis):**
- Substrate memory decouples: raw Hebbian follows AGS 1985 theory; cleanup provides orders-of-magnitude capacity boost that grows with N. Cortex can query either readout at appropriate regime.
- Composition depth is REGIME-limited not primitive-count-limited (Sonnet Dim P + Stage 3 stack MM). Disjoint substrate bands prevent multiplicative error accumulation.
- Transitions compose as JOINT hypersurface (Dim T HP smoke). M1.4 refuse-gate needs 2D upgrade.
- Substrate is surprisingly adversarially-robust at direct-key attack; encoder is sole M3 attack surface.
- Commercial-M viable: M=1M mechanism CG + cleanup real-time viable on GPU at commercial scale.

## Next Session Priorities (post-drain)

1. Skunkworks batch on CLARIFY 3-seed FULL (5-primitive META CG-eligibility)
2. Skunkworks batch on Dim T 3-seed FULL (joint-surface + M1.4 upgrade justification)
3. Skunkworks batch on Dim L v2 partial or full (Stage 2/3 boundary)
4. Skunkworks batch on β=5 3-seed (factorization META CG-eligibility)
5. Skunkworks batch on commercial_M v2 (M3 SLA verdict CG)
6. Skunkworks batch on Dim F 3-seed (M3 100-user shard verdict)
7. Skunkworks batch on Dim I A2 (hrr_depth_budget when it finally lands)
8. Author M1.4 joint-controller upgrade cell (Dim T CG → M1.4 v9)
9. Author M1.9 REFLECT primitive cell (per Sonnet Dim P Rank 2)
10. Author cross-axis β=5 3-seed FULL (if smoke lifts to CG expectation)

## Cross-References

- Session BACKUP: `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-01_LATE.md`
- Sonnet drills: `notes/research_dim_[a,e,p,t,f,sparse_coding,dense_hopfield_underloaded,hidden_phase_diagram]_*_2026-07-0[1,2].md`
- Cell hand-off notes: `notes/exp_dev_findings/` (multiple)
- MEMORY.md CURRENT STATE updated to CERT 697 with session summary
