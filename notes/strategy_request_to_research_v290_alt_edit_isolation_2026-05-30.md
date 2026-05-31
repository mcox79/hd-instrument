# strategy_request_to_research: alternative edit-isolation mechanisms (post-COW infeasibility)

**Origin.** v290 cap_map; U3 `edit_isolation_guard_probe_v1_n4096` HARD_FAIL: COW MECHANISM correctness OK (cons=1.00 + audit=5/5 unanimous pre/mid/post) but COST infeasible (10.13x mem-amp vs 4x target = 2.5x over; 6-7/s throughput vs 50/s target = 7-8x slower). Path D achieves edit-resilience via per-hop Bayesian independence (T2 PASS) — DIFFERENT MECHANISM.

**Task.** Research drill on alternative edit-isolation mechanisms with better cost profile than COW. Goal: identify 2-4 candidate mechanisms with empirical or theoretical precedent at cost levels closer to substrate's production target (mem-amp <= 4x, throughput >= 50/s, consistency >= 0.95).

**Specific lit-scan directions.**
1. **Delta-encoding / diff-storage** — store edits as compact diffs to W rather than full W copies. Database log-replay + content-addressable storage + delta-compression literature.
2. **Edit-log replay** — append-only log of edits; materialize edit-applied W only at retrieval (lazy materialization). LSM-tree literature.
3. **Per-hop independence (generalize Path D's mechanism)** — Path D's per-hop Bayesian decoupling from W mutation propagation IS the mechanism that worked in T2; can it be generalized as a substrate-wide isolation primitive at architectural level? Literature on conflict-free replicated data types (CRDTs) + per-operation independence.
4. **Locality-sensitive isolation** — only invalidate / re-copy the W subspace touched by the edit (similar to copy-on-write but at subspace-granularity rather than whole-W). Locality-sensitive hashing + partial-copy literature.
5. **Snapshot-then-edit-then-rollback SDK layer** — operational pattern from databases; SDK design more than research.

**Constraints.**
- Generic terms only per [[feedback-query-privacy-decomposition]].
- Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: deflate P 0.15-0.25; cap novel-synthesis P at 0.50.

**Deliverable.** 2-4 candidate mechanisms with deflated P estimates + cost-profile sketches (mem-amp / throughput predictions) + smoke-test design suggestions.

**Not auto-dispatched.** Orchestrator decides timing; this is engineering work needing careful design.
