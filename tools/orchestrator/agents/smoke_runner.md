# smoke_runner — rote smoke + queue_add + verify agent

**Purpose:** offload the rote "smoke + queue_add + REMOTE VERIFY + status_log" step from exp_dev to a lighter agent. Lets exp_dev focus on design (script + prereg + parameter calibration) while smoke_runner handles the mechanical ship step.

**Model:** sonnet (this is pure rote — no design judgment needed).

**Risk:** MEDIUM. Per `notes/efficiency_rollout_2026-06-02.md` item #8, first 2 runs require manual audit:
- Verify smoke_runner ran smoke correctly (GPU util > 5%, exit 0)
- Verify timeout computed per PROT-019 formula
- Verify queue_add landed (REMOTE VERIFY hit)
- Verify status_log entry emitted
- Promote to default only after 2 manual-audit PASS runs

---

## Handoff protocol

After exp_dev designs N anchors, it writes a handoff file:

`notes/exp_dev_handoff_to_smoke_runner_<timestamp>.json`

Schema:
```json
{
  "cycle": "v347",
  "anchors": [
    {
      "name": "q_b1_chain_depth_90_v1_n8192",
      "script": "experiments/exp_q_b1_chain_depth_90_v1_n8192.py",
      "prereg": "preregs/2026-06-02_q_b1_chain_depth_90.md",
      "queue": "overnight_queue",
      "smoke_n": 4096,
      "smoke_seeds": 2,
      "full_n": 8192,
      "full_seeds": 5,
      "scaling_exp": 1.5
    }
  ]
}
```

exp_dev's final responsibility (when smoke_runner is enabled):
- Scripts + preregs written
- Handoff file emitted
- Return ONE line: "DESIGNED: N anchors; handoff at <path>"

exp_dev does NOT call smoke / queue_add / REMOTE VERIFY in this mode.

---

## smoke_runner workflow

1. Read handoff file
2. For each anchor:
   - Call `python tools/ship_anchor.py --name <name> --script <script> --prereg <prereg> --queue <queue> --smoke-n <smoke_n> --smoke-seeds <smoke_seeds> --full-n <full_n> --full-seeds <full_seeds> --scaling-exp <scaling_exp>`
   - On exit 0: record SHIPPED
   - On non-zero: capture the GATE_FAIL message; abort the batch and route the failed anchor + remaining unshipped anchors back to exp_dev
3. Delete handoff file on full success
4. Return ONE line: "SHIPPED: <N> anchors; REMOTE VERIFY pass/total"; any failures named + reason

---

## Dispatch prompt template

```
SMOKE+SHIP — handoff file: <path>

Read the file. For each anchor, call `tools/ship_anchor.py` with the supplied parameters. Record results. If any ship_anchor.py exits non-zero, capture the failure and route back to exp_dev (don't continue shipping the batch — exp_dev needs to see the failure context).

DISCIPLINE:
- No design work (don't redesign on failure; route back)
- No commit (main thread commits)
- ASCII

Return ONE line: SHIPPED N + REMOTE VERIFY pass/total + any failures (name + reason).
```

---

## When NOT to use smoke_runner

- Novel anchor family (smoke may need design judgment; keep in exp_dev)
- Smoke failure expected (debugging cycle; keep in exp_dev for iteration)
- The anchor uses a non-standard ship path (cloud, custom timeout, etc.)
- ship_anchor.py doesn't support the family yet

Default: when exp_dev determines all anchors are standard ceiling-chases with templates available, route to smoke_runner. Otherwise, exp_dev does the smoke step itself as today.

---

## Shadow-mode tracking (first 2 runs)

When invoking smoke_runner for the FIRST 2 times, ALSO have exp_dev keep its smoke step (instead of just designing). Then COMPARE:
- exp_dev's smoke results vs smoke_runner's smoke results (should be identical for deterministic scripts)
- exp_dev's computed timeout vs smoke_runner's computed timeout (should be identical via PROT-019 formula)
- exp_dev's queue entry vs smoke_runner's queue entry (should be identical)

Document in `notes/efficiency_rollout_2026-06-02.md`:
- Run N: <date>
- Smoke diff: <PASS|FAIL>
- Timeout diff: <PASS|FAIL>
- Queue entry diff: <PASS|FAIL>
- Wall time: smoke_runner vs exp_dev

After 2 PASS runs, promote: exp_dev returns "DESIGNED" after writing handoff file; smoke_runner is the smoke+ship path.
