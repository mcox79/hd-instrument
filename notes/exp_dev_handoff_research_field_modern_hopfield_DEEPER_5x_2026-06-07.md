# exp_dev hand-off -- research: modern hopfield DEEPER 5x

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_field_modern_hopfield_DEEPER_5x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously.

---

## Pause State Block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered by actionability + P_deflated)

### 1. MANIFOLD-D-EFF -- Participation Ratio of Real Encoder Embeddings
Anchor pointer: MANIFOLD-D-EFF-P1 (new; not yet queued)
Substrate-product reading: measures the actual effective dimensionality d_eff of BGE-large
  embeddings on a real KB sample; this corrects the Lucibello-Mezard capacity bound from
  2^2836 (iid) to 2^(0.693*d_eff); if d_eff < 30 the N=4096 safety margin is materially
  reduced and a recommendation to upgrade N becomes critical for production KBs > 10^6.
  If d_eff > 100, the corrected headroom is still 10^14x -- no action needed.
Tier hint: CPU; < 5 min wall; no GPU needed; single matmul + eigendecompose
Why-now: cheapest decisive test in this drill; directly grounds the customer capacity-safety
  claim with a real-encoder correction; P_deflated=0.55 (theory predicts d_eff 50-200 for
  semantic embeddings; result determines whether any capacity-related alarm is warranted)
Priority: HIGHEST (5-minute test; blocks correct customer pitch)

### 2. KHOP-N16K -- K-hop Depth Scaling at N=16384
Anchor pointer: KHOP-N16K-P2 (new; not yet queued)
Substrate-product reading: cycle 176 established K=12 at N=4096 with recovery=0.987;
  theory predicts K_max = floor(r/epsilon_hop) where r increases with N; at N=16384
  r -> ~0.9995 and K_max >> 12 if epsilon_hop is the bridge-entity-noise limit;
  if K_max < 15 at N=16384, the bottleneck is epsilon_hop (LLM bridge quality), not
  the substrate basin geometry, and bridge improvements become the next priority.
Tier hint: GPU preferred (BGE-large encoder + N=16384 substrate); K in {12, 15, 18, 21, 24}
Why-now: K=12 is an extraordinary result; 2x confirmation that K_max > 20 would make
  multi-hop the headline differentiation claim; if K_max stalls at 12 even at N=16384,
  the epsilon_hop characterization guides the next round of bridge engineering.
P_deflated: 0.65 (straightforward N-scaling experiment; baseline at K=12 already proven)
Priority: HIGH

### 3. INT8-QUANT -- Synaptic Noise Formula Verification at int8
Anchor pointer: INT8-QUANT-P3 (new; not yet queued)
Substrate-product reading: arXiv 2503.00241 (2025) predicts capacity retention = exp(-sigma^2*N/2)
  at synaptic noise sigma; at int8 (sigma=2^-7, N=4096) the formula predicts 99.8% retention;
  if recall@1 > 0.99 at int8 (HARD-PASS), substrate pattern storage can be compressed 2x
  (fp16 -> int8) with no observable degradation; this halves the 8GB storage cost to 4GB.
Tier hint: CPU; < 10 min wall; P=10^4 sufficient for this verification
Why-now: 4x memory reduction (fp16->int8) unlocks a significant cost reduction at provider
  scale; the formula is clean but has not been empirically validated for this substrate.
P_deflated: 0.60 (formula derivation is standard; main risk is systematic biases in the
  substrate's weight matrix beyond iid Gaussian assumption)
Priority: MEDIUM-HIGH (cheap; high cost-reduction upside)

### 4. ENERGY-MON -- Hopfield Energy Monitoring for KB Health
Anchor pointer: ENERGY-MON-P4 (new; not yet queued)
Substrate-product reading: arXiv 2605.27975 (2026) establishes that Hopfield energy E(xi_mu)
  increases as a stored pattern's basin integrity degrades; a monitoring pass after each
  batch insert checks whether any previously stable facts have had their energy increase
  beyond a threshold; this provides a proactive alert before recall failures occur;
  directly extends the cycle 175 GDPR-deletion capability (0.0004ms) to a full lifecycle.
Tier hint: CPU; < 5 min per 10^4-fact KB; single matmul over stored patterns
Why-now: adds zero latency to retrieval path; runs as a background health check;
  directly monetizable as a "KB health dashboard" feature; threshold calibration is the
  only empirical question.
P_deflated: 0.55 (computationally trivial; threshold calibration requires a few empirical
  runs across varied KB compositions)
Priority: MEDIUM (high product value; low effort; can ship alongside existing pipeline)

### 5. KRR-STORAGE -- Kernel Ridge Regression vs Hebb Storage at Near-Capacity
Anchor pointer: KRR-STORAGE-P5 (new; not yet queued)
Substrate-product reading: arXiv 2504.12561 (2025) shows KRR-fitted weight matrix achieves
  higher recall than Hebb at the same P/N density; HARD-PASS if KRR recall > 0.998 where
  Hebb gives 0.990 at N=2048 and P near the Hebb-degradation point; this determines whether
  KRR is the recommended storage strategy for high-density KBs (>10M facts) and gives a
  concrete path to doubling effective capacity at fixed N.
Tier hint: CPU; ~30 min wall; N=2048, P sweep to find Hebb-degradation point then compare
Why-now: only needed if customer KB density exceeds Hebb-comfortable regime; currently the
  substrate is far from this regime; useful for forward planning of N=4096 high-density KB.
P_deflated: 0.45 (KRR gains shown in 2025 lit; main uncertainty is cost of KRR solver at
  P=10^6 scale and whether gains persist beyond toy N=256-512)
Priority: MEDIUM (longer timeline; run after simpler anchors above)

---

## Context Pointers

Research note (primary): d:/AI/hd-instrument/notes/research_drill_field_modern_hopfield_DEEPER_5x_2026-06-07.md
Prior Hopfield drill: d:/AI/hd-instrument/notes/research_drill_field_modern_hopfield_5x_2026-06-07.md
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
K-hop empirical result: cycle 176 (K=12, recovery=0.987) -- see notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
fp16=bf16 + 1M empirical result: cycle 175 -- same brief
Prior handoffs: scan notes/exp_dev_handoff_*.md sorted by mtime for conflicting dispatches
Key papers (for implementation context):
  - arXiv 2511.20698 (MHA hidden state, NeurIPS 2025)
  - arXiv 2503.09518 (manifold capacity, March 2025)
  - arXiv 2503.00241 (synaptic noise, March 2025)
  - arXiv 2605.27975 (continual learning + Hopfield energy, May 2026)

---

## Contract Section

exp_dev owns: anchor design, sweep grid, pre-registration bands, queue assignment,
  smoke gate, dispatch, remote verify.

research sub-agent delivered: P_deflated estimates, HARD-PASS / HARD-FAIL thresholds,
  mechanism references, priority ranking.

Orchestrator owns: pause-flag gate, final dispatch authorization.

---

## Autonomy Declaration

exp_dev has full autonomy to:
  - Design the exact experiment scripts for P1-P5 above
  - Choose queue (local CPU / remote GPU) per tier hint
  - Set pre-registration bands independently from the P_deflated estimates here
  - Batch P1 (5 min) + P3 (10 min) into a single local CPU run since both are cheap
  - Defer P5 (KRR) until after P1-P4 complete and results are digested

exp_dev must NOT:
  - Dispatch if data/orchestrator_paused.flag exists
  - Modify the research note or cap_map
  - Pre-frame any anchor as expected-PASS in the task prompt (per [[feedback-no-preframe-batch-all-pass]])
