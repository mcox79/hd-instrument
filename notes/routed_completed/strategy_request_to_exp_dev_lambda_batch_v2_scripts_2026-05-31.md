# Routing: exp_dev -- 3 Lambda experiment scripts for authorized batch v2

**From**: testbed session
**To**: exp_dev (via orchestrator)
**Date**: 2026-05-31
**Type**: experiment-script ship request
**Authorization**: user authorized batch per
`notes/testbed_handoff_lambda_and_anthropic_authorized_2026-05-31.md`
**Total budget**: ~$1.45 (cumulative session + this batch = ~$2.85)

## Context

Per session ownership, testbed does NOT write to `experiments/`. Needs
3 new experiment scripts shipped to `experiments/` (or per orchestrator's
preferred path) so testbed can dispatch via launch_experiment.py.

All 3 anchors are fully spec'd in the user-authorized handoff. The
specifications below are reproduced verbatim from that handoff so
exp_dev has the full contract.

## Anchor 1: a_query_sim cross-N replication at N=16384

- **Anchor name suggestion**:
  `adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384`
  (PROT-018 compliant: `_n16384` suffix bound to N)
- **Defense mechanism**: a_query_sim (the one that PASSED at N=4096
  today as G8_HARD_PASS with def=1.000 fp=0.000 across 5 seeds)
- **Configuration**: N=16384, M in {4096, 8192, 12288}, 5 seeds
- **Measurements**: defense rate, false-positive rate, latency
  overhead at large N
- **HP**: defense rate >= 0.95 AND fp <= 0.05 across all 15 cells
  (3 M-values x 5 seeds)
- **HF**: defense degrades sharply at N=16384 (rate < 0.50 OR
  fp > 0.20 at any cell)
- **MIDDLE**: anything in between
- **Strategic value**: closes the "single-N defense" caveat on
  today's adversarial-sub-row LIFT (would move 0.45-0.65 -> 0.55-0.75
  if PASS)
- **Budget**: ~$0.50 (5-seed * 3-M-values; modest GPU wall)

## Anchor 2: a_query_sim vs p4 edit-fact-traverse

- **Anchor name suggestion**:
  `adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096`
- **Attack pattern**: edit-fact-traverse (the second known adversarial
  pattern; the U2 99.4% breach reference)
- **Configuration**: N=4096, M=2048 (same operating point as today's
  G8_HARD_PASS), 5 seeds
- **Measurements**: defense rate against p4 attack, false-positive
  rate on legitimate edit-fact-traverse queries
- **HP**: defense rate >= 0.95 AND fp <= 0.05
- **HF**: defense rate < 0.50 OR fp > 0.20
- **MIDDLE**: anything in between
- **Strategic value**: tests whether a_query_sim is GENERAL (defeats
  both codebook-collision AND edit-fact-traverse) or
  codebook-collision-specific. If general, the D7 edit-log-replay
  engineering motivation reduces substantially (P6 in handoff).
- **Budget**: ~$0.30

## Anchor 3: Path D 48N-64N envelope extension

- **Anchor name suggestion**:
  `path_d_48n_64n_envelope_v1_n4096`
- **Extends**: today's G7_HARD_PASS at 24N-32N (`path_d_24n_32n_envelope_v1_n4096`)
- **Configuration**: N=4096, M in {196608, 262144} (= 48N, 64N),
  depth in {30, 50}, 3 seeds per cell (reduced from 5 to fit budget;
  rationale: today's 5-seed test at 32N showed near-zero variance, so
  3-seed sample is adequate at the new envelope)
- **Measurements**: accuracy, latency, KF stability per cell
- **HP**: all 12 cells (2 M-values * 2 depths * 3 seeds) acc >= 0.95
- **HF**: any cell acc < 0.50 (sharp cliff found)
- **MIDDLE**: anything in between
- **Strategic value**: completes Path D ceiling characterization at
  N=4096; would LIFT R-PATH-D-NO-CEILING from 0.88-0.97 toward
  0.92-0.98+ if PASS.
- **Budget**: ~$0.65

## Dispatch discipline (testbed will follow on launch)

- Pre-launch snapshot + 5xx retry + orphan reconcile (already in
  launch_experiment.py)
- Always-verbose: set -ex + python -u + stdbuf -oL + tee + SCP-back
  (already in launch_experiment.py)
- 6-attempt terminate retry + leak flag (already in launch_experiment.py)
- Generic progress wrapper with `--total-cells` set per-anchor
  (15 cells for A, 5 for B, 12 for C)
- Status_log HIGH for each PASS/FAIL verdict
- Routing file to orchestrator with all 3 verdicts after batch
  completes

## What testbed needs from exp_dev

1. The 3 experiment scripts written to `experiments/exp_*.py` paths
   (or whichever path exp_dev prefers; launch_experiment.py just takes
   `--script <path>`).
2. Scripts pushed to origin/main so cloud bootstrap pulls them.
3. A brief confirmation in this file's reply (or via
   `notes/exp_dev_decisions_<date>.md`) of:
   - Final anchor names (may differ from my suggestions)
   - Final script paths
   - Final --total-cells counts per anchor
   - Any change to the spec (HP/HF thresholds, sweep grid, etc.)

After exp_dev ships, testbed dispatches sequentially (one at a time
per user-authorized model; budget cap on each launch).

## Closing the routing

This routing closes when exp_dev replies (or moves it to
`routed_completed/` after shipping the scripts).

## exp_dev completion note (2026-05-31)

3 scripts scaffolded, self-tests PASS all 3. Final anchor names:
- A: adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384 (15 cells) -- N=16384
- B: adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096 (5 cells) -- N=4096
- C: path_d_48n_64n_envelope_v1_n4096 (12 cells) -- N=4096
HP/HF bands preserved verbatim from spec. COMMIT+PUSH deferred to main thread.
