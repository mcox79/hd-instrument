# exp_dev hand-off -- research: next batch standard cells synthesis

Filed-by: research sub-agent (2026-06-06)
Trigger: notes/research_drill_next_batch_standard_cells_synthesis_2026-06-06.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor
candidates, context pointers, and strategic rationale. exp_dev designs the
actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT
exist (or check with orchestrator). Do not ship if paused.

Current queue state at time of filing: both overnight_queue and remote_cpu_queue
have 0 pending/running entries. Pipeline refill is URGENT.

---

## Anchor Candidates (rank-ordered by strategic priority)

### 1. HOC1 word bigram order-sensitivity (CHEAPEST DECISIVE -- run first)

Anchor pointer: hoc1_word_bigram_v1
Substrate-product reading: closes or routes the KF-1 negation production gate.
If AUC >= 0.90, gate closes with no additional engineering; if MID-band,
pairs with NEG1; if HARD-FAIL, NEG1 becomes mandatory.
Tier hint: CPU; <2 min wall
Why-now: <2 min, no dependencies, immediately prices NEG1 priority. Ship first.

### 2. EFFECTIVE-RANK SVD diagnostic (CHEAPEST DECISIVE -- framework gate)

Anchor pointer: effective_rank_svd_v1
Substrate-product reading: validates the intrinsic-dim-limited retrieval
framework (d_eff ~50-80) that underpins CS-1, DIMSPARSE3, SIG-1, NRO-1.
If HARD-FAIL (d_eff > 300), DT-framework cells need reassessment.
Tier hint: CPU; 5-10 min wall
Why-now: Zero dependencies; 10 min; framework-level payoff for all downstream cells.

### 3. analogy_map capability class probe (CHEAPEST DECISIVE -- new cap class)

Anchor pointer: analogy_map_v1
Substrate-product reading: confirms or denies native relational reasoning
(A:B::C:? via arithmetic in bundle space). If HARD-PASS, new capability class
opens; direct product implication: relational queries without LLM call.
Tier hint: CPU; 3 min wall
Why-now: 3 min, independent, high information gain per unit time.

### 4. frame_slot_fill k=16 multi-attribute entity test

Anchor pointer: frame_slot_fill_k16_v1
Substrate-product reading: how many attributes a single stored entity can
carry without inter-frame interference. Knowledge-graph use case dependency.
Tier hint: CPU; 2 min wall
Why-now: Fast, cheap, directly resolves a product-schema question.

### 5. CS-1 Donoho-Tanner algebraic audit (HIGHEST LEVERAGE -- framework)

Anchor pointer: cs1_dt_algebraic_audit_v1
Substrate-product reading: validates the DT phase boundary (delta, rho) as
the unifying framework for all activation-regime rescue axes. If validated,
every future compound-axis design becomes algebraically principled.
Tier hint: CPU; ~1h wall
Why-now: Batch while Ranks 1-4 run; result arrives quickly and accelerates
all subsequent compound-axis cells.

### 6. DIMSPARSE3-alpha compound stacking at M near M_c (HIGHEST LEVERAGE)

Anchor pointer: dimsparse3_alpha_at_mc_v1
Substrate-product reading: Hadamard x sparse-KEY compound test on real encoder
at M near the critical boundary. Super-additive => Phase 4 v3 recipe locked.
Destructive => operating point must move; follow-up cell needed.
Tier hint: CPU; ~30 min wall
Why-now: The most important unresolved compound question in Phase 4 v3 recipe.

### 7. NEG1 DeBERTa NLI drop-in

Anchor pointer: neg1_deberta_nli_v1
Substrate-product reading: resolves KF-1 negation gate. DeBERTa NLI
no-training drop-in; if AUC >= 0.90, negation gate closes immediately.
Tier hint: CPU; ~30-60 min wall (model load + inference)
Why-now: Run in parallel with Rank 6. Priority adjusted by HOC1 result.

### 8. fact_checked_khop per-hop hallucination detection

