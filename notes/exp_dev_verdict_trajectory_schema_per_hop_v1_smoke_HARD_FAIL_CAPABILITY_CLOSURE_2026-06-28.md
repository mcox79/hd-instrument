# exp_dev VERDICT — Drill B trajectory_schema_per_hop_v1 smoke HARD_FAIL CAPABILITY CLOSURE

**Filed:** 2026-06-28 by exp_dev (sub-agent).

**Anchor:** `substrate_partition_oracle_trajectory_schema_per_hop_v1_seed_7` (CHUNKED single-seed sibling; siblings seed_13, seed_19 NOT dispatched per smoke gate)

**Metrics file (absolute path):** `d:/AI/hd-instrument/data/exp_substrate_partition_oracle_trajectory_schema_per_hop_v1_seed_7_smoke/metrics.json`

**Cell:** `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_trajectory_schema_per_hop_v1_seed_7.py`

**Pre-reg:** `d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_trajectory_schema_per_hop_v1.md`

**Driving drill / handoff:**
- `d:/AI/hd-instrument/notes/research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md`
- `d:/AI/hd-instrument/notes/exp_dev_handoff_research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md`

---

## Verdict

`HARD_FAIL_CAPABILITY_CLOSURE` per 2x-discipline (`feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`).

**Multiple HARD_FAIL gates tripped simultaneously:**
- D_below_abs (PATH4 top1=0.0000 <= 0.30)
- lift_C_below (PATH4 - PATH3 = 0.0000 < 0.10)
- D_below_A (PATH4 0.0000 < BASELINE 0.4000; cascade collapse)
- per_hop_h10_below (per-hop part-acc 0.220 <= 0.25; at chance)

---

## Per-arm metrics (MEASURED@2026-06-28 from metrics.json)

| Arm | top1 | Per-hop part-acc h5/h10/h15 | Notes |
|---|---|---|---|
| A BASELINE | 0.4000 | n/a | Rail OK; matches Drill A measured 0.40 |
| B PATH2_PERCHAIN | 0.0100 | 0.220/0.200/0.240 | Reproduces today's HARD_FAIL @0.01 |
| C PATH3_4PRIM_HOP0_LOCKED | 0.0000 | 0.190/0.180/0.230 | **Gate D PASS** - reproduces Drill A SUB_A @0.00 within expected [0.00, 0.30] |
| **D PATH4_TRAJECTORY_SCHEMA (mechanism)** | **0.0000** | **0.150/0.220/0.250 (CHANCE)** | **HARD_FAIL** |
| E ORACLE_PER_HOP | 0.8400 | 1.000 all hops | Matches Drill A oracle 0.84 |
| F RANDOM | 0.0000 | 0.190/0.220/0.230 | Floor; below 0.05 ceil |

- arms_distinct=True (META_RULE_AF; 6 unique SHA-256 hashes; Drill A FAILED this, Drill B PASSED)
- cardinality_ok=True (expected_n_units=6, observed=6)
- saturated_any=False
- elapsed_s_smoke=888.1
- baseline_rail_ok=True

---

## Diagnostic: WHY arm D HARD_FAILed (drill pre-mortem mode #1 P=0.40 CONFIRMED)

**Trajectory readout cosine per hop (arm D):** strong signal across all hops:
`[0.70, 0.69, 0.76, 0.69, 0.74, 0.76, 0.74, 0.76, 0.74, 0.72, 0.75, 0.72, 0.69, 0.70, 0.78]`

The S matrix IS storing and reading per-(cluster, hop) -> partition pairs with high signal-to-noise (>=0.69 throughout). Capacity is NOT the bottleneck (K_seq=300, ratio=0.037 well below cliff). Edge 3 (S @ traj_key readout) is working as theorized.

**k_pred vs k_train mismatch rate per hop (arm D):** dominant failure mode:
`[0.92, 0.84, 0.86, 0.85, 0.79, 0.78, 0.75, 0.69, 0.57, 0.56, 0.51, 0.48, 0.41, 0.25, 0.00]`

At early hops (0-8), schema-Bayes using past-hop predicates only picks k_pred that mismatches the training-time k_train in 57-92% of cases. The trajectory readout reads the WRONG ROW of S because the cluster key is wrong. By hop 14, full-chain predicates are available and mismatch drops to 0% — but by then per-hop partition is already at chance.

