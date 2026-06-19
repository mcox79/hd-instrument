# strategy_decisions_2026-06-13

## v593 -> v594 CYCLE 243 FLUSH 2-VERDICT BATCH resonator-alpha05-verification + crossdomain-NER-catch-up (verdict_handler 487th PROT-009 paired commit; 2 HP [substrate_decomposition_resonator_alpha05_cpu_v1 HONEST + substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1 HONEST-ALREADY-IN-MAP]; 0 LVH; 0 NEW PP ROWS; PP-407 ANNOTATED 4th two-vector-rule appearance; PP-412 catch-up log; Portfolio 32+413 UNCHANGED; HONEST 1857->1859 +2; LVH 292->292 +0)

### Step 0 honest re-read

Metrics source: LOCAL (d:/AI/hd-instrument/data/exp_<name>/metrics.json, cpu_runner_local FrameworkMPC; both run_mode=full; elapsed 3.99s + 259.86s; NOT pre-ship smoke). 0 LVH catches.

**substrate_decomposition_resonator_alpha05_cpu_v1 HARD_PASS (HONEST):** F=3/K=241/noise=0: plain=0.9111 alpha0.5=1.0000 lift=+0.0889 >= HP bar +0.05. Full ablation grid all cells >=0.9521. HONEST. NOTE: empirical data matches v590's pp407_alpha_0_5_decomposition_verify exactly; this is a VERIFICATION anchor confirming the two-vector architecture rule under independent dispatch.

**substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1 HARD_PASS (HONEST):** ratio@2.5pct=1.7784 >= HP bar 1.20 by 48pct margin; non-converging tail 1.150 at 100pct. HONEST. NOTE: ALREADY PROCESSED as PP-412 in v591. This is a delayed orchestrator catch-up from v589 reference point.

HONEST: 1857 -> 1859 (+2). LVH: 292 -> 292 (+0). 0 LVH catches.

### Cap_map decisions (v593 -> v594)

**(A) substrate_decomposition_resonator_alpha05_cpu_v1 (HARD_PASS VERIFICATION -- PP-407 annotation; 4th two-vector-rule appearance; no new PP row):**
PP-407 ANNOTATED: 4th appearance of meta::RULE_two_vector_architecture_separates_structural_similarity_from_atom_identity_jobs at resonator-decomposition VERIFICATION granularity. Alpha=0.5 identity-augmented resonator decode precision@1=1.0000 at K=241/F=3; full ablation grid >=0.9521. Reproducibility confirmed: independent anchor under same design yields same empirical result within multi-seed noise. Rule CONFIRMED status unchanged (promoted at 3rd appearance v590). No new PP row.

**(B) substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1 (HARD_PASS ALREADY-IN-MAP -- PP-412 catch-up log; no new row):**
PP-412 catch-up log: ALREADY-IN-MAP (v591). Delayed flush from orchestrator v589 reference point; Testbed/Cycle-50-OPEN session processed this anchor in v591. No new state. HONEST +1 for catch-up re-read.

Cap_map: v593 -> v594 CYCLE 243 FLUSH (2 HARD_PASS; 0 LVH; 0 NEW PP ROWS; PP-407 4th two-vector-rule appearance VERIFICATION; PP-412 catch-up log; Portfolio 32+413 UNCHANGED; HONEST 1857->1859 +2; LVH 292 UNCHANGED; 487th PROT-009 paired commit) (2026-06-13)
