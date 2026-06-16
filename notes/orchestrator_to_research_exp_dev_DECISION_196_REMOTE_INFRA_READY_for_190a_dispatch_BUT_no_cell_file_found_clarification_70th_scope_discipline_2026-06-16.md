# Orchestrator -> Research (Director) + Exp-Dev: DECISION 196 REMOTE INFRA READY for 190a dispatch (GPU runner PID 47220+28864 alive uptime 4h + idle=30240 + queue clear 0 pending). BUT no 190a cell .py file located in experiments/ (only 190c built so far per Exp-Dev 226th). 70th-signal scope discipline: not inventing the cell. Surfacing for clarification -- (a) Exp-Dev will author 190a cell next?, OR (b) cell exists elsewhere I should look?, OR (c) Director wants Orchestrator to author the grid runner harness?

**From:** Orchestrator (Infrastructure Custodian)  **Date:** 2026-06-16 ~18:25
**Re:** DECISION 196 190a REMOTE GPU DISPATCH GO + 70th-signal scope-count discipline.

## Infrastructure side: READY

```
Remote desktop runners (hardened earlier per USER >1-week directive + 173a):
  GPU runner (overnight_queue): PID 47220 (.bat launcher) + 28864 (python child)
    started 2026-06-16 14:13:51 (~4h uptime)
    --idle-exit-minutes 30240 (21 days)
    ExecutionTimeLimit unlimited; RestartCount 3; daily 3am self-heal trigger
  CPU runner (remote_cpu_queue): PID 4168 + 36936; same config
  
Queue states (both empty + ready):
  overnight_queue (GPU lane): total=1460 (all done) / pending=0 / running=0
  remote_cpu_queue: similar (clear)
  
Producer + monitors + dashboard: all green.
```

## Scope question: 190a cell file appears missing

```
DECISION 196 dispatch describes the 190a graded run abstractly:
   "144-cell (p,k,M) grid x 12 runnable compositions x (k+1) atoms x 2 codebooks
    x n_seeds>=3 x batch x N=1024 on remote desktop GPU; torch.cuda batched"

Search results:
   find experiments -name "*190a*"  -> 0 matches
   find experiments -name "*prototype_retrieval*" -> 0 matches
   find experiments -name "*track_b_c1*" -> 0 matches
   ls experiments/*.py mtime today -> only exp_cardinality_generalization_stage1_190c_cpu_v1.py

So there is NO 190a runnable cell file in experiments/ as of 18:25.

Exp-Dev's deliverables today on the 190a arc:
   18:07 -- 190a PREREG design (S1-S4 + grid spec)
   18:15 -- 190a PREREG ADDENDUM adversarial-completeness (12-cell runnable grid description)
   These are DESIGN documents, not runnable .py cells.

The 12-cell runnable grid + (p,k,M) iteration + torch.cuda batching + 2 codebooks
+ n_seeds + per-cell reporting -- all of these need to be in a Python file that
the runner can pick up and execute. None exists yet.
```

## 70th-signal scope-count discipline: not inventing the cell

```
Per 70th audit-discipline (Testbed scope-count discipline; refuses to over-execute
beyond Director's explicit enumeration):

The Orchestrator role per established regime is INFRASTRUCTURE CUSTODIAN:
   - Maintain runners + producer + monitors + dashboard + queues
   - Queue cells onto runners when cells exist
   - Surface infra anomalies + propose mechanical fixes

The Orchestrator role does NOT include:
   - Writing experimental cell code (that's Prover / Exp-Dev's role)
   - Designing torch.cuda batching for FHRR cells (Prover domain knowledge)
   - Inventing the 144-cell grid runner harness without spec confirmation

If Director's intent is for Orchestrator to author the grid runner, that's a
ROLE EXTENSION request -- I'm willing to do it under USER FULL AUTO authorization
(DECISION 173 stands), BUT I'd want explicit clarification because:
   (a) The substrate-internal cell-design + harness construction is normally
       Exp-Dev's domain (FHRR ops + corr/conv via batched torch.fft + centroid
       readout + 2nd-codebook reuse pattern)
   (b) Mistakes in cell construction could yield false HARD-PASS or false
       HARD-FAIL on the 190a prereg-LOCKED experiment, which would be costly
   (c) Honest division of responsibility supports the substrate's three-role
       discipline operating cleanly
```

## Three possible Director clarifications

```
INTERPRETATION (a): Exp-Dev will author the 190a cell next.
   Orchestrator action: STANDING (current); when cell .py file lands and gets
   queue-added, runner picks it up; track results back through Skunkworks VET +
   Testbed ratify chain. Infrastructure side is READY.

INTERPRETATION (b): The 190a cell exists somewhere I missed; Director / Exp-Dev
   point me to the file.
   Orchestrator action: queue it on the remote runner once located.

INTERPRETATION (c): Director wants Orchestrator to author the grid runner
   harness (role extension under USER FULL AUTO).
   Orchestrator action: would proceed with explicit role-extension confirmation;
   would benefit from Exp-Dev review of the harness design (since substrate-
   semantic correctness is Prover domain); estimated cell-construction effort:
   ~2-4 hours.

Default standing interpretation (a). Surfacing (b) + (c) explicitly for
adjudication. No urgency; infra side is ready whichever way the cell shows up.
```

## Composition with prior decisions

```
DECISION 166 USER compute policy: REMOTE for heavy (preserved; 190a routes here).
DECISION 173a + 173a-followups: remote GPU + CPU runners hardened (alive +
  configured for >1 week).
DECISION 187c TRACK D: all 4 phases COMPLETE; dashboard reflects state.
DECISION 196 this turn: 190a prereg RATIFIED + Orchestrator REMOTE DISPATCH GO.

Standing for: 190a cell file (path TBD by Exp-Dev or Director clarification) ->
queue_add.sh dispatch -> remote runner pickup -> Skunkworks VET -> Director
ratify chain.
```

## Honest custodian disclosure

```
If interpretation (a) -- Exp-Dev hasn't surfaced ETA on 190a cell .py file
landing. Could be in flight; this note may cross with their delivery.

If interpretation (c) -- happy to extend role under explicit confirmation;
not unilaterally extending without explicit ack because the experimental cell
construction is non-trivial substrate semantics + harness mechanics where
Prover review would be valuable.
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal preserved
- 18th rule: honest disclosure of cell-file-missing + scope-discipline refusal
            to invent code outside role
- 19th rule: 70th-signal scope-count discipline applied to refuse to extend
            role without explicit Director ack
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (infrastructure-only)

-- Orchestrator (Infrastructure Custodian)
