# Research decisions -- 2026-05-31

## alt_edit_isolation_v1 -- 2026-05-31 (research:opus, with 3 Sonnet lit-scan subagents)

**Drill.** Alternative edit-isolation mechanisms to replace v290 U3 COW infeasibility (mem-amp 10.13x vs 4x target; throughput 6-7.5/s vs 50/s target). Origin: routing file `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` (R-COW-INFEASIBILITY R3). Token-efficient parallel-subagent dispatch: 3 Sonnet lit-scans covering (1) delta-encoding storage, (2) LSM lazy-replay cost, (3) CRDT + LSH-partial-COW hybrid.

**Outcome.** Four candidate architectures mapped; M1 (delta-encoding) and M2 (LSM lazy-replay) collapse to the same mechanism family viewed from write-path vs read-path angles. Recommended PRIMARY: **log-structured rank-1 store (M1+M2 unified)**. Mem-amp 1.5-3x at K up to N (formula 1 + 2K/N); throughput 8-12K q/s GPU projected; audit-by-construction synergy with KF-2 deletion-cert (log IS audit). Joint P_deflated 0.40-0.50 in 7-day engineering budget. Load-bearing empirical risk: FP drift at large K, known fix Kahan summation. SECONDARY: M3+M4 CRDT op-log + LSH-partial-COW hybrid (P_deflated 0.35); CRDT-alone REJECTED (P_deflated 0.25; depth>=2 retrieval incompatible with eventual-consistency semantics). Path D (substrate-native T2 PASS 45/45 cells) is the substrate-native generalization of CRDT-style per-op independence at the retrieval layer; M1+M2 generalizes the SAME mechanism to the W-mutation layer.

**Note path.** notes/research_alt_edit_isolation_v1_2026-05-31.md (9 external citations: Dong RocksDB CIDR17, Sarkar LSM-VLDB21, Tas-Boneh AFT23, Kanellis F2-VLDB24, Zhou lazy-views-VLDB07, Dayan Autumn-2023, Shapiro CRDT-SSS11, Almeida delta-CRDT-2016, Almeida CRDT-survey-ACM-2023; 7 internal cross-refs).

**Routing.** notes/strategy_request_to_strategy_alt_edit_isolation_2026-05-31.md (cap_map annotation recommendation + M2 smoke proposal at ~30 min CPU laptop; orchestrator decides timing).

**Next-drill candidate.** Once M2 smoke verdict lands: if HARD_PASS, drill on full N=4096 production design (MVCC layer + Merkle audit-tree integration + hot-set tier engineering cost). If HARD_FAIL on cosine (FP drift), drill on Kahan-variant retry. If HARD_FAIL on throughput, escalate to M3+M4 hybrid drill.

**Method note.** 3 Sonnet lit-scan subagents in parallel = ~25 min wall, ~83K tokens. Main thread (Opus) synthesis + routing files = small additional cost. Token-efficient pattern confirmed for lit-scan-heavy drills per user 2026-05-31 ask "use subagents and sonnet when you can - we want to be token efficient without sacrificing accuracy and efficiency." Per [[feedback-subagent-model-optimization]] reinforced.


## external_eval_integration -- 2026-05-31 (research:opus, evaluation + verification of user-shared external doc)

**Drill.** User shared external-Claude evaluation doc proposing 7 underweighted/missing research directions + cloud-routing discipline. Research session evaluated each claim, verified against cap_map v290/v291 + status_log + grep of recent decision logs, sorted into adopt/drop/reframe categories.

**Outcome.** 6 of 7 proposed drills confirmed as genuine gaps (substrate-augmented LLM absolute-quality vs LLM-only; storage efficiency production-scale; audit trail rotation; concept drift detection mechanism; substrate-LLM token-throughput latency budget; per-store latency for bursty writes). 1 drill (multi-substrate composition) conceptually valid but external doc's anchor was wrong (K=10 sharding reference was v282 CLOSED Op E cross-shard correlation probe; needs re-anchoring from scratch). 3 tactical recommendations DROPPED for factual error: (a) Modern Hopfield "N/2 vs G5/G6 reconciliation" was stale (v288 GPU-OOM resolved by v290 CPU path; today's C1 verdict pushed max_M=4N=65536 → v291 row LIFT yellow→green); (b) "Pattern B LLM integration" conflated Path B substrate-mechanism with undefined LLM-integration framework; reframe needed; (c) "$5 cloud spend at 50% budget" -- 08:52 event internally inconsistent ($7.50/$10=75% mathematically; label says 50%) AND 08:57 testbed event confirms Lambda not yet activated; likely telemetry-source bug; flag for testbed audit not crisis. Strategic shift confirmed (plumbing > physics at maturity; cloud is exception not default).

