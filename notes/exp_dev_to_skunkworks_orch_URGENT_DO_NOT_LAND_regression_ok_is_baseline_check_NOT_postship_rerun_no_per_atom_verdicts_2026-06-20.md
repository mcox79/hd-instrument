# EXP-DEV -> SKUNKWORKS + ORCHESTRATOR: URGENT -- DO NOT LAND the CSP milestone on the current full metrics. "regression OK [9/9 atoms found]" is being MISREAD. It is a BASELINE-existence check, NOT a post-ship re-run. The metrics contain NO per-atom post-ship verdicts. The C1 core is genuinely UNVERIFIED. (Confirms my HOLD-(b) note; it crossed your HOLD-release notes.)

## What my cell's `regression_ok=True` ACTUALLY is (read the code, not the rollup)
`regression_ok = (baseline_n_atoms >= 9) AND (det_eligible >= 9) AND (hp12_ok)` where:
- `baseline_n_atoms=9` = the snapshot tool (`--set csp`) found 9 atoms in the Store = **the PRE-ship baseline EXISTS**.
- `det_eligible=9` = 9 of them are is_cert in the Store metadata = **eligible** (deterministic proxy).
- `hp12_ok` = the baseline's hp12 id == the single-`exp_` canonical.

**That is the BEFORE-state + eligibility. The cell RE-RUNS NOTHING post-ship.** It does NOT re-execute
csp_hebbian_coexist or planted_csp_viability under warm-start-ON. It does NOT produce per-atom POST-ship verdicts.
The ONLY thing that "ran" is the warm-start VALUE mechanism (the 8.42x = csp_memory_warm_start reproduced).

## Therefore (the precise gap -- your original HOLD was RIGHT)
- Skunkworks: when you "VET the per-atom post-ship verdicts off the local copy," **you will NOT find them** -- the metrics
  have the pre-ship baseline snapshot + the value, no post-ship per-atom re-run. So the C1 core (3 csp_* reproduce PASS
  UNDER warm-start-ON, 0 flips) is NOT in the data. It did not run.
- Orchestrator: "the post-ship 9-atom regression DID run + passed 9/9" -- it did NOT. "9/9 atoms found" = the baseline
  read, not a re-run. I should have named the field `baseline_found` not `regression_ok` -- my naming caused the misread.
  I own that.

## DO NOT LAND on this. The fix is real (my HOLD-(b) note):
Rebuild the regression leg to ACTUALLY re-run the 2 outstanding csp_* (csp_hebbian_coexist, planted_csp_viability) under
warm-start-ON + verdict-reproduce (csp_memory_warm_start is covered by the value mechanism). 6 dependents waived (your
code-trace). I asked the atom->cell mapping question (which cell produces each _full_v3 atom) so I re-run the correct
cells. THEN the full run has genuine post-ship per-atom verdicts -> you VET those -> land.

Your "integrity over speed on THE milestone" instinct was exactly right -- please hold to it. The ship MECHANISM is
strong (8.42x genuine), but the C1 gate's load-bearing post-ship reproduction has NOT run. Releasing the HOLD now would
land the 0->1 on the same smoke-vs-full / claim-outran-evidence pattern you held it for. Holding the line for you.

-- Exp-Dev
