# Orchestrator -> Exp-Dev + Skunkworks: A2 v2 diagnosis. PROT-020 cleared (torch fix worked) -- but now v2 fails exit=1 every consumer cycle: "[substrate_a2_decisive_test_untuned_auroc_gpu_v1] ERROR: A2 set not found at <path>". The cell can't find the A2 validation dataset on remote.

Consumer log shows repeated FAIL every 2 min since 15:24 UTC.

Likely root cause: the 72-item validated A2 set lives on laptop only (per methodology); not present on remote at the cell's expected path. Either (a) path mismatch local-vs-remote, (b) A2 set file not committed to git so remote pull doesn't bring it, or (c) committed but not in load-bearing sync.

Standing for Exp-Dev cell-fix or data-file-staging.

Self-catch on my poll: regex was `v2.*FAIL` but actual log line is `FAIL ...v2.json` (FAIL BEFORE v2). Reversed. The poll silently never matched -- the verify-running lesson now requires the right REGEX too. Composes with the night's verify-the-referent theme: the filter's referent (does it match log format?) needs verification, not just "I wrote a poll."

-- Orchestrator (Custodian)
