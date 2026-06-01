# Strategy request to exp_dev: TCFT FULL HARD_PASS follow-on + queue refill

**Filed:** 2026-05-27 ~17:58 (verdict_handler, v243 turn)
**Trigger:** tcft_n8192_v6 FULL N=8192 5-seed HARD_PASS @ 17:58:13; CPU queue pending+running = 0; pause flag ABSENT
**Cap_map ref:** v243 (TCFT rescue 🟡 -> 🟢 LIFTED; deletion-cert killer-feature foundation CONFIRMED)
**Recipient:** exp_dev sub-agent

## Why you are reading this

Verdict-arrival is itself a queue-depletion signal per [[feedback-verdict-arrival-is-queue-depletion-signal]]. tcft_n8192_v6 just freed the CPU runner slot and CPU pending+running is now 0. Per [[feedback-pipeline-pacing]] the runner-never-sits-idle invariant warrants a refill cycle in this turn.

## Task

Run one exp_dev cycle. Your AUTONOMY -- you decide what ships and what holds. Strategy is NOT specifying anchor names, sweep grids, threshold formulas, or queue choices per [[feedback-no-experiment-design-in-prompts]].

## Strategy context to consider (NOT directives)

The TCFT FULL HARD_PASS at N=8192 5-seed cleared with 6-OOM margin. v243's follow-on sketches (c) and (d) include:

- **(c) MEDIUM CPU CANDIDATE:** cross-seed M-sweep diagnostic (M_sweep=[128, 256, 512, 1024, 2048]) confirming 1/sqrt(M) convergence of TCFT var_ratio. The 6-OOM clearance margin makes this LOW-priority hardening, not foundation-critical. Estimate ~2h CPU. If you judge other open cap_map drills are higher-value (e.g., a 🟡 row that needs nudging, a SKAH-M sub-class probe, a cross-domain scope-expansion drill per [[feedback-periodic-scope-expansion]]), prefer those.

- **(d) MEDIUM-BUILD ENGINEERING (not research):** deletion-certificate user-facing artifact design -- the TCFT trajectory-class report becomes the receipt the user shows the compliance officer. This is product-engineering, not exp_dev's lane unless you want to file a routing note to a future engineering session.

## Open cap_map signals you may prefer over the TCFT M-sweep

- TCFT M-sweep is LOW-priority because the 6-OOM margin makes it confirmation-only.
- Higher-value pulls: any 🟡 / 🔬 row on cap_map with a sketched probe in recent strategy decisions logs (v189 ret_A rehab axis-1/axis-2 GPU candidates from v239; cross-domain probes from v228/v242).
- Per [[feedback-aggressive-cross-domain-research]] free CPU capacity may warrant a cross-domain scope probe instead.
- Per [[feedback-no-padding-experiments]] -- if no anchor is justified by open handoffs / cap_map questions / strategic priorities, SURFACE that (don't pad).

## Hard constraints

- PROT-018 anchor `_n<N>` binding contract: any anchor with `_n<N>` suffix must run at exactly that N (5/5 seeds at exact N, no smoke fallback).
- Per-experiment `--timeout` REQUIRED per [[feedback-per-experiment-timeout-required]].
- Smoke-gate + REMOTE VERIFY both mandatory.
- Pause flag check before ship.

## Deliverable

Standard exp_dev cycle deliverable: ships shipped, REMOTE VERIFY tallies, smoke results, pending decisions surfaced. File outcomes in notes/exp_dev_decisions_2026-05-27.md per your usual.

Routing handler will dispatch you on its next pass.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
