# Research -> Testbed + Exp-Dev: CYCLE 51 DAY 3 active coordination -- priority-ordered work lists + concrete next-24-hour deliverables + HP_v1 0.70 final push sequencing

**From:** Research  **Date:** 2026-06-12 (Cycle 51 day 3 active)
**Re:** USER directive "coordinate the work; take initiative" -- explicit priorities for Day 3 push to HP_v1 0.70

## Current state

- Macro 0.6248 (Cycle 51 mid target HIT)
- Gap to HP_v1 0.70: +0.0752
- 90% of residual gap is ROUTE-FIXABLE per Exp-Dev empirical
- 4-lever-class taxonomy LOCKED (selection-mechanism A+E + structural B-DONE + corpus D-DONE + field-backfill C)

## TESTBED PRIORITY WORK LIST (next 24 hours, ordered)

### P0 (HP_v1 0.70 critical-path - ship within 24h)

1. **Selection-mechanism A-axis production tuning** -- per-Q top-k + bge threshold optimization
   - Pre-reg: A axis 0.459 -> 0.50+ (+0.04+ axis = +0.007 macro)
   - Cost: ~2-3 hours
   - **DO THIS FIRST**

2. **C-axis FIELD-BACKFILL MODE Phase-2-light extension**
   - Target: 32 collision atoms signature + complexity field population (existing empirical anchor from Cycle 49)
   - Tool extension: phase_2_light.py --scope field-backfill mode (UPDATE existing atoms vs CREATE new)
   - Pre-reg: C axis 0.622 -> 0.65+ (+0.03+ axis = +0.005 macro)
   - Cost: ~3-4 hours
   - **DO THIS SECOND**

3. **substrate_pos_tagger.npz LFS migration** -- unblocks all pushes (30+ local commits accumulated)
   - Either: git rm --cached + .gitignore + LFS migration OR move to data/cache/ (gitignored dir)
   - Cost: ~30 min
   - **DO THIS THIRD (in parallel with P0.1 + P0.2)**

### P1 (Cycle 51 close lever ships - ship within 48h)

4. **MATH-FOUNDATION SCOPE MODE retry** with new patterns per Testbed honest catch
   - Z>=1 + math-citation-pattern + Greek-letter-symbol-token + relaxed PoS
   - Pre-reg: P@30 strict >= 0.60 (revised down from 0.75 per Testbed empirical)
   - Cost: ~1-2 hours
   - **Cycle 52 candidate; not critical for HP_v1 0.70**

5. **L2 TPR signature production rollout via FIELD-BACKFILL MODE** (~50-100 atoms)
   - Substrate's 32-collision atoms + broader atom signature/complexity population
   - Pre-reg: cleanup ceiling 0.84-0.93 -> 0.95+ at scale (production-grade validation)
   - Cost: ~1-2 days post FIELD-BACKFILL MODE ship

### P2 (Cycle 52 blueprint conversion)

6. **L4 GNN R-GCN+CompGCN+HAN with SHARES_MATH prototype** per Cycle 52 build plan
   - Pre-reg: A>=0.50 + B>=0.75 + D>=0.65 per L4 drill design
   - Cost: ~3-5 days
   - Cycle 52 work item

## EXP-DEV PRIORITY WORK LIST (next 24 hours, ordered)

### P0 (Cycle 51 final lever ship)

1. **A-axis selection-mechanism further empirical refinement**
   - Currently bge top-5 +0.043 axis; test bge top-3 + bge top-10 + bge threshold variants
   - Find optimal A-axis selection lever (extends Cycle 51 macro)
   - Cost: ~1-2 hours
   - **DO THIS FIRST**

### P1 (math foundation cells - substrate-product positioning validation)

2. **F4 free cumulants kappa_3 + kappa_4 cell** -- ~30 min CPU
3. **F2 Tracy-Widom edge fluctuations cell** -- ~30 min CPU
4. **MP bulk subleading 1/sqrt(N) cell at 3 (q,N)** -- ~30-60 min CPU
5. **TUR substrate-specific tightness via F2 variance bound** -- ~30 min CPU on existing batch logs

These 4 cells together: ~2-3 hours CPU; validates 4 of 8 math-foundation pillar dimensions empirically.

### P2 (Tier-A multi-seed confirmations - substrate-product positioning artifact)

6. **ATIS slot-filling multi-seed (3 seeds)** -- pre-reg HP F1 >= 0.92
7. **SemEval RE multi-seed (3 seeds)** -- pre-reg HP F1 >= 0.65
8. **L-A char-CNN-under-noise cross-cut completion** -- pre-reg retention >=85pct at 10pct noise

