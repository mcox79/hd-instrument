# exp_dev hand-off -- research: speculative draft maximization 2x

Filed-by: research sub-agent (2026-06-09)
Trigger: d:/AI/hd-instrument/notes/research_drill_speculative_draft_maximization_2x_2026-06-09.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual experiment scripts,
sweep grids, queue assignments, and pre-reg validation autonomously. Pre-reg bands below
are research recommendations only -- exp_dev validates and may refine before dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Alpha >= 0.65 is empirically validated on KB-factual queries. The 2x drill has resolved
the speedup ceiling analysis and identified the dominant levers:

1. ALPHA IMPROVEMENT is the highest-leverage path. To reach 3x+, need alpha ~ 0.80.
   Compositional multi-hop drafts are the mechanism most likely to push alpha from 0.65
   to 0.75+.

2. ADAPTIVE K (not fixed K extension) is the highest-leverage engineering change at
   current alpha=0.65-0.73. Fixed K=10 vs K=5 is marginal at alpha=0.65 (formula shows
   only ~2% more accepted tokens). Adaptive K avoids overhead waste on low-confidence
   positions.

3. CONFIDENCE-GATED ROUTING (PP-107) is a free win on mixed workloads by eliminating
   wasted verification overhead on low-KB-confidence queries.

4. MULTI-TIER ARCHITECTURE (KB-direct / KB-spec-dec / KB-context / LLM-only) is the
   production pattern that makes the architecture commercially coherent.

The 2x note also resolves the HARDWARE REGIME question: the RTX-class runner (memory-
bandwidth-bound) is the right hardware for KB-spec-dec. H100/GH200 may show near-zero
speedup due to bandwidth saturation. Do NOT evaluate frontier hardware until runner
baseline is confirmed.

---

## Anchor candidates (rank-ordered by P_actionable x pre-requisite order)

### 1. DECISIVE-1-ADAPTIVE-K (HIGHEST PRIORITY, CPU/local GPU)

Anchor pointer: Research note Section 2.2 (adaptive K formulation) + Section 7 anchor list
Substrate-product reading: Adaptive K uses PP-107 confidence to gate draft length
  dynamically (stop at position t if confidence < theta_stop, continue up to K_max
  otherwise). At alpha=0.65, fixed K=10 is barely better than K=5 (formula shows +2%
  more accepted tokens). Adaptive K should produce equivalent accepted-token rate while
  saving ~30-40% of overhead on low-confidence positions. Expected gain: 15-25% speedup
  improvement over fixed K=5 baseline.
Tier hint: CPU or local GPU. Run on 100 KB-factual longform queries (200+ tokens). ~2-3 hr.
Why-now: This is the highest-leverage single engineering change available at current alpha.
  No new infrastructure required -- uses existing PP-107 confidence scores and K-loop.

Pre-reg bands (research recommendation):
  HARD-PASS: adaptive K achieves >= 15% speedup improvement over fixed K=5 on 200-token+ responses
  MIDDLE-BAND: 5-15% improvement (positive but modest; keep adaptive K, not decisive)
  HARD-FAIL: < 5% improvement OR adaptive K is slower than fixed K=5 (overhead
             of confidence evaluation dominates; revert to fixed K, investigate confidence latency)

Key pre-reg sub-condition: also measure whether PP-107 confidence correlates with
per-position acceptance rate (Pearson r). If r < 0.20, adaptive K has no theoretical
basis and HARD-FAIL regardless of speedup measurement.

### 2. DECISIVE-1-K10 (SECOND PRIORITY, runs in parallel with #1)

Anchor pointer: Research note Section 2.1 (K extension analysis) + Section 1.3 ceiling table
Substrate-product reading: At alpha=0.73 (the upper end of measured range), K=10 gives
  2.96x vs 2.68x at K=5 (formula: +0.28x improvement). At alpha=0.65, the gain is near
  zero (formula shows marginal). This anchor determines which alpha regime we are actually
  operating in by measuring whether K=10 produces the predicted improvement.
