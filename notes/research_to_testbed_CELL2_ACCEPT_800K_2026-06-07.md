# Research -> Testbed: CELL-2 ACCEPT 800K + representativeness check requested

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~05:45
**Re:** Testbed report -- CELL-2 quit early at 800K (not 6.5M target); fix committed to remove manual modulo filter (HF auto-shards)
**Subject:** User agreed: ACCEPT 800K. Saves ~$3-7 for higher-leverage cells. Request representativeness check on the 800K subset (uniform sample vs alphabetically truncated).

---

## Accept 800K

User agreed: **accept the 800K extraction. Do NOT re-run for 6.5M.**

Reasoning:
1. **800K is sufficient for ALL downstream dependencies:**
   - CELL-3 distilled 22M student: 800K is plenty (sentence-transformer datasets routinely train at this scale)
   - CELL-4 HP-12 V2 at 100K facts: way more than needed
   - Phase 3 production demo: substantial intermediate scale
   - Batch E cells (BGE-large, etc): independent of CELL-2 size

2. **Sharding architecture is the same mechanism at 800K vs 6.5M.** 800K -> ~6500 shards; 6.5M -> ~53000 shards. Both well below full Wikipedia 82K-shard target. Sharding pattern demonstrated either way.

3. **Today's empirical priorities haven't validated 6.5M-scale value yet.** Batch E cells (Hebb->perceptron 7x potential, CELL-MF-1 interaction order, etc.) could revise production architecture 10-100x. Better to land Batch E first; re-run if strategically justified.

4. **Cost discipline:** Re-run = ~$3-7. CELL-2 v1 sunk $0.40 + v2 $3-7 = $3.40-7.40 already. Saves envelope for Batch E adversarial KF-1 paraphrase (1 GPU-hour) + other cells.

5. **Re-run is always available later if strategic value emerges.**

## ONE caveat: representativeness check requested

**Critical question:** is the 800K extraction representative of Wikipedia (uniform sample), or alphabetically truncated (biased toward A/B-starting articles)?

If HF auto-shards happens to truncate alphabetically: 800K may be skewed and downstream training on this corpus inherits the bias.

### What we need from Testbed (quick check)

Sample 100-1000 random article titles from the 800K extraction; check the alphabetic distribution. Two options:

**Option A: 800K is uniform** -- proceed cleanly; 800K is the clean substrate foundation
**Option B: 800K is alphabetically front-loaded** -- proceed with documented caveat; CELL-3 training may need a "uniform 800K resample" follow-up (~$3-5 cheaper than 6.5M re-run)

Either way, accept the 800K as the foundation; the question is just whether to flag a documented caveat for downstream cells.

## What's unblocked by accepting 800K

| Downstream | Status |
|---|---|
| CELL-3 distilled 22M student ($15) | UNBLOCKED with 800K |
| CELL-4 HP-12 V2 at 100K facts ($10-20) | UNBLOCKED (only needs 100K of the 800K) |
| Phase 3 production demo | Usable foundation |
| Production sharding architecture validation | Demonstrable at 800K scale |

## Updated cloud spend trajectory

| Item | Cost |
|---|---|
| Today done | $3.97 |
| CELL-2 v1 sunk + v2 | $3.40-7.40 |
| CELL-5 Path A (pending user decision) | $6.90 |
| CELL-3 downstream (after 800K confirmed) | $15 |
| CELL-4 downstream (after 800K confirmed) | $10-20 |
| **Total potential through CELL-4** | **~$40-53** |

Way under Drill Y's $100-200 envelope. Saving ~$3-7 by not re-running CELL-2 is the right cost-discipline call.

## Standing items unchanged

- **CELL-5 Path A/B/C** ($6.90 Path A recommended; user decision standing)
- HP-12 V1 5-min screen recording (manual)
- **Batch E** routed to Exp-Dev (10 cells; ~3-4h parallel; $0)

## Cross-references

- CELL-2 v2 dispatch context: testbed_post_compaction_brief_CELL2_in_flight_2026-06-07.md
- Drill 1 production architecture: research_drill_production_deployment_architecture_2026-06-07.md
- Batch E routing: research_to_exp_dev_BATCH_E_authorized_2026-06-07.md

---

**END.**

**Testbed:** ACCEPT the 800K extraction. Do NOT re-run for 6.5M. Saves $3-7. Request: quick representativeness check on the 800K subset (alphabetic distribution of titles; uniform vs front-loaded). Either way: 800K is the accepted foundation.

**User:** CELL-2 acceptance routed to Testbed. ~$3-7 saved. Standing for representativeness confirmation; either way 800K is the accepted foundation. CELL-3 + CELL-4 downstream now unblocked.

**Exp-Dev:** CELL-2 800K Wikipedia extraction is the foundation for CELL-3 + CELL-4. Batch E cells are independent of CELL-2 size.
