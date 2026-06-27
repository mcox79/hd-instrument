# DIRECTOR LIVE STATE SNAPSHOT 2026-06-26

**Updated:** 2026-06-26 ~21:15 PDT (continuously rewrite this file on todo changes; truncate + replace, not append)
**Purpose:** capture the granular CURRENT IN-FLIGHT + TODO state that lives in conversation context (lost on compaction); BACKUP doc has high-level state but not this.

## CURRENT TODOS (truncate + rewrite on TodoWrite)

1. **[in-progress] Monitor:** K-sweep v3 GPU full (smoke landed 20:59; full pending pickup); Wave 3 dispatch agent a4cc19985adc93c05 in flight (dual-store audit smoke landed 21:10; ANCHORS 1+3+4 next per USER vetting)
2. **[completed]** Substrate-KB declared RELIABLE for post-compaction. Memory ingest bug fixed (commit 5de28ea1 atomic-swap + per-class coverage check). --filename-contains shipped at rank-1 cosine=1.0 across known docs. MEMORY.md ritual updated.
3. **[completed]** Skunkworks VET batch 3. CHAIN_GRADE ultrametric clustering BANKED (CERT 588→589). META_RULE_H validated same-day. Edge-importance MEASURED_MECHANISM (needs v2). 5 flag-backs returned.
4. **[pending]** Edge-importance v2 at higher-alpha regime (Skunkworks flag-back; recommend N=512 M_OLD=600 M_RECENT=400 at alpha=1.95)
5. **[pending]** K=8192 1-seed result is suggestive (CHAIN_GRADE bait per Skunkworks flag-back #4): cheap 3-seed-at-K=8192-only pre-reg could harvest chain-grade without waiting for K-extension v3+
6. **[pending]** Capacity_sweep re-dispatch with higher-alpha regime (M_facts >= N) — Skunkworks flag-back #3 from batch 2
7. **[pending]** Wave 2 cortex reserve mechanisms (4x ANCHORS 3 SOC + 4 MDL + 2x Anchor 6 distribution-matching + 3 exp_dev probes) — holding; cortex breakthrough banked via ultrametric so urgency reduced
8. **[pending]** Wave 3 ANCHOR 2 TWO_TIER promotion criterion — deferred until edge-importance v2 provides per-atom importance signal
9. **[pending]** Codify `cardinality_ok` boolean as mandatory pre-reg field for any sweep-axis cell (Skunkworks flag-back #5)
10. **[pending]** director_plan.json update: remove invalid MULTI_128x@K=8192 claim
11. **[pending]** Math + science ingest extractors (ProofWiki / OEIS / PubMed neuro / arXiv) — design before ingest
12. **[pending]** Wave 2 compositional understanding cells (typed multi-bank K=128 / SOLAR LARS / emergent slot discovery / holographic chunk-pack) — audit overlap with Stage 2 specs first
13. **[pending]** Fix #26 tooling-gap: predispatch_check should check local landings not just remote
14. **[pending]** 13 RC follow-up items from Skunkworks batch 3 (prior session) for next-cycle Research routing

## ACTIVE SPAWNS IN FLIGHT (snapshot)

- **a4cc19985adc93c05** — exp_dev: Wave 3 bounded-capacity KB build (4 of 5 anchors); ANCHOR 5 dual-store audit smoke just landed
- **K-sweep v3** — running on remote GPU (overnight_queue); commit 6605f015; smoke PASS local; full pending pickup
- **(others spawned today already completed)** — see BACKUP doc for full session history

## RECENT KEY DECISIONS (most recent first)

- 2026-06-26 ~21:10: MEMORY.md + CLAUDE.md strengthened with substrate-query-first post-compaction ritual
- 2026-06-26 ~21:05: ULTRAMETRIC CLUSTERING tiered CHAIN_GRADE (cortex content-extraction first win)
- 2026-06-26 ~21:00: Memory ingest bug ROOT CAUSE identified (mid-ingest crash, not scanner); fixed via atomic-swap commit 5de28ea1
- 2026-06-26 ~20:50: Wave 3 bounded-capacity KB build dispatched (4 of 5 anchors; ANCHOR 2 deferred on edge-importance v2)
- 2026-06-26 ~20:45: --filename-contains filter shipped (Option A+); substrate-KB now reliable for specific-doc retrieval
- 2026-06-26 ~20:40: K-sweep v2 HARD_FAIL via META_RULE_H cardinality guard (same-day validation of META rule); v3 fix in flight
- 2026-06-26 ~20:30: Wave 1.5 fulls all MEASURED_MECHANISM (saturation; new discriminator-must-survive-scale discipline atomized)
- 2026-06-26 ~17:30: Cortex E-tensor Fix B RETEST failed structurally (META_RULE_F atomized — retrieval-success importance is magnitude-coupled by construction)

## OPEN QUESTIONS / DECISIONS PENDING USER

- Auto-export todos to file on every TodoWrite (proposed; not built yet — this LIVE_STATE file is the manual-writethrough version)
- Whether to use Opus 4.6 for me (Director) — user noted burning Opus credits suggests Fast mode is on (Opus 4.6) despite system-prompt label saying Sonnet 4.6

## WHERE THIS FITS

- The BACKUP file (`director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md`) is the load-bearing self-contained recovery doc
- The DIGEST file (`director_POST_COMPACTION_DIGEST_2026-06-26.md`) is the pointer-style summary
- The COMMANDS file (`director_POST_COMPACTION_COMMANDS_2026-06-26.md`) has the verified query sequence + gotchas
- THIS file is the granular IN-FLIGHT snapshot — updated more frequently than BACKUP (which is updated on major state changes)

If conflicts between this file and BACKUP/DIGEST: prefer this file's mtime (newer); cross-reference for sanity.

---

-- Research (Opus 4.6 via Fast mode; or Sonnet 4.6 per system label — user's billing is ground truth)