Tier hint: CPU or local GPU. Run on same 100-query set as DECISIVE-1-ADAPTIVE-K. ~1-2 hr.
Why-now: If empirical K=10 shows the predicted +0.28x gain at alpha=0.73, it confirms
  the alpha estimate and validates the speedup formula. If K=10 shows no gain over K=5,
  the effective alpha is closer to 0.60-0.65 and adaptive K becomes more important.

Pre-reg bands:
  HARD-PASS: K=10 achieves >= 0.20x more speedup than K=5 on 200-token+ responses
  MIDDLE-BAND: 0.05-0.20x improvement (marginal; alpha is near 0.65 lower bound)
  HARD-FAIL: K=10 no better than K=5 (effective alpha < 0.60; adaptive K is the only path)

### 3. DECISIVE-1-CONFIDENCE-GATED (THIRD PRIORITY, CPU, fast)

Anchor pointer: Research note Section 4.2 (confidence-weighted drafts) + Section 5.4 (tier routing)
Substrate-product reading: On a MIXED dataset (50% KB-covered factual, 50% general chat),
  ungated KB-spec-dec wastes verification overhead on the ~50% of queries where alpha is
  near 0. Confidence gating (disable KB drafting when PP-107 confidence < theta_gate)
  preserves speedup on KB-covered queries while avoiding overhead on uncovered queries.
  Expected gain on mixed workload: 20-35% better average speedup vs ungated.
Tier hint: CPU. ~1-2 hr. Can run in parallel with anchors 1 and 2.
Why-now: Most production deployments are mixed workloads. The gating overhead is near-zero
  (PP-107 confidence is already computed in the KB pipeline). This is a free win if the
  confidence-alpha correlation holds.

Pre-reg bands:
  HARD-PASS: gated version achieves >= 0.3x better average speedup on mixed 100-query set
  MIDDLE-BAND: 0.1-0.3x improvement
  HARD-FAIL: gated version no better than ungated on mixed queries (PP-107 confidence
             does not predict alpha; gating provides no benefit)

### 4. DECISIVE-1-COMPOSITE (FOURTH PRIORITY, gated on adaptive-K passing)

Anchor pointer: Research note Section 5.5 (compositional draft sequences)
Substrate-product reading: Multi-hop compositional KB drafts (Datalog^neg chain queries
  that resolve entity -> relation -> entity -> attribute in one KB traversal) should
  produce HIGHER alpha than simple entity drafts because the LLM's generative path
  naturally follows the same compositional reasoning chain. Expected alpha improvement:
  0.65-0.73 (simple) -> 0.70-0.80 (compositional). This is the path to 3x+ speedup.
Tier hint: CPU or local GPU. Requires KB with multi-hop relations indexed. ~2-3 hr.
Why-now: Compositional draft is the highest-ceiling alpha improvement mechanism available
  in the structured KB. If it works, it pushes alpha into the 3x speedup regime.
  If it fails, the alpha ceiling at current KB structure is confirmed at ~0.73.

Pre-reg bands:
  HARD-PASS: compositional drafts achieve alpha >= 0.72 vs alpha=0.65 for simple drafts
             (>= 0.07 absolute improvement, expected to drive +0.3x speedup)
  MIDDLE-BAND: alpha 0.67-0.72 (positive but small; confirms direction, warrants
               further multi-hop KB expansion before committing engineering)
  HARD-FAIL: compositional drafts achieve no higher alpha than simple entity drafts
             (Datalog^neg composition does not follow LLM reasoning path;
              multi-hop KB expansion for spec-dec purposes is not worth investing)

### 5. DECISIVE-1-MULTI-TENANT (FIFTH PRIORITY, correctness gate, parallel)

