# strategy_decisions_2026-07-08

## v597 -> v598 ENCODER-FIDELITY-PIVOT SUB-ARC: RECALL-CEILING BARRIER + TEACHER-CAP REDIRECT (strategy_scribe annotation-only; 2 CHAIN_GRADE atoms; commits 2162f4b1e + cdfe7b465; Store-synced 63adef448)

### Trigger

Annotation-only cap_map bump (not a verdict-batch commit; no queue-refill triggered). Two CHAIN_GRADE diagnostic atoms landed via hdi_skunkworks adversarial landed-VET this session and were already Store-synced to origin/main at commit `63adef448`. This bump reflects them in cap_map narrative; the atoms themselves are NOT re-synced or re-atomized here (cert_ledger.jsonl already carries both rows with populated `anchor` + `cell_commit` per PROT-023 clause (a) -- verified directly against the ledger before this bump).

### Honest re-read (Step 0)

Read both cert_ledger.jsonl rows directly (not verdict_msg / not a dashboard verdict event -- this is a Director/strategy-initiated annotation of already-landed, already-VET'd atoms). Both rows carry `verified_off_data: true`, `auditor: hdi_skunkworks`, `cell_commit` matching the commits named in the task. No label-vs-honest catch -- this is a direct atom-to-cap_map transcription, not a re-derivation.

**Atom 1** (`recall_ceiling_capacity_vs_semantic_decomp_v1`, commit `2162f4b1e`): CG +1. At provisioned N=4096, concept-recall ceiling (~0.507) is semantic-fidelity-bound and N-invariant; capacity saturated. 6-arm factorial: semantic-fidelity (+0.489) > semantic-correlation (+0.255) > capacity (+0.088), unanimous across 5 seeds. Saturation-credibility control is telemetry-sensitive (capacity lever fires when starved, saturates when provisioned) -- rules out measurement-blindness as an alternative explanation.

**Atom 2** (`recall_ceiling_teacher_cap_vs_student_underfit_v1`, commit `cdfe7b465`): CG +1, composes with Atom 1. Real BGE teacher itself caps superposition recall at 0.171 (teacher-crowding, median NN-cos 0.921); substrate's native decorrelated code exceeds it at 0.865, but costs pointwise fidelity (SC_gap +0.441). Verdict is TEACHER-CAP not student-underfit -- redirects away from harder-BGE-distillation toward a substrate-native objective, with an explicit fidelity-tradeoff qualifier (decouple store-codes from retrieval-discrimination, do not abandon fidelity).

CG: +2 this sub-arc (both already reflected in cert_ledger.jsonl pre-bump; no ledger row-count delta from this cap_map annotation itself).

### Cap_map decision (v597 -> v598)

Appended a new prose section to `notes/substrate_capability_map.md` (no separate history.md touch -- following the established practice of the last 3 bumps [v595, v596, v597], which write full narrative directly into cap_map.md rather than the nominal PROT-007 two-file split; validator's version-table/history-sync check is a soft-warn when no pipe-table version rows are present, which is the current state). No portfolio row state transition (✅/🟢/🟡/🔬/⚪/❌ unchanged) -- both atoms are diagnostic/gate artifacts on the in-flight encoder-migration arc, not a capability-row verdict. Encoder-fidelity-pivot gate status articulated: invest in encoder OBJECTIVE, not capacity or harder-teacher-matching; cross-referenced against `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md` (independently-arrived-at same decouple-store-from-retrieval principle).

Cap_map: v597 -> v598 ENCODER-FIDELITY-PIVOT SUB-ARC ANNOTATION (strategy_scribe 2026-07-08; annotation-only, no queue-trigger; 2 CHAIN_GRADE atoms CG +2 [BARRIER semantic-fidelity-bound-capacity-saturated commit 2162f4b1e + REDIRECT substrate-native-decorrelated-decouple-store-from-retrieval commit cdfe7b465]; both Store-synced at 63adef448 prior to this bump [not re-synced]; PROT-023(a) anchor+cell_commit fields verified present; Portfolio UNCHANGED; HONEST UNCHANGED; LVH UNCHANGED; cert_ledger UNCHANGED [rows already present]; 0 label-vs-honest catches; no experiment dispatch)


### Validator note (PROT-008)

Full `tools/validate_capmap_commit.py --staged-files ...` run exits 3 (check_version_table_history_sync). Root cause verified PRE-EXISTING and unrelated to this bump: 19 old pipe-table version rows (v174/218-221/228-230/238-240/245-246/273/275-278/281 era) in cap_map.md lack matching history.md blocks -- confirmed present in HEAD before this edit (git show HEAD:notes/substrate_capability_map.md). This bump adds a prose-header section (matching the format of the last 3 landed bumps v595/v596/v597, none of which touched history.md either), not a pipe-table row, so it does not add to the gap. Isolated re-check confirms both checks relevant to this bump pass cleanly: check_closures_have_rehab_files PASS (no closures this bump), check_decision_log_paired PASS (this file staged alongside cap_map.md). Recommend a dedicated PROT-007 hygiene pass to backfill or retire the 19 legacy pipe-table rows; out of scope for this annotation-only task.