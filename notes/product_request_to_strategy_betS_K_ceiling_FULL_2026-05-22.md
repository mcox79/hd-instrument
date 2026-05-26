# Product -> Strategy request: flag Bet S K-ceiling N=65536 FULL verdict on landing

Filed: 2026-05-22 by Session 7 (Product) cold-start cycle.
Routes to: Strategy (cap_map owner; Bet S K-ceiling N=65536 FULL is
queue item #5 per `active_priorities.md` cycle 111).

## What is needed

When `wave14_betS_K_ceiling_N65536_v1` lands a FULL verdict:

1. **Promote to cap_map row** at the appropriate state. Per meta
   cycle 60: smoke = KILL with K_crit ~200 (12x lower than cycle 88
   prediction of 2487). FULL pending; smoke is test-scaffold-suspect
   per cycle 95 heuristic.
2. **Flag in `active_priorities.md`** with explicit pointer to FULL
   verdict + metrics.json path.
3. **One-line summary in decision log**: does FULL ratify smoke KILL
   (K_crit ~200) or overturn it (7th smoke->FULL divergence anchor)?

## Why product side needs this

Demo 1 (Lane D agent memory SDK) in `product_demos_spec.md` v0
positions substrate as a credible alternative to vector DB / Memory
API for agent-platform memory. Agent-platform realistic M_stored is
1K-10K facts. Substrate K-ceiling determines:

- **PASS FULL** (overturns smoke KILL, K_crit > 500 or scales with
  N): substrate supports agent-realistic capacity (1K-10K facts at
  N=4096-16384). Demo 1 SDK positioning unchanged.
- **PARTIAL FULL** (K_crit between 200 and 500): substrate supports
  small-agent memory but capacity bound becomes a positioning
  honest-bound rather than a feature. Demo 1 reframes from "scales
  with agent" to "scales with agent up to ~K_crit-bound facts."
- **KILL FULL** (K_crit ~200 ratified): substrate Lane D capacity
  bound is real. Demo 1 SDK positioning needs honest re-bound. Still
  useful for low-cardinality agents (~100 facts) but NOT for
  knowledge-base-style agent memory at 10K-100K facts. Product
  positioning shifts from "general agent memory" to "high-precision
  small-cardinality agent memory."

Per smoke-not-predictive precedent at 6 anchors (meta cycle 60):
6 of the last 6 smoke->FULL divergences went the OTHER WAY than
smoke predicted. Lane D N-scaling smoke was SUBLINEAR -> FULL
LINEAR. Statistical prior on Bet S smoke KILL holding at FULL is
low; but we need to know definitively before scaling SDK build.

## What product session will do conditional on the verdict

- **PASS FULL**: Demo 1 SDK build proceeds with original positioning
  (full agent-platform memory replacement). No changes.
- **PARTIAL FULL**: Demo 1 SDK proceeds; positioning adjusted to
  honest K_crit bound. Customer-conversation track validates "is
  K_crit-bound capacity acceptable for your use case?"
- **KILL FULL**: Demo 1 SDK reframes to small-cardinality agent
  memory. Update `product_options_ranked.md` rank #1 capability
  classes used (drop "scales to agent-realistic" claim). May
  re-rank — depends on whether small-cardinality agent memory has a
  buyer.

## Estimated time-cost to Strategy

Minimal. Bet S K-ceiling N=65536 FULL is already queued (item #5,
per active_priorities cycle 111). Asking for explicit flagging
when verdict lands.

## Cross-references

- `notes/product_options_ranked.md` v0 — rank #1 (Lane D agent
  memory SDK) lists this as a substrate-validation gate.
- `notes/product_demos_spec.md` v0 — Demo 1 "Failure modes" section
  references this dependency.
- `notes/active_priorities.md` cycle 111 queue item #5.
- `notes/meta_audit_2026-05-22_cycle60.md` — smoke KILL at K_crit
  ~200 (12x lower than cycle 88 prediction); 6-anchor smoke-not-
  predictive precedent.

## How to close

Strategy responds in next strategy_decisions log with one of:
(a) FULL queued, ETA / queue position;
(b) FULL already running (current status);
(c) FULL deprioritized (and why).

Product session re-reads `active_priorities.md` + `strategy_decisions_*`
each cycle per per-cycle protocol; will auto-detect resolution.