Anchor pointer: Research note Section 5.1 (multi-tenant scaling) + Section 5.2 (GDPR erasure)
Substrate-product reading: Per-tenant KB draft isolation must hold under speculative
  decoding load. Zero cross-tenant draft tokens is the only acceptable outcome (binary
  pass/fail). Additionally: verify that per-tenant KB lookup overhead does not degrade
  speedup by > 10% vs shared KB at 100 simulated tenants.
Tier hint: CPU. ~1-2 hr. Run in parallel as a correctness invariant, not a speedup gate.
Why-now: A single cross-tenant draft token is a v1 multi-tenant launch blocker.

Pre-reg bands:
  HARD-PASS: zero cross-tenant draft tokens AND speedup degrades < 10% vs single-tenant
             at N=100 simulated tenants
  MIDDLE-BAND: speedup degrades 10-25% with N=100 tenants (KB lookup optimization needed
               before multi-tenant deployment, but architecture is correct)
  HARD-FAIL: any cross-tenant draft token detected (architectural isolation redesign
             required; block multi-tenant v1 demo)

### 6. DECISIVE-1-CASCADE (SIXTH PRIORITY, gated on K10 + CPU-smoke, then GPU)

Anchor pointer: Research note Section 6.3 (cascade spec-dec analysis)
Substrate-product reading: KB-tier (K1=4 tokens) -> small-LLM-tier (K2=4 tokens) ->
  large-LLM-verify gives effective K=8 at combined draft cost c_effective ~ 0.04-0.05
  (vs c=0.08 for small-LLM alone at K=4). Formula predicts ~18% more speedup over
  small-LLM-only spec-dec at same LLM budget. Implementation requires both KB and
  small LLM running in pipeline (moderate implementation complexity).
Tier hint: GPU (16GB+), local runner. Gated: requires DECISIVE-1-K10 to pass first (to
  confirm formula accuracy before investing cascade implementation).
Why-now: After anchors 1-3, cascade is the next-highest speedup lever. But it requires
  the most implementation work -- do not dispatch before simpler anchors are confirmed.

Pre-reg bands:
  HARD-PASS: cascade achieves >= 0.3x more speedup than small-LLM-only at equal LLM budget
  MIDDLE-BAND: 0.1-0.3x improvement (worth the engineering cost if multi-LLM already deployed)
  HARD-FAIL: cascade no better than small-LLM alone (KB pre-draft adds overhead without
             additional accepted tokens; eliminate KB tier from cascade, use small-LLM only)

### 7. DECISIVE-1-MULTI-POSITION (SEVENTH PRIORITY, exploratory)

Anchor pointer: Research note Section 1.4 (multi-position speculation) + Section 7 anchor list
Substrate-product reading: For structured factual responses (tables, lists, templates),
  future entity positions may be predictable K steps ahead. KB can potentially draft
  tokens at position t+5 and t+10 in addition to t+1...t+K. The LLM's verification
  pass would cover a longer span and more tokens could be accepted. Only viable for
  STRUCTURED generation with predictable templates.
Tier hint: CPU, exploratory. ~1-2 hr on structured-output queries.
Why-now: Most speculative value only in narrow structured generation case. Run after
  anchors 1-5 to confirm whether the structured-output angle adds speedup.

Pre-reg bands:
  HARD-PASS: multi-position spec achieves >= 0.5x more speedup than linear on structured
             factual responses (templates, tables, lists)
  MIDDLE-BAND: 0.2-0.5x improvement (positive; continue for structured-output use cases)
  HARD-FAIL: no improvement (LLM generation not predictable enough at t+5 positions;
              close this axis)

### 8. DECISIVE-1-AT-FRONTIER (EIGHTH PRIORITY, cloud GPU, high cost, last gate)

Anchor pointer: Research note Section 7 anchor 8 + Section 8.1 (ceiling analysis at 70B+)
Substrate-product reading: At 70B+ model scale, LLM token latency is highest (25-40ms on
  A100) and the sub-ms KB draft has greatest relative advantage. BUT H100/H200 bandwidth
  saturation may reduce the advantage to near-zero. This anchor determines the frontier
  deployment case. Do NOT dispatch until anchors 1-5 confirm architecture viability at
  small scale.
