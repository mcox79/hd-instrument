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
1. Exp-Dev: F1 lean batched scorer (DECISION 25; Option B) -- BLOCKER unblock     [Exp-Dev]
2. Exp-Dev (Prover, parallel): Tier 2 production-scale validation (DECISION 26b)  [Exp-Dev]
3. Skunkworks (Auditor): STRICT RECOUNT after Tier 2 validation (DECISION 26c)    [Skunkworks]
4. Skunkworks NESS Crooks-ratio test (DECISION 16) = UNRUNNABLE on current ledger (no per-pair credence values; refuse to fabricate; 18th rule on own audit); Option (b) DROPPED for now; Option (a) instrumentation deferred as future-work-if-needed; SOUNDNESS_DRIFT_TEST remains operative safety floor
5. Future Prover cell: T2_FAM per-family L6-PROOF provability check (DECISION 21 = INCONCLUSIVE; T2_FAM is real hierarchical taxonomy; do NOT refuse) -- deferred behind F1+integration  [Exp-Dev future]
```

PAUSE further Tier 3 integration wiring (DECISION 26; consolidate before expand). Tier 3 stays DEFERRED unless USER explicitly wants specific capabilities online.
ONLINE counter 30pct -> projection ~44-48pct (cumulative Tiers 1+2 verified by execution); STRICT recount pending Auditor.
KP P3 Q4 = MIDDLE-BAND (deeper drill deferred).

## OPEN BLOCKERS

| Item | Blocker | Owner |
|---|---|---|
| F1 final number | BLOCKER: full-corpus scorer pathologically slow (GPU 0pct; CPU per-question stuck); DECISION 25 GO Option B lean batched scorer + cached bge index | Exp-Dev |
| Integration push Tier 1 | Testbed ship + Auditor verify | Testbed + Skunkworks |
| P3 archetype criterion (final) | deeper drill (AEP / typed-bisim) | Research (deferred) |
| F2 CROSS_DOMAIN tightening | DONE -- all 3 groups TENTATIVE; F2 strict = 18.8pct | (closed) |
| B' v2 ship | F1 + F3 sequencing | -- (queued) |

## OBJECTIVE PROGRESS

| Metric | Target | Current | Delta-to-target |
|---|---|---|---|
| Capability ONLINE | 70pct | **~44-48pct projected (Tiers 1+2 verified by execution; STRICT recount pending Auditor)** | +22-26pp to ship |
| **F1 macro-F1 full A-G canonical (Auditor-headline)** | **>= 0.50 HARD-PASS** | **~0.55 MET-PROVISIONAL** (30q full A-G macro; conservative measure; Auditor-recommended headline) | **MET-PROVISIONAL** pending DECISION 30 provenance check |
| F1 macro-F1 A-E factual subset 30q | -- | 0.568 (excludes F 0.074 + G 0.460; reported for transparency, not headline) | -- |
| F1 macro-F1 60q (DECISION 28 CI tightness) | >= 0.50 | **0.585 A-E MET** (slightly higher; result stable on larger-n; A 0.53 / B 0.54 / C 0.57 / D 1.00 / E 0.76 / F 0.25 / G 0.41 / neg 1.00); 60q full A-G also clears | MET CONFIRMED on larger-n |
| F1 negative-honesty (refuses made-up queries) | == 1.0 | 1.000 (both 30q + 60q) | 18th rule live at measurement layer |
| F1 30q held-out provenance (Goodhart guard; DECISION 30) | GENUINELY HELD-OUT | Auditor checking authoring timestamps + mechanism reach + HP_v1 reference | pending; locks MET-DECISIVE on pass |
| Axiom termination | 100pct | 100pct (193/193) | INVARIANT |
| Capability_preservation | 1.0 | 1.0 | INVARIANT |
| Grounding precision | >= 0.95 | 0.951 | MET |
| F2 REALIZED strict (proven; same-domain SHARED_ABSTRACTION) | >= 0.05 HARD-PASS | **0.188** (Auditor-corrected; was inflated to 0.50 by output-type-only TENTATIVE) | MET |
| F2 INDEPENDENT FLOOR (held-out + reverted authoring) | >= 0.15 | 0.19 | MET (Lakatos strongest signature) |
| F2 cross-domain TENTATIVE (output-type-only; NOT compression) | tracked separately | 0.31 | reported but NOT counted toward F2 headline |
| Cross-domain L6-PROOF COMPLETE | >= 1 | 1 (conv-theorem; first ever) | MET |

## RECENT MILESTONES

- 2026-06-14 ~09:05: First fully-assembled cross-domain L6-PROOF (convolution_theorem_synthesis COMPLETE; VSA binding <-> signal processing)
- 2026-06-14 ~08:30: 100pct axiom termination (193/193 typed operators)
- 2026-06-14 ~08:25: First autonomous-discovery edge (gradient -> derivative; PROACTIVE_GAP_LOOP)
- 2026-06-14 ~08:30: F2 INDEPENDENTLY VALIDATED floor 0.19 (LAKATOS strongest signature)
- 2026-06-13 ~21:00: PROACTIVE_GAP_LOOP v0 BUILT end-to-end

## ACK / CHANGES THIS TURN (latest first)

- **F1_RESULT (DECISION 25 lean bge-only) = 0.4505 / 0.4396 tau-gated** -- H1 CONFIRMED; 0.0067 was degraded scorer. Per-axis: A_content 0.498 (strong); B/D/F = 0.04 / 0.00 / 0.00 (structural axes -- bge can't answer relation/composition/gap; canonical does via DEPENDS_ON + L6-PROOF). DECISION 27 GO canonical now (bge-cached so fast). 0.50 floor approachable: canonical macro-F1 >= 0.45 by construction; structural axes are the gap path.
- **Tier 2 PRODUCTION-VERIFIED** per Exp-Dev Prover (DECISION 26b): bayes_update + map_estimate 0.9512 on UCI mushroom NB / EMMixture purity 1.0 on 3-Gaussian / IntentClassifier 0.9125 on ATIS. 3/3 HARD_PASS. Tier 1+2 ALL production-verified at held-out scale. Caveat: sst2 sentiment-NB scores 0.78 (sentiment harder than mushroom; reported for honesty). Skunkworks (Auditor) auto-triggered for DECISION 26c STRICT recount.
- **DECISION 25 BGE CACHE BUILT** as Option B dual-purpose payoff: `data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz` (158.6 MB; 20820 atoms). ALL future bge-enabled runs load in seconds (vs 50-min rebuild). Substrate-infrastructure win.
- **F1 scoring phase RUNNING NOW** in lean batched scorer; F1_RESULT imminent. Stalled canonical run killed (65-min GPU-idle; superseded by cache).
- **DECISION 16 NESS Crooks-ratio = UNRUNNABLE** per Skunkworks Auditor 18th-rule on own audit: existing 46-pair ledger has only binary verdicts (PROVABLY_EQUIVALENT vs UNDECIDABLE_BY_PROVER); no per-pair credence values; Crooks ratio undefined; refused to fabricate. Director call: **Option (b) DROPPED for now**; Option (a) credence-logging instrumentation deferred as future-work-if-needed. SOUNDNESS_DRIFT_TEST remains operative safety floor; capability_preservation=1.0 + 0 false merges across 25 integrations is the empirical safety floor (held).
- **DECISION 21 T2_FAM = INCONCLUSIVE** per Skunkworks Auditor 19th-rule self-correction: quick `operation_type` heuristic was artifact (members are non-operator atoms + sub-families); T2_FAM is real hierarchical operation-taxonomy (transformers->binders->algebraic_binding->{fhrr_bind, circ_conv, group_axioms} etc.); DO NOT refuse/delete; proper provability check requires Prover L6-PROOF cell (per-family: do members share derivable common operation?); deferred behind F1+integration.
- **DECISION 26** PAUSE further integration wiring (Tier 3 stays DEFERRED) + 26b Prover validates Tier 2 production-scale + 26c Auditor STRICT recount after Tier 2 validation.
- **Tier 2 AUDIT_PASS** per Skunkworks Auditor: bayesian_inference (bayes_update + map_estimate + EMMixture 3-Gaussian purity=1.0) + intent_classifier (3/4 + 1 correct ABSTAIN per 18th-rule refuse-discipline) verified by execution. Counts toward 70pct ONLINE. Cumulative projection ~44-48pct.
- **DECISION 25** F1 BLOCKER unblocked via Option B (lean batched scorer + cached full-corpus bge index + tau-gate; ~30-60 min ETA); keep current full-corpus run alive as cross-check.
- **Tier 1 PRODUCTION-VERIFIED** per Exp-Dev Prover (DECISION 24b): HMM viterbi 0.9028 + StructuredPerceptron 0.9149 + NERTagger BIO-F1 0.9307 on public UD en_ewt + conll2000. 3/3 HARD_PASS. Quality status upgraded from "executes-on-live-query" to "production-verified at held-out scale." Caveats: PTB unavailable (used public UD); BIO-F1 validates tagger machinery not 4-type NER specifically; HMM needs SUFFIX-OOV backoff (per module docstring) for 0.90 -- naive add-k scores 0.8832.
- **F2 HONEST CORRECTION** per Skunkworks Auditor: cross-domain (~31pct) was OUTPUT-TYPE-ONLY (4 distinct operations per group); TENTATIVE not PROVEN. Strict/honest F2 REALIZED = 18.8pct (not 50pct). LAKATOS F2 floor STILL MET (>=5pct via strict). State board carries strict number; cross-domain tracked separately as TENTATIVE.
- DECISION 24 GREENLIT Tier 2 batch + Exp-Dev PTB-scale tag_acc Prover task (non-blocking parallel)
- AUDIT_PASS Tier 1 (3/3 by execution): HMM decoders + StructuredPerceptron + NER/SlotFiller; counts toward 70pct ONLINE; net 30 -> ~37-41pct projection
- DECISION 23 Tier 1 INTEGRATION COMPLETE: Testbed shipped 3/3 with LIVE_QUERY_PASS in ~10 min (cefecf48 + 1249308d + 8930bdda)
- HOW_TO_MONITOR_INBOX broadcast: persistent tail+grep method taught to all sessions
- Cross-session monitor armed (now `bre7let60`; prior `bsd90u9zb` ended); plus research.log monitor `brm9l5ue6`
- CONV-THEOREM COMPLETE milestone (first fully-assembled cross-domain L6-PROOF)
- KP P3 Q4 = MIDDLE-BAND (bisim 0->1; AEP/typed-bisim deeper drill deferred)
- F1 RUNNING on remote (BGE already installed; Exp-Dev launched canonical benchmark; result imminent)
- 24 decisions cumulative; FROZEN at 24

---

**This file is the single source of truth. All other notes are handoffs + blockers + concrete deliverables.**
