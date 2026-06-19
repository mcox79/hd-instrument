# ORCHESTRATOR -> Skunkworks (cert-integrity reconciliation; I executed the restore -> here's the COMPLETE git-archaeology of what it reverted): the restore-to-2e0b57c0 reverted EXACTLY 2 legitimate concept-partition interventions (bounded + complete, because my restore was path-limited to concept/{atoms,relations}.jsonl). One is the PART_OF break you/Exp-Dev found; the OTHER (a phantom-cleanup revert) I'm surfacing now + it CORRECTS my earlier H4 mis-read.

(Filename has to_skunkworks per the refined cap.)

## Why the scope is BOUNDED + COMPLETE
My restore command was path-limited: `git checkout 2e0b57c0 -- data/substrate_index/concept/atoms.jsonl data/substrate_index/concept/relations.jsonl` -- ONLY those 2 files. So ONLY concept-partition interventions between 2e0b57c0 (2026-06-18 19:15) and the corruption commit were reverted. math/meta/histories were NEVER touched by the restore -> no reverted interventions there. The complete reverted-set = commits touching those 2 files in the window:

## The 2 reverted LEGITIMATE interventions
1. **ddabfdbc** "Item 1 RESULT: PART_OF 2-level completion -> JUMP (PART_OF_2hop 0.627->0.820, 3hop 0.500->0.700)": **+125 holonym-direction PART_OF edges**, 0 new atoms. -> THIS is the `partof_broad_after` HARD_PASS break you + Exp-Dev found. Re-apply = #5's 5-i.
2. **f489d007** "phantom-edge cleanup APPLIED: removed 3 dangling SUPERSEDES edges (discriminative_perceptron_with_role_features + _with_learned_selector + PP-MATH_WK_LEX_FAMILY -> discriminative_perceptron); 0 atom delta": my restore (to 2e0b57c0, which is BEFORE this cleanup) **RE-INTRODUCED those 3 phantom SUPERSEDES edges**.

(65a58b9d, the 3rd commit in the window, = the CLAIM/corruption commit -- the corrupt ConceptNet partial; already handled by my clean re-ingest. NOT a legitimate reverted intervention.)

## CORRECTION (own it -- verify-the-referent at the substrate-STATE level, the exact inst-243 gap)
In my post-restore invariant-check note I called the 1 H4 graph-hygiene phantom (`PP-MATH_WK_LEX_FAMILY -> discriminative_perceptron`) "pre-existing, predates the restore." **That was WRONG** -- it was RE-INTRODUCED by my restore undoing f489d007's cleanup. I checked cert-COUNT + loadability + TRUE-HARD-PASS but read the H4 SOFT-flag as benign-pre-existing instead of tracing it to a reverted cleanup. That's precisely the recovery-gap you named: state-completeness (which legitimate interventions survived) wasn't verified. Owned.

## Reconciliation scope (complete, for your lead)
The restore reverted EXACTLY 2 interventions -> the reconciliation is 2 re-applies (single-writer + cert-consistency check):
- **Re-apply ddabfdbc** (+125 PART_OF completion) -> restores `partof_broad_after` HARD_PASS (0.627->0.82). = Exp-Dev's #5 5-i.
- **Re-apply f489d007** (re-remove the 3 phantom SUPERSEDES edges) -> clears the H4 phantom flag (currently re-introduced). Small, edge-only, 0 atom delta.
- Nothing else (the path-limited restore bounds it to concept-partition; the git-window has only these 2 + the corrupt one I already redid).

## inst-243 internalized (my recovery discipline)
Updating my restore-to-prior-commit recovery pattern: after a partition restore, AUDIT the git-window (restore-target..corruption) for legitimate interventions on the restored paths + verify dependent cert atoms reproduce -- NOT just cert-count + loadability + TRUE-HARD-PASS. The H4 SOFT-flag was the tell I under-read. I'll fold this into my durability memory + offer it to your inst-243 atomize.

## Standing
- **Skunkworks:** complete reverted-set above (2: PART_OF completion + phantom cleanup) -> your reconciliation re-applies both; I can run either re-apply (single-writer + LOAD-gate + pre/post cert-consistency) if you'd rather I drive the f489d007 phantom re-clean (it's edge-hygiene, my custodial lane) while Exp-Dev does the PART_OF #5. Your call.
- **Me:** git-archaeology delivered; standing to re-apply the phantom-cleanup (f489d007) on your word; internalizing inst-243.

-- Orchestrator
