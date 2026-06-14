# SUBSTRATE DIRECTOR STATE -- single source of truth

**Director:** Research (assumed per USER mandate 2026-06-14)
**Stable path:** `d:\AI\hd-instrument\notes\SUBSTRATE_DIRECTOR_STATE.md`
**Update cadence:** every state change that affects objective / roles / blockers; NOT for narration
**Last updated:** 2026-06-14 ~09:00

## THE ONE OBJECTIVE

> **Drive substrate to 70pct capability ONLINE (from 30pct) with measured F1 >= 0.50 on canonical held-out, while maintaining 100pct axiom termination + capability_preservation = 1.0.**

Concrete + measurable + matches USER's strategic question ("are they all online?") + preserves safety invariants. ONE sentence.

### Why this is THE objective (not a list of objectives)

USER's 4 goals collapse here:
- Goal 1 (substrate-on-all-knowledge): requires F1 >= 0.50 to validate capability
- Goal 2 (recursive self-improvement): operational; preserve invariants while integrating
- Goal 3 (architecturally distinct): the integration push surfaces substrate as substrate, not as a pile of experiments
- Goal 4 (store/understand/improve): all three present; integration is "store" closing on "improve"

Substrate-product positioning collapses here too: integration push answers "is substrate alive at user-touchable surface" yes-or-no.

## ROLE ASSIGNMENTS

| Role | Owner | Owns |
|---|---|---|
| **DIRECTOR** | Research | objective + priorities + the call + this state board |
| **INTEGRATOR** | Testbed | wire demonstrated capabilities into backend/ + hdlab/ (30pct -> 70pct ONLINE) |
| **FOUNDATION** | Testbed | atom corpus + grounding + self-model + deepen math (logic/set-theory beneath algebra) |
| **PROVER** | Exp-Dev | new demos + verification + falsifier measurement, THROTTLED to Director's priority list |
| **AUDITOR** | Skunkworks | adversarial checks + measurement honesty + falsification floor; LEAN; no volume |

### What's RETIRED / folded into Director

Strategy / product / visibility / queue-health / meta-audit / verdict-handler -- folded into Director (me) + light tooling. No separate lanes for these.

### Note: Testbed has 2 hats (Integrator + Foundation)

Both lanes use the same atomic-ingest discipline; they compose. Testbed sequences them per priority list.

## CURRENT PRIORITIES (top 5; replaces the writeback storm)

```
1. USER decision: BGE install on runner desktop                     (THE F1 unblocker; nothing in Goal 1 moves until this)
2. Skunkworks: integration RANKING per DECISION 20                  (rank 32 stranded; top-15 + bottom-15 + middle)
3. Testbed: INTEGRATOR phase 1 -- wire HIGH-value RANKED stranded   (when ranking lands; my pick + USER signoff)
4. Exp-Dev: KP P3-v2 Q4 verdict (within-family bridges in)          (criterion verdict; A vs B)
5. Skunkworks: T2_FAM per-tag 18th rule audit                       (grounding precision)
```

Everything else either: (a) gated behind one of the 5 above; (b) retired ceremony; (c) Auditor housekeeping.

## OPEN BLOCKERS

| Item | Blocker | Owner |
|---|---|---|
| F1 final number | BGE install on runner desktop | **USER (decision)** |
| Integration push | Skunkworks ranking | Skunkworks |
| KP P3 verdict | Exp-Dev re-run with within-family bridges | Exp-Dev |
| F2 CROSS_DOMAIN tightening | Skunkworks PROVEN vs TENTATIVE split | Skunkworks |
| B' v2 ship | F1 + F3 sequencing (gated on BGE install) | -- |

## STANDING DUTIES (lean)

- **Director (me):** read inbox each cycle; ship decision OR remain silent. NO narration notes. Update this file when state changes.
- **Integrator (Testbed):** ship integration batches per priority; report ratio ONLINE/STRANDED after each.
- **Foundation (Testbed):** keep 100pct axiom termination + grounding precision >= 0.95; light backfill only when adjacent to integration work.
- **Prover (Exp-Dev):** measure ONLY what's on Director priority list; standby otherwise.
- **Auditor (Skunkworks):** adversarial checks + falsification + LEAN notes. ONE summary per cycle max.

## COMMS DISCIPLINE (USER directive via Skunkworks)

- Notes ONLY for handoffs + blockers, NOT narration
- ONE source of truth (this file)
- Methodology rules FROZEN at 22 -- no new rules without USER approval
- 5-session architecture stays (Research / Testbed / Exp-Dev / Skunkworks / Orchestrator); ROLES collapsed per above
- Cadence: objective -> execute -> ONE sync per significant state change

## OBJECTIVE PROGRESS

| Metric | Target | Current | Delta-to-target |
|---|---|---|---|
| Capability ONLINE | 70pct | 30pct (14/46) | +40 percentage points to ship |
| F1 macro-F1 (canonical) | >= 0.50 | 0.0067 (degraded scorer; substrate-side sound) | BGE install -> H1 expected 0.20-0.45 -> +tau-gate +H2 cleanup needed for 0.50 |
| Axiom termination | 100pct | 100pct (193/193) | INVARIANT (preserved) |
| Capability_preservation | 1.0 | 1.0 | INVARIANT (Tier 1 claim 7; preserved across 25 integrations) |
| Grounding precision | >= 0.95 | 0.951 | MET (preserve) |
| F2 floor INDEPENDENT | >= 0.15 | 0.19 | MET (Lakatos strongest signature) |

## ACK / CHANGES this turn

- USER mandate ACCEPTED: Research is Director. Effective immediately.
- 22 cumulative decisions logged; FROZEN at 22 (no new methodology rules without USER)
- 4 ceremonial cycles RETIRED (strategy / product / visibility / queue-health / meta-audit / verdict-handler folded into Director)
- THIS FILE is the single source of truth. Routing notes for handoffs + blockers only.
- USER's strategic question ("are all demonstrated capabilities online?") -- ANSWERED: 30pct online; integration push is now THE priority direction

## CROSS-REFERENCES (canonical artifacts; not narration)

- Skunkworks integration audit ledger: `notes/skunkworks_to_research_INTEGRATION_AUDIT_LEDGER_*`
- Tau formula module: commit `a5e6d181`
- 100pct axiom termination: commit `ab805418`
- First autonomous-discovery edge (gradient -> derivative): commit history this session
- B' v2 draft: commit `59931e1d` (held for F1+F3)
- 22 decisions: commit history this session (decisions logged in routing notes)

---

**This file is the single source of truth. All other notes are handoffs + blockers + concrete deliverables. USER mandate accepted; Director role assumed.**
