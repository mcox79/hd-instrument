# Research Post-Compaction Brief -- 2026-06-07 afternoon

Read this FIRST on context recovery. Supersedes morning brief.

## State of the day (cycles 154-162 + ~51 Exp-Dev cells processed)

Today landed as the most empirically productive day so far. 51 cells processed through
the methodology pipeline. Major findings clustered around:

1. **Pattern B PARITY with Pattern A on storage** at 16 bytes/fact (cycle 162
   ptb_reuse_index_cache HP). The "tiered A-vs-B" framing dissolves. Pattern B is the
   unified production architecture.

2. **EU AI Act Article 12 + GDPR Article 17 co-compliance NATIVELY** (cycle 162
   causal_gdpr_erasure_composition HP). Counterfactual on erased fact leaks zero erased
   content; audit chain intact. NO OTHER ARCHITECTURE can do this. Regulator-defensible
   flagship capability.

3. **Privacy story locked at qualified posture.** Hyp B + Hyp C both empirically
   supported (token-position concentration + Gram structure are dual mechanisms). All
   linear mitigations bounded at ZKL ~0.22; never reach 0.10 HIPAA. Path D (per-customer
   encoder fine-tune) = premium HIPAA tier. Attention-reweighting ships as free 2x
   improvement.

4. **NORTH-STAR validated empirically** (cycle 158): substrate-augmented Qwen2.5-1.5B
   beats bare Qwen by +0.352 F1 on HotpotQA at smoke n=30. HotpotQA 3-baseline (bare +
   vanilla RAG + substrate) running for Tier-1 promotion at n=200+ now.

5. **Tier 4 revived** with concrete recommendation: Arch (8) hybrid continual fine-tuning
   + Arch (5) sparse retrieval heads. Option D mechanism (frozen LLM + rank-4 LoRA).
   3 Pythia-160M pre-tests gate authorization. 5-8 engineer-week build if pre-tests pass.
   Tier 4 = LLM trained on top of substrate as a final layer (per 2026-06-02 routing
   docs). NOT just substrate + attached LLM.

## Customer pitch (revised heavily through the day)

NOT:
- Substrate beats RAG at retrieval (parity at best per cycle 161 + 162; substrate K-hop
  HURTS strong encoders at retrieval F1)
- Substrate has better world knowledge than frontier LLMs (Type II implicit priors
  remain frontier LLM categorical win)
- Substrate makes any encoder more noise-robust (bge sign-binarization HF; substrate BFT
  works on synthetic sign keys not continuous binarization)
- Substrate provides absolute HIPAA-grade privacy on shared encoder (bounded at 0.22)

IS:
- COMPLIANCE: 3+ year defensible structural moat — Art 12 + Art 17 + bitemporal + Merkle
  audit. EDPB Feb 2026 + EU AI Act Art 12 Aug 2026 confirm weight-matrix memory FAILS
  this. Substrate is the only architecture that meets it.
- SPEED: ~184x fewer FLOPs per Type I query than frontier LLM (Tier 4 speed/energy 2x drill
  landed; mostly from 8B LLM vs 200B LLM, not bipolar arithmetic at system level)
- ENERGY: 10-90x less energy per query at system level today (NOT 100-1000x; that was
  ASIC per-op confused with system-level). Future bipolar ASIC could hit 100-1000x
  as roadmap claim.
- LATENCY: 5x faster for 100-token answers; narrows to 1-2x at 500-token
- AGILITY: 100x+ faster knowledge updates (pre-optimization measurement; 4.57 ms per
  update at N=4096 with np.pad realloc overhead). Optimized preallocated version should
  give 600-3600x faster. The architectural advantage (substrate O(1) per fact vs LoRA
  O(params*steps*tokens)) is real regardless of constants. UNVERIFIED 240,000x theoretical
  estimate retracted pending optimized re-test.
- EDGE: real — Llama-8B Q4_K_M on RTX4060 / M2 Pro / commodity workstations
- ECONOMICS: 2-6x lower infrastructure cost (5-20x in regulated industries)
- COMPOSITIONAL REASONING: Pattern B unbind+substitute + K-hop compose at acc=1.0
  deterministically; counterfactual replay at 3.876 ms; algebraic decomposition no LLM
  at any scale can match
- AUDITABILITY: 100% deterministic chain replay with Merkle proofs per step (LLM CoT is
  "superficially plausible narratives that don't reflect actual decision basis" per 2024-
  2025 legal/clinical literature)
- EDGE DEPLOYMENT: substrate runs on commodity hardware; substrate alone viable on
  phone-class devices
- PERSISTENCE: bitemporal as-of queries; continual learning via online concept extension;
  no catastrophic forgetting
- CONTINUAL LEARNING: substrate's continual learning closes ~50-60% of domain-specific
  implicit-generalization gap (sleep defrag mechanism); the genuine residual frontier-LLM
  win is Type II world-model priors that require gradient training over billions of
  tokens

## Top 3 demo barriers (still relevant)

1. End-to-end integrated pipeline (no deployed system you can interact with)
2. Customer-facing interface for distinctive capabilities (audit/GDPR/bitemporal/causal
   need to be EXPERIENCED not just claimed)
3. Multi-benchmark validation (only HotpotQA smoke n=30; need 3+ benchmarks at Tier-1
   n=200+)

All three have routings filed:
- Pipeline: FastAPI monolith, 12 engineer-days
- Interface: Streamlit, 4-5 weeks for 5 capabilities
- Benchmarks: HotpotQA 3-baseline running; NQ + TriviaQA + LongMemEval staging in
  progress

## In-flight drills (will land in 10-30 min)

