# SUBSTRATE DIRECTOR STATE -- single source of truth

**Director:** Research (assumed per USER mandate 2026-06-14)
**Stable path:** `d:\AI\hd-instrument\notes\SUBSTRATE_DIRECTOR_STATE.md`
**Last updated:** 2026-06-14 ~09:10
**Update cadence:** every state change that affects objective / roles / blockers; NOT for narration

## THE ONE OBJECTIVE

> **Drive substrate to 70pct capability ONLINE (from 30pct) with measured F1 >= 0.50 on canonical held-out, while maintaining 100pct axiom termination + capability_preservation = 1.0.**

## ROLE ASSIGNMENTS

| Role | Owner | Owns |
|---|---|---|
| **DIRECTOR** | Research | objective + priorities + the call + this state board |
| **INTEGRATOR** | Testbed | wire stranded capabilities into backend/ + hdlab/ (30pct -> 70pct ONLINE) |
| **FOUNDATION** | Testbed | atom corpus + grounding + self-model + deepen math (logic/set-theory beneath algebra) |
| **PROVER** | Exp-Dev | new demos + verification + falsifier measurement, THROTTLED to Director's priority list |
| **AUDITOR** | Skunkworks | adversarial checks + measurement honesty + falsification floor; LEAN; no volume |

Retired into Director + light tooling: strategy, product, visibility, queue-health, meta-audit, verdict-handler.

---

## COMMUNICATION PROTOCOL (canonical; effective immediately)

### MONITORING METHOD

**Inbound channel.** All cross-session events route through `tools/event_bus.sh` (single producer; PID `1650183`; alive since 2026-06-13 20:41) into `data/events/<session>.log`. Director consumes:

```
tail -n0 -F data/events/research.log | grep --line-buffered -E "<filter>"
```

**Active monitor.** Persistent Monitor armed this turn (`task brm9l5ue6`); filter:
```
ROUTING | BROADCAST | INTEGRATION_RANKING | Q4 | F1_FINAL | F1_RESULT | MILESTONE | HARD_PASS | HARD_FAIL | BLOCKER
```

Director is NOTIFIED IN-CHAT the instant an event matching the filter lands. No polling. No sweep-by-mtime.

**Backup sweep.** If monitor dies (timeout / restart), Director performs manual inbox sweep every 30 min via:
```
ls -lat notes/*_to_research_*.md notes/*_to_all_*.md | head -10
```

### TIMING

| Event type | Director response window |
|---|---|
| Monitor-fired notification (ROUTING/BROADCAST/Q4/F1/MILESTONE/etc.) | within 1 cycle of arrival (~immediately on read) |
| BLOCKER-tagged event | within 1 cycle; ship decision or escalate to USER |
| HARD_FAIL verdict | within 1 cycle; dispatch 2x drill if negative finding warrants |
| Routine state update (no decision needed) | acknowledge in DIRECTOR_STATE; no routing note |
| USER message | always immediate |

### DIRECTOR TIMER (prod-to-action)

**Primary.** `/loop 15m` already firing per session memory (standing duties: inbox sweep + heartbeat + commit + dispatch if anchor list thin). This is the regular prod.

**Backup.** If `/loop` not firing or session restarts, Director arms `ScheduleWakeup` (15-30 min cadence) at end of each cycle. Sentinel prompt re-enters the standing duties.

**Director self-check (every cycle):**
1. Has monitor fired since last cycle? If yes -> respond to events.
2. Has 30+ min passed without monitor event? If yes -> manual inbox sweep (backup).
3. Are top-5 priorities still current? If no -> update SUBSTRATE_DIRECTOR_STATE.md.
4. Any BLOCKER unresolved >2 cycles? If yes -> escalate (decision or USER ask).
5. Heartbeat write + commit at cycle close.

### OUTBOUND PROTOCOL

**Decisions.** When Director ships a decision: ONE routing note targeted to affected sessions (not _to_all_). Format:

```
notes/research_to_<recipient>_<topic>_<date>.md
```

Each routing note contains: DECISION # + spec + falsifier + reservations + cross-references.

**State updates.** SUBSTRATE_DIRECTOR_STATE.md is the canonical state board. Updated on:
- New objective / role change
- Priority shift (top-5 changes)
- Blocker added or resolved
- Cycle close (heartbeat refresh)

**NO narration notes.** No status pings ("standing"), no recap notes, no per-task acknowledgments. ACK-and-move-on inline; ship decisions only.

**Methodology rules FROZEN at 22.** No new rules without USER approval.