**Note path.** Routing file `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (6 new research-only rows; 1 needs-re-anchoring row; cloud-routing discipline; queue-weighting shift; immediate/near-term/medium-term/longer-term sequencing).

**Method note.** Pull-before-significant-work caught uncommitted state from other sessions; autostash + commit pattern verified clean. Verification grep against cap_map + status_log surfaced 3 factual errors that would have introduced wrong work into the queue if adopted verbatim -- value of "verify before adopting" loop demonstrated. ~12 min wall, low-token (no subagent dispatch needed; main-thread verification sufficient).

**Next-drill candidate.** Highest-leverage among the 6 new rows: LLM-integration latency budget characterization (Missing 7) -- cheapest scope, gates everything LLM-integration-flavored. Storage efficiency analysis (Missing 2) is the most independent (CPU-bound, doesn't depend on queue state). Substrate-augmented absolute-quality benchmark (Missing 1) is the longest scope but highest-leverage product test; that's the load-bearing one.


## substrate_llm_deep_integration_v1 -- 2026-05-31 (research:opus, 3 Sonnet lit-scan subagents)

**Drill.** User raised codebook-native LLM integration question -- substrate's bipolar codewords could potentially be consumed by an LLM WITHOUT text-tokenization round-trip; deeper than RAG. Research session dispatched 3 parallel Sonnet lit-scans: (A) vector-native LLM memory interfaces, (B) multi-hop reasoning offload from LLM to external structured memory, (C) cheapest engineering path on consumer GPU.

**Outcome.** Architectural primitives exist: 4 published patterns (RETRO chunked cross-attention, Memorizing Transformers gated kNN, Flamingo/Q-Former cross-attention bridge, DNC/Memory-Layers VSA-style memory layer). DNC's outer-product write `M = M + w v^T` is MATHEMATICALLY IDENTICAL to substrate `W = (1/N) sum v_l k_l^T` modulo bipolar quantization. NVSA (Hersche, Nature MI 2023) is closest published bipolar-bridge precedent BUT in OPPOSITE direction (neural -> bipolar VSA memory; not bipolar codeword -> LLM input). Recommended starting architecture: Pattern 3 (Flamingo/LLaMA-Adapter style) -- frozen 1-3B base LM (Phi-3-mini-3.8B MIT license) + ~27M-param bidirectional MLP bridge + substrate Path D depth=5 autonomous multi-hop. Three rescues for the query-decomposition bottleneck at 1-3B scale (Subagent B's binding research risk); Rescue C (substrate-autonomous depth-5 iteration; LLM emits single initial query) is most substrate-leveraging. 6 risks identified; 8GB VRAM hardware constraint is the binding feasibility item. Build plan: 4-6 weeks single-person; Week 1 feasibility smoke is cheap insurance against committing to full 4-6w on a blocker. P_deflated 0.40-0.45 on 24GB GPU; 0.25-0.30 on 8GB.

**Note path.** notes/research_substrate_llm_deep_integration_v1_2026-05-31.md (12 external citations, 6 internal cross-refs; build plan week-by-week; test design with LLM-only vs LLM+text-RAG vs LLM+substrate comparison + substrate-favored bespoke benchmarks).

**Routing.** notes/strategy_request_to_strategy_substrate_llm_deep_integration_2026-05-31.md (cap_map new research-only row "Substrate-LLM deep integration via codebook-native interface" at 0.30-0.45 P-band; 3 decision gates -- GPU resource / feasibility smoke / queue sequencing -- NONE auto-dispatched).

**Method note.** 3 Sonnet lit-scan subagents in parallel = ~30 min wall, ~110K tokens combined. Same pattern as morning's alt-edit-isolation drill; token-efficient pattern reconfirmed. The "intrinsic language" framing IS unpublished (NVSA opposite direction; substrate is the inverse case) -- this drill formalized the design space that was implicit in the user's question.

**Next-drill candidate.** Once user decides GPU resource + sequencing: Week 1 feasibility smoke (Phi-3-mini-4bit baseline on lm-eval-harness + bridge scaffold + smoke forward-pass) is the cheap-decisive-test that gates the full 4-6w commit. Alternatively: ship the 3 cheaper drills first (Missing 7 LLM-integration latency budget; Missing 2 storage efficiency; Missing 3 audit-trail rotation) per [[feedback-rescue-sketch-first-sequencing]] cheapest-first principle -- they inform the larger build.

**Routing update (later same turn, after user said "good experiment to run; route it to testbed and/or orchestrator to implement"):** Testbed handoff filed at `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`. The handoff:
- Hands the engineering build to testbed (Phi-3-mini loader + bridge MLP + substrate-codeword glue + Path D autonomous multihop + synthetic training data + lm-eval-harness + LLM+text-RAG baseline + 3 substrate-favored bespoke benchmarks)
- Pre-decides design choices testbed implements without re-arbitrating (base LM, adapter pattern, Rescue C multi-hop strategy, training procedure, discrete-gradient handling)
- BLOCKS work-start on 3 user-side decisions: (a) GPU resource 8GB/24GB/cloud; (b) commitment depth Week 1 smoke vs full 4-6w; (c) queue sequencing vs the 3 cheaper drills
- Surfaces 3 top risks (query-decomposition bottleneck, bridge-alignment training, 8GB VRAM ceiling)
- Per session-architecture session-ownership: I (research) wrote the handoff routing file; testbed implements; orchestrator coordinates cap_map decisions + cloud-cost approvals if applicable. I do NOT cross into experiments/ or testbed/ directories.

**Decisions resolved (user 2026-05-31 "agreed - lets get these tests going"; testbed UNBLOCKED):**
- (a) GPU: LOCAL remote desktop. Default assumption marsh@home 8GB; testbed verifies actual VRAM at Week 0 start; upgrade to fp16 + faster wall if >8GB. NO cloud spend authorized.
- (b) Commitment depth: Week 1 feasibility smoke FIRST as GO/NO-GO gate.
- (c) Queue sequencing: WEEK 0 = Missing 7 LLM-integration latency budget (gates architectural assumption that substrate Path D + bridge fit in LLM token window); WEEK 1 = substrate-LLM feasibility smoke; WEEKS 2-6 = full build if Week 1 PASS. Missing 2 + Missing 3 in parallel as CPU-bound work.

Testbed handoff updated inline with Week 0 Missing 7 spec (4 measurements + PASS/MIDDLE/FAIL criteria) + full 7-week sequence table. Testbed begins Week 0 upon reading.


## substrate_llm_interface_optimization_v1 -- 2026-05-31 (research:opus + 1 Sonnet drill)

**Drill.** User asked "should we do a research turn on how we can optimize this substrate interface with the LLM?" + raised eval-rigor concerns. Research session: (a) locked 9-section eval-rigor protocol into testbed handoff inline (Phase 2 QLoRA confounder control variant = highest-rigor item; 4-way comparison: LLM-only / LLM-only-control / LLM+text-RAG / LLM+substrate; pre-registration before Week 5); (b) dispatched 1 Sonnet ~45-min optimization drill on 6 axes (bridge depth, codebook representation, prefix-token granularity, Path D output, training schedule, inference-time tricks).

**Outcome.** Optimization drill identified 3 high-impact deviations from the original baseline that lift joint P_def by ~+0.18-0.29:
- D1 (P_def lift +0.08-0.12): Q-Former cross-attention bridge (8-16 query tokens per codeword, ~30-50M params) REPLACES 2-layer MLP. Cross-attention preserves per-hop posterior sparse-bit-structure that flat MLP destroys.
- D2 (+0.06-0.10): BLIP-2 two-stage training. Stage 1 bridge-alone with contrastive+ITM+ITG auxiliary losses; Stage 2 joint LLM-bridge with next-token loss. Stage 2 halts if discriminability drops below Stage 1 endpoint.
- D3 (+0.04-0.07): Per-hop codeword sequence as separate prefix-token groups (5 hops x 8 tokens = 40 prefix tokens at depth=5) REPLACES single converged codeword. CoT mechanistic evidence at 2.8B+ supports.

Also: hybrid bipolar-storage + continuous-bridge-projection (Codebook Option 3) supersedes the spec's continuous-relaxed-during-training (Option 2). Natural fit with Q-Former. Adaptive Path D depth + speculative substrate prefetch DEFER to Phase 2 (highest-leverage substrate-unique inference tricks; require substrate async API + LLM forward-pass hooks).

Updated joint P_def: 8GB GPU **0.43-0.55** (was 0.25-0.30); 24GB GPU **0.55-0.65** (was 0.40-0.45). Optimization closes most of the 8GB-vs-24GB gap; rate-limiter shifts from architecture-choice to wall-time-on-consumer-GPU.

**Note path.** `notes/research_substrate_llm_interface_optimization_v1_2026-05-31.md` (6 external citations: BLIP-2 + Memory Layers at Scale + MM1 + STE-ICML22 + CoT-mechanistic-Nag2025 + TeleRAG; 4 internal cross-refs; 5 open synthesis questions empirically resolvable in Phase 1).

**Testbed handoff updated.** Revised baseline section locked in (Q-Former + 2-stage training + per-hop prefix-token groups + hybrid codebook handling). Decision matrix table contrasting original vs revised spec; trainable param count +40-75% (57M -> 80-100M); Phase 1 wall +1 week (~16-32h -> ~40-80h on 8GB). Eval-rigor 9-section protocol (Phase 2 QLoRA confounder control variant, 4-way comparison, pre-registration, 3 bespoke benchmarks, etc.) also locked.

**Method note.** Single Sonnet subagent ~45 min wall, ~36K tokens. Token-efficient pattern reconfirmed: targeted optimization drill is cheaper than full re-architecting research drill; the 6-axis structure surfaces high-impact deviations without re-litigating the integration premise.

**Next-drill candidate.** Once testbed Week 0 Missing 7 latency measurement lands: if substrate Path D + Q-Former bridge fit within 50ms p99 (PASS gate), proceed to Week 1 feasibility smoke with revised baseline. Hold any further research drills until Week 1 / Week 2 empirical answers to the 5 open questions land.


## substrate_llm_aggressive_eval_v1 -- 2026-05-31 (research:opus; main-thread audit, no subagent)

**Drill.** User: "why are we deferring some of the most exciting things?" + "do another aggressive evaluation just to be safe." Systematic audit of every Phase 2 deferral, every cap_map-validated capability not yet exposed, every substrate-unique inference trick, every eval-rigor gap, and hardware fallback paths. No external lit-scan; pure cross-reference against cap_map v290-v291 + the two morning drills.

**Outcome.** Honest result: I was over-conservative on 3 deferrals and under-considered 3 ablations + 1 benchmark + hardware fallback spec. PROMOTIONS to Phase 1: (1) adaptive Path D depth based on LLM uncertainty (~1-2 days; fixed-max-prefix + zero-mask sidesteps the variable-length-prefix concern I cited as defer reason); (2) real-time learning during inference (~1 day; substrate writes correct-answer atoms during eval; demonstrates v191 ✅ Validated Tier-2 killer at 11x HARD-PASS threshold; the strongest empirically-validated substrate-distinctive feature); (3) mixed-confidence Path D retrieval (~2 days; surfaces Bayesian posterior entropy as confidence scalar; T1 calibration validated conservative-direction). ADDITIONAL: 3 ablations (static-vs-adaptive depth; per-hop vs single-converged; frozen-Stage-2 vs Phase-2-QLoRA), 5-tier hardware fallback ladder, test-set contamination acknowledgment, 4th bespoke benchmark "real-time-learn-then-query." STAYS DEFERRED with explicit reasons after re-audit: speculative prefetch (small payoff at our latency regime where LLM dominates), trainable VSA-layer (multi-month), Path E (niche use cases don't fit Phase 1), N=8192/16384 substrate (bridge unvalidated at higher input dim), compositional query construction (substantial design), concept drift (separate research drill needed), cross-modal (text-only Phase 1), edit-with-impact (SVD-cascade falsifier HARD_FAILED, parked).

Updated joint P_def for "working build delivering substrate-augmented gain on at least one benchmark AND demonstrating all substrate-distinctive killer features": 8GB **0.51-0.65** (was 0.43-0.55 post-optimization, 0.25-0.30 pre-optimization); 24GB **0.63-0.75**. Phase 1 budget extends from ~6 weeks to ~7-8 weeks; still inside 24-36mo competitive window per `project_substrate_strategic_inversion_48h_2026-05-26`.

**Note path.** `notes/research_substrate_llm_aggressive_eval_v1_2026-05-31.md` (full audit + reasoning + updated budget + P_def table; all internal cross-refs, no new external lit-scan since this is audit not lit-search).

**Testbed handoff updated.** AGGRESSIVE-EVAL ADDITIONS section locked in: 3 promotions, 3 ablations, 5-tier hardware fallback, eval-rigor additions, 4th bespoke benchmark spec, updated Phase 1 budget table, updated P_def table, explicit defer-reasons table. Open-questions list extended from 5 to 6 (added calibration-under-real-time-learning + uncertainty-threshold for adaptive depth).

**Method note.** Aggressive audit completed in main thread (no subagent dispatch needed); ~20 min wall. Pattern: when the work is critique-of-own-work + cross-reference against existing artifacts, main-thread audit is cheaper and more accurate than subagent dispatch (subagent doesn't have access to memory of own prior reasoning).

**Next-drill candidate.** None pending; the substrate-LLM Phase 1 spec is now fully scoped at the most-aggressive defensible Phase 1 scope. Testbed Week 0 Missing 7 latency measurement remains the next concrete action. Concurrently, the cheaper drills from morning's research-focus-expansion routing (Missing 2 storage efficiency; Missing 3 audit-trail rotation) can run in parallel as CPU-bound work; Missing 6 concept drift detection mechanism needs its own ~2-3w research drill before any engineering.


## capability_exploration_12_directions_audit_v1 -- 2026-05-31 (research:opus + 3 parallel Sonnet drills)

**Drill.** User shared external Claude evaluation proposing 12 substrate capability-exploration directions ("eventually deep dive into all of the below; can we start researching these"). Research session: (a) main-thread audit categorizing 12 directions into 4 ownership classes (substrate-physics / capability tests of validated mechanisms / new mechanism design / engineering integrations); (b) cross-reference against substrate-LLM build's 4 bespoke benchmarks revealed Directions 5/7/10 partially covered; (c) dispatched 3 parallel Sonnet drills on highest-leverage subset.

**Outcome.** 12-direction audit + 3 experiment designs:

- **Direction 1 (compositional binding algebra)**: production-scope envelope M=3-5×M_c, d={3,4,5}, K=500, 32-64 n_queries, 5 seeds, 20% memorization trap density. 4-protocol audit-trail verification (binding-op null test corrupts intermediate key → if accuracy stable, audit decorative). HARD-PASS comp accuracy ≥0.78 across depths + trap selection ≤0.08 + Path D-Path B margin ≥0.15. **P_def=0.42**. Substrate-physics moat-strengthening.

- **Direction 6 (hierarchical concept formation)**: cheap INSTRUMENTATION on EXISTING post-V2 24h substrate W; SVD spectral concentration as primary signature (algebraically guaranteed by predicate-sharing: sum_l v_l p^T = (sum_l v_l) p^T); semantic-ablation discrimination (substrate-physics claim predicts spectral structure survives substituting random value codewords). HARD-PASS σ_1/σ_2 > 3.0 + silhouette > 0.25 vs null < 0.10 + cross-relation transfer cos > 0.35. **P_def=0.35-0.50**. ~1 week analysis; no new experiment.

- **Direction 7 (Bet B 4-stage ret_A rescue)**: top candidate Hebbian replay of Stage-A atoms during Stage B/C/D writes at p_replay=20-30%. Closes KNOWN cap_map gap (ret_A=0.745 vs HARD-PASS threshold 0.80; missing 5.5pp; 5 stage A/B/C/D continual learning Tier-1 killer at 🟡 PARTIAL @ v189). HARD-PASS ret_A>=0.820 + ret_B/C don't drop below 0.800. **P_def=0.57** standalone Rank 1; **0.65** combined Rank 1+2 (replay + orthogonal codebook).

**Routing.** `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md` proposing 3 experiments + 3 cap_map row movements + sequencing recommendation (D7 first, D6 parallel, D1 last). Cumulative ~4-5 person-weeks engineering + ~5-10 hours compute; no cloud spend; compatible with parallel substrate-LLM build.

**12-direction prioritization (different from doc):**
- HIGHER than doc: Direction 7 (closes known gap; doc had MEDIUM, I argue HIGH); Direction 5 partial-duplication with build flagged not buried
- SAME as doc: Directions 1, 6 top-3
- DEFERRED with explicit criteria: Directions 3 (counterfactual; SVD-cascade falsifier HARD_FAILED predecessor parked), 8 (meta-learning), 9 (causal binding semantics), 11 (DP), 12 (universal approximator); NEXT-CYCLE candidates Directions 2 (analogical), 4 (cross-domain), 5 (few-shot generalization scoped distinctly from build), 10 (ML-pipeline-integration variant of explainability)

**Note path.** `notes/research_capability_exploration_12_directions_audit_v1_2026-05-31.md` (12-direction audit; 4-category split; overlap analysis; sequencing; deferral criteria).

**Method note.** 3 Sonnet drills parallel ~30 min wall, ~100K tokens combined. Pattern recommended for multi-direction prioritization drills: dispatch 3 highest-leverage in parallel; main-thread audit categorizes the broader N; routing synthesizes the 3 with concrete experiment designs. Avoids 12-simultaneous-drill padding per [[feedback-no-padding-experiments]].

**Next-drill candidate.** If orchestrator queues D7 + D6 + D1 per sequencing, no further research drills needed in this cycle. Watch for D7 verdict → potential Direction 7 cap_map row promotion 🟡 → 🟢; D6 verdict → new cap_map row; D1 verdict → new cap_map row at production-validated substrate-physics moat. After 1-2 of these land, Direction 5 (few-shot generalization scoped distinctly from substrate-LLM build) becomes the natural next research drill.


## substrate_as_reasoning_store_audit_v1 -- 2026-05-31 (research:opus main-thread audit + 1 Sonnet drill)

**Drill.** User shared external evaluation proposing 8 experiments for "substrate as memory and reasoning layer for context-limited LLMs" with reasoning-store framing distinct from current fact-store framing. Research session: (a) main-thread audit categorizing 8 experiments by overlap with in-flight/filed work; (b) identified ONE genuinely-new experiment (Exp 2 reasoning amortization); (c) identified ONE unaddressed prerequisite (reasoning-step bipolar-encoding scheme); (d) dispatched 1 Sonnet drill on the prerequisite.

**Outcome.** 5 of 8 experiments DUPLICATES of existing work: Exp 1 (reasoning chain storage + retrieval) substantively same as D1 compositional binding production-scope filed earlier today; Exp 3 (standard benchmarks) same as substrate-LLM Week 5 4-way comparison + 4 bespoke benchmarks already locked; Exp 6 (hybrid retrieval + LLM extension) same as Rescue C in substrate-LLM build; Exp 7 (compositional reasoning over stored chains) same as D1; Exp 8 (cross-session reasoning persistence) covered by V2 24h sustained workload COMPLETE + Pattern B service capability validation 5/5 PASS. 1 GENUINELY NEW experiment: Exp 2 reasoning amortization measurement (cost-economics scenario; ~2-3w + $50-100 API; uses Tier 2b LLM comparison harness already complete; Anthropic key already available). 2 DOMAIN-SPECIFIC DEPLOYMENTS deferred to pilot scoping: Exp 4 compliance corpus, Exp 5 real-time decision support.

The UNADDRESSED PREREQUISITE: HOW does a reasoning step become a single bipolar codeword in W? The doc's `key=(reasoning_context, current_state); value=(next_state, justification, derivation_method)` doesn't specify the encoding. The substrate-physics question: does reasoning storage REDUCE to "multi-hop fact retrieval where relation slot encodes inference-rule-applied" (Scheme A; what D1 already tests) -- OR -- require a DISTINCT binding mechanism for inference rules with universal-quantification semantics (Scheme B)? If Scheme A is sufficient, "reasoning storage" is a free framing relabel; if Scheme B is required, it's a distinct substrate-physics capability worth dedicated experiment.

Sonnet drill dispatched on the encoding-scheme question (Plate HRR, Eliasmith SPA, Kanerva SDM, recent HDC reasoning lit). When it returns, the answer determines whether reasoning storage needs its own experimental track or is subsumed by D1.

**The framing shift IS valuable** independent of the experimental verdict: cap_map is fact-framed throughout; reasoning-store framing opens compliance-customer positioning lane (verifiable DERIVATION chains, not just verifiable fact storage). ~30min annotation work for orchestrator. Worth adopting.

**Quantitative claims to deflate when communicating externally**: 10-25x cost / 100-1000x latency / 20-40pp accuracy are mostly standard RAG-vs-LLM numbers, not substrate-specific. Substrate-distinctiveness is in audit + edit-isolation + deletion-cert OVERLAY on amortization, not in amortization itself (any caching layer would amortize).

**Note path.** `notes/research_substrate_as_reasoning_store_audit_v1_2026-05-31.md` (8-experiment overlap audit; 5 duplicates surfaced with explicit cross-refs; encoding-scheme prerequisite drill dispatched; framing-shift recommendation). `notes/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (Exp 2 routing filed as new experiment proposal; HARD-PASS/HARD-FAIL/MIDDLE-BAND pre-registered; sequencing after D7 + Week 0, before D1).

