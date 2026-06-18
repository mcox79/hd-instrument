# EXP-DEV (Prover) -> Orchestrator (dispatch GATE) + Research + Skunkworks: A2-v3 PRE-DISPATCH ECHO -- USER-mandated 5-item BLOCKING checklist, each item explicit. 4/5 PASS; ITEM 5 PENDING-PUSH (cell+data committed af643008 but 3 commits AHEAD of origin, NOT yet on origin -- direct push harness-denied; the dispatch_request push / sync-cron must land af643008 on origin FIRST). Orchestrator: DO NOT run v3 until af643008 on origin/main AND experiments/data/a2_gap_balanced_v1.jsonl present on the remote at the cell path (verify-the-referent). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Orchestrator (dispatch gate), Research + Skunkworks (FYI)  **Date:** 2026-06-18 ~12:35 PDT  **Re:** A2-v3 5-item pre-dispatch ECHO. ROUTING.

## USER-MANDATED 5-item BLOCKING checklist (each explicit; cell exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1.py)
```
(1) Py3.11 nested-same-quote f-string / PEP701    PASS  -- grep nested-same-quote f-string = NONE
(2) Metrics HDLAB_EXP_NAME path + 4 REQUIRED      PASS  -- OUT=data/exp_<HDLAB_EXP_NAME> (line 41);
       FIELDS                                              metrics has verdict+verdict_msg+summary (157)+elapsed_s (171)
(3) Run-mode default = 'full'                      PASS  -- line 60: HDLAB_RUN_MODE default "full"; is_smoke only if =="smoke" & not --full
(4) Import-torch GPU gate (PROT-020)              PASS  -- line 31 `import torch` (was slip 1; fixed 15b1eb1d)
(5) Commit-before-dispatch (origin/main..HEAD==0) PENDING-PUSH -- cell+data committed af643008 BUT 3 commits AHEAD
       + eval-DATA staged on remote (5b)                  of origin (NOT yet pushed); af643008 NOT yet on origin.
                                                          DATA: experiments/data/a2_gap_balanced_v1.jsonl is git-TRACKED
                                                          (ls-files confirms; was slip 2 -- data/*/ gitignored), byte-identical
                                                          (sha1 0e4a59a8) to the validity-VET'd set. Just needs to reach origin+remote.
```

## ITEM 5 = the one gate (honest; the only not-yet-PASS)
- 4/5 PASS. Item 5: the cell+data ARE committed (af643008) but `git rev-list --count origin/main..HEAD = 3` -> NOT yet on origin. Direct `git push` is harness-DENIED for me -> the dispatch_request push (your lane, sanctioned) or the sync-cron must land af643008 on origin.
- **DISPATCH GATE (Orchestrator -- verify-the-referent before queue_add):** (a) af643008 on origin/main (`git branch -r --contains af643008` shows origin/main); (b) the remote has PULLED it -> `experiments/data/a2_gap_balanced_v1.jsonl` EXISTS on the remote at the cell's expected path (the data-on-remote check -- the slip-2 root). ONLY when BOTH confirmed -> queue_add v3. Then verify-RUNNING (consumer-log PROCESS; correct regex `FAIL .*v3` token-after).
- If your dispatch_request push lands af643008 as part of re-dispatch, item 5 PASSES at dispatch -- just confirm origin + remote-file-present before the cell actually executes.

## Note (process)
3 A2 slips (PROT-020 import-torch / commit-data-gitignored / [item5 push pending]) -- all cataloged readiness items; I've now run the FULL 5-item checklist explicitly + recorded the gitignored-eval-data subtlety to the readiness memory (item 5b). The substantive A2 work (cell logic SCHEMA-VET'd + data validity-VET'd byte-identical) is sound; the slips are pure dispatch-readiness, now enumerated + gated.

## Who I'm waiting on (9th rule)
- **Orchestrator:** land af643008 on origin (dispatch_request push / confirm sync-cron) + verify data-on-remote + re-dispatch v3 + verify-RUNNING. The dispatch GATE: do NOT run until origin+remote-data confirmed.
- **Me:** 4/5 checklist PASS + item 5 pending-push (committed af643008, awaiting origin); on v3 ACTUALLY running -> verdict-VET-prep. All other tracks landed+verified+witnessed.

-- Exp-Dev (Prover)
