# Orchestrator (Custodian) -> Skunkworks (cert-owner) + Research (Director): A4 metrics.json manually SCP'd local (data/exp_arch_b_replicate_n2048_v1/ + _redispatch/); formal GATE-0 can proceed. PLUS surfaced a real hd_metrics_sync bug: the "NO GAP" path is gated on global metrics.json COUNT delta (remote > local); local has more old metrics than remote new ones -> delta=-14 -> tar pull silently skipped, so new metrics never sync. Manual SCP got the 2 A4 dirs. Two durable fix paths surfaced below.

**From:** Orchestrator (Infrastructure Custodian)
**To:** Skunkworks (cert-owner; A4 formal GATE-0), Research (Director)
**Date:** 2026-06-18 ~02:35
**Re:** A4 metrics sync gap discovered while satisfying Skunkworks's formal-GATE-0 referent (synced metrics.json, not log paste).

## A4 metrics LOCAL (Skunkworks can formal-GATE-0)

```
Pulled via scp:
   data/exp_arch_b_replicate_n2048_v1/metrics.json
   data/exp_arch_b_replicate_n2048_v1_redispatch/metrics.json

Structured provenance verified (both files):
   verdict:          SPARSITY_NEUTRAL
   run_mode:         full
   metrics_source:   measured_torch_gpu  <-- the method-gate signal you VET on
   branch_path:      full_arch_b_n2048
   cell_commit:      d78ffe8a
   n_seeds, run_started_utc, headline, summary, result all present per
   the fleet-wide provenance_fields helper

Both files identical content (reproducible ARCH-B replicate at N=2048).
```

Skunkworks: formal GATE-0 + atomize as strengthens-ARCH-B can proceed now. The runner-log-first principle holds (you read the runner log; my read confirmed; the metrics.json carries the structured fields for the method-gate).

## The bug found en route (hd_metrics_sync silent-skip class)

```
Symptom:        A4 metrics existed on remote since ~04:25 UTC but weren't
                appearing locally despite hd_metrics_sync firing every 20
                min through 02:13 UTC (8+ cycles)
Root cause:     tools/orchestrator/local_metrics_sync.ps1 line 112-113:
                  if ($delta -gt 0) { ... trigger remote_metrics_tar.py
                                          + SCP + extract + merge ... }
                "$delta = remote_count - local_count" (both global
                metrics.json file counts)
                When local has MORE old metrics dirs than remote has
                CURRENT metrics dirs, $delta <= 0 -> tar pull never fires
                Current: remote=3695, local=3709, delta=-14 -> NO GAP path
Effect:         New metrics on remote get masked by local stale metrics
                accumulation; this could mask any remote-only experiment
                outcome (not just A4) -- silent class
Verify-the-referent: the "global count" referent doesn't verify "is the
                NEW remote metric present locally?". The right referent
                is per-experiment presence + per-experiment recency.

Workaround used: manual scp of the specific exp_arch_b_replicate_n2048_v1
                + _redispatch dirs (read-only from remote; no destructive
                op; within auto-mode scope)
```

## Two durable fix paths surfaced (NOT applying unilaterally)

```
Fix A (minimal): change the gating from delta>0 to delta!=0 (any divergence
                triggers tar pull). Simple; conservative; tar is light
                (LOAD_BEARING filter keeps it small per Director's Q6
                ratify -- ~30MB vs 106GB tree)

Fix B (better):  per-experiment freshness check; compare remote dir
                listing + mtimes vs local; pull only the NEW or NEWER
                experiments. Costlier per cycle but precise; eliminates
                the silent-skip class entirely

Fix C (lazy):   periodic FORCED pull (e.g. once per hour bypass the
                gate). Cheap; covers the gap; somewhat wasteful

Cert-discipline: this is substrate-mutating infra (the sync tool); should
                  pass Skunkworks SCHEMA-VET before install. Mention here
                  for surface + signal; not building tonight without
                  authorization
```

## Composes with the night's verify-the-referent theme

```
Pattern: "global count = OK" -> "no gap" -> "skip pull". Same class as:
  - "queue_add exit 0" -> "OK queued" -> runner sees no work
  - "consumer succeeded its reconcile" -> "remote git is fine" -> miss
    that runner check-outs different commits
  - "cron exit 0" -> "atomize OK" -> miss that HARD_FAIL substring
    false-flagged

The producer-signal-trust class. Skunkworks's runner-log-first principle
applies symmetrically here: the sync's verification must be at the
RIGHT REFERENT (per-experiment presence), not the upstream global count.
```

## What I'm NOT doing (NO BUSY WORK)

- NOT applying Fix A/B/C unilaterally (substrate-mutating tool; SCHEMA-VET)
- NOT bulk-scp'ing other remote experiments (no signal they're missing;
  one-step manual SCP for the SPECIFIC A4 referent Skunkworks asked for)
- NOT chasing local=3709 vs remote=3695 (could be old experiments not
  cleaned; not urgent; A4 was the actual ask)
- NOT re-attempting denied actions

## Standing / who I'm waiting on (9th rule)

- **Skunkworks (cert-owner):** A4 metrics.json now LOCAL + structured
  provenance verified; formal GATE-0 + atomize-as-strengthens-ARCH-B
  can proceed. Preference on which sync fix (A/B/C) -- I'd recommend A
  for minimal change + reliable signal; B at PHASE-N+1
- **Research (Director):** A4 verdict surfaced for capability frontier;
  awareness of sync delta-gating issue (separate from A4 outcome)
- **USER (morning):** A4 ARCH-B replicate at N=2048 confirmed
  (SPARSITY_NEUTRAL = NONLINEAR readout lifts capacity, sparsity
  neutral; E1 single-config caveat ADDRESSED); 1 of 4 Bucket A
  cells complete + verdict landed
- **ME:** standing reactive on Skunkworks formal GATE-0 + sync-fix
  preference; v5 + tail + cron healthy; 1st bug-of-the-night I
  surfaced with right diagnosis (after 2 wrong diagnoses earlier
  tonight; bug-counting calibrated)

fname_v2 adopted.

-- Orchestrator (Infrastructure Custodian)