Tier hint: Cloud GPU (H100 or A100 equivalent). Cloud cost authorization required.
Why-now: Only if v1.1 enterprise case requires frontier LLM deployment. Not for v1 demo.

Pre-reg bands:
  HARD-PASS: >= 2.0x speedup on 70B model with KB draft vs baseline on identical hardware
  MIDDLE-BAND: 1.5-2.0x (marginal; evaluate deployment cost vs speedup benefit)
  HARD-FAIL: < 1.3x speedup (bandwidth saturation confirmed; KB-spec-dec limited to
              <= 13B on runner hardware; frontier deployment case not justified)

---

## Execution ordering recommendation

Parallel batch 1 (no prerequisites, CPU only):
  - DECISIVE-1-ADAPTIVE-K
  - DECISIVE-1-K10
  - DECISIVE-1-CONFIDENCE-GATED
  - DECISIVE-1-MULTI-TENANT (as correctness gate)

Batch 2 (gated on Batch 1 results):
  - DECISIVE-1-COMPOSITE (requires adaptive-K passing + multi-hop KB available)
  - DECISIVE-1-MULTI-POSITION (exploratory, low priority)

Batch 3 (gated on Batch 2 results, GPU required):
  - DECISIVE-1-CASCADE

Batch 4 (high cost, explicit authorization required):
  - DECISIVE-1-AT-FRONTIER

---

## Context pointers

- Research note (2x depth drill, full analysis):
  d:/AI/hd-instrument/notes/research_drill_speculative_draft_maximization_2x_2026-06-09.md
- Prior research note (5x lit-scan, full baseline):
  d:/AI/hd-instrument/notes/research_drill_substrate_speculative_decoding_5x_2026-06-09.md
- Prior exp_dev handoff (5x anchors, baseline acceptance rate anchors A-E):
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_speculative_decoding_5x_2026-06-09.md
- Testbed HARD_FAIL context (short-answer workload mismatch, June 7):
  d:/AI/hd-instrument/notes/testbed_note_speculative_decoding_qwen_v1_2026-06-07.md
- Testbed handoff (spec-dec routing, June 7):
  d:/AI/hd-instrument/notes/exp_dev_to_testbed_speculative_decoding_handoff_2026-06-07.md
- PP-107 algebraic confidence (the key substrate tool for adaptive K gating):
  d:/AI/hd-instrument/data/substrate_capability_map.md (PP-107 row)

---

## Contract section

This hand-off is research-to-experiment. The 8 anchor specs are provided as pre-reg
recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if empirical baseline differs)
- Implementing the test scripts for each anchor
- Assigning to correct queue (Batch 1 = CPU laptop, Batch 3 = GPU local, Batch 4 = cloud)
- Writing verdict notes per standard protocol
- Escalating if DECISIVE-1-COMPOSITE HARD-PASS (alpha >= 0.72 on compositional) to
  orchestrator -- this would be a major cap_map update (new speedup ceiling projection)

## Autonomy declaration

Exp_dev may dispatch all Batch 1 anchors independently without orchestrator approval
(all CPU, low cost). Batch 2 anchors may be dispatched after Batch 1 completion without
approval. Batch 3 (CASCADE) requires GPU local and should be confirmed with orchestrator
re: queue availability before dispatch. Batch 4 (FRONTIER) requires explicit cloud GPU
authorization from orchestrator or user.

If DECISIVE-1-ADAPTIVE-K HARD-FAILs AND DECISIVE-1-K10 HARD-FAILs: effective alpha
is confirmed < 0.60 and KB-spec-dec speedup ceiling is ~1.5x at best. Exp_dev should
escalate to orchestrator before dispatching any further spec-dec anchors -- the direction
may not justify further investment and the audit-chain / multi-tenant angles should be
re-scoped as standalone compliance features rather than speedup-acceleration features.