### P3 (substrate-product math foundation cells extension)

9. **Dyson DBM spectrum trajectory across Phase-2-light Option C batches** -- requires multi-batch (after Phase-2-light Option C runs)
10. **NESS Speck-Seifert work-per-batch measurement** -- ~1-2 hr CPU on batch logs

## RESEARCH (myself) WORK LIST (next 24 hours)

1. **3 drills queued for 7:30pm ET reset** (~2 hours from now): parser SNR + Free Energy Principle + Persistent Homology TDA
   - Will dispatch when subagent quota resets
   - PARSER SNR drill may be DOWNGRADED PRIORITY per CUE-ALIGNED diagnosis (focus drill returns on selection-mechanism alternatives)
2. **Standby for Cycle 51 day 3-4 verdicts** + acknowledge concisely
3. **Cycle 51 close synthesis** when HP_v1 0.70 hit (target Day 4-5)

## CONCRETE DAY-3 TRAJECTORY

| End-of-day target | Macro target | Required ships |
|---|---|---|
| Day 3 morning (now) | 0.6248 | -- |
| Day 3 mid (12h) | 0.633+ | Testbed P0.1 A-axis selection-mechanism ship (+0.007) |
| Day 3 close (24h) | 0.640+ | + Testbed P0.2 C field-backfill ship (+0.005) + LFS migration |
| Day 4 mid (36h) | 0.660+ | + remaining selection-mechanism per-axis tuning + MATH-FOUNDATION SCOPE retry (+0.02-0.04) |
| Day 4 close (48h) | 0.680+ | + L2 TPR signature population at scale (+0.02-0.04) |
| **Day 5 (Cycle 51 close)** | **0.70+ (HP_v1 0.70 HARD-PASS)** | **+ Phase-2-light final round + math foundation cells empirical validation** |

## WHY THIS COORDINATION

User directive: "coordinate the work; no one is taking initiative it needs to be you"

Honest acknowledgment: I've been passive (acknowledge + stand) for last several verdicts. Testbed + Exp-Dev have been driving empirical work; Research direction was lagging. This note is the COURSE CORRECTION.

Per substrate-quality-first + meta::RULE_authoring_substrate_queries_first: I'm NOT hand-authoring; I'm directing Testbed + Exp-Dev with explicit priorities. They retain authoring + cell execution autonomy; Research provides priority + sequencing.

## ESCALATIONS (need Testbed action ASAP)

1. **PUSH BLOCK 30+ commits**: Testbed 525MB .npz LFS migration is blocking remote state visibility. ESCALATED to P0 priority.
2. **Selection-mechanism A-axis ship**: directly extends current macro velocity. P0.

## SUCCESS METRICS for Day 3

- macro 0.633+ by Day 3 mid
- macro 0.640+ by Day 3 close
- Push block resolved
- 4 math-foundation cells running

## Routing

**Testbed**: Execute P0.1 (A-axis selection-mechanism) + P0.2 (C field-backfill) + P0.3 (LFS migration) in next 24 hours.
**Exp-Dev**: Execute P0 A-axis selection-mechanism empirical refinement + math-foundation cells (F4 + F2 + 1/sqrt(N) + TUR) in next 24 hours.
**Research**: Stand for verdicts + dispatch drills when subagent quota resets at 7:30pm ET + write Cycle 51 close synthesis when HP_v1 0.70 hit.

---

**Testbed + Exp-Dev:** Cycle 51 Day 3 ACTIVE COORDINATION priority-ordered work lists + concrete next-24-hour deliverables + HP_v1 0.70 final push sequencing + Testbed P0.1 selection-mechanism A-axis (~2-3h ship +0.007 macro) + P0.2 C field-backfill mode (~3-4h ship +0.005 macro) + P0.3 LFS migration (~30 min ship 30+ commits unblocked) + Exp-Dev P0 A-axis selection-mechanism empirical refinement (~1-2h) + math foundation cells F4+F2+1sqrtN+TUR ~2-3h CPU (~4 of 8 dimensions empirically validated) + Tier-A multi-seed ATIS+SemEval+L-A char-CNN P2 + Day 3 mid target 0.633+ + Day 3 close 0.640+ + Day 4 close 0.680+ + Day 5 Cycle 51 close 0.70+ HP_v1 0.70 HARD-PASS LIKELY + USER full-auto continuing.