**Method note.** Audit + 1 drill = ~25 min main-thread + ~40 min Sonnet (in flight). Pattern: when external doc proposes large N of experiments, cross-reference against in-flight work FIRST, then dispatch drills only on genuinely-novel questions. Avoids 8-simultaneous-drill padding per [[feedback-no-padding-experiments]] and [[feedback-no-smoke]] (don't validate by dispatch volume; validate by leverage and overlap).

**Next-drill candidate.** When encoding-scheme drill returns: if Scheme A sufficient, reframe D1 to optionally include reasoning-chain corpus (modest scope expansion); if Scheme B required, file a separate experiment for the distinct binding scheme. No additional drills pending in this cycle.


## reasoning_storage_2x_deep_synthesis_v1 -- 2026-05-31 (research:opus + 3 parallel Sonnet drills)

**Drill.** User: "re your research of storing reasoning chains on substrate - do 2x deep research" per [[feedback-2x-means-depth]]. Three parallel Sonnet drills covering complementary depth angles: (A) encoding-scheme question Scheme A vs B vs C (which scheme actually works in bipolar algebra?); (α) structured-key Path D analysis (does validated 32N envelope transfer to reasoning chains with structural constraints?); (β) operational worked example (explicit bipolar math through Path D depth=5 for one concrete reasoning chain).

**Outcome.** 2x deepening produced SHARPER + MORE HONEST picture than original "substrate-as-reasoning-store" framing:

- **Drill A**: Scheme B IS distinct from Scheme A under bipolar MAP-B algebra. Three-way binding `k_step = r_type ⊙ k_premise1 ⊙ k_premise2` decomposes EXACTLY via element-wise multiplication. Hersche NVSA Nature MI 2023 closest precedent (87.7% RAVEN). HARD-FAIL threshold: >~44K shared-rule-atoms at N=4096 (32N/3 from interference math). P_def 0.62 Scheme B unlocks capabilities Scheme A cannot.

- **Drill α**: Path D's 32N envelope DOES NOT transfer to structured-key reasoning chains without mitigation. P_def 0.35 unmitigated. De Marzo-Iannelli (Physica A 2023) + Amit-Gutfreund-Sompolinsky (1985) predict 5-25% capacity degradation with pattern correlation. Critical operational finding: depth-50 chain accuracy compounding -- 2% per-hop bias → (0.98)^50 ≈ 0.36 chain accuracy. Top mitigation: conclusion re-encoding via binding transform (Steinberg-Sompolinsky 2022 precedent), cost = 1 binding op per hop.

- **Drill β**: 6 OPERATIONAL GAPS that abstract framing hid. Most important: substrate is a RETRIEVAL primitive not REASONING primitive. After hop 1 retrieves v_BookA, substrate CANNOT autonomously construct q_1 = bind(v_BookA, v_author) -- the relation v_author comes from outside (LLM OR pre-stored rule-atoms via Scheme B Proposal 2). Other gaps: composition atom blowup (5-20x capacity at N=16384 for Proposal 1), control flow external, unbinding exact for stored but approximate after retrieval noise (depth >5 needs hop-by-hop cleanup), grounding gap, capacity saturation requires N≥65K for F=10K + R=100.

**The honest product framing** (replaces original doc's "substrate as reasoning store"):
> Substrate is a fast, algebraically-auditable fact store that can execute PRE-SPECIFIED reasoning chains with microsecond-per-hop latency and unbinding-based audit, WHEN orchestrated by an external agent that supplies the initial query and rule-activation markers. Open-ended reasoning remains LLM-driven; substrate's contribution is speed, isolation, and audit fidelity for retrieval steps.

This is substrate-distinctive but narrower than original framing. Competitive moat real (algebraic audit + ~1000x latency for pre-stored chains + edit-isolation) but substrate doesn't autonomously discover new chains.

**Updated P-bands:**
- Substrate Scheme B reasoning storage at N=16384 sub-saturation with re-encoding mitigation: **0.40-0.55** (cap_map new row)
- Substrate autonomously discovers new reasoning chains (original doc's strongest claim): 0.05-0.10 (very low)
- Substrate retrieval of pre-stored chains at ~1ms vs LLM CoT ~1s (latency): 0.85-0.95
- Algebraic audit via exact unbinding under MAP-B: 0.85-0.95
- Amortization economics for repeated reasoning patterns (Exp 2 still valid): 0.55-0.70

**Routing.** `notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md` (full synthesis; 6 operational gaps; mitigation rankings; pre-registered thresholds). `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` (concrete experiment design: 4 arms - Scheme B encoding exactness + structured-key Path D differential + conclusion re-encoding mitigation + shared-rule threshold sweep; ~3 weeks engineering + ~4-8h GPU, NO cloud spend; sequenced after D7 + Week 0, before D1 + amortization).

**Cap_map implications.**
- NEW row proposed: "Substrate reasoning-storage via Scheme B three-way binding" at 0.40-0.55
- UPDATE to substrate-product-feature row: "reasoning storage" scoped to PRE-STORED chains with external chain construction; not autonomous open-ended reasoning
- D1 (Scheme A compositional binding) STAYS as is — doesn't subsume Scheme B
- Amortization experiment (filed earlier today) STAYS as is — reframed as caching pre-stored Scheme B chains
- Substrate-LLM build's Rescue C is HONEST per worked-example finding; caveat-list update recommended

**Method note.** 3 Sonnet drills parallel ~45min each, ~135K tokens combined. Main-thread synthesis ~25min. The 2x deepening was significantly more valuable than the original encoding drill alone -- without drills α + β, the Scheme B encoding finding would have created FALSE CONFIDENCE that "Scheme B works algebraically therefore reasoning storage works." Drills α + β surfaced (a) structured-key envelope problem and (b) inter-hop key construction gap -- both load-bearing operational constraints. Pattern reconfirmed per [[feedback-2x-means-depth]]: 2x = depth not verification.

**Next-drill candidate.** None pending in this cycle. Watch for orchestrator to dispatch the reasoning-storage Phase 1 smoke; results will inform whether the cap_map row promotes to 🟡 (Arm 2 HARD-PASS or with-mitigation HARD-PASS) or stays 🔬 with documented limits (HARD-FAIL across multiple arms). If smoke passes, the amortization experiment becomes meaningful empirically. If smoke fails, reasoning storage row stays at 0.20-0.35 with mitigation tracks pursued in research.


## external_reviewer_feedback_integration -- 2026-05-31 (research:opus main-thread audit; no subagent)

**Trigger.** User shared the bridge design with an external technical reviewer (LLM-class reviewer per user disclosure); 3 substantive feedback points returned.

**Per-point evaluation:**

1. **STE/binarization risk**: reviewer correctly identified the train/test distribution-shift failure mode (tanh values hover near 0 during training to maintain gradient flow; sign() snaps violently at inference). Their proposed VQ-Bottleneck (VQ-VAE-style learned codebook of memory-query centroids with commitment loss) is a genuinely good alternative not in our spec. At inference, nearest-neighbor lookup matches training behavior → no distribution shift. Bonus: constrained output space likely improves training stability. Gumbel-Softmax suggestion is less clean fit (our query side is high-dim sign-thresholded continuous, not categorical distribution over codebook entries).

2. **Stage 1 hard-negative data construction**: reviewer correctly flagged that contrastive + ITM losses need HARD negatives to avoid shallow lexical-matching shortcuts. Original spec was underspecified ("paired examples from substrate population"). Their teacher-model-bootstrap suggestion (use Anthropic API to generate (query, GT trace, hard-negative trace, answer) tuples) maps cleanly to existing Tier 2b infrastructure + Anthropic key already available.

3. **Attention collapse + zero-out ablation diagnostic**: reviewer correctly flagged attention collapse risk at small/quantized base-LM scale (4-bit Phi-3-mini + 40 prefix tokens). Their proposed diagnostic (zero out intermediate hop prefix tokens; if LLM accuracy unchanged → LLM treating memory as single-hop lookup; if drops meaningfully → LLM is using the reasoning trace) is a sharp single-arm null test that wasn't in my Phase 1 spec.

**What the reviewer MISSED:** all substrate-side empirical risks (structured-key envelope from drill α; inter-hop key construction gap from drill β; 44K shared-rule-atoms threshold from drill A). Reviewer engaged with the LLM-side bridge but implicitly assumed substrate multi-hop primitive transfers to structured reasoning chains. These remain the higher empirical risks.

**Verdict:** "grain of salt" framing was too dismissive. 3 of 3 points substantive; 2 of 3 result in concrete updates to testbed handoff; 1 is a candidate architectural alternative (Tier 1.5 VQ fallback) worth specifying with trigger conditions.

**Action items implemented:**
- Testbed handoff updated with 3-section "EXTERNAL-FEEDBACK UPDATES" block:
  - Tier 1.5 VQ-Bottleneck fallback (decision authority delegated to testbed if trigger conditions fire)
  - Stage 1 hard-negative generation via teacher-model bootstrap (reuses Tier 2b infrastructure + Anthropic API)
  - Zero-out ablation arm added to Week 3 (alongside Ablation B; ~0 incremental wall)
- Open-questions list extended from 6 to 9
- Explicit annotation that reviewer did NOT touch substrate-side risks; those remain the higher empirical unknowns

**Method note.** Main-thread audit ~20 min; no subagent dispatch needed (the work is critique-of-external-input + cross-reference against existing spec). Per [[feedback-no-smoke]] honest engagement: reviewer was sharp on bridge engineering, blind on substrate physics; don't dismiss because non-human source AND don't over-defer because authoritative-sounding.


## llm1_token_prediction_2x_deep_optimization_v1 -- 2026-05-31 (research:opus + 2 parallel Sonnet drills)

**Drill.** User: "do a 2x deep research on this experiment to maximize possibility of passing" per [[feedback-2x-means-depth]] = operational depth on design choices that determine pass/fail. Main-thread audit FIRST identified 5 design issues with original spec (ambiguous encoding; hand-waved capacity; wrong retrieval primitive; weak baselines; worst-case open-domain Wikipedia). 2 parallel Sonnet drills then OPERATIONALIZED the open design questions: (A) encoding + capacity; (B) domain + baseline + criteria.

**Outcome.** The original LLM-1 spec was set up to fail (1M-token open-domain Wikipedia at ~2% coverage with weak baselines like uniform/random which are trivially beatable). 2x deep optimization produced a config with substantively better pass odds:

- **Drill A (encoding + capacity)**: Permutation binding recommended (vs Plate HRR bundling -- better capacity scaling for sequence encoding). N_substrate = 16384 (use modern Hopfield validated envelope per v297). N_ctx = 4-5 (NOT 8 -- interference quadratic in context length). |V| = 8000 BPE. PMI-weighted storage (medium-entropy contexts where Kneser-Ney handles worst, NOT random/frequency-weighted which give trivial coverage of patterns KN already captures perfectly). P_def 0.15 on open-domain Wikipedia. **Load-bearing open risk**: Zipfian function-word interference (frequent tokens appear in nearly every context, creating systematic off-diagonal interference in W not captured by random-pattern capacity analysis).

- **Drill B (domain + baseline + criteria)**: Python source code is the strongest domain (high structural regularity; coverage compounds in repetitive code; baseline n-gram models on code already report much lower perplexity than on natural language). Baseline set: MKN-5 (modified Kneser-Ney 5-gram via KenLM) + FAISS k-NN (closest competitor for product positioning) + tiny LSTM (~1-2M params) + GPT-2-small reference. Primary metric: Coverage-Weighted Top-1 (CWT1) + Coverage Fraction (CF) reported separately. Composite score = 0.40 × CWT1 + 0.20 × audit + 0.20 × edit-consistency + 0.20 × deletion-consistency (substrate-distinctive headline because baselines score 0 on the last 3 columns). P_def **0.37 raw CWT1 wins** vs full baseline set; **0.60-0.70 composite-score wins** even if losing CWT1.

**Joint P_def**: ~0.55-0.70 for at least one HARD-PASS band (raw OR composite-only); ~0.15-0.25 for HARD-FAIL across all bands.

**Honest framing**: substrate at 50K patterns on Python source has ~37% chance beating MKN-5 + FAISS k-NN on raw next-token accuracy; ~65% chance winning on composite that includes audit + edit + deletion. The composite-win case is NOT a consolation -- it shifts the strategic narrative from "substrate is a next-token-predictor" to "substrate is an auditable retrieval system that handles cases LLMs structurally cannot." Both outcomes are pre-registered as meaningful per [[feedback-no-smoke]].

**Cap_map implications.**
- NEW row proposed: "Substrate as next-token-predictor at limited-capacity (Python source)" at 0.30-0.45 raw / 0.55-0.70 composite P-bands
- Caveats: Python source code specifically; coverage fraction >= 0.10 is the meaningful-comparison threshold; Zipfian interference is the load-bearing open risk; single-hop classical retrieval NOT Path D depth=5

**Note path.** `notes/research_llm1_design_audit_v1_2026-05-31.md` (5 design issues with original spec). `notes/strategy_request_to_strategy_llm1_token_prediction_optimized_2026-05-31.md` (full optimized experiment spec; ~1-2w + ~1-2h GPU local; NO cloud spend; pre-reg HARD-PASS/HARD-FAIL/MIDDLE-BAND for both raw and composite tracks).

**Method note.** Main-thread audit FIRST (~25 min) surfaced design issues; 2 Sonnet drills parallel ~45 min wall each, ~90K tokens combined; main-thread synthesis ~25 min. Pattern reconfirmed: audit before drill dispatch when the input spec has hand-waved design choices; the audit informs which drills to dispatch (encoding + domain were the highest-leverage open questions; capacity math and baseline strength followed). Per [[feedback-2x-means-depth]] -- the drills did NOT re-verify "can substrate do next-token prediction" abstractly; they operationalized "WHICH config gives substrate fair shot" empirically.

**Next-drill candidate.** None pending. Watch for orchestrator queueing the experiment. If LLM-1 PASSES (either band), LLM-2 (compositional generation through binding) becomes the natural follow-on; LLM-3 (substrate-only language modeling at narrow scale) is contingent on LLM-2 PASS. If LLM-1 HARD-FAILs across both bands, the substrate-as-LLM-replacement direction is closed empirically; memory-layer positioning is definitively right.


## continuous_embedding_storage_2x_deep_synthesis_v1 -- 2026-05-31 (research:opus + 2 parallel Sonnet drills)

**Drill.** User shared 5 experiments (R-1 through R-5) framing substrate as "continuous, relational, compositional knowledge store with audit + edit-iso + deletion-cert + real-time learning"; "do 2x deep research." Per [[feedback-2x-means-depth]] = operational deepening on prerequisites. Main-thread audit FIRST identified: (a) the fundamental representation gap (substrate is BIPOLAR, NOT continuous); (b) overlap matrix (4 of 5 substantially duplicate existing in-flight work); (c) the load-bearing new question (continuous-to-bipolar projection scheme + moat preservation under projection). 2 parallel Sonnet drills on the prerequisite questions.

**Outcome.**

- **Drill A (projection schemes + capacity)**: SimHash (random Gaussian + sign) at N=16384 recommended. Native bipolar output, no training overhead, moat-compatible structurally. Recall@10 expectations: 75-82% unaided / 85-90% with over-sampling vs FAISS 92-95%. Learned hashing closes the recall gap (85-92%) BUT BREAKS the moat (audit no longer meaningful; learned hash codes not mutually quasi-orthogonal). Storage: 1.5x more compact than FAISS fp32. Latency: 10-20x faster via XOR-popcount. **Strict-moat P_def 0.10 (near-impossible because projection is irreversible)**; operational-moat P_def 0.30 with mitigations.

- **Drill B (per-property moat analysis under projection)**:
  - **Real-time learning SURVIVES INTACT** (P_def 0.92) -- write mechanism unchanged
  - **Algebraic audit DEGRADES** (P_def 0.70 with sha256 side-data mitigation) -- decomposes to projected codeword lineage, not original embedding; mitigation: store sha256(x) at write time, +32 bytes per entry
  - **Edit isolation DEGRADES for semantic neighbors** (P_def 0.40 unmitigated, 0.55-0.70 mitigated) -- semantically similar embeddings → bit-close codes → collateral edit propagation; mitigations: higher N, learned binarization with orthogonalization, OR VQ-style discrete codebook
  - **Deletion-cert DEGRADES/BREAKS for compliance** (P_def 0.35 unmitigated, 0.50-0.60 mitigated) -- collision ambiguity may erase wrong user's data; mitigation: sha256 + W_seed + timestamp in cert
  
  Joint full-moat-with-mitigations: **P_def 0.35-0.45**.

**The honest product reframing** (replaces doc's "substrate is a continuous, relational, compositional knowledge store"):
> "Substrate is an audit-grade vector store + reasoning sidecar. Native representation is bipolar codewords with algebraic moat. Continuous embeddings ingested via SimHash projection layer with documented moat-degradation characteristics. Real-time learning intact; algebraic audit + edit-iso + deletion-cert operate at projection layer with side-data mitigations for compliance."

Competitive positioning that survives: trades ~10-15pp recall for algebraic moat + 10-20x retrieval speed + 1.5x storage compactness + real-time updates without rebuild. Honest narrower than doc's "fundamentally new kind of system" framing.

**Overlap audit verdict (5 → 1)**: R-1 is the ONE genuinely-new experiment. R-2/R-3/R-5 are continuous-projection ANGLES on already-filed work (D1 compositional binding, reasoning storage Phase 1, T2 edit isolation validated). R-4 is essentially substrate-LLM Phase 1 Week 5 4-way comparison already locked.

**Routing.** `notes/strategy_request_to_strategy_continuous_embedding_storage_2026-05-31.md` -- ONE consolidated experiment `continuous_embedding_storage_substrate_v1_n16384` with 4 arms (retrieval recall, audit preservation, edit isolation under projection, deletion cert under projection). HARD-PASS/HARD-FAIL/MIDDLE-BAND pre-reg for each arm. ~2 weeks + ~2-4h GPU. NO cloud spend. 4 of 5 proposed experiments REJECTED with explicit cross-refs to in-flight work.

**Cap_map implications.**
- NEW row proposed: "Substrate as audit-grade continuous-embedding store via SimHash projection" at 0.35-0.45 (full-moat) / 0.55-0.65 (retrieval-only) bands
- UPDATE substrate-product-feature row with honest reframing: NOT "stores any continuous representation"; INSTEAD "audit-grade vector store with documented moat-degradation under projection"
- D1, reasoning storage Phase 1, T2 edit isolation, Week 5 4-way comparison ALL STAY as is -- the continuous-projection question doesn't subsume them; it complements

**Method note.** 2 Sonnet drills parallel ~45 min each, ~90K tokens combined. Main-thread audit + synthesis ~30 min. Pattern reconfirmed per [[feedback-2x-means-depth]]: the deepening was on the underlying ENGINEERING QUESTION (projection scheme + moat preservation), NOT re-running the 5 experiments as separate drills. Per [[feedback-no-padding-experiments]] not dispatching 5 drills when 2 deeper drills resolved the prerequisite. The doc's 5 experiments were product-positioning questions; the substantive empirical question that gated all 5 was the projection question.

**Next-drill candidate.** None pending. If continuous-embedding storage experiment HARD-PASSes, substrate has a defensible "audit-grade vector store" product category. If HARD-FAILs, "continuous embeddings" direction closes and memory-layer / bipolar-atom / reasoning-storage positioning remains the strategic focus. The R-4 RAG-replacement question is already covered by substrate-LLM Phase 1 Week 5 verdict.


## hierarchical_substrate_2x_deep_synthesis_v1 -- 2026-05-31 (research:opus + 3 parallel Sonnet drills)

**Drill.** User shared hierarchical substrate proposal ("galaxy of substrates" architecture; meta-substrate stores leaf shards as facts; 6 proposed experiments H-1 through H-6 over 3-4 months). "2x research where relevant" per [[feedback-2x-means-depth]] = operational depth on prerequisites. Main-thread audit FIRST identified 5 issues with doc's framing (capacity math hidden assumption; v282 closure not addressed; vs-single-big-N comparison missing; LLM-integration latency budget; loose brain analogy). 3 parallel Sonnet drills on highest-leverage questions: (A) meta-storage scheme; (B) hierarchical latency vs single-big-N; (C) cross-shard composition mechanism.

**Outcome.** The hierarchical substrate architecture is architecturally interesting but NOT strategically superior to single-big-N within 12-month horizon. Doc's 6-experiment program substantially overscoped.

- **Drill A (meta-storage)**: Scheme A pointer atom recommended; clean algebra + full moat preservation; 26-262x capacity advantage under CLEAN partition, 5-15x under messy real-domain partition. Scheme B not closed by v282 (first-order vs second-order distinction); K_leaf < ~4K limit. Scheme C complement not replacement. **P_def 0.40** for ≥5x effective capacity advantage at equivalent engineering effort. Critical honest finding: hierarchy's advantage MOST RELIABLE on operational isolation axis (independent audit/delete per shard), NOT raw capacity.

- **Drill B (latency + single-big-N)**: HARD-PASS NOT MET at matched parameter count -- hierarchy wins 1.5 of 4 criteria. **Modern hardware kills "too big to fit" argument**: BF16 N=65K = 8.6GB fits H100 alongside Phi-3-mini. **P_def 0.18** for hierarchy strategically superior in 12-month horizon. Hierarchy worth Phase 2+ ONLY when (capacity >500K AND latency ≤20ms AND multi-tenancy) all hold; 24-36mo not 12mo. CHEAPER alternative surfaced: amortized prefetch (substrate query 2-5 tokens ahead) decouples latency from per-token budget; lower eng cost than full hierarchy.

- **Drill C (cross-shard composition)**: v282 Op E second-order closure EXCLUDES Mechanisms 3+4 (algebraic cross-shard binding, aggregate query bundling). Mechanism 2 (sequential multi-hop with LLM bridge) is ONLY substrate-deployable option; structurally equivalent to substrate-LLM build's Rescue C extended across shard boundaries -- NOT a fundamentally new architecture. **P_def 0.35-0.42**. Subtle: v282 closure applies to Tr(W_i^T W_j) specifically; circular-convolution binding over ACTIVATION VECTORS may escape closure -- worth targeted falsification before retiring Mechanism 3.

**The honest product reframing** (replaces doc's "galaxy of substrates with multiplicative capacity scaling"):
> "Single-big-N substrate is the 12-month strategic path. Hierarchical extension is a Phase 2+ ambition contingent on capacity demand >500K + multi-tenancy requirements; deferred with explicit crossover criteria."

The product moat that actually differentiates substrate (across ALL morning's research drills): real-time learning, algebraic audit via element-wise unbinding, edit isolation, cryptographic deletion certificates, 10-20x retrieval speed vs FAISS, 1.5x storage compactness. These DON'T require hierarchy.

**Rescoped experimental program** (1-2 experiments + deferred items; not 6):
- H-1-LITE (Scheme A pointer routing smoke at S=100): ~1 week, 1 GPU hour. HARD-PASS top-1 recall@1 ≥0.97.
- ALT-experiment (BF16 single-N=32K/65K capacity probe): ~1 week, 2-4h GPU. Tests whether single-big-N matches hierarchy capacity within 12mo. Strategically higher value than H-1-LITE because it tests whether hierarchy is even necessary.
- H-2 REJECTED: Mechanism 2 = Rescue C extended; same pattern as substrate-LLM build + reasoning storage Phase 1.
- H-3 REJECTED: cheaper version = ALT-experiment BF16 single-N.
- H-4 REJECTED: 3-level hierarchy = 4TB GPU footprint multi-machine; Phase 3+.
- H-5 REJECTED: edit isolation already validated at bipolar atom level (T2 v290 45/45 cells); shard-level inherits via routing layer.
- H-6 DEFERRED: multi-tenancy is the strongest unique-to-hierarchy advantage; pilot-deployment-driven scoping.

**Explicit crossover criteria** for revisiting hierarchy: capacity demand >500K AND per-token latency ≤20ms AND multi-tenancy product requirement. Until 2 of 3 hold, single-big-N + amortized prefetch is the right path.

**Routing.** `notes/strategy_request_to_strategy_hierarchical_substrate_2x_synthesis_2026-05-31.md` -- ONE cap_map row proposed at 0.30-0.45 P-band; rescoped to 2 experiments; 4 rejections with cross-refs; 1 deferral with crossover criteria.

**Cap_map implications.**
- NEW row proposed: "Hierarchical substrate via Scheme A pointer routing (multi-tenant operational isolation)" at 0.30-0.45
- UPDATE substrate-product-feature row: explicit "single-big-N is 12-month strategic path; hierarchy deferred Phase 2+"
- Document v282 Op E closure explicitly in the hierarchy row caveat list (Mechanisms 3+4 excluded; Mechanism 2 = Rescue C extended)

**Method note.** 3 Sonnet drills parallel ~45 min each ~130K tokens combined. Main-thread audit + synthesis ~35 min. Per [[feedback-2x-means-depth]] -- drills did NOT re-verify the 6 proposed experiments separately; they OPERATIONALIZED the prerequisite engineering questions (meta-storage scheme + single-big-N comparison + cross-shard composition mechanism). Per [[feedback-no-padding-experiments]] -- not dispatching 6 drills when 3 deeper drills resolved the prerequisites. The doc's 6 experiments were product-positioning questions; the substantive empirical questions that gated all 6 were the 3 drilled.

**Next-drill candidate.** None pending. Watch for orchestrator queueing H-1-LITE OR ALT-experiment. If ALT BF16 single-N at N=32K/65K HARD-PASSes (max_M ≥ 8N at N=65K), hierarchy direction can stay deferred indefinitely. If ALT HARD-FAILs (capacity scaling breaks at larger N), hierarchy becomes the necessary path and full H-1 + H-6 multi-tenant experiments get prioritized.
