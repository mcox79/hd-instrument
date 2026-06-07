# strategy_decisions_2026-06-07

## v473 -> v474 CYCLE 153 CAUSAL BATCH (2026-06-07)

Verdicts processed: causal_correlational_disambig_v1 (HP) + causal_intervention_isolation_v1 (HP) + causal_counterfactual_replay_v1 (HP)

### Step 0 honest re-read

- causal_correlational_disambig_v1: HONEST. 3-seed FULL remote. per_seed: prec=1.0/1.0/1.0 (mean=1.000); recall=0.94/1.0/0.98 (mean=0.973). BOTH >= HP threshold 0.85 on EVERY seed. Comparative claim ">=0.85" verified on all 3 per-seed cells. HARD_PASS label CORRECT. No LVH.
- causal_intervention_isolation_v1: HONEST. 3-seed FULL remote. per_seed: deg=0.0/0.0/0.0 (mean=0.000); non-target recall after=1.0/1.0/1.0. Threshold claim "<0.02 degradation; others >=0.95" verified on EVERY seed; deg=0.0000 and non-target recall=1.000 unanimous. HARD_PASS label CORRECT. No LVH.
- causal_counterfactual_replay_v1: HONEST. 3-seed FULL remote (N=1024). per_seed: acc=1.0/1.0/1.0 (mean=1.000); intervention_ms=4.148/3.738/3.740 (mean=3.876ms). Accuracy >=80% and latency <10ms verified on ALL seeds. EU AI Act Art. 12 product framing consistent with empirical numbers. HARD_PASS label CORRECT. No LVH.

HONEST: 1111 -> 1114 (+3). LVH: 250 UNCHANGED.

### Cap_map decisions

**(A) NEW TOP-LEVEL ROW PP-81: Substrate causal-graph role-vector disambiguation.**
causal_correlational_disambig_v1 GENUINE FULL HARD_PASS at N=4096 3-seed. Mechanism A (causal binding via role vectors): CAUSE_OF vs CORRELATED_WITH bindings algebraically separable with prec=1.000 recall=0.973 unanimous across seeds. Substrate-product implication: substrate stores and retrieves causal-vs-correlational relationship distinctions as native role bindings -- no separate causal inference engine needed; causal knowledge graph is first-class in the storage algebra. Cross-references: PP-35 graph retrieval (PP-81 extends to typed causal edges); PP-39 neural-symbolic bridge (PP-81 adds causal-binding to symbolic rule engine); PP-25 retrieval explainability (PP-81 enables causal-attribution readout). Filed at 0.60-0.75 EXPLORATORY (base 0.65-0.80 - 0.05 lit-scan calibration; N=4096 3-seed founding; production-N and heteroassoc-scale confirmation pending).

**(B) SUB-PROPERTY PP-81a: Causal intervention isolation (do() operator is LOCAL -- zero non-target degradation).**
causal_intervention_isolation_v1 GENUINE FULL HARD_PASS at N=4096 3-seed. Performing a do() hetero-assoc target swap on one binding does NOT degrade non-target bindings (deg=0.000 unanimous; non-target recall=1.000). Algebraic isolation is EXACT in this scope. Product implication: causal interventions are safe -- editing one causal fact does not corrupt other stored facts. PP-81a sub-property: EMPIRICAL VALIDATED (3-seed scope). Cross-references: PP-9 deletion-cert (causal isolation analogous to deletion-cert locality); PP-28 edit-impact-DAG (PP-81a provides zero-crosstalk intervention guarantee).

