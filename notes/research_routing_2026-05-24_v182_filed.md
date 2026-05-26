# Research routing filed at v182 (2026-05-24 Cycle 204)

Filed by orchestrator main thread during the v181 -> v182 batched 4-verdict commit cycle. These are research drills the wrapper-first rule says should be picked up by the next Research sub-agent dispatch; main thread does not synthesize them inline.

## R1. 2x Research drill on LR_DOSE_MONOTONIC mechanism (EXPANDED scope from v181 LR_ENVELOPE_MIXED)

**Hand-off** (per [[feedback-no-experiment-design-in-prompts]] -- pointers, not designs):

The v181 LR_ENVELOPE_MIXED finding (E4 long-tail RM tau=40 WINS over baseline; E3 extended-rectangular LOSES contra Gong 2026 prediction; E2 brief-spike LOSES) had a 2x Research drill triggered on the mechanism question. v182 LR_DOSE_MONOTONIC verdict (tau=160 retention 1.000; monotonic ramp tau=10->160; spread=0.133; no plateau ceiling at tau<=160) DEEPENS the finding: the substrate prefers longer-tail RM envelopes MONOTONICALLY across the tested range with no observed plateau ceiling. The mechanism question now sharpens to:

- Why does the substrate not saturate at moderate tau? Is there an upper-bound tau plateau (or does the WIN extend indefinitely)?
- Mechanism candidates carried from v181 (variance-averaging at later iterates / late-stage exploration-vs-exploitation tradeoff / Hopfield-attractor-basin late-stage settling / Gong 2026 under-modeled late-stage regime) -- which is/are load-bearing for the monotone-no-plateau finding?
- Production-N substrate-physics layer: does the long-tail RM envelope have a substrate-physics interpretation at production N (the substrate-physics layer is the v169 Pauli-twirled-Clifford-design framing; the LR schedule layer is the Cap 5 continual-editing layer)?

Pointers:

- cap_map v182 Cap 5 row (substrate_capability_map.md tail) -- envelope-extension annotation deepened from v181 tau>=40 to v182 tau<=160 monotone WIN
- v181 LR_ENVELOPE_MIXED full detail (cap_map.md v181 block + strategy_decisions_2026-05-24.md v180 -> v181 block)
- v182 LR_DOSE_MONOTONIC tally (cap_map.md v182 block + strategy_decisions_2026-05-24.md v181 -> v182 block)
- [[feedback-2x-means-depth]] -- 2x means DEEPER drill not verification
- Gong 2026 (cited in v181); look for late-stage regime under-modeling

Deliverable (per [[feedback-no-experiment-design-in-prompts]] CONTRACT): research_note Markdown file under notes/research_field_advisor.py output's top-3 next-drill candidates; deliverable shape mechanism explanation that could inform Cap 5 row annotation extension AND inform future LR-schedule pre-registrations; word cap 1500.

## R2. Cap-13 candidate substrate-novel narrowing rehab at production-N substrate-physics layer (NEW v182)

**Hand-off** (per [[feedback-no-experiment-design-in-prompts]]):

The closed-form-margin paired-continent program for Cap-13 candidate has been empirically refuted at theory level across all three planned continents (F-14 Tropical KILLED v181 + F-4 Clifford-TN MIDDLE v181 + F-6 Boolean-noise-stability KILLED v182). 15 rescue sketches filed across the three continents. The R5 substrate-novel narrowing rescue is the load-bearing framing per [[feedback-no-smoke]]; the substrate-novel narrowing IS the substrate-product framing.

The reframing direction per [[feedback-dont-overextend-theorems]] is: move from "closed-form-margin theory at smaller-N" (empirically refuted) to "production-N substrate-physics layer" where the Cycle 203 v180 paired anchor at F-4 Clifford-TN continent passed at machine precision (magic_max=0; rel_err_max=6.5e-9). The substrate IS approximately-Clifford at production N; the bond-dim-1 closed-form reduction is NOT the load-bearing theory anchor at small N. The reframing direction:

- What IS the substrate's audit-trail capability at production-N substrate-physics layer (where magic content is at machine precision)?
- How does the bounded magic content scale with N? Is it monotone-decreasing such that at production N it crosses machine precision?
- Can the v169 Pauli-twirled-Clifford-design framing be extended into an audit-trail capability at production N?
- Are there independent (non-closed-form-margin) audit-trail capabilities the substrate carries at production N that survive the trilogy-rejection conclusion?

