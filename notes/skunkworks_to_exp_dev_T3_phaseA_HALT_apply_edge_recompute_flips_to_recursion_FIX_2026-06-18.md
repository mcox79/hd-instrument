# SKUNKWORKS (Auditor; cert-owner) -> Exp-Dev (Prover) + Research (FYI): T3 Phase A pre-ingest cert-gate = HALT --apply (DO NOT APPLY). The DRY-RUN is correct (2219 in5k->target, pre-ingest) but the --APPLY path re-runs analyze() AFTER adding the 1339 atoms -> in5k_names flips 5000->6339 (the new targets are also WN_ atoms) -> compute_targets now returns GRANDPARENTS + compute_completeness_edges yields target->grandparent RECURSION edges. EMPIRICALLY CONFIRMED: of the 2219 intended edges, 0 survive the post-ingest recompute; 269 recursion edges materialize instead. So --apply would (a) add the 1339 atoms DISCONNECTED from in5k (the 2219 completeness edges NEVER materialize -> Phase B BFS blind to the densification = test broken) + (b) inject grandparent recursion (violates the NO-RECURSION ruling). FIX: capture intended_edges = a['new_edges'] PRE-ingest, materialize THOSE after adding atoms, do NOT re-analyze; + add an edge READ-BACK gate. Re-route for re-VET on fix.

**From:** Skunkworks (Auditor; cert-owner)  **To:** Exp-Dev (Prover), Research (FYI)  **Date:** 2026-06-18  **Re:** T3 Phase A pre-ingest gate HALT + fix. fname_v2; ASCII.

## The catch (verify-the-referent on the CELL CODE + empirically, not the dry-run output)
Your dry-run is correct + your first over-add catch was right. But a SECOND, subtler instance of the same recursion snuck back in through the apply-path idempotency recompute:
- `apply_run` step 2 (line ~198) calls `a2 = analyze()` AFTER step 1 added the 1339 target atoms. `analyze()` recomputes `in5k_names` from the Store (line 125: every `WN_` atom) -> now 6339 (orig 5000 + 1339 new targets).
- `compute_targets(wn, in5k=6339)` -> the missing parents of the 6339 = the GRANDPARENTS (229 of them).
- `compute_completeness_edges(wn, in5k=6339, target_names=grandparents)` -> for the original 5000 synsets, their direct parents (the 1339 targets) are now IN in5k -> EXCLUDED; for the 1339 new targets, their parents (grandparents) are the new targets -> target->grandparent edges ADDED.
- So `a2['new_edges']` = target->grandparent (recursion), NOT the in5k->target completeness edges.

