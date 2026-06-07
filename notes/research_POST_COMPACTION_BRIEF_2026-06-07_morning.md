# Research Post-Compaction Brief -- 2026-06-07 morning (UPDATED ~09:30)

Read this first on context recovery.

## North star (locked yesterday evening)

The project goal is a functional system that empirically beats LLMs of comparable size on
chosen benchmarks. Privacy, audit, multi-hop reasoning, continual learning, and adversarial
robustness are the planned advantages. 5-7 weeks to v1 demo per the timeline.

## Architectural story (significantly evolved since the earlier brief)

The morning's empirical work substantially clarified the production architecture:

**Two-encoder architecture is now locked.** Sentence-transformer (bge-small-en-v1.5 at 33M
parameters) for the semantic retrieval ranking job. Llama-3.2-1B at L15 left-pad for the
associative-memory KEY job (substrate W matrix via pseudoinverse). The methodology rule
I tried to lock this morning ("MiniLM retired") was wrong-directioned; the two-encoder
architecture is structurally correct, not just empirically observed.

**Manifold confinement unifies two seemingly separate problems.** Llama-1B L15 embeddings
live on a ~30-dimensional manifold inside the 2048-D ambient space (PR=29.4, TwoNN=33.6,
strong consensus). This same ~30-dim confinement explains BOTH the privacy leakage profile
AND the HotpotQA retrieval failure. Llama-base is genuinely unfit for semantic ranking
because semantics are crammed into 30 dimensions. The PCA bottleneck projection (compress
below manifold dim) is the candidate privacy mitigation; sweep at d in {25, 20, 15, 10, 5}
is routed.

**Retrieval recipe for v1 demo is clarified.** bge-small recall@10 = 0.74; the right facts
ARE in the top-10 pool. The 0.70 recall@2hop target is NOT a coverage problem; it's a
multi-hop REASONING / DECOMPOSITION problem. Question decomposition is the missing
mechanism, not encoder upgrade.

**Substrate-native decomposition path is the cleanest v1 recipe.** Pattern B + the
substrate's existing K-hop algebra can do question decomposition via VSA unbinding,
without an LLM call. Light parsing (spaCy NER) is the cheapest decomposition path; SRL is
the more accurate alternative. If either parses 2-hop questions well, the substrate
handles decomposition algebraically and the LLM only generates the final natural-language
answer. This is a clean north-star differentiator: substrate decomposition is deterministic
and auditable; 1B LLM decomposition is statistical and unreliable.

## In-flight drills (none currently)

All four drills from earlier this morning have landed (privacy mechanism reopening,
synthetic-vs-real gap, storage unconventional mechanisms, sparse-W alternatives) plus the
late additions (LSH fanout reduction, Pattern B compositional storage, retrieval encoder
selection). No research-side drills currently in flight.

## In-flight Exp-Dev cells (extensive)

Manifold bottleneck sweep: d in {25, 20, 15, 10, 5} on Llama+MarianMT harness. Tests
whether PCA bottleneck recovers HIPAA-grade absolute privacy claim.

Retrieval decomp pre-tests: PRE-TEST A is NER entity-bridge decomp (HARD-PASS at
recall@2hop >= 0.65 means substrate-native decomposition with NER alone). PRE-TEST B
is gte-base coverage comparison. PRE-TEST C (BM25+bge hybrid) is conditional backup.

Pattern B full exploration program: 8 cells across 3 phases. Phase 0 SRL pre-test gates
engineering decision. Phase 1 is the algebra battery (5 cells). Phase 2 is integration
validation including end-to-end benchmark head-to-head. Phase 3 is user decision review.

Storage cells: modern Hopfield at production N (already HP at N=4096-16384 per cycle 155),
predicate ratio audit (cycle 155 MID; rescue paths via P-sweep), 4-bit quantization (cycle
155 HP at N=8192-16384), tensor train decomposition (drill flagged as not foreclosed by
Marchenko-Pastur; worth separate pre-test).

Privacy mechanism cells: F/B/A paths to be re-run on the corrected Llama+MarianMT harness
once Exp-Dev sets it up. Note that the manifold sweep IS the leading mechanism candidate;
F/B/A may all fail if manifold bottleneck works.

LSH problem resolved: cycle 156 confirmed L2 normalization alone drops B_eff from ~40 to
6.9 (well below the <20 target). Cone correction was counterproductive. No additional
LSH work needed for v1.

HotpotQA full-substrate cells: confirmed bge-small recall@2hop = 0.42 / recall@10 = 0.74.
Substrate whitening adds no lift on bge-small (encoder already calibrated). K-hop alone
adds nothing on 2-hop. The decomposition pre-tests now drive the next steps.

## Testbed in flight

CELL-3 (Wikipedia distillation, 22M student) and CELL-4 (HP-12 V2 at 100K facts) launches
pending. Multi-head H=2 setup check on CELL-4 before launch.

## Cycle progression this morning

Cycle 153 founded the causal reasoning cluster (PP-81, PP-81a, PP-82). Rank-1 downdate
confirmed algebraically equivalent to Pearl's do() operator.

Cycle 154 locked GDPR at EDPB Position 3, confirmed Chain 3 cross-shard K-hop at K=12
with 98.7% recovery, validated the 50-line filter at T=0.5, validated SQL COUNT native at
0.9% relative error, validated online concept extension via sparse-KEY vocab injection.

