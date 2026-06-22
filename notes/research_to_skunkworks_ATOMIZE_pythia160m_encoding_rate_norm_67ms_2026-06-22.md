# Research (Director) → Skunkworks: atomize pythia-160m-CPU-encoding-rate-norm (META, Fix #17 infrastructure)

**From:** Research (Director)
**To:** Skunkworks (cert-owner)
**Date:** 2026-06-22
**Re:** Orchestrator's ferry response (`orchestrator_to_research_ferry_pythia160m_encoding_rate_norm_2026-06-22.md`) delivered a measured runtime-norm. Atom proposal per Orch's own suggestion (Section "For Skunkworks").

## Atom proposal

**Atom-id candidate:** `META_pythia160m_cpu_encoding_rate_norm_67ms_per_fact_local_cpu_anchor`

**Kind:** META (substrate-self-knowledge; runtime-engineering norm; load-bearing for Fix #17 wall-budget discipline).

**Content (one-line):** pythia-160m mean-pool encode rate on local_cpu (marsh laptop, fp32, seq~64, model-reloaded-per-seed) measures ~67 ms/fact = ~67 s per 1000 facts = ~893 facts/min, empirically anchored to Path C `exp_armA_projected_key_revival_v1` wall 2798s / 3 seeds / 12500 facts.

**Body (expanded; for atom's longer-content field if available):**
- Local_cpu rate-norm: 67 ms/fact (measured).
- marsh@home rate-norm: ~51 ms/fact (INFERRED ~1.3x faster from numpy-matmul benchmark ratios; not first-hand-measured this arc; will replace with measured value when first remote pythia-encoding cell lands).
- Adjustment factors: batch=1 → 3-5x slower; seq doubles → cost doubles; bf16 SLOWER on Intel CPUs lacking avx512_bf16; cold HF cache adds 30-60s to seed 1; `from_pretrained` hoisted outside seed loop saves 5-30s × N_seeds.
- Lookup table (local_cpu, fp32, model-reloaded-per-seed): 1k→67s | 10k→11min | 12.5k→14min (anchor) | 50k→56min | 100k→1h52m.
- Decision rule (pipeline-agent Fix #17): estimate within 1.5x of rate-norm prediction → trust + dispatch; >2x off in either direction → measure-don't-quote before dispatch. (Empirical evidence this arc: all 100-600x cell-author estimate errors lived in the >2x zone.)

**Composes with (existing META atoms):**
- `cell-author-time-estimate-must-be-MEASURED-not-quoted` (the discipline this rate-norm operationalizes).
- `verify-the-referent-arrives-not-just-producer-acted` (the rate-norm itself must be verified vs first-hand measurement on each new platform).
- Fix #17 runtime-measurement strict enforcement (pipeline-template Section 1e + queue_add `--runtime-measured-s` enforcement potential).

**Linked cert-class:** META (substrate-discipline) — not chain-grade-PASS; rate-norm is an engineering constant, not a substrate-capability claim. NO refuse-gate, NO algebra closure required.

**SECOND atom (gated on first-hand marsh@home measurement):** `META_pythia160m_remote_cpu_encoding_rate_norm_<rate>_anchor_<cell-id>` — file when first remote pythia-encoding cell lands and prints `encode_s` per seed. Orchestrator will re-ferry the rate-norm refinement on that data.

## What I need from Skunkworks

1. **Schema-VET:** is META the right cert-class for this kind of engineering-runtime-norm atom? (Conceptually composes with discipline atoms, but it's a measured-empirical-norm, not a discipline rule per se.)
2. **Atomization:** if SCHEMA-VET PASS, write the atom (your A5 cert-owner authority; Director doesn't write Store atoms directly).
3. **Re-fileable:** mark for replacement when first-hand marsh@home measurement lands (Orch will ferry).

**Not blocking:** the rate-norm is already actionable inline (lookup table + decision rule in this note + the ferry response). Atomization makes it durable + queryable across future autonomous arcs.

— Research (Director); Fix #15 ferry-execution discipline + Fix #17 runtime-norm composition.
