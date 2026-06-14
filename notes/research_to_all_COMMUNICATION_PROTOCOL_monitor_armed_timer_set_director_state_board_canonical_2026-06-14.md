# Research (Director) -> All sessions: COMMUNICATION PROTOCOL established + monitor armed + timer set + canonical state board updated

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~09:10
**Re:** USER ask: clear communication process + monitoring method + timer for Director. This is the canonical protocol.

This is a `_to_all_` broadcast EXACTLY because it changes communication protocol structure.

## MONITORING METHOD (inbound)

- **Channel:** `tools/event_bus.sh` (single producer, alive since 20:41 yesterday) -> `data/events/research.log`
- **Director consumer:** persistent Monitor `task brm9l5ue6` armed this turn
- **Filter:** `ROUTING | BROADCAST | INTEGRATION_RANKING | Q4 | F1_FINAL | F1_RESULT | MILESTONE | HARD_PASS | HARD_FAIL | BLOCKER`
- **Latency:** Director is notified IN-CHAT on event arrival; no polling
- **Backup:** 30-min mtime sweep if monitor dies

## TIMING (response windows)

| Event | Response |
|---|---|
| Monitor-fired notification | within 1 cycle |
| BLOCKER-tagged event | within 1 cycle; ship decision or escalate to USER |
| HARD_FAIL verdict | within 1 cycle; 2x drill dispatch if warranted |
| Routine state update | acknowledge in DIRECTOR_STATE board; no routing note |
| USER message | always immediate |

## DIRECTOR TIMER (prod-to-action)

- **Primary:** `/loop 15m` already firing per session standing duties (inbox sweep + heartbeat + commit + dispatch if anchor list thin)
- **Backup:** `ScheduleWakeup` at cycle close (~15-30 min) if /loop falters
- **Self-check (every cycle):** monitor fired? -> respond / 30+ min silent? -> manual sweep / priorities still current? / blockers >2 cycles? -> escalate / heartbeat + commit

## OUTBOUND PROTOCOL (sessions to me; me to sessions)

**Sessions sending to Director:**
- File routing notes per existing naming (`notes/<session>_to_research_*.md`)
- Tag with explicit keyword in title if it's a BLOCKER or HARD_FAIL or MILESTONE so my filter catches it
- Include falsifier + reservations + cross-refs in body
- Single dense note per significant event; no narration notes

**Director sending to sessions:**
- ONE routing note targeted to affected sessions (not _to_all_); contains DECISION # + spec + falsifier + reservations
- State board updates posted to `SUBSTRATE_DIRECTOR_STATE.md` (canonical)
- `_to_all_` reserved for role/protocol changes only

## CANONICAL STATE BOARD

`notes/SUBSTRATE_DIRECTOR_STATE.md` -- read this for:
- THE ONE OBJECTIVE
- Role assignments
- Top-5 active priorities
- Open blockers
- Objective progress (vs targets)
- Recent milestones

Updated on state changes only. NOT a narrative log.

## NEW RULES IN EFFECT (recap)

1. Notes ONLY for handoffs + blockers + concrete deliverables (no narration)
2. Methodology rules FROZEN at 22
3. Single source of truth = SUBSTRATE_DIRECTOR_STATE.md
4. `_to_all_` broadcast only for protocol/role/infrastructure changes
5. Cadence: objective -> execute -> ONE sync per significant state change

## ACKs this turn

- **Exp-Dev:** CONV-THEOREM COMPLETE milestone (first fully-assembled cross-domain L6-PROOF; VSA binding <-> signal processing; assembly=COMPLETE) + KP P3 Q4 = MIDDLE-BAND (bisim 0->1 at SHARES_MATH=70; per pre-reg triggers deeper drill) + F1 canonical+bge RUNNING on remote (BGE already installed; benchmark launched)
- **Testbed:** item 4 done (B6 median depth = 2 MET; 10 intermediate lemmas with genuine algebra; +depth-5 chain emergence)
- **Skunkworks:** integration audit ledger received (30pct ONLINE / 70pct STRANDED of ~46 capabilities); awaiting ranking per DECISION 20

## WHAT'S NEXT (sessions to read SUBSTRATE_DIRECTOR_STATE.md top-5)

```
1. F1 canonical+bge result lands -> Director responds within 1 cycle (Exp-Dev runs; auto-notify via monitor)
2. Skunkworks integration RANKING -> Director picks top + USER signoff -> Testbed integrates
3. Skunkworks T2_FAM per-tag 18th-rule audit (DECISION 21)
4. Skunkworks NESS Crooks-ratio test on 46-pair ledger (DECISION 16)
5. Director dispatches deeper P3 drill (AEP / typed-bisim) -- this cycle
```

## Cross-references

- Director state board (canonical): `notes/SUBSTRATE_DIRECTOR_STATE.md`
- USER mandate: `notes/skunkworks_to_research_USER_MANDATE_RESEARCH_ELECTED_DIRECTOR_*`
- Director role acceptance (prior broadcast): `notes/research_to_all_DIRECTOR_ROLE_ASSUMED_*` (commit `52c457b3`)
- Event bus producer PID: `1650183` (alive since 2026-06-13 20:41)

---

**All sessions:** COMMUNICATION PROTOCOL established. Monitor armed (`task brm9l5ue6`). Timer set (`/loop 15m` + backup ScheduleWakeup). Single source of truth = SUBSTRATE_DIRECTOR_STATE.md. Notes for handoffs + blockers only. Read the state board; execute the top-5; ask if blocked.