**Root cause CONFIRMED:** the per-hop schema query (past predicates only) is NOT a stable cluster-identity signal. Schema-Bayes' cluster identity emerges only when most/all predicates of the chain are in scope; partial-prefix queries land in different clusters than full-chain queries. This is structural to the schema-Bayes primitive itself.

---

## §15 Gate audit

- Gate A (effective vs nominal): N/A
- Gate B (discriminating bracket): bracket WORKED — D should have separated from C, but D=C=0.00 (the bracket discriminated correctly: ORACLE 0.84 >> BASELINE 0.40 >> PATH2 0.01 >= PATH3 0.00 = PATH4 0.00). Discriminator confirmed; mechanism is what failed.
- Gate C (signal-shape audit): SHAPE_MATCH at every edge verified by traj cosine 0.72; the structural composition WORKED.
- **Gate D (positive control reproduce AT TEST REGIME):** PASSED. arm_c=0.00 reproduces Drill A SUB_A=0.00 at identical regime (N=8192 V_C=4000 d=15 psz=800 K=200). Regime invocation correct; this is a real mechanism failure, NOT a setup bug.
- Gate E (FR decomposition): the mechanism implemented all 5 FRs as designed; FR2 (per-hop schema firing) is structurally the bottleneck — partial-prefix schema query is not informative early in chain.

---

## CAPABILITY CLOSURE per 2x-discipline

Per `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`:

- Drill A (state-bias adapter; 3 adapter sub-mechanisms) HARD_FAILed: 4-primitive composition with hop-0-locked map cannot rescue per-hop discrimination.
- Drill B (trajectory-schema primitive redesign via sequence-binding S) HARD_FAILed: replacing the hop-0-locked map with a per-(cluster, hop_idx) trajectory store does not rescue, because the schema-Bayes cluster identity at partial-prefix is not stable.

**Two structurally-different mechanism classes (state-bias adapter; primitive output redesign) both NULL.** 2x discipline satisfied. **Brain-faithful 4-primitive multi-hop chain composition CAPABILITY BOX CLOSES on the substrate's chain-grade primitive set.**

M3 multi-hop Barrier 1 at depth=15 requires:
- (a) non-brain-faithful composition (acknowledged trade-off; external cortex layer / learned co-training adapter) per architecture decision filed, OR
- (b) a 5th primitive class (NEW BIOLOGICAL primitive, e.g., dopaminergic gating of per-state schemas, online cluster re-identification) per Drill C if user authorizes.

---

## Dispatch decision

**NO FULL DISPATCH.** Per the smoke gate in pre-reg (`feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26`): smoke at full N=8192 + full depth=15 triggered the HARD_FAIL CAPABILITY CLOSURE gate. Siblings seed_13 and seed_19 are NOT queued; no further compute spent on this mechanism class.

Sibling cells exist on disk for audit / re-dispatch if Skunkworks requests confirmation seeds:
- `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_trajectory_schema_per_hop_v1_seed_13.py` (self-test PASS; not dispatched)
- `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_trajectory_schema_per_hop_v1_seed_19.py` (self-test PASS; not dispatched)

If Skunkworks wants the 3-seed cv: spawn hdi_orchestrator to queue smoke siblings (seed_13, seed_19) via local_cpu_queue; each ~15 min wall.

---

## Recommended downstream actions (for Director / Skunkworks)

1. **Skunkworks landed-VET:** validate HARD_FAIL_CAPABILITY_CLOSURE classification. Confirm 2x-discipline gateway satisfied (Drill A + Drill B both null on brain-faithful 4-primitive composition).
2. **Research M3 architecture decision:** invoke the pre-filed pivot — external cortex layer for multi-hop chain composition, OR authorize Drill C (5th primitive class exploration).
3. **Atomize capability-closure evidence:** safe_append_atom to substrate with this verdict + Drill A reference; tag CAPABILITY_CLOSED for queryability.

---

## Filed by

exp_dev (sub-agent, opus), 2026-06-28. Verdict ready for Skunkworks landed-VET and Research M3-pivot processing.