**(C) NEW TOP-LEVEL ROW PP-82: Substrate causal counterfactual replay (do() API, <4ms, EU AI Act Art. 12 audit-ready).**
causal_counterfactual_replay_v1 GENUINE FULL HARD_PASS at N=1024 3-seed. Counterfactual replay via hetero-assoc target swap: accuracy=1.000 (all seeds), mean_intervention=3.876ms. HP thresholds (>=80% accuracy, <10ms) passed with substantial margin on all seeds. Substrate-product implication: substrate exposes a native "what-if?" API -- swap a stored causal fact and instantly retrieve the modified conclusion at <4ms; first-class audit primitive for EU AI Act Article 12. No separate counterfactual engine needed; replay is algebraic. Cross-references: PP-49 hierarchical refusal counterfactual abduction (PP-82 is causal-graph what-if vs PP-49 refusal subtree what-if -- same algebra family, distinct product scopes); PP-25 retrieval explainability (PP-82 provides causal-counterfactual primitive); PP-46 GDPR non-repudiation (PP-82 enables "what-if this fact were deleted" query). Filed at 0.60-0.75 EXPLORATORY (base 0.65-0.80 - 0.05 lit-scan calibration; N=1024 founding only; production-N=4096+ needed for band-LIFT).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-81 causal disambiguation (HP founding -- rescues for scale confirmation):**
R1 (0-compute, ANNOTATION): N=4096 3-seed founding confirmed. Band UNCHANGED pending production-N cross-N.
R2 (CHEAP, CPU <30min): 3-seed at N=8192 to confirm prec/recall >= HP at production scale.
R3 (CHEAP, CPU <30min): M-sweep (M=50..200 bindings) to characterize disambiguation at larger KG sizes.
R4 (MEDIUM, CPU <2h): 3-class disambiguation (causal+correlational+confounded) to test multi-class causal structure.

**PP-81a causal isolation (HP sub-property -- rescues for capacity stress):**
R1 (0-compute, ANNOTATION): N=4096 3-seed zero-degradation confirmed. Band UNCHANGED pending M-capacity sweep.
R2 (CHEAP, CPU <30min): M-sweep (M=10..100) to characterize isolation at larger memory load.
R3 (CHEAP, CPU <30min): Adversarial isolation (M neighboring semantically similar bindings) to probe crosstalk at high density.

**PP-82 counterfactual replay (HP founding -- rescues for production-N):**
R1 (0-compute, ANNOTATION): N=1024 founding confirmed. Production-N required for band-LIFT.
R2 (CHEAP, CPU <30min): N=4096 3-seed replay to confirm accuracy >= 80% and latency < 10ms at production-N.
R3 (CHEAP, CPU <30min): Multi-step counterfactual (chain 2-3 do() ops) to characterize composability.
R4 (MEDIUM, CPU <2h): EU AI Act Art. 13 audit stress test -- 100+ concurrent counterfactual queries at N=4096 for throughput characterization.

### Portfolio: 32+80 -> 32+82 (+2 NEW ROWS: PP-81 causal-disambiguation + PP-82 counterfactual-replay; PP-81a isolation as sub-property of PP-81). 0 BAND-LIFTS. 0 closures.

### PROT compliance (v473 -> v474)

- PROT-004/006: No closures. 2 NEW TOP-LEVEL ROWS (PP-81 + PP-82). 1 NEW SUB-PROPERTY (PP-81a). Rescue sketches filed cheapest-first (R1 annotation always first; R2-R4 CPU/GPU in cost order).
- PROT-007: v474 history row appended to substrate_capability_map_history.md.
- PROT-008: 2 new top-level rows + 1 new sub-property. State-transition validator: PP-81 prec=1.0/recall=0.973 all-seed HP + PP-82 acc=1.0/ms=3.876 all-seed HP = FOUNDING CRITERIA MET. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 386th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 3 anchors. CLEAN.
- PROT-019: LVH 250 UNCHANGED. No new LVH catches.
- PROT-021: All 3 source=remote run_mode=full n_seeds=3. No smoke contamination. CLEAN.
- PROT-022: Causal anchors 1+2 at N=4096 3-seed; prec always 1.0; recall=0.94-1.0 seed variance acceptable at N=4096. Anchor 3 at N=1024 acc=1.0 all seeds; ms=3.74-4.15 timing variance acceptable. No HP-fragility concern.

Cap_map: v473 -> v474 CYCLE 153 (3 HP: causal_correlational_disambig-PREC1.0-RECALL0.973-CAUSE_VS_CORR-N4096-3SEED + causal_intervention_isolation-DEG0.000-NON_TARGET_RECALL1.000-ZERO_CROSSTALK + causal_counterfactual_replay-ACC1.0-3.876ms-DO_OPERATOR-EU_AIACT_ART12; 0 LVH; HONEST 1111->1114 +3; LVH 250 UNCHANGED; 2 NEW PP ROWS: PP-81 causal-disambiguation 0.60-0.75 EXPLORATORY + PP-82 counterfactual-replay 0.60-0.75 EXPLORATORY; 1 NEW SUB-PROPERTY PP-81a zero-crosstalk isolation; Portfolio 32+80 -> 32+82; 386th PROT-009 paired commit) (2026-06-07)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
