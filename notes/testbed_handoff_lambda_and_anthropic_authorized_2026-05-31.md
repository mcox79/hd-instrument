# Testbed handoff: Lambda batch + Anthropic API both AUTHORIZED

**From**: orchestrator
**To**: testbed
**Date**: 2026-05-31
**Closes/extends**: `notes/testbed_handoff_external_distribution_2026-05-31.md` priorities P1 + P2

## TL;DR

User authorized both items. Testbed cleared to dispatch:
- **Lambda batch (~$1.45 total)** — 3 experiments per the P1 spec in the external-distribution handoff
- **Anthropic API (~$30-75 across 3 phases)** — Pattern B production-LLM integration

## Authorized Lambda batch (3 experiments)

Spec from `testbed_handoff_external_distribution_2026-05-31.md` P1; reproduced here:

### Experiment A — a_query_sim cross-N replication at N=16384 (~$0.50)

- Defense mechanism that PASSED at N=4096 today (G8_HARD_PASS, 1.000 def @ 0.000 fp, 5-seed)
- N=16384, M ∈ {4096, 8192, 12288}
- 5 seeds per cell
- Measurements: defense rate, false-positive rate, latency overhead at large N
- HP: defense rate >= 0.95 + false-positive rate <= 0.05 across all 3 M values, all 5 seeds
- HF: defense degrades sharply at N=16384 (rate < 0.50 OR fp > 0.20 at any cell)
- Strategic value: closes the "single-N defense" caveat on today's adversarial-sub-row LIFT (0.45-0.65 -> 0.55-0.75 if PASS)

### Experiment B — a_query_sim vs p4 edit-fact-traverse (~$0.30)

- Second known adversarial pattern (edit-semantics 99.4% breach per U2)
- N=4096, M=2048 (same operating point as p2 PASS)
- 5 seeds
- Measurements: defense rate against p4 attack, false-positive rate on legitimate edit-fact-traverse queries
- HP: defense rate >= 0.95 + fp <= 0.05
- Strategic value: tests whether a_query_sim is general (defeats both codebook-collision AND edit-fact-traverse) or codebook-collision-specific. If general, the D7 edit-log-replay engineering motivation reduces substantially.

### Experiment C — Path D 48-64N envelope extension (~$0.65)

- Continues today's G7_HARD_PASS past 32N
- M ∈ {196608, 262144} (48N, 64N at N=4096)
- Depth ∈ {30, 50}
- 3 seeds per cell (reduced from 5 to fit budget)
- Measurements: accuracy, latency, KF stability
- HP: all 12 cells (M × d × seed) acc >= 0.95
- HF: any cell acc < 0.50 (sharp cliff found)
- Strategic value: completes the Path D ceiling characterization at N=4096; would LIFT R-PATH-D-NO-CEILING from 0.88-0.97 toward 0.92-0.98+ if PASS.

## Dispatch discipline reminders

- Pre-launch snapshot + 5xx retry + orphan reconcile (per [[feedback-cloud-launch-snapshot-reconcile]])
- Always-verbose remote dispatch: set -ex + python -u + stdbuf -oL + tee + SCP-back (per [[feedback-always-verbose-remote-dispatch]])
- 6-attempt terminate retry with exponential backoff + leak flag (already in launch_experiment.py)
- log_event(source='testbed') after each experiment lands (HIGH for PASS/FAIL verdicts)

## Authorized Anthropic API (Pattern B production-LLM integration)

Spec from external-distribution handoff P2; budget tolerance ~$30-75 total across 3 phases.

### Phase 1 — Mock vs real wiring smoke (~$1-5)

Run mock LLM wiring tests against actual Anthropic API. Verify all 5 capability tests still pass with real LLM (audit-cert completeness, deletion correctness, edit-then-query coherence, multi-hop accuracy, latency).

### Phase 2 — Production query evaluation (~$20-50)

Substrate-backed Pattern B vs LLM-only baseline + LLM+RAG baseline on realistic queries.
Measurements: response quality, audit completeness, latency, cost per query.

### Phase 3 — Distinctive-value scenarios (~$10-20)

Edit-then-query coherence, deletion-with-certificate scenarios at production scale. Document where substrate adds value beyond LLM-only.

## API key location

Per memory `project_anthropic_api_key_available`: user has Anthropic key ready. If testbed cannot locate the key in the standard env var locations, file a quick orchestrator routing requesting the key location/handoff (do NOT bring up auth concerns again — auth is granted; only key-location is the open question).

Likely env var: `ANTHROPIC_API_KEY` in either user shell env or a `.env.anthropic` file in repo root (analogous to `.env.lambda` for Lambda creds, which is gitignored).

## Cost discipline reminders

- `tools/cloud/cost_tracker.py` already tracks Lambda spend cumulatively per [[feedback-cloud-launch-snapshot-reconcile]] commits
- Anthropic API costs should similarly accumulate in `data/anthropic_cost_tracker.json` if testbed wants symmetry (or just track at the script level)
- Daily Lambda cap remains $10; current cumulative ~$1.40 + $1.45 batch = ~$2.85 daily — comfortably within bounds
- Anthropic $75 across phases is a 1-2 week budget envelope, not single-day; pace accordingly

## Strategic note for ordering

- Lambda batch is INDEPENDENT of Anthropic work — testbed can dispatch in parallel or sequentially per testbed's preference
- Anthropic Phase 1 smoke (~$1-5) should be near-immediate after V2 drains and testbed has its evening complete; gates Phase 2/3 ramp
- Lambda batch results inform tomorrow morning's verdict review (cross-N adversarial defense + Path D ceiling closure)
- Anthropic Phase 2/3 results inform the Week 1 substrate-LLM feasibility smoke design (research P1)

## Closing the routing

Move this file to `notes/routed_completed/` after testbed reads + dispatches.
