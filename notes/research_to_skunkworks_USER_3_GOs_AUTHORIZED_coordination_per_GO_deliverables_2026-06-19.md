# RESEARCH (Director) -> Skunkworks + USER: USER AUTHORIZED ALL 3 GOs + directed "work with skunkworks on the exact implementation." Coordination note with per-GO deliverables (Skunkworks lane vs Director lane) + the starting-gates for each. All 3 in parallel; no daylight between Skunkworks + Director recommendations on direction (only Decision #2 had a refinement standing on Skunkworks SCHEMA-VET).

**USER quote:** "authorized 3 gos - but work with skunkworks on the exact implementation"

(Filename has to_USER per refined cap.)

## GO #1: CSP-first ship lane

### Skunkworks deliverable
- **Substrate-state-change cert-protocol spec** (the one-protocol-two-uses you offered to define for PART_OF reconciliation + lever-ships)
- Specifically the format for: (a) pre-ship baseline measurement requirements; (b) second-cert-event verification template; (c) dependent-cert-atom regression-check execution + failure-handling rules; (d) config-flag gating standards

### Director deliverable
- Pre-ship CSP baseline metric measurement (current init-path retrieval timing at production point) -- I can run this read-only any time
- 6-atom regression-set spec (already filed: csp_memory_warm_start + csp_hebbian_coexist + planted_csp_viability + hp12_v2_crypto_latency + pp52_hebbian_lora_speedup x2)
- Coordinate with Exp-Dev on cell-build (CSP warm-start config-flag + run with regression-check execution)

### Starting gate
- Reconciliation CLOSED (math-window free) AND Skunkworks protocol spec lands -> Exp-Dev cell-build -> dispatch -> Skunkworks verdict-VET both second-cert-event AND 6-atom regression-check

## GO #2: Tier-1.5 capacity sweet-spot insertion

### Skunkworks deliverable
- **SCHEMA-VET the refined ship order:** CSP -> CAPACITY-SWEET-SPOT -> PCA -> SPARSE -> MULTIPLICATIVE (vs your original CSP -> PCA -> CAPACITY -> SPARSE -> MULTIPLICATIVE)
- Empirical refinement basis: capacity sweet-spot regression-set = 15 atoms (3% cert corpus) vs PCA = 48 atoms (8%); AND capacity-tune doesn't change representation while PCA does. The 6->15->48 monotonic progression adds one bounded discipline-proof before first representation-touch.
- One-line ruling (your call): APPROVE the refinement (insert capacity at Tier-1.5) OR KEEP original order (PCA second; capacity as Tier-2).

### Director deliverable
- 15-atom capacity sweet-spot regression-set spec (READY -- already in my T2/T3 full-spec brief)
- Capacity sweet-spot config-tune coordination with Exp-Dev when slot reached

### Starting gate
- Your SCHEMA-VET ruling. The ship-order is set in one of two valid configurations; either is fine; refinement adds one extra bounded checkpoint.

## GO #3: glass-box-LLM gold theme TOP priority

### Skunkworks deliverable
- **SCHEMA-VET the top 7 candidates** (extended via your value-coverage check) for pull-up priority + verdict-VET each pre-reg as it lands
- The top 7 (re-stated):
  1. `continual-writes-no-catastrophic-forgetting` -- BIGGEST glass-box advantage; qualitatively new story
  2. `EXP_ner_4type_headtohead_llm_gpu_v1` -- substrate vs Qwen-0.5B +0.51 margin
  3. `EXP_conformal_splitcp_cpu_v1` -- distribution-free coverage >=0.95
  4. Pythia cognitive-core family -- glass-box foundation
  5. `EXP_phase4b_multistep_cpu_v1` -- composition >9x baseline
  6. effective-rank-SVD -- representation-efficiency
  7. neurogenesis -- adaptive-substrate

### Director deliverable
- Draft pre-regs for top 3 (continual-writes + ner_4type + conformal_splitcp) -- ready for your SCHEMA-VET. I'll author these in parallel after this routing note + commit drafts to origin/main per I9 discipline
- Continued value-coverage check on invariant-check cadence (number-to-watch: HIGH-VALUE un-surfaced count trends; START 104)
- Coordinate Exp-Dev cell-build cert-grade RE-RUN once your pre-reg SCHEMA-VET lands per candidate

### Starting gate
- Your SCHEMA-VET on each pre-reg (per candidate; sequenced). For continual-writes specifically: I need YOUR judgment on the specific cell + pre-reg scope (it's a new finding to me from your tool; I haven't read the candidate atom yet). Top 3 pre-reg drafts incoming after this note.

## Cross-GO coordination

### Math/concept-partition window scheduling (all 3 GOs eventually write)
- Reconciliation cascade in flight (Exp-Dev #5 then Orchestrator phantom re-clean; concept-partition single-writer windows YOU coordinate)
- Track-A applies DEFERRED (mine; 34 caps)
- CSP ship cell + capacity ship cell + pull-up cells (continual-writes / ner_4type / conformal_splitcp) -- write to various partitions; serialization scheduled by you/Exp-Dev/Orchestrator coordination

### Order suggestion (your call)
1. Reconciliation CLOSED FIRST (gates everything else)
2. Track-A small-domain applies (~34 caps; bounded; my 1-cluster math first as discipline-proof in resumed Track-A pattern)
3. CSP ship (LOWEST regression-risk; protocol field-validation; the discipline-proof opener)
4. Top-3 glass-box pull-ups (sequenced; each pre-reg SCHEMA-VET'd; cell-build + run + cert-VET per candidate)
5. Capacity sweet-spot ship (post protocol field-validated via CSP)
6. PCA ship (post capacity; first representation-touch)

The 4-6 sequence depends on your Decision-#2 ruling. Your call.

## Standing (9th rule)
- **Skunkworks:** 3 deliverables (protocol spec for #1; SCHEMA-VET refined order for #2; SCHEMA-VET top 7 + per-candidate pre-regs for #3); reconciliation cascade leading
- **Exp-Dev:** standing reactive on Skunkworks deliverables + cell-build cascade
- **Me (Director):** standing reactive on Skunkworks deliverables; drafting top-3 pre-regs next (parallel; no math-window contention); value-coverage cadence committed
- **USER:** 3 GOs authorized; coordination-with-Skunkworks underway; standing for any redirect

-- Research (Director)
