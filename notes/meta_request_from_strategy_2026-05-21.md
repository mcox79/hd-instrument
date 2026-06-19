# Meta request from Strategy — 2026-05-21 cycle 4

**Sender**: Strategy session (session 1)
**Recipient**: META session (session 6)
**Topic**: Propose PROT-003 — closure requires rehab block + research-routed 2x pass

## What I'm asking

Add a new protocol to `notes/active_protocols.md` (META owns; Strategy
cannot self-write). I'm proposing the rule; META decides whether to
draft, route to user for approval, and add.

## The rule

Every ❌ closure that any session adds to `notes/substrate_capability_map.md`
or any other cross-session capability ledger MUST include, in the same
commit:

1. **3-5 axis-combination rescue sketches** (per [[feedback-rehabilitation-after-rejection]])
2. **A Research request entry** in `notes/active_priorities.md` flagging
   that 2x deep research is needed to *generate* the actual rescue list
   (per [[feedback-unbiased-research]] and [[project-research-playbook]]
   item 9)
3. **An explicit "PROVISIONAL" tag** on the closure until R + first
   rescue-experiment lands

The rescue sketches are placeholders — Strategy may not have the
literature background to vet them, and the "for AI" framing bias is a
documented failure mode. The actual rescue list is Research's output,
not Strategy's.

## Why this is structural

User caught two related gaps in cycles 3 and 4:

1. Cycle 3 ("did you research all negative results aggressively?"):
   v12 + v13 cap_map closures shipped without rehab blocks. I had
   the memory `feedback_rehabilitation_after_rejection.md` indexed but
   didn't honor it under multi-update batch pressure.

2. Cycle 4 ("are you incorporating 2x unbiased deep research for
   strategy investigation?"): the rehab blocks I drafted in cycle 4
   were my own brainstorm, framed "X for substrate," not Research-led
   "what does X do in the wild." Violated
   `feedback_unbiased_research.md` and the research playbook.

Both gaps share a root cause: Strategy's per-cycle protocol doesn't
**structurally require** routing closures through rehab + research.
Memorial honor system isn't enough — under multi-trigger batches
or session resets, the protocol drops.

PROT-003 makes it structural: cap_map closures literally can't pass
the protocol without (a) sketch + (b) R-routing + (c) PROVISIONAL tag.

## Proposed text for `active_protocols.md` if you approve

```
## PROT-003 — Closure requires rehab block + research-routed 2x pass

- Status: <pending approval>
- Applies to: Strategy (sole cap_map writer); any session that owns a
  capability ledger
- Trigger: writing a ❌ closure in cap_map or any cross-session
  capability ledger
- One-shot: no — every closure

What to do: in the same commit as the ❌ closure, include:
1. 3-5 axis-combination rescue sketches (DRAFT, your own brainstorm)
2. An R-request entry in active_priorities.md routing 2x deep research
   to populate the actual rescue list
3. PROVISIONAL tag on the closure until R + first experiment lands

Why: prevents single-pass closures from becoming load-bearing without
the rehabilitation discipline the project requires. Memorial reading of
feedback files isn't structural enough under batch-update pressure.
```

## What happens if you decline

I'll continue to self-enforce via Strategy's per-cycle decision log
and trust the user to call out drift. That's the cycle-3/cycle-4
pattern — it works but depends on the user's vigilance, which is
fragile.

## What you need from me

Nothing — file the proposal, route to user for approval, add the
protocol if approved. I'll self-implement next cycle if it lands.

## Cross-references

- v14 cap_map already includes DRAFT rescues + R7/R8/R9 for the three
  pending closures (Bet 3 chargeflip, multi-hop, Yonelinas DPSD).
- `notes/active_priorities.md` cycle 4 update added R7/R8/R9 entries.
- This request is the structural follow-up so cycles 5+ don't drift
  back to single-sentence closures.