Pointers:

- cap_map v182 Cap 13 candidate row tail (substrate_capability_map.md) -- CLOSED-VIA-3-of-3-CONTINENT-REJECTION at closed-form-margin theory level
- v180 Cycle 203 paired anchor F-4 Clifford-TN production-N GPU sanity (rel_err_max=6.5e-9 + magic_max=0)
- v181 rescue sketches R1-R5 for F-14 + F-4 (10 sketches)
- v182 rescue sketches R1-R5 for F-6 (5 sketches)
- v169 Pauli-twirled-Clifford-design framing (Cap 1/Cap 3/Cap 8 closed-form annotations)
- [[feedback-rehabilitation-after-rejection]] -- 5+5+5=15 sketches filed BEFORE pursuing
- [[feedback-dont-overextend-theorems]] -- the closed-form-margin theory at smaller-N is empirically refuted; the substrate-physics layer at production-N remains an open question

Deliverable (per [[feedback-no-experiment-design-in-prompts]] CONTRACT): research_note Markdown file with reframing recommendation; deliverable shape "substrate-product narrative direction for Cap 13 candidate after trilogy-rejection at closed-form-margin theory level"; word cap 1500.

## R3. antiRM mechanism Research drill (CARRIED from shoreup matrix; pre-existing flagged item)

**Hand-off** (per [[feedback-no-experiment-design-in-prompts]]):

antiRM mechanism is flagged in the shoreup matrix as a Cap-5-adjacent direction (Bet T closure on anti-RM Mondrian conformal at v172 was the kill-trigger; the underlying anti-RM dynamics on substrate may be Cap-5-adjacent). The Research drill question: what does the antiRM mechanism on substrate look like at the substrate-physics layer (independent of the Bet T audit-cert framing that closed)?

Pointers:

- Bet T row at cap_map (closed at v172 via Mondrian on anti-RM HARD-FAIL); v172 commit message
- shoreup matrix flagging antiRM as still-open mechanism direction
- [[feedback-strategy-shore-up-capabilities]] -- Strategy actively drills 🟡/🔬 rows and establishes new caps

Deliverable: research_note Markdown file with antiRM mechanism summary; deliverable shape "is antiRM a substrate-physics direction worth Strategy drilling next cycle?"; word cap 1000.

## R4. Bet B retention path other rescue paths from the 15-angle research_15_angles_triage list (NEW from EWC closed-deferred 2-observation lock)

**Hand-off** (per [[feedback-no-experiment-design-in-prompts]]):

Bet B retention rehab via EWC-class is CLOSED-DEFERRED at the 2-observation threshold (wave14e_betB_ewc_smoke_v1 INCONCLUSIVE + wave15_ewc_betB_smoke_v1 INCONCLUSIVE). Per [[feedback-lock-in-inefficiency-fixes]] the EWC-class is locked-deferred. The Research drill question: which of the OTHER 15-angle rescue paths (from notes/research_15_angles_triage_2026-05-24.md if present) should be pursued next for Bet B retention?

Pointers:

- notes/research_15_angles_triage_2026-05-24.md (if exists; check)
- v181 / v182 strategy_decisions_2026-05-24.md EWC closed-deferred entries
- [[feedback-lock-in-inefficiency-fixes]] -- 2-observation closure-deferred discipline

Deliverable: research_note Markdown file ranking the next 2-3 most-promising Bet B retention rescue paths from the 15-angle list (excluding EWC-class which is closed-deferred); deliverable shape "Strategy's next dispatchable Bet B retention probe"; word cap 1000.

## Routing

These research routings are filed as PRE-REGISTERED FUTURE ROUTING per [[feedback-dispatch-wrappers-default]]; the next Research sub-agent dispatch (whether triggered by user / by routing_ratio_low watchdog / by Strategy's scope-expansion cadence per [[feedback-design-space-and-audit-cadence]]) should pick up R1-R4 in priority order.

Pause flag state at filing: ACTIVE (no flag on disk).

Filed by orchestrator main thread (sub-agent context; Agent dispatch unavailable per orchestrator post-compaction brief Section 2 execution model clarification) at 2026-05-24 ~12:35 EDT.
