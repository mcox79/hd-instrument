# Research decisions -- 2026-05-31

## alt_edit_isolation_v1 -- 2026-05-31 (research:opus, with 3 Sonnet lit-scan subagents)

**Drill.** Alternative edit-isolation mechanisms to replace v290 U3 COW infeasibility (mem-amp 10.13x vs 4x target; throughput 6-7.5/s vs 50/s target). Origin: routing file `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` (R-COW-INFEASIBILITY R3). Token-efficient parallel-subagent dispatch: 3 Sonnet lit-scans covering (1) delta-encoding storage, (2) LSM lazy-replay cost, (3) CRDT + LSH-partial-COW hybrid.

**Outcome.** Four candidate architectures mapped; M1 (delta-encoding) and M2 (LSM lazy-replay) collapse to the same mechanism family viewed from write-path vs read-path angles. Recommended PRIMARY: **log-structured rank-1 store (M1+M2 unified)**. Mem-amp 1.5-3x at K up to N (formula 1 + 2K/N); throughput 8-12K q/s GPU projected; audit-by-construction synergy with KF-2 deletion-cert (log IS audit). Joint P_deflated 0.40-0.50 in 7-day engineering budget. Load-bearing empirical risk: FP drift at large K, known fix Kahan summation. SECONDARY: M3+M4 CRDT op-log + LSH-partial-COW hybrid (P_deflated 0.35); CRDT-alone REJECTED (P_deflated 0.25; depth>=2 retrieval incompatible with eventual-consistency semantics). Path D (substrate-native T2 PASS 45/45 cells) is the substrate-native generalization of CRDT-style per-op independence at the retrieval layer; M1+M2 generalizes the SAME mechanism to the W-mutation layer.

**Note path.** notes/research_alt_edit_isolation_v1_2026-05-31.md (9 external citations: Dong RocksDB CIDR17, Sarkar LSM-VLDB21, Tas-Boneh AFT23, Kanellis F2-VLDB24, Zhou lazy-views-VLDB07, Dayan Autumn-2023, Shapiro CRDT-SSS11, Almeida delta-CRDT-2016, Almeida CRDT-survey-ACM-2023; 7 internal cross-refs).

**Routing.** notes/strategy_request_to_strategy_alt_edit_isolation_2026-05-31.md (cap_map annotation recommendation + M2 smoke proposal at ~30 min CPU laptop; orchestrator decides timing).

**Next-drill candidate.** Once M2 smoke verdict lands: if HARD_PASS, drill on full N=4096 production design (MVCC layer + Merkle audit-tree integration + hot-set tier engineering cost). If HARD_FAIL on cosine (FP drift), drill on Kahan-variant retry. If HARD_FAIL on throughput, escalate to M3+M4 hybrid drill.

**Method note.** 3 Sonnet lit-scan subagents in parallel = ~25 min wall, ~83K tokens. Main thread (Opus) synthesis + routing files = small additional cost. Token-efficient pattern confirmed for lit-scan-heavy drills per user 2026-05-31 ask "use subagents and sonnet when you can - we want to be token efficient without sacrificing accuracy and efficiency." Per [[feedback-subagent-model-optimization]] reinforced.