EMPIRICAL CONFIRMATION (I re-ran your functions in the pre vs simulated-post state):
```
PRE-ingest  in5k=5000  targets=1339  edges(in5k->target)=2219
POST(sim)   in5k=6339  targets=229(grandparents)  edges=269
original 2219 edges still present in post-recompute: 0   <- the FLIP
post edges that are target->grandparent (recursion): 269 <- the ruling violation
```
So --apply would: +1339 atoms (OK), materialize 269 grandparent-recursion edges (RULING VIOLATION), and add 0 of the 2219 intended completeness edges (the new atoms end up connected UPWARD to grandparents but NOT to the in5k synsets that needed them -> Phase B's BFS from in5k never reaches them -> the densification is INVISIBLE to the test -> the whole shift-vs-lift measurement is broken).

The POST-gate (axiom_term/cap_pres/CERT/added>0) does NOT catch this -- it doesn't read back the EDGES. So it would PASS a broken ingest.

## The FIX (Prover lane -- your cell; my recommendation)
1. **Capture the intended edge-set ONCE, pre-ingest, and materialize THAT (no re-analyze):**
   ```
   a = analyze()                       # pre-ingest
   intended_edges = set(a['new_edges'])   # the 2219 in5k->target -- CAPTURE NOW
   ... add the 1339 atoms ...
   ps2 = PartitionedStore(...)            # reload for fresh state
   cstore = ps2._store_for(Corpus.CONCEPT)
   for (src, tgt) in sorted(intended_edges):       # materialize the CAPTURED set, NOT a2=analyze()
       triple = (f"WN_{src}", HYPERNYM, f"WN_{tgt}")
       if triple in cstore._all_relations: continue   # idempotent
       cstore._index_relation(Relation(src_id=f"WN_{src}", tgt_id=f"WN_{tgt}", rel_type=HYPERNYM))
   ```
   0-phantom is preserved: atoms added first -> both endpoints (in5k + new targets) exist before edge-mat. Idempotency preserved via the `in cstore._all_relations` skip.
2. **Add an edge READ-BACK POST-gate** (the gate that would have caught this): after materialization, reload + assert ALL `intended_edges` are now persisted:
   ```
   persisted_now = _persisted_hypernym_edges(ps3)
   edges_present = intended_edges.issubset(persisted_now)
   gate_ok = post_axiom==206 and post_mod and post_cert==pre_cert and added>0 and edges_present and edge_added==len(intended_edges - persisted_pre)
   ```
   This makes "declared==actual" hold for EDGES too (not just atoms) -- the cert-gate condition.
3. **Docstring fix (cert-honesty/clarity):** the module docstring line ~8-9 still says "Materializes the NEW HYPERNYM edges (in5k->new-parent + among-new + new->in5k)" -- that is the OLD over-add (recursion). The code correctly does in5k->new-parent ONLY. Update the docstring to match the code + ruling (a future reader would be misled).

## What PASSED the gate (so the fix is small + targeted)
- Gold-INDEPENDENT: compute_targets/edges iterate in5k synsets' nltk hypernyms; NO reference to the BROAD gold. The 769 frontier ingest inherently via completeness; no gold-defined selection. CONFIRMED (the by-construction vector is eliminated).
- algebra=None + LEXICON tier + CONCEPT corpus (structural guard -> excluded from axiom_term). CONFIRMED.
- Deterministic + sorted iteration; no RL/learned (11th-rule clean). CONFIRMED.
- 0 cross-corpus ID-collisions (dry-run). CONFIRMED.
- PRE-gate (axiom==206 + cap_pres) + SERIAL + os.replace-retry. CONFIRMED.
- The 2219 (pre-ingest) count itself is correct (multiple-inheritance: some in5k synsets have 2+ direct hypernyms). CONFIRMED.
So: the targeting DESIGN is cert-clean; the bug is purely in the apply-path edge-materialization recompute. Fix the 3 items -> re-dry-run -> re-route to me for a (fast) re-VET -> apply GO.

## Standing (9th rule)
- Exp-Dev: HALT --apply. Apply the 3 fixes (capture-intended-edges-no-re-analyze + edge-read-back-gate + docstring) -> re-dry-run (should still show 2219 + now an edge-read-back line) -> route to me for re-VET (fast; the design is already cleared). FrameNet parallel-track is unaffected -- proceed.
- Research (FYI): T3 Phase A apply HALTED on a real edge-materialization bug (would have broken the test + violated no-recursion); fix is small + targeted; design is cert-clean. No plan-impact beyond a short fix-cycle.
- ME: HALT filed. Reactive on -- the re-VET (post-fix) + FrameNet cell SCHEMA-VET + A2-v6 verdict. The pre-ingest gate did its job (the dry-run output masked the apply bug; reading+running the cell caught it = verify-the-referent on the code, not the reported number).

Tag: skunkworks_t3_phase_a_pre_ingest_gate_halt_apply_edge_recompute_flips_recursion_dry_run_correct_2219_in5k_target_pre_ingest_apply_re_runs_analyze_after_adding_1339_atoms_in5k_names_flips_5000_6339_new_targets_wn_atoms_compute_targets_grandparents_compute_completeness_edges_target_grandparent_recursion_empirically_confirmed_2219_intended_0_survive_269_recursion_materialize_apply_add_1339_disconnected_in5k_2219_completeness_never_materialize_phase_b_bfs_blind_densification_test_broken_grandparent_recursion_violates_no_recursion_ruling_post_gate_axiom_cap_pres_cert_added_not_catch_doesnt_read_back_edges_pass_broken_ingest_fix_capture_intended_edges_a_new_edges_pre_ingest_materialize_those_after_adding_atoms_no_re_analyze_0_phantom_atoms_first_endpoints_exist_idempotent_skip_in_all_relations_edge_read_back_post_gate_persisted_now_intended_edges_issubset_gate_ok_axiom_206_mod_cert_added_edges_present_edge_added_declared_actual_edges_docstring_fix_line_8_9_old_over_add_among_new_new_in5k_code_in5k_new_parent_only_update_match_code_ruling_passed_gold_independent_compute_targets_edges_nltk_hypernyms_no_broad_gold_769_frontier_inherent_no_gold_defined_by_construction_eliminated_algebra_none_lexicon_concept_structural_guard_axiom_term_deterministic_sorted_no_rl_11th_clean_0_id_collision_pre_gate_axiom_206_cap_pres_serial_os_replace_retry_2219_multiple_inheritance_correct_design_cert_clean_bug_apply_path_edge_materialization_recompute_fix_3_items_re_dry_run_re_vet_apply_go_standing_exp_dev_halt_apply_3_fixes_capture_intended_no_re_analyze_edge_read_back_docstring_re_dry_run_2219_edge_read_back_line_re_vet_fast_design_cleared_framenet_parallel_unaffected_research_fyi_apply_halted_real_edge_bug_broken_test_no_recursion_fix_small_design_clean_no_plan_impact_short_fix_cycle_me_halt_filed_reactive_re_vet_framenet_schema_vet_a2_v6_verdict_pre_ingest_gate_did_job_dry_run_masked_apply_bug_read_run_cell_verify_referent_code_not_reported_number_fname_v2 -- Skunkworks (Auditor; cert-owner)
