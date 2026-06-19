# Research (Director) -> Orchestrator + Testbed: PHASE II Lean install bridge hit specific error -- lake init succeeded but the math template's mathlib4 revision pin `v4.31.0` not a valid tag in mathlib4 repo; 3 resolution paths surfaced; not silently trying more Bash per USER directive; STANDING for Orchestrator/Testbed response on path + execution

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~20:01 local
**Re:** lake init background task bwvi9caq5 completed with error. fname_v2 47 chars.

## ERROR

```
Output of bwvi9caq5 (lake init pythagoras_ip_v1 math):
   info: pythagoras_ip_v1: no previous manifest, creating one from
         scratch
   info: leanprover-community/mathlib: cloning
         https://github.com/leanprover-community/mathlib4
   error: .lake\packages\mathlib: revision not found 'v4.31.0'

Lakefile created in d:/AI/hd-instrument/lean_oracle/pythagoras_ip_v1/
   but mathlib4 dependency unresolved.
```

## 3 RESOLUTION PATHS (cert-owner/infra judgment)

```
1. Edit lakefile.lean to use mathlib4 master branch:
   require mathlib from git
     "https://github.com/leanprover-community/mathlib4" @ "master"
   Most flexible; current Lean 4.31.0 should be compatible per mathlib
   master toolchain.

2. Find the matching mathlib4 release tag:
   Check https://github.com/leanprover-community/mathlib4/tags
   Find tag matching Lean 4.31.0 (e.g. "v4.31.0-rc1" or similar)
   Pin lakefile to that tag.

3. Use a specific commit hash known compatible with Lean 4.31.0:
   Lookup mathlib4 commit that points to Lean 4.31.0 in its
   lean-toolchain file.
   Pin lakefile to that rev.

ORCHESTRATOR INFRA JUDGMENT (which path):
   - 1 is fastest (just `master`); risk: mathlib master may have
     just bumped to newer Lean
   - 2 is safest (pinned to release); requires GitHub query
   - 3 is most precise; requires commit lookup
```

## DIRECTOR NOT CROSS-LANE'ING further

```
Per USER directive: "the solution here isn't for you to fucking do it
   - it's to make this process work properly. coordinate with
   orchestrator. maybe a session that doesn't do shit, like testbed,
   could do it. use your brain"

The lake init bridge was the one bridge action. Will NOT silently try
   more Bash to fix the revision error.

Director coordination posture:
   - Surfaced error specifics + 3 resolution paths
   - Orchestrator/Testbed pick path + execute the fix
   - On execution: lake update -> lake exe cache get (~10-20 min
     download)
   - Director ratifies + integrates result
```

## STANDING / who I'm waiting on (9th rule)

- **Orchestrator (URGENT):** filesystem cross-check + pick resolution
  path (1/2/3) + execute; report cache-get progress
- **Testbed (BACKUP):** if Orchestrator still silent past 5-min timer
  (20:03), take over with resolution path + execution
- **Director (me):** coordination; will NOT try more Bash; ratifies
  results when delivered
- **Skunkworks (Auditor; cert-owner):** SEMANTICS-MATCH VET cycle
  standby (LOCKED rubric pre-VET PASS earlier)
- **Exp-Dev (Prover):** Pythagoras.lean proof writing standby when
  install clean
- **USER:** time-bounded ~1-hour window; ~13 min consumed; error
  surfaced + 3 paths; awaiting Orchestrator/Testbed pick + execute

Tag: phase_ii_lean_install_bridge_error_lake_init_succeeded_mathlib4_revision_pin_v4_31_0_not_valid_tag_3_resolution_paths_master_branch_flexible_release_tag_safest_commit_hash_precise_orchestrator_infra_judgment_director_not_cross_lane_user_directive_coordinate_orchestrator_testbed_use_brain_lake_init_bridge_one_action_no_silent_bash_surfaced_error_paths_orchestrator_testbed_pick_execute_lake_update_cache_get_director_ratify_integrate_standing_orchestrator_urgent_filesystem_check_path_execute_testbed_backup_5_min_timer_director_coordination_no_bash_skunkworks_semantics_match_vet_locked_rubric_pre_vet_pass_exp_dev_proof_writing_standby_install_clean_user_1_hour_13_min_error_paths_awaiting_pick_execute_fname_v2_47

-- Research (Director)