**`_to_all_` broadcast use:** ONLY for role-structure changes, USER-LOCKED rules, infrastructure migrations. Last broadcast: 2026-06-14 09:00 (Director role assumed).

### CADENCE SUMMARY

```
Monitor -> NOTIFIED -> Director reads + ships decision OR updates state board OR silent ACK
   |
   +-> ~every 15 min /loop prods Director self-check
   |
   +-> backup mtime sweep every 30 min if monitor silent
```

---

## CURRENT PRIORITIES (top 5)

```
1. F1 canonical+bge rerun RUNNING on remote (NOTIFIED via monitor when lands)        [Exp-Dev]
2. Testbed (Integrator): ship Tier 1 batch per DECISION 23                           [Testbed]
   - Item 1: HMM decoders (viterbi + forward + backward) -> backend/substrate_index
   - Item 2: discriminative_perceptron -> hdlab (parallel with 1)
   - Item 3: NER + slot-filling -> backend (after 1)
3. Skunkworks (Auditor): verify each Tier 1 integration (works-online + no-regression) [Skunkworks]
4. Skunkworks: T2_FAM per-tag 18th-rule audit per DECISION 21                        [Skunkworks]
5. Skunkworks: NESS Crooks-ratio test on existing 46-pair ledger per DECISION 16    [Skunkworks]
```

KP P3 Q4 verdict = MIDDLE-BAND (deeper drill: AEP / typed-bisim alternatives) — dispatch when bandwidth permits (lower priority than F1 + integration push).

## OPEN BLOCKERS

| Item | Blocker | Owner |
|---|---|---|
| F1 final number | running on remote (BGE already installed); imminent | -- |
| Integration push Tier 1 | Testbed ship + Auditor verify | Testbed + Skunkworks |
| P3 archetype criterion (final) | deeper drill (AEP / typed-bisim) | Research (deferred) |
| F2 CROSS_DOMAIN tightening | Skunkworks PROVEN vs TENTATIVE split | Skunkworks |
| B' v2 ship | F1 + F3 sequencing | -- (queued) |

## OBJECTIVE PROGRESS

| Metric | Target | Current | Delta-to-target |
|---|---|---|---|
| Capability ONLINE | 70pct | 30pct (14/46) | +40pp to ship |
| F1 macro-F1 (canonical) | >= 0.50 | RUNNING on remote (number imminent) | TBD |
| Axiom termination | 100pct | 100pct (193/193) | INVARIANT |
| Capability_preservation | 1.0 | 1.0 | INVARIANT |
| Grounding precision | >= 0.95 | 0.951 | MET |
| F2 floor INDEPENDENT | >= 0.15 | 0.19 | MET |
| Cross-domain L6-PROOF COMPLETE | >= 1 | 1 (conv-theorem; first ever) | MET |

## RECENT MILESTONES

- 2026-06-14 ~09:05: First fully-assembled cross-domain L6-PROOF (convolution_theorem_synthesis COMPLETE; VSA binding <-> signal processing)
- 2026-06-14 ~08:30: 100pct axiom termination (193/193 typed operators)
- 2026-06-14 ~08:25: First autonomous-discovery edge (gradient -> derivative; PROACTIVE_GAP_LOOP)
- 2026-06-14 ~08:30: F2 INDEPENDENTLY VALIDATED floor 0.19 (LAKATOS strongest signature)
- 2026-06-13 ~21:00: PROACTIVE_GAP_LOOP v0 BUILT end-to-end

## ACK / CHANGES THIS TURN

- DECISION 23 Tier 1 INTEGRATION COMPLETE: Testbed shipped 3/3 with LIVE_QUERY_PASS in ~10 min (cefecf48 + 1249308d + 8930bdda); awaiting Skunkworks Auditor verification
- HOW_TO_MONITOR_INBOX broadcast: persistent tail+grep method taught to all sessions (USER-flagged monitoring gap fix)
- Second cross-session monitor armed for MILESTONE/HARD_PASS/HARD_FAIL/BLOCKER across all session logs
- COMMUNICATION PROTOCOL section (prior turn)
- Monitor `brm9l5ue6` armed (persistent; research.log filtered)
- CONV-THEOREM COMPLETE milestone (first fully-assembled cross-domain L6-PROOF)
- KP P3 Q4 = MIDDLE-BAND (bisim 0->1; AEP/typed-bisim deeper drill needed; deferred)
- F1 RUNNING on remote (BGE already installed; Exp-Dev launched canonical benchmark; result imminent)
- 23 decisions cumulative; FROZEN at 23

---

**This file is the single source of truth. All other notes are handoffs + blockers + concrete deliverables.**
