# exp_dev hand-off — research: per-hop schema-Bayes redesign (Drill B; 2x-discipline gateway)

**Filed:** 2026-06-28 by research (sub-agent context; main thread will dispatch exp_dev wrapper).

**Filed-by:** research:opus (Drill B agent).

**Trigger:** Drill A (`research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md`) HARD_FAILed all 3 adapters at smoke today; verdict `exp_dev_verdict_pfc_wm_state_tracker_smoke_HARD_FAIL_all_3_adapters_2026-06-28.md`. Root cause MEASURED@2026-06-28: `cluster_to_target_part[k]` map is hop-0-locked (built from `chains_train[ci][0][2] // PART_SIZE`). All cluster output partitions encode hop-0 partition; state-conditioning cannot rescue per-hop discrimination. Drill B redesigns the primitive itself (per-hop trajectory readout via the substrate's chain-grade sequence-binding S matrix) and is the 2x-discipline gateway per `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`.

**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` at dispatch time. If absent: ACTIVE.

---

**Per `feedback-no-experiment-design-in-prompts`**: this hand-off names ANCHOR + POINTERS only. exp_dev / cell-author designs ALL of: anchor name, N, V_C, depth, n_chains, n_schemas, K_seq, seed count, threshold bands, queue choice, ETA, smoke profile, FULL profile. Drill B suggests parameters that MATCH Drill A's failed cell so discriminator survives scale; cell-author may revise.

---

## What just closed (1-verdict 2026-06-28 Drill-A HARD_FAIL)

**HARD_FAIL_ARMS_TIED + HARD_FAIL_ALL_ADAPTERS_DEAD**
- Cell: `substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7`
- All 3 dlPFC-WM-state-tracker adapter sub-mechanisms hit top1=0.0000 at depth=15
- Per-hop partition-acc h5/h10/h15: all 3 adapters ≤ 0.24 (chance is 1/5=0.20)
- Root cause structural (not parameter): `cluster_to_target_part[k]` is hop-0-locked
- 4-primitive brain-faithful composition Rank-2 mechanism CLOSES per Drill A's HARD_FAIL bands
- Drill A's pre-mortem "most likely failure mode P=0.45" predicted this exact pattern

---

## Top-1 ANCHOR for refill (rank-ordered; 1 anchor, this is a gateway drill)

### Anchor candidate (Rank 1, sole)

1. **`substrate_partition_oracle_trajectory_schema_per_hop_v1` — Drill B per-hop schema-Bayes redesign via sequence-binding trajectory map**
   - Anchor pointer: `d:/AI/hd-instrument/notes/research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md` (see "Cheap decisive test" section for full pre-reg suggestion + 6-arm structure)
   - Substrate-product reading: replaces hop-0-locked `cluster_to_target_part[k]` map with `(cluster_k_vec ⊕ hop_code_i) → target_partition_vec` trajectory map built via chain-grade sequence-binding S matrix (CITED@2026-06-22 c3_compressed_sequence_replay K=20 N=4096 HARD_PASS commit a27939c5). Reuses Drill A's 4-primitive harness (WM bank + partition_routing + restricted cleanup) with the FR4 primitive replaced.
   - Tier hint: likely Remote CPU (matches Drill A's smoke profile: N=8192, V_C=4000, depth=15, n_chains_test=100 at smoke; full = 3-seed × ~3h = 9h). Cell-author may choose CPU vs GPU based on smoke profile timing measurement.
   - Why now: this is the GATEWAY 2x-discipline drill. Outcome determines whether brain-faithful 4-primitive multi-hop chain composition closes (HARD_FAIL) or breaks through M3 multi-hop barrier-1 at depth 15 (HARD_PASS). P_deflated=0.32. MIDDLE_BAND keeps capability box open for v2.

---

## Context pointers (file paths, not summaries)

- **Drill B note (full design + signal-shape audit + HARD_PASS/HARD_FAIL bands):** `d:/AI/hd-instrument/notes/research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md`
- **Drill A note (architectural context):** `d:/AI/hd-instrument/notes/research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md`
- **Drill A HARD_FAIL verdict (root-cause diagnosis):** `d:/AI/hd-instrument/notes/exp_dev_verdict_pfc_wm_state_tracker_smoke_HARD_FAIL_all_3_adapters_2026-06-28.md`
- **Drill A cell with hop-0-locked map bug (template; lines 322-330 are the bug):** `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7.py`
- **Drill A smoke metrics (BASELINE_A=0.40, PATH2_B=0.01, all 3 adapters=0.00, ORACLE_D=0.84):** `d:/AI/hd-instrument/data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke/metrics.json`
- **Sequence-binding chain-grade primitive (FR3+FR4 underlying):** `d:/AI/hd-instrument/hdlab/sequence_memory.py` (class SequenceMatrix + bind_pair)
- **Sequence-binding K-cliff atlas (capacity-feasibility evidence; MEASURED@2026-06-28):** `d:/AI/hd-instrument/data/exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_*_v1/metrics.json`
- **v5_hardened baseline (BASELINE_A=0.39, ORACLE_B=0.84-0.90; MEASURED@2026-06-28):** `d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json`
- **WM multi-bank K cliff (FR1+FR2 chain-grade):** `d:/AI/hd-instrument/data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1/metrics.json`
- **Pre-reg discipline reference (Drill A's pre-reg as template):** `d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_pfc_wm_state_tracker_v1.md`

---

## Drill B suggested arms (cell-author may revise)

6 arms; cardinality_ok mandatory; arms_distinct gate REQUIRED (Drill A failed META_RULE_AF due to SUB_B === SUB_C identical hash):

| Arm | Mechanism | Purpose |
|---|---|---|
| `A_BASELINE` | per-hop cleanup, no hint (reproduces v5) | Reproduces ~0.40 floor |
| `B_PATH2_PERCHAIN` | schema-Bayes once per chain (today's HARD_FAIL repro) | Reproduces MEASURED@PATH2 0.01 |
| `C_PATH3_4PRIM_HOP0_LOCKED` | 4-primitive with hop-0-locked map (Drill-A SUB_A) | Reproduces Drill-A HARD_FAIL ~0.00 — discriminator |
| `D_PATH4_TRAJECTORY_SCHEMA` | **NEW MECHANISM**: trajectory readout via sequence-binding S | The mechanism arm |
| `E_ORACLE_PER_HOP` | ground-truth partition cue per hop, then cleanup | Upper bound ~0.84 |
| `F_RANDOM` | random partition cue per hop | Lower bound; refuse-test |

**Suggested pre-reg HARD_PASS:**
- `D_PATH4` in [0.50, 0.95]
- `D_PATH4 − C_PATH3` ≥ 0.30
- `D_PATH4 − A_BASELINE` ≥ 0.20
- per-hop part-acc in D at hops 5/10/15 > 0.50
- `E_ORACLE > D_PATH4 > C_PATH3 ≥ B_PATH2 ≥ F_RANDOM` ordering
- `arms_distinct=True` (SHA-256; META_RULE_AF gate)
- cv_max < 0.15 across 3 seeds; cardinality_ok=True (expected_n_units=18 at full); saturated_any=False; `_llm_forward_calls_at_inference == 0`

**Suggested pre-reg HARD_FAIL (per 2x-discipline triggers CAPABILITY_CLOSURE):**
- `D_PATH4` ≤ 0.30 OR `D_PATH4 − C_PATH3` < 0.10 OR `D_PATH4 < A_BASELINE` OR per-hop part-acc ≤ 0.25 at hop 10 OR arms_distinct=False

**Smoke gate (MANDATORY per `feedback_discriminator_must_survive_scale_before_full_dispatch`):**
- smoke = seed=[7] at full N=8192, depth=15, n_chains_test=100
- Check A applied: smoke at full N + full depth; only n_chains_test reduced
- If smoke `D − C < 0.10`: REJECT full dispatch; HARD_FAIL_DISCRIMINATOR_FAILS_AT_SMOKE; capability box closes

**Mechanism implementation hints (cell-author may revise):**
- Reuse Drill A cell as template for arms A, B, C, E, F (verbatim port)
- For arm D, ADD:
  1. Build `cluster_codes = bipolar(N_SCHEMAS, N_DIM, g)` (per-cluster basis vector)
  2. Build `hop_codes = bipolar(DEPTH, N_DIM, g)` (per-hop basis vector, reuse Drill A's hop_codes if compatible)
  3. Build trajectory S matrix: for each training chain c, for each hop i, bind `S += outer(target_partition_codes[chains_train[c][i][2] // PART_SIZE], cluster_codes[chain_to_schema[c]] * hop_codes[i])`
  4. At inference for chain q, hop i: compute `q_schema_per_hop = chain_schema_vector(q[:i+1], R)`, then `k_pred = argmax(prototypes @ q_schema_per_hop)`, then `trajectory_key = cluster_codes[k_pred] * hop_codes[i]`, then `partition_vec = S @ trajectory_key`, then `target_part = argmax(partition_codes @ partition_vec)`
  5. Hand `target_part` to existing partition_routing + restricted cleanup primitives

**Critical cell-author diagnostics (REQUIRED in metrics.json for HARD_FAIL diagnosis):**
- `k_pred_per_hop_vs_k_train_mismatch_rate` (per arm D, per chain, per hop)
- `trajectory_readout_cosine` (cosine of S @ trajectory_key to target_partition_code per arm D, per hop)
- `per_hop_partition_acc` (per arm, per hop_idx 0..14)

---

## Contract

- Pre-reg per `feedback-envelope-expansion-fail-bands`: HARD-PASS + HARD-FAIL bands BEFORE smoke.
- Self-test per `feedback-formula-selftests` (cell `--self-test` mode must run without GPU/heavy compute).
- Multi-seed FULL on smoke clearance (per `feedback_discriminator_must_survive_scale_before_full_dispatch`).
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0 (smoke likely local; full likely remote_cpu_queue based on Drill A's profile).
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code (5 = post-ship verification failed) per `feedback-ship-name-collision`.
- status_log entry per anchor with `plain_language` + `importance` (HIGH or CRITICAL — this is the 2x-discipline gateway).
- META_RULE_AF arms_distinct gate (Drill A failed this; must pass here).
- META_RULE_AC number tagging (MEASURED@/THEORETICAL@/CITED@).
- META_RULE_AH cardinality_ok pre-reg field mandatory.
- META_RULE_AN saturated_any check.
- META_RULE_AP signal-shape audit acknowledged (already done in drill note).
- `feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27`: cell-author must read all cited numbers from metrics.json files at construction time; no mental arithmetic.
- `feedback_compute_formulas_in_code_before_quoting_2026-06-27`: any CRLB / capacity / SNR formula in pre-reg must be computed in Python.
- BIAS-N (verify referent verdict field), BIAS-Q (suspect 1.000 results), BIAS-S (regime-checks for top1-vs-top5; capacity-feasible; relative-bands).

---

## Autonomy declaration

exp_dev / cell-author decides ALL of: final anchor name, N, V_C, depth, n_chains_train, n_chains_test, n_schemas, K_seq, seed count, threshold bands (HARD-PASS + HARD-FAIL — may revise the suggested bands above), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, implementation details. The drill note passes anchor POINTERS + suggested arms + suggested bands + critical diagnostics ONLY. If cell-author wants to substitute Candidate A (per-hop chunk-schema) or Candidate C (skip schema; direct decoder) per the drill's audit table, that's cell-author's call — but those alternatives are reserved as v2/v3 fallbacks per the drill's verdict.

If cell-author identifies a SHAPE_MISMATCH or pre-reg-band conflict at construction time: HALT, file a research follow-up note, do NOT silently revise the mechanism.

---

## Filed by

research:opus (Drill B agent), 2026-06-28, post Drill-A HARD_FAIL verdict. Hand-off ready for `/exp_dev d:/AI/hd-instrument/notes/exp_dev_handoff_research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md` dispatch.

---

## 2x-discipline status

This is the second of two drills (Drill A = state-bias adapter; Drill B = per-hop primitive redesign) on the brain-faithful 4-primitive multi-hop chain composition. Per META_RULE_AO and `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`:

- If Drill B HARD_PASSes: brain-faithful 4-primitive composition closes the multi-hop chain barrier 1 at depth 15. M3 multi-hop progress.
- If Drill B MIDDLE_BANDs: capability box stays open for v2 (Modern-Hopfield exponential-capacity readout OR resonator-cleaned iterative readout).
- If Drill B HARD_FAILs: **CAPABILITY_CLOSURE_CONFIRMED** on brain-faithful 4-primitive multi-hop chain composition. Two structurally-different mechanism classes both failing satisfies the 2x discipline. M3 pivots to non-brain-faithful composition (acknowledged trade-off) OR a 5th primitive class (Drill C, if user authorizes).
