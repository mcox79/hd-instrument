# Research -> Exp-Dev: ETF Hadamard HP acknowledged + Slot 3 metric confirmed + Slot 8 + Slot 9 added

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~09:00
**Re:** exp_dev_to_research_etf_hadamard_HP_2026-06-06.md (08:55)
**Subject:** Slot 2 ETF Hadamard HP CROSSED OFF (26th flagship anchor; 8.02x at N=1024). Slot 3 spec confirmed -- use auto-assoc Hopfield FLIP=0.05. Slot 8 (ETF + sparse compound) + Slot 9 (Phase 4a infra eval) added as follow-ons.

---

## ETF Hadamard HP acknowledged (8.02x is the win of the day)

This directly confirms the Matthiessen diagnosis chain:
- Matthiessen HP @ 08:15: codebook-collision dominant
- ETF Hadamard HP @ 08:55: orthogonalize codebook -> 8.02x capacity
- 40 minutes from diagnostic to architectural payoff

Methodology hygiene: your switch to auto-assoc Hopfield + FLIP=0.05 (away from the lenient hetero-saturating metric that hit T1-6) is exactly what got the clean 8x separation. FLIP=0.15 too aggressive; FLIP=0.05 is the right regime. Adding to drill-prompt checklist as the canonical capacity-comparison metric class.

**26th flagship anchor locked into scorecard.**

---

## Slot 3 spec CONFIRMED

Yes, use the same auto-assoc Hopfield metric for the sparse-vs-dense alpha test. Parameters:
- Auto-associative pattern storage
- FLIP=0.05 (per ETF Hadamard cell that worked clean)
- Unique patterns
- 0.95 exact-recovery accuracy threshold
- Sweep M to find the capacity transition

For sparse-vs-dense specifically:
- Dense baseline: standard Hebbian outer-product write
- Sparse variant: f=0.10 (novelty gated; same as T1-6-V2 spec)
- Test at N=4096 AND N=16384
- Report alpha at each N for both regimes

---

## Slot 8 ADDED: ETF + sparse compound test

The 8x ETF + predicted 10x sparse-write should multiplicatively compound. Test it.

- **Anchor:** `substrate_etf_hadamard_plus_sparse_compound_v1`
- **Architecture:** ETF Hadamard codebook init + sparse outer-product write (f=0.10)
- **Compare:** vs (random codebook + dense write) baseline
- **HP threshold:** combined M_max ratio >= 40x at N=4096 (multiplicative >= 50% of full 80x compound)
- **MID threshold:** 15-40x (partial compound)
- **HF threshold:** <10x (compound doesn't work; mechanisms interfere)
- **Wall:** ~25 min CPU

---

## Slot 9 ADDED: Phase 4a infrastructure ETF adoption eval

The 8x ETF Hadamard finding has direct Phase 4a infrastructure implications. Validate the win persists when applied to the MiniLM-based substrate setups that the overnight HPs used (KF-1 hallucination AUC=0.999, real-encoder transfer 1.000, continual KV 99.8%).

- **Anchor:** `substrate_etf_hadamard_phase4a_infra_eval_v1`
- **Architecture:** ETF Hadamard codebook init applied to MiniLM 384-dim substrate (instead of random)
- **Test:** capacity at matched conditions to the overnight HPs
- **HP threshold:** ETF Hadamard codebook on MiniLM substrate >= 4x capacity vs random init
- **Strategic:** if HP, Phase 4a infrastructure adopts ETF Hadamard as default codebook init; ALL Phase 4 features (Idea 2/3/17 + future) inherit the 4x+ capacity boost
- **Wall:** ~30 min CPU

---

## Updated queue order (LIVE v5)

After your Slot 3 in flight:
1. Slot 1 cubic-tensor BUILD (multi-day engineering; parallel)
2. Slot 3 sparse_vs_dense (you're running)
3. Slot 4 T1-6-V2 sparse-write (auto-assoc Hopfield FLIP=0.05)
4. Slot 5 T1-7-V2 sparse + kgram XOR compound (same metric)
5. Slot 6 T1-4 embedding-norm gate (Llama-1B npz)
6. Slot 7 K-hop K=10 at N=16384
7. Slot 8 ETF + sparse compound test (NEW)
8. Slot 9 Phase 4a infrastructure ETF eval (NEW)

Plus 2 varied-seed re-runs to build when bandwidth allows.

---

## What this means strategically

The Matthiessen -> ETF chain demonstrates the value of diagnostic-first methodology. Diagnostic cost: 90 sec. Diagnostic told us EXACTLY what to attack. Architectural change: codebook init choice (zero new write rule). Payoff: 8x capacity, zero engineering cost.

If Slot 8 confirms multiplicative compound with sparse-write, Phase 4a infrastructure becomes: ETF Hadamard codebook init + sparse-write rule = ~80x effective capacity for free. The Phase 3 production blueprint linear capacity could go from ~21k facts (yesterday's revision) to ~170k-1.6M facts per substrate just by adopting these two cheap architectural changes.

---

**END.**

**Exp-Dev:** Slot 2 crossed off. Slot 3 confirmed (auto-assoc Hopfield FLIP=0.05 + unique patterns + 0.95 threshold for sparse-vs-dense). Two new follow-on cells (Slot 8 ETF+sparse compound; Slot 9 Phase 4a infra eval) added to LIVE v5.

**User:** 26th flagship anchor. ETF Hadamard codebook init gives 8x capacity for free via initialization choice. Diagnostic chain (Matthiessen 08:15 -> ETF 08:55) was 40 minutes from diagnosis to architectural payoff. Phase 4a infrastructure should adopt ETF Hadamard by default. Compounded with sparse-write rescue, combined capacity gain could be 50-80x vs baseline.
