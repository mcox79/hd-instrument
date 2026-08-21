# CORRECTION -- **THE REGISTRY IS NOT BLIND. IT DOCUMENTS 101 UNREACHED CAPABILITIES, ACCURATELY, AND NOBODY ACTS ON IT.**

**An hour ago I wrote: *"THREE WORKING, CONTROLLED CAPABILITIES THAT NOTHING CONSUMES ... that is why
the owner had to remember this work: the registry-first check returns NOTHING for it."*
That was true of ONE of the three. I checked the other two instead of assuming, and the registry has
rows for both -- accurate ones.**

| capability | registry row | what it says |
|---|---|---|
| `gap_driven_reader` | ✅ **`gap_driven_reader_self_directed_order`** | `WIRE` / **`WIRED_BUT_NOT_PIPELINE_REACHABLE`** |
| `information_foraging` | ✅ **`information_foraging_mvt_leave_rule`** | `WIRE` / **`WIRED_BUT_NOT_PIPELINE_REACHABLE`** |
| cold placement | 🔴 **absent** (now registered) | -- |

**➡️ THE REGISTRY ALREADY KNEW. It says, in its own field, that these are built and NOT REACHED BY
THE PIPELINE. My "the system's inventory omits its best work" framing was wrong for two of three.**

*(Also confirmed: `gap_detector_familiarity_gate` is `WIRED_AND_PIPELINE_USED` -- consistent with
tonight's runtime probe, where the gap detector discriminated perfectly on the live foundation.)*

## 🚨 AND THE CORRECTED VERSION IS A WORSE PROBLEM, NOT A SMALLER ONE

| `pipeline_status` across 209 rows | n |
|---|---|
| **`WIRED_BUT_NOT_PIPELINE_REACHABLE`** | **101** |
| `N_A` | 59 |
| `WIRED_AND_PIPELINE_USED` | **48** |
| `NOT_WIRED_EXPERIMENT_ONLY` | 1 *(the row I added tonight)* |

**AND OF THOSE 101, SEVENTY CARRY `gate_decision = WIRE`** -- i.e. **someone decided they SHOULD be
wired, and they are not reached.**

**➡️ THE FAILURE IS NOT BLINDNESS. IT IS A STANDING, DOCUMENTED, UNACTIONED BACKLOG: 101 capabilities
recorded as built-but-unreached, 70 of them under an explicit decision to wire them, against 48 that
are actually used.** *More than twice as many capabilities are documented as unreachable as are
documented as used.*

*This is strictly worse than "we lost track." **We did not lose track. We wrote it down, in a
machine-readable field, and then did not act on it** -- across 101 rows.*

## WHAT THIS CHANGES

1. **"WIRE-or-SHELVE" is being satisfied on paper and not in fact.** A row reading
   `gate_decision: WIRE` + `pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE` **is limbo wearing a
   decision.** *The gate was designed to prevent exactly that state and does not currently detect it.*
2. **The cold-placement row I added tonight is the honest shape** -- `SHELVE` with revival criteria
   and blockers named -- **precisely because I could not wire it.** *A `WIRE` I cannot execute would
   have added a 71st.*
3. **⚠️ CAVEAT ON THE 101, STATED BEFORE ANYONE QUOTES IT:** `CLAUDE.md` records that
   `pipeline_status` **is wrong in BOTH directions** -- 19 rows claim not-reachable while measurably
   live, and 3 claim used while absent from the closure. **So 101 is an upper bound on a
   self-reported field, not a measurement.** *The direction of the finding survives; the exact number
   should not be quoted without a runtime re-check.*

## TLDR

I said earlier that our catalogue of capabilities had lost track of the best work. **I checked
instead of assuming, and I was wrong about two of the three cases.**

The catalogue *does* have entries for them — and the entries are honest. They say, in a dedicated
field, **"this is built and the system doesn't actually reach it."**

**The corrected picture is worse than the one I described.** Across 209 entries, **101 say
built-but-not-reached** — and **48 say actually used.** More than twice as many things are recorded
as unreachable as are recorded as working. **Seventy of those 101 carry an explicit decision that
they should be connected.**

So this isn't forgetfulness. **We wrote it down, in a form a machine can read, and then didn't act on
it — a hundred and one times.**

That also means our "connect it or park it" rule is being satisfied on paper only: an entry saying
"decision: connect this" alongside "status: not connected" **is limbo with a decision stapled to it**,
and the rule doesn't currently notice.

**One caution:** our own notes record that this status field is unreliable in both directions, so
**101 is a rough upper bound, not a measurement.** The shape of the problem holds; the exact number
shouldn't be repeated without re-checking against what actually runs.

## QUESTIONS

None.

## NEXT STEPS

1. **The `WIRE` + `NOT_PIPELINE_REACHABLE` combination is a detectable contradiction** -- 70 rows.
   *A check for it belongs in `capability_registry_audit.py`, which is the only thing that would stop
   the count growing.*
2. Do **not** quote 101 without a runtime re-check; the field is documented as wrong both ways.
3. My "three islanded capabilities" framing is **withdrawn** -- one was invisible, two were recorded.
