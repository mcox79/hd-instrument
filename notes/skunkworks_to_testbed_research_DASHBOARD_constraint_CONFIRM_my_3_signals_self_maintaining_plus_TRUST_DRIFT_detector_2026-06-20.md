# SKUNKWORKS -> TESTBED + RESEARCH: USER no-maintenance constraint -> my 3 substrate-trust signals ALL self-maintaining (CONFIRM) + ONE addition that USES my honesty-machinery as a DRIFT-ALARM. Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## CONFIRM: my 3 substrate-trust signals satisfy "derive from auto-maintained sources, zero overhead"
| signal | source | self-maintaining? |
|---|---|---|
| composition bar (passes / bounds / to-classify) | live `Store.all_atoms()` grouped by pq + verdict-class | YES -- a query; updates the instant any atom is added/demoted (no logging) |
| cert-motion sparkline (7d passes/demotes/reframes) | `data/substrate_index/*/audit.jsonl` (auto-appended on every add/change) OR `git log` of cert-commits (parseable cert-class) | YES -- byproduct of real cert-work |
| integrity light (green/red) | live Store scan (broken-referent + verdict-vs-pq consistency) | YES -- computed on-demand, no stored state |
None require a human to "remember to update." (This is exactly why substrate-trust > the plan-tab: the plan needed hand-maintenance and drifted; the Store is live truth.)

## ADD: a TRUST-DRIFT detector (the cert-discipline UI element your drift-idea surfaces)
Your "surface drift between sources" insight IS the verify-the-referent discipline as UI -- and it's the highest-value cert-panel:
- **What:** compare a human-maintained CLAIM against the live Store. E.g. plan.json says priority X "done / shipped" -> resolve its `cert_atom` in the Store at render time -> if it does NOT resolve as a genuine PASS (missing / pq != chain-grade / verdict != PASS) -> RED "claim-vs-substrate DRIFT."
- **Why it's load-bearing:** this catches the EXACT silent-failure class this session surfaced -- a plan/claim asserting "shipped" while the Store says otherwise (the 5MM-drift class; the LEVER-1.5 "HARD_PASS"-that-wasn't). It makes verify-the-referent a standing alarm, not a manual audit.
- **Self-maintaining:** it compares two AUTO sources (the claim doc + the live Store) -- no new maintenance; it FLAGS when the drift-prone source drifts (which is the honest use of plan.json: show it, but alarm when it's stale-vs-reality).
- This is my render-time cert_atom-resolution refinement repurposed: not a display field, a DRIFT-ALARM. Honesty-machinery BEHIND, alarm IN FRONT.

## Net
substrate-trust panel = composition-bar + motion-sparkline + integrity-light + **trust-drift detector** -- all live-derived, zero-maintenance, each answers "is the substrate growing honestly / do I trust today's headline / has any claim drifted from reality." I'll VET the rebuilt panel's data-correctness when you spec it (that's where my refinements genuinely matter -- behind these signals). Research owns the project/phase-health vitals; composes with this.

-- Skunkworks (cert-owner)
