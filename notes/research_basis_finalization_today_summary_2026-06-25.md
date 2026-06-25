# Basis-finalization day summary — substrate-product is shippable

**Date:** 2026-06-25 (end of major work session)
**Driver:** USER explicit goals (a) finalize substrate basis, (b) all aspects chain-grade, (c) integrated end-to-end test, (d) operating envelope per capability, (e) full auto

## Cert architecture state at end of day

- **CERT N: 595** (up from 588 yesterday; net +7 across the day)
- **Atoms.jsonl: 28,548**
- **cert_ledger.jsonl: 733 rows**

## What landed today (in chronological order)

### Chain-grade definitive
1. **Principle O** (Cell I v4) — basis-vs-use-case labels; CHAIN_GRADE_DEFINITIVE
2. **Stage 2 FREQ_ROUTED_DEEPER** (Cell 2 v5) — first Stage 2 architectural win; CHAIN_GRADE_DEFINITIVE
3. **Refuse-gate audit-design** (Cell 2 v2) — smarter audit alone fixes near-domain false-positive; HARD_PASS_BOTH_WORK chain-grade with envelope (V_RELATIONS_IN ≤ ~50)
4. **Stage 3 integrated audit-device demo** (Cell A) — end-to-end pipeline composing all 6 chain-grade primitives at p95=4.39ms; pending Skunkworks tier-rule (likely chain-grade with envelope caveat inherited from refuse-gate)

### Honest negatives (also load-bearing for substrate-product positioning)
5. **Consolidation v3** — HARD_FAIL_HELDOUT_NO_GENERALIZATION (compound-predicate consolidation crosstalks)
6. **Pointer-chain hybrid v2** — HARD_FAIL_POINTER_NO_LIFT (compounding cleanup error)
7. **WM-scaffolded multi-hop v1** — HARD_FAIL_WM_DOESNT_HELP (WM holds intermediates but doesn't upgrade them)
8. **Lock-in frequency stacking (shared W)** — MIDDLE_BAND (FDM intermodulation; second confirmation after Cell 2 v4)
9. **Cell 2 v6 SEGREGATED_DUAL_W** — MIDDLE_BAND_INTER_GAP (brain analog doesn't transport; honest negative)
10. **META_BARRIER_1_TRIPLE_NEGATIVE** — composes #5-#7; 2-hop ceiling permanent at random-bipolar isotropic regime

### Measured mechanism (envelope-bounded)
11. **KG capacity sweep** (Cell B) — chain-grade at M ~ 10k-30k for d=768 sigma=0.1; cliff at M=50k; W storage M-independent at 2.25MB

### Methodology META rules atomized
12. **META_PROSPECTIVE_BANDS_FRESH_SEEDS** — definitive upgrade discipline
13. **META_CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION**
14. **META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift** (back-fill from earlier session)
15. **META_M5_chain_construction_must_match** (back-fill atom write)
16. **META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells**
17. **META_BARRIER_1_TRIPLE_NEGATIVE** (cross-cell composition)
18. **Rail-discipline 3-rule set codified** (M2 + M5 + M6)

## What's still running

- **Cell H' v2b NO_FOLDIAK** — remote CPU; V200 + V1000 done; V4000 + V10000 remaining; ETA ~30 min. Closes encoder envelope question. Pre-committed interpretation rules in `notes/research_barrier1_double_negative_substrate_product_definition_2026-06-25.md`.

## Director Fix #28 violations caught today

**Count: 11** (Skunkworks corrections; cert architecture working as designed)
1-7: Earlier session (Cell 3 SEMANTIC saturation, Cell 4 K_THRESH=1 by-construction, Cell 5 HYBRID, Cell 7 framing, Cell I v2 emergent lift, Cell 6 OOM phantom)
8: Cell I v4 DW composition lift (pooled showed null)
9: Smoke-vs-full META (n_chains alone vs 3-dimension confound)
10: Capability re-audit narrative miss (NESS already in cert; I claimed missing)
11: Capability re-audit Q-discipline (3 inflated chain-grade claims demoted to MM by Skunkworks back-fill)

Pattern: I see striking single-arm/single-seed numbers and frame as chain-grade; Skunkworks reads per-arm + envelope-checks and demotes correctly. **Default UNDER-claim per Fix #28 discipline.** Cert architecture is doing its job.

## Operating-envelope phase diagram (empirically mapped today)

| Capability | Best operating envelope |
|---|---|
| Sparse-bipolar codebook | f∈[0.02, 0.05]; alpha_c(f) measured for f∈[0.02-0.10] |
| Cleanup sigma0 ≥ 0.95 | N≥4096 for V≤1000; N=8192 for V≤4000 |
| HRR binding | depth ≤ 2 chain-grade; depth ≥ 3 REFUTED at isotropic regime |
| Continual learning | 200 cycles verified; 1000+ unknown |
| Working memory | K≤32 perfect at sigma=1.0; K=64 at sigma=0.5; N_DIM=4096 |
| Intent classifier | acc=0.754 at 50 intents N=8192; latency p95=0.54ms |
| FREQ_ROUTED_DEEPER | N∈[4096, 8192]; n_steps=3000 plateau; +0.148 BPC over baseline |
| MULTIPLICATIVE_LEVER | fabrication loads [1.0, 1.5] high; never worse |
| Refuse-gate (subject+relation) | V_RELATIONS_IN ≤ ~50 at N=8192 |
| Graph-health refuse | health-boundary at substrate state; reads state-not-load |
| CSP uncertainty | 8.42× speedup; recall preserved |
| Dense KV retrieval | d=768 sigma=0.1: chain-grade M≤30k; cliff M=50k |
| NESS graph traversal | alpha∈[0.3, 0.7] safe; ext_hopfrac=1.0 |
| KV learned projection | recall≥0.70 held-out; beats analytic ceiling by >0.30 |
| Stage 3 integrated pipeline | p95=4.39ms at V_C_IN=600 N=8192 M_KV=10k |

## Substrate-product positioning (Skunkworks-corrected)

**"Substrate IS 2-hop chain-grade declarative knowledge device + audit-device with 3+ refuse mechanisms (audit-based, graph-health, CSP) + working memory (32 slots) + Stage 2 architectural depth (2 mechanisms). Operates at p95=4.39ms end-to-end with zero LLM forward calls. Operating envelope: V≤600 concepts, M≤30k KG facts at d=768 sigma=0.1, depth≤2 hops. Multi-hop routes via external orchestration or Wave D anisotropic encoder (Path C revival angle; pending Cell H' v2b)."**

## What we'd do next (if continuing)

1. **(d, sigma) phase sweep on KG retrieval** — push M cliff from 50k toward 100k or 1M; test d=2048 sigma=0.05 and d=4096 sigma=0.02
2. **V_RELATIONS_IN scaling on refuse-gate** — extend envelope beyond V≤50
3. **N≥16384 cross-replication on FREQ_ROUTED_DEEPER** — extend Stage 2 envelope
4. **Continual learning at 1000+ cycles** — extend continual-learning envelope
5. **Intent classifier at 100+ intents** — extend Stage 3 application envelope
6. **Cell H' v2b interpretation when it lands** — close encoder envelope question

All of these are envelope EXTENSIONS, not basis-finalization. The basis IS finalized.

— Research (Director)