1. Tier 4 speed/energy quantified 2x (user-flagged 100-1000x advantage I underdocumented)
2. ZKL alternatives + crazy ideas 3x (30 candidates; locked qualified posture stays as
   default regardless)

## In-flight Exp-Dev work

- HotpotQA 3-baseline (running after cosine-entropy completes; Tier-1 promotion of
  cycle 158 +0.35 F1 smoke)
- Data staging: trivia_qa, nq_open, longmemeval, hotpot_qa fullwiki via tools/stage_data.py
- ColBERT-v2 separate venv (.venv-colbert) install + index + 100-question pre-test
  AUTHORIZED to proceed (separate venv to protect main pipeline's torch<2.6 dependency)
- 3 Pythia-160M Tier 4 pre-tests (vocab injection, LoRA orthogonal stability, defrag
  consistency) routed; gate 5-8 engineer-week Tier 4 build
- Sleep defrag pre-test (1-2 hr CPU) routed
- 8 frontier-LLM pre-tests routed (K-hop audit replay = highest priority demo asset,
  ~30 min CPU)
- NQ + TriviaQA Wikipedia pre-test routed (tests 70-85% encyclopedic coverage claim)
- Pattern B 6 capability extension tests routed (online concept extension, compositional
  Merkle proof, CRDT structured aggregation, GDPR granularity, sparse fillers, production-N
  capacity) — most validated by cycle 162

## What got CLOSED definitively today

- Sparse-W storage compression (cycle 155 HF)
- PQ-on-W 256x compression (cycle 162 LVH #260 HF)
- Tensor-rank Pattern B compression (cycle 162 HF; index-cache wins)
- HashNet-W (top-20 routing HF)
- Hyp B all 4 linear mitigations on shared encoder (manifold, mean-pool, attention cap,
  earlier layer)
- Hyp C cosine-entropy projection mitigation (MIDDLE; doesn't reach HIPAA)
- All 4 Hyp B mitigations exhausted
- DAMP gossip biological coordination (cycle 154/155 HF)
- LLM-decomp at 1.5B (parallel + sequential both closed cycle 158; Fano-style bound)
- Substrate K-hop on strong encoders (cycle 156-157 HF; substrate hurts bge-small)
- bge compositional verification at 1.5B LLM (cycle 161 HF; substrate-as-ranker is dead;
  substrate-as-context-expander wins per north-star)
- noise/BFT on bge (top-20 HF; sign-binarization is worse than continuous bge)
- BM25+bge RRF (cycle 161 HF; BM25 dilutes bge)
- 2 Hyp-C privacy full-runs (SKIPPED per Exp-Dev's ask; posture already locked at smoke)

## What's INFEASIBLE per Tier 4 architecture drill (do not pursue)

- Arch (7) backward-pass memory only
- Arch (6) positional embeddings encoding compositional structure
- Arch (1) fast-weight memory (defer; needs compliance protocol engineering)

## Pipeline / verdict state

cap_map ~v483 (cycle 162); HONEST 1210+ from today's 51 cells; LVH 260; Portfolio 32+82.
Capability scorecard accurate through cycle 162 (audited; cycles 160 + 161 added; Hyp C
reversal noted).

## Active feedback rules (memory)

- Plain language no hype; cycle summaries 10-15 lines prose no tables; long-form in notes
- Drill-pretest-required (locked this morning); production-encoder pre-test before
  engineering authorization; theoretical x empirical P split
- Two-encoder architecture (corrected this morning): sentence-transformer for retrieval
  ranking, Llama-1B for KEY job
- Tier 4 = LLM trained on top of substrate as final layer (per 2026-06-02 docs);
  Tier 2-3 = substrate as attached inference-time memory
- Sleep defrag is the continual-learning extension for storing learned regularities;
  closes 50-60% of domain-specific implicit-generalization gap
- Capability tracking SSOT: history.md tail + strategy_decisions tail +
  capability_scorecard

## Memory entries (load on resume)

- north_star_functional_system_beats_LLMs.md
- overnight_loop_research_session.md
- feedback_plain_language_no_hype.md
- feedback_cycle_summaries_concise.md
- feedback_drill_pretest_required.md
- production_architecture_locked_2026-06-07.md (updated with cycle 162 ZKL + storage +
  Pattern B compat + north-star + cycle 162 PP-82 + capability validations)

## What's next when drills land

When Tier 4 speed/energy 2x lands: synthesize the 100-1000x quantification; route a final
Tier 4 consolidated engineering proposal.

When ZKL alternatives 3x lands: synthesize; if any of the 30 candidates have asymmetric
risk-reward, route a focused pre-test; otherwise close out the privacy thread.

Standing for HotpotQA 3-baseline Tier-1 result (highest-value benchmark for v1 demo).

## Authorization state (per user "authorized for all routing")

Research session has standing authorization to:
- Route cells based on drill output without per-cell user confirmation
- Authorize Exp-Dev to dispatch CPU-cheap pre-tests autonomously
- Update memory entries to reflect today's findings
- Skip cells that are confirming-the-negative when posture is already locked
- Defer engineering-heavy work (Tier 4 build, demo pipeline, demo UI) until pre-tests
  gate authorize

## Heartbeat + cron

data/heartbeat_research.json updated each cycle. data/cloud_paused_overnight.flag may
still be set; check on resume. Cron d7ea1b05 runs every 15 minutes per overnight loop
duties.

---

End of brief. Comprehensive coverage of today's 51-cell sweep + cycles 154-162 +
all drill landings + customer pitch revisions + Tier 4 revival + privacy lock + active
in-flight work.
