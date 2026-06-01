# strategy -> exp_dev: Round 3 Tier 1 dispatch

Filed-by: strategy_scribe
Trigger: cap_map v315 Round 3 capability-expansion adoption; 5 Tier 1 anchors ready to ship
Pause state: ABSENT (all operations normal)

Per [[feedback-no-experiment-design-in-prompts]]: this file names ANCHORS + POINTERS only. exp_dev determines sweep grids, exact thresholds, queue command, and timeout.

## Round 3 Tier 1 anchors (5 total; all remote_cpu_queue)

### T1.6 Retrieval explainability cosine-contribution score
- Row: PP-25 substrate retrieval explainability primitives
- What to test: cosine-contribution decomposition -- for a given retrieval result, decompose the similarity score into per-atom contributions (sum of inner products by linearity); validate that top-K contributing atoms match the stored bundle at query time
- Why now: cosine-contribution is mathematically guaranteed for linear superposition; empirical validation is <10s CPU; immediate empirical foothold for PP-25 row
- Queue: remote_cpu_queue
- Expected wall: <10s CPU
- Pre-reg bands: exp_dev autonomy (contribution decomposition sum = cosine similarity is algebraically exact; the test validates the implementation not the math)

### T1.7 Counterfactual probe (retrieval explainability)
- Row: PP-25 substrate retrieval explainability primitives
- What to test: remove one atom from a bundle via deletion-cert mechanism, measure retrieval-score change; validates that deletion-cert primitive serves as counterfactual explainability tool
- Why now: deletion-cert is already validated (PP-9); counterfactual probe is a direct application; <5s CPU
- Queue: remote_cpu_queue
- Expected wall: <5s CPU
- Pre-reg bands: exp_dev autonomy; cross-ref PP-25 counterfactual anchor pointer

### T1.8 Effective channel capacity sweep
- Row: PP-27 information-theory readout suite + PP-2a sub-property
- What to test: per-atom entropy sweep over M values at N=4096; measures substrate information density (bits per stored concept) as function of load M
- Why now: channel capacity monitoring is PP-2 sub-property; CPU-bound sweep; ~10min; establishes baseline for information-theoretic readout API
- Queue: remote_cpu_queue
- Expected wall: ~10 min CPU
- Pre-reg bands: exp_dev autonomy; research synthesis does not specify numerical thresholds for first entropy sweep

### T1.9 FAISS hybrid sidecar smoke
- Row: PP-22 audit-grade ML feature store (sidecar) + PRIMARY GTM (COMPLIANCE SIDECAR)
- What to test: substrate sidecar alongside FAISS baseline; write same feature bundles to both; FAISS serves hot-path queries, substrate serves audit-cert queries; measure audit-cert generation latency overhead vs FAISS-only baseline
- Why now: sidecar GTM is PRIMARY architecture; empirical foothold needed for latency overhead claim; 1-2h CPU
- Queue: remote_cpu_queue
- Expected wall: 1-2h CPU
- Pre-reg bands: exp_dev autonomy; source notes suggest audit-cert overhead target <50ms p99 sidecar path (not hot path)

### T1.10 Federated deletion certificate smoke
- Row: PP-24 federated learning substrate
- What to test: 2-client federated round at N=4096; per-client delta-rule write; per-client deletion-cert; validate that per-client cert is algebraically independent; measure post-erasure accuracy delta
- Why now: federated unlearning is deletion-cert SHARED PRIMITIVE; cheapest possible federated smoke; ~60s CPU
- Queue: remote_cpu_queue
- Expected wall: ~60s CPU
- Pre-reg bands: exp_dev autonomy; HARD_PASS: per-client cert algebraically independent (cross-cert contamination = 0); post-erasure target-client accuracy drops while non-erased client accuracy preserved

## Context pointers
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md (PP-21 through PP-27 rows added v315)
- Source research: d:/AI/hd-instrument/notes/research_capabilities_expansion_round3_8_drills_2026-06-01.md
- Pre-reg discipline: d:/AI/hd-instrument/notes/active_protocols.md (PROT-018 _n<N> anchor naming required)

## Contract
- Per-experiment --timeout required per [[feedback-per-experiment-timeout-required]]; formula: 1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)
- ASCII-only in print()/verdict_msg per [[feedback-ascii-only-in-scripts]]
- set -ex + python -u + stdbuf -oL + tee remote log per [[feedback-always-verbose-remote-dispatch]]
- Post-ship REMOTE VERIFY via queue.json state

## Autonomy declaration
exp_dev has full autonomy on: anchor naming (must include _n<N> per PROT-018), sweep grids, exact threshold formulas, pre-reg HF/HF bands where research has not specified them, queue command construction, timeout calculation, smoke vs FULL sizing decision.

---

**ROUTING STATUS**: Acted-on 2026-06-01: 5 Round 3 Tier 1 anchors shipped + verdicts processed in v316