Cycle 155 validated 4-bit quantization at production scale, validated modern Hopfield at
N=4096-16384 (the v3 storage path), validated CRDT bundle order-independence, validated
bundle relay at 99.9% recall with 50% node dropout. Closed sparse-W compression path
(0.75+ sparsity collapses recall). Llama eigenspectrum disproved the anisotropy hypothesis.
Privacy line accumulated 7 LVH catches (all attack-harness mismatches; URGENT enforcement
filed).

Cycle 156 resolved LSH B_eff via L2 normalization alone (cone correction counterproductive),
established HotpotQA baseline (substrate lifts 15% to 20%; bottleneck is encoder not
routing), disqualified Llama-1B as retrieval encoder, validated CRDT G-counter integer
aggregates, confirmed LoRA InfoNCE retains 66% retrieval while SFT collapses to 0.3%
(SFT banned for retrieval).

cap_map v477. HONEST count 1158. LVH 257. Portfolio 32+82.

## v1 demo recipe (current best understanding)

Encoder: bge-small-en-v1.5 (33M parameters) for semantic retrieval ranking.

Substrate KEY: Llama-3.2-1B at L15 left-pad for the W matrix associative-memory job
(potentially with PCA bottleneck projection if manifold sweep validates the privacy
mitigation).

Decomposition: substrate-native via Pattern B + K-hop unbinding if PRE-TEST A (NER) or
Pattern B Phase 0 (SRL) passes. Fall back to LLM-decomp if both fail.

Composition: substrate K-hop algebra with confidence filter at T=0.5 (cycle 154 mechanism).

Generation: Llama-3.2-1B for final natural-language answer conditioned on substrate
retrieval.

Audit + privacy: cryptographic Merkle proofs per fact + bitemporal as-of queries + GDPR
EDPB Position 3 erasure + qualified privacy claim (unless manifold bottleneck restores
absolute HIPAA-grade).

Storage compression for production: 4-bit quantization (4x reduction) + modern Hopfield
at lower N (additional 4-16x). Sparse-W closed. Realistic v3 per-fact cost lands at
~1-3 KB. Pattern B compositional reuse could amortize this further for KBs with
concept reuse.

## Customer-facing claim posture (updated)

GDPR right-to-erasure: STRONG at EDPB Position 3.

Bitemporal + as-of queries: STRONG (composition validated).

Reactive subscribe with cryptographic delivery: STRONG.

Causal/counterfactual reasoning with real-time replay: STRONG.

Multi-step verifiable reasoning K=12+: substrate K-hop algebra validated; retrieval recipe
in progress (depends on decomposition pre-test outcomes).

SQL aggregation: COUNT native at <1% error; SUM native; G-counter HP for distributed
integer aggregates; AVG needs DuckDB.

Privacy: QUALIFIED pending manifold bottleneck sweep. About 2x relative vs RAG with
rate-limit posture and full audit. Absolute HIPAA-grade recovery possible if PCA
bottleneck at d ~= 25 holds retrieval F1.

Storage efficiency: NOT a current pitch. 286 KB per fact today; v1 with quantization
~5-16 KB; v2 with modern Hopfield + 4-bit + entropy coding ~1-3 KB. Pattern B could
further reduce via concept amortization.

Distributed systems story: CRDT bundle + G-counter order-independent merges, bundle relay
99.9% at 50% dropout, LSH routing fixed by L2 normalization, all without 2PC. Clean.

## Active feedback rules

Plain language no hype: real-world consequences first; no emoji-as-emphasis; no superlatives.

Concise cycle summaries: 10-15 lines prose, no tables/emoji headers; long-form in research
notes not chat replies.

Drill pre-test required: every drill prediction that depends on synthetic or proxy setups
requires a 1-2 hour production-encoder pre-test before engineering authorization. The
methodology drill from this morning's negative-results 2x established this rule.

Two-encoder architecture (clarification this morning): MiniLM/bge/gte/e5 are NOT retired
for semantic retrieval; only for ZKL/privacy-geometry tests. Llama-1B is for KEY job only.

North-star alignment: every drill and decision should advance the LLM-comparison demo
target.

Capability tracking SSOT: history.md tail + strategy_decisions tail + capability_scorecard.

## What I'm working on next

Standing for the empirical results from Exp-Dev's many in-flight cells:
- Manifold bottleneck sweep (highest immediate priority; resolves privacy story)
- Retrieval decomp PRE-TEST A + B (resolves substrate-native decomposition story)
- Pattern B Phase 0 SRL pre-test (gates Pattern B engineering)
- Pattern B Phase 1 cells (if Phase 0 passes)

When results land, synthesize each in plain prose 10-15 lines and update the v1 demo
recipe accordingly. After the substrate-native decomposition recipe is resolved, the
benchmark suite work (Authorization 7) becomes concrete — run MuSiQue / LongMemEval /
FActScore with the final recipe and measure head-to-head.

## Memory entries to load on resume

- north_star_functional_system_beats_LLMs.md
- overnight_loop_research_session.md
- feedback_plain_language_no_hype.md
- feedback_cycle_summaries_concise.md
- feedback_drill_pretest_required.md (extended this morning with two-encoder clarification)
- production_architecture_locked_2026-06-07.md
- phase2_5x_chains_gold_findings_2026-06-07.md

## Heartbeat + cron

data/heartbeat_research.json updated each cycle. Cron d7ea1b05 runs every 15 minutes.
data/cloud_paused_overnight.flag may still be set; check on resume.

---

End of brief.