Anchor pointer: fact_checked_khop_v1
Substrate-product reading: composition of K-hop reasoning (K=10, 100%) x KF-1
hallucination detection (AUC 0.975). Required to determine whether per-hop
hallucination localization is achievable before building Rank 9.
Tier hint: CPU; 10-20 min wall
Why-now: Gate for auditable_khop_kf1 (Rank 9). Run before Rank 9.

### 9. auditable_khop_kf1 Phase 4 v3 KILLER DEMO (HIGHEST LEVERAGE)

Anchor pointer: auditable_khop_kf1_v1
Substrate-product reading: the flagship integration demo. K=10 chain reasoning
+ per-hop hallucination detection + full audit trace. The "look inside every
reasoning step" demo that no transformer KV-cache can replicate.
Tier hint: CPU; 20-40 min wall
Why-now: KILLER DEMO. Depends on fact_checked_khop (Rank 8) HARD-PASS.

### 10. SIG-1 polyphony SNR formula

Anchor pointer: sig1_polyphony_snr_v1
Substrate-product reading: product-spec formula for multi-tenant concurrent
query capacity. Required for compliance-sidecar architecture sizing.
Tier hint: CPU; ~1h wall
Why-now: Product-spec cell; run overnight alongside NRO-1.

### 11. NRO-1 hippocampus chain-binding K-hop extension to K=15

Anchor pointer: nro1_khop_chain_binding_v1
Substrate-product reading: extends K-hop reasoning ceiling from K=10 to K=15.
If >= 0.95 accuracy at K=15, reasoning depth capability increases 50%.
Tier hint: CPU; ~2h wall
Why-now: Run overnight; expensive but high-value capability extension.

### 12. PSE3 codebook collapse monitoring validation

Anchor pointer: pse3_codebook_monitor_v1
Substrate-product reading: HARD PRODUCTION DEPLOYMENT GATE. Confirms
ETF Hadamard codebook collapse alarm fires on injected collapse AND
does not false-positive on 10k normal insertions.
Tier hint: CPU; ~1-2h wall
Why-now: Pure infrastructure validation; run in parallel with Ranks 10-11.

---

## Recommended dispatch sequence

Batch A (immediate, parallel): Ranks 1, 2, 3, 4 -- all CPU, total <20 min.
  Ship as a single CPU batch now; results arrive fast and price Batch B.

Batch B (parallel with or after Batch A): Ranks 5, 6, 7, 8 -- CPU, ~1-2h.
  Ship while Batch A completes; CS-1 and DIMSPARSE3 are the framework bets.

Batch C (after Batch B result for Rank 9; others independent): Ranks 9, 10, 11, 12.
  Rank 9 depends on Rank 8 HARD-PASS. Ranks 10-12 are independent and can run
  overnight.

---

## Context Pointers

Research note: d:/AI/hd-instrument/notes/research_drill_next_batch_standard_cells_synthesis_2026-06-06.md
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Phase 4 v3 production roadmap: d:/AI/hd-instrument/notes/exp_dev_handoff_research_phase4_v1_production_deployment_roadmap_2026-06-06.md
Prior handoffs: scan notes/exp_dev_handoff_*.md sorted by mtime for any
  conflicting dispatches (especially DIMSPARSE, NEG1, HOC1 in-flight checks)

---

## Contract

exp_dev designs anchor names, sweep grids, pre-reg thresholds, timeout
formulas, and queue assignments.
exp_dev verifies queue presence post-ship per [[feedback-ship-name-collision]].
exp_dev confirms no redundant dispatch if anchor is already in flight
(check queue.json before ship).
exp_dev does NOT re-derive the compound math or framework geometry.

## Autonomy Declaration

exp_dev has full autonomy over: anchor naming, N/seed/layer sweep parameters,
timeout calculation, queue choice (GPU vs CPU vs remote), pre-reg HP/MID/HF
numerical thresholds, and decision to batch vs serialize. The rank ordering
above is a recommendation; exp_dev may reorder if queue state or runner
availability argues for it. The only hard dependency is: Rank 9 must not
ship before Rank 8 completes with HARD-PASS verdict.
