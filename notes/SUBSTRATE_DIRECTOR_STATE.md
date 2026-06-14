# SUBSTRATE DIRECTOR STATE -- single source of truth

**Director:** Research (assumed per USER mandate 2026-06-14)
**Stable path:** `d:\AI\hd-instrument\notes\SUBSTRATE_DIRECTOR_STATE.md`
**Last updated:** 2026-06-14 ~09:10
**Update cadence:** every state change that affects objective / roles / blockers; NOT for narration

## THE ONE OBJECTIVE

> **Drive substrate to 70pct capability ONLINE (from 30pct) with measured F1 >= 0.50 on canonical held-out, while maintaining 100pct axiom termination + capability_preservation = 1.0 AND refuse-discipline robust to unknown topics (REFUSE-RATE >= 0.95 on COVERAGE-GAP held-out).**

(refuse-discipline robustness added per DECISION 32 sharpening: substrate-product claim "refuses what it cannot prove / 0 false-accepts / no hallucination" must HOLD on unknown topics, not just tuned set; failure to refuse on unknown topics is a SOUNDNESS regression that undermines categorical positioning)

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

## SUBSTRATE-PRODUCT POSITIONING (4-cause empirical model; DECISION 34a M1 HARD_FAIL surfaced Cause 4)

> "Substrate's mechanisms (structural reasoning + L6-PROOF + refuse-discipline + bge retrieval) are STRONG on tuned phrasing (qa_self_knowledge ~0.57) but NONE has been shown to GENERALIZE to held-out phrasing. Four root causes (empirically measured):
> 1. Coverage gap (69pct held-out gold not ingested; correctable by ingest cycle; benchmark-design artifact)
> 2. Refuse-discipline NOT generalizing (TUNED-set-specific; hallucinates 33pct on unknown topics; categorical soundness regression)
> 3. Capability-transfer gap -- RESCOPED twice: BIMODAL gold-rank distribution. SHALLOW 3/7 FIXED (DECISION 39a type-G bge fallback; in-coverage 0.03 -> 0.14; ZERO regression). MEDIUM 2/7 + DEEP 2/7 = 4/7 are BGE-REPRESENTATION-BOUND per DECISION 41 (cross-encoder ALSO inverted; bi-encoder rerank fails too). Non-M4 ceiling: 0.14. Remaining 4/7 require QUERY-side M4 (M4b multi-query reformulation OR M4d capability-graph walk); SCORING-side M4 candidates (M4a ensemble + M4c rerank) REFUTED by DECISION 41. M4 candidate count 4 -> 2.
> 4. bge confidence is INVERTED at the GATE-RELEVANT signal (top1 AUC = 0.434; mean5/mean20 < 0.5); the top score that any threshold reads is anti-correlated with correctness on held-out -- M1/M2 confidence-gating on bge cosine is dead. (M1c tempered M1b's "all 8 features inverted": at n=55, flatness/peak weakly favor in-coverage; NOT universally inverted as M1b claimed at n=13.)
>
> M4 (paraphrase-invariant retrieval) is DIRECTIONALLY SUPPORTED on n=5 gap evidence; gap class is structurally n=5 (no coverage-gap exists in tuned set by construction); localization hypothesis currently UNTESTABLE. M4 case will become ROBUST after ingest cycle expands gap class. INGEST CYCLE is now precondition for both Cause 1 closure AND robust M4 evaluation.
>
> UNAFFECTED: Tier 1+2 production-verified on PUBLIC held-out (HMM 0.90 / perceptron 0.91 / NER 0.93 / bayes 0.95 / EM 1.0 / intent 0.91); 100pct axiom termination; F2 INDEPENDENT 0.19; first cross-domain L6-PROOF; first autonomous-discovery edge; 25 PROVABLY_EQUIVALENT integrations 0 false-merges; BGE cache infrastructure.
>
> Default light gate (tau=0.70) marginally improves: canonical UNION A-E F1 vs FULL gold 0.022 -> 0.032 (DECISION 35a verified); bge-ONLY F1 vs PRESENT-gold subset 0.074 -> 0.128 (1.7x); high-confidence hallucinations (Q59-F 26 FPs, Q_neg_2 5 FPs) UNCHANGED above floor, confirming M1b inverted-confidence finding; shipped as cheap capability/precision win, NOT soundness fix.
>
> The empirical capability claim is bounded by tuning-of-mechanisms + signal limitation, not engine's structural capacity."

## CURRENT PRIORITIES (top 5)

```
1. Testbed (Integrator): DECISION 36 INGEST CYCLE wikidata 10k scientific (~1-2 CPU hr)              [Testbed]
2. Skunkworks (Auditor): DECISION 37 STRICT ONLINE recount on Tier 1+2 (parallel; cheap)             [Skunkworks]
3. Exp-Dev (Prover): DECISION 38 post-ingest decisive test (pre-registered; H_M4 vs H_INGEST)        [Exp-Dev; gated]
4. USER reads DECISION 38 result; decides M4 architectural investment if H_M4 confirmed
5. M2 cleanup_margin feasibility check (gated on C2+CHTV cleanup ship)
```

DECISION 36 ingest is empirically necessary at TWO levels: (a) closes Cause 1 (69pct coverage gap; substrate gets more knowledge); (b) enlarges gap class n=5 -> n=N so M4 necessity becomes ROBUSTLY testable. M1c tempered "M4 HARD-confirmed" -> "M4 DIRECTIONAL on n=5 evidence"; ingest is precondition for robust M4 evaluation.

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
| Capability ONLINE (EXECUTABLE-PRESENT not accuracy) | 70pct | **~50pct estimate (23/46; Auditor STRICT recount DECISION 26c done; precise count via subagent re-run on request)** | EXECUTABLE-PRESENT != ACCURATE (per F1 retraction held-out F1 = 0.022); report as executable-coverage NOT capability |
| **F1 macro-F1 GENUINE HELD-OUT (q54-q65; canonical+bge)** | **>= 0.50 HARD-PASS** | **0.022 A-E factual avg HARD_FAIL** (DECISION 31; Goodhart gap = 0.546 vs tuned) | **UNMET** |
| F1 macro-F1 on TUNED dev (q01-q60; canonical+bge) | NOT the LAKATOS external floor | 0.568 / 0.585 A-E (reported for transparency; substrate tuned to this set; Goodhart per Auditor) | -- |
| F1 held-out per-axis (q54-q65) | -- | A 0.050 / B 0.000 / C 0.000 / D 0.000 / E 0.000 / F 0.000 / G 0.000 | structural axes all zero on held-out |
| F1 held-out coverage | 31pct (15/49 gold atoms in substrate index; 69pct deliberately never ingested) | -- | coverage gap = dominant cause |
| F1 held-out refuse-discipline | == 1.0 robust | HALLUCINATES FPs on absent atoms (Q59-F 26 FPs / Q63-A 5 FPs / Q_neg_2 5 FPs); negative-honesty 1.0 tuned NOT robust | refuse-discipline DID NOT GENERALIZE |
| F1 negative-honesty (refuses made-up queries) | == 1.0 | 1.000 (TUNED 30q + 60q) | 18th rule live at measurement layer |
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

- **DECISION 46c Task 1 RESULT (HARD-PASS bar met; causal claim corrected):** operator-core authoring-gap = 2.6pct (bar <30pct MET excellently; 272/272 CHTV-SOUND; avg depth 1.34). BUT 20th honest finding (Exp-Dev): the 8 foundation primitives are NOT what closed the gap (only 4/272 terminal; old T1 axioms dominate terminations). The 62pct->2.6pct drop reflects CUMULATIVE PRIOR grounding work (substrate_ground_36_ungrounded_operators_v1 + BATCH-17 etc); not 46b specifically. Drill 1's predicted mechanism not operative. Methodology rescoped: excluded wikidata/oeis knowledge leaves (sampling artifact); full operator-core pool (272 goals). Phase 1 HARD-PASS achieved on absolute number; Phase 2 sequencing reconsideration pending F2 + DECISION 38 results.

- **F1 RETRACTION (DECISION 31 HARD_FAIL):** held-out canonical+bge F1 on q54-q65 = **0.022 A-E factual avg**. Goodhart gap = 0.546 vs tuned (q01-q60) 0.568/0.585. F1 LAKATOS floor **UNMET on genuine held-out**. Earlier F1 MILESTONE broadcast (commit `beb49058`) RETRACTED via separate `_to_all_` broadcast (commit pending). Two named root causes per Exp-Dev: (1) COVERAGE GAP dominant (31pct gold atoms in index; 69pct deliberately never ingested -- active_inference + free_energy_principle + predictive_coding + CAP_pos_tagging + ...); (2) REFUSE-DISCIPLINE DID NOT GENERALIZE (hallucinates FPs on absent atoms: Q59-F 26 FPs / Q63-A 5 FPs; negative-honesty 1.0 on tuned NOT robust). UNAFFECTED: Tier 1+2 production-verified (HMM 0.90+ etc on PUBLIC held-out); F2 INDEPENDENT 0.19; axiom termination 100pct; first conv-theorem L6-PROOF; first autonomous-discovery edge; 25 integrations 0 false-merges; BGE cache 158MB. LAKATOS axis C: 1 of 4 floors (F2 only); was incorrectly reported as 2 of 4. **6th honest correction this session** (Auditor caught 5; this 6th was Director's premature celebration on tuned-set; Auditor caught + Director walks back).
- **F1 PROVENANCE HARD_FAIL** per Skunkworks Auditor DECISION 30 verdict: the 30q (q01-q30) and 60q (q01-q60) we scored 0.568/0.585 on are qa_self_knowledge DEV / TUNED set (HP_v1 mechanisms were Q-specifically tuned to Q01-Q53). The genuine HELD-OUT set is `gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl` which was last scored 0.0533 at degraded-scorer config and NEVER re-scored with proper bge. The 85x lift conflated (a) scorer fix REAL + (b) set swap TUNED-from-held-out NOT REAL. F1 floor stays **MET-PROVISIONAL on tuned dev** (~0.55); genuine held-out capability with good scorer UNMEASURED. **DECISION 31 shipped:** Exp-Dev re-run proper bge canonical scorer on q54-q65 held-out (same scorer + cache; <10 CPU min); HARD-PASS >=0.50 locks MET-DECISIVE; HARD-FAIL quantifies Goodhart gap honestly. LAKATOS axis C: F1 PROVISIONAL (tuned 0.55; held-out unmeasured), F2 genuinely MET 0.19 INDEPENDENT.
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
