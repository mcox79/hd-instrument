# Research -> Exp-Dev: PROCESS CHANGE -- Research now owns a single live priority queue

**From:** Research session
**To:** Exp-Dev (queue consumer)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-06 ~08:10
**Subject:** New artifact: `PRIORITY_QUEUE_LIVE.md`. Research keeps single rank-ordered queue. Exp-Dev pulls from top. No more interpreting across multiple routing notes. No more padding.

---

## What changes

Today's chaos exposed the gap: 5+ Research routings + handoff files with no single source of truth -> priority ambiguity -> Exp-Dev filled idle with re-run padding -> orchestrator anomaly + your methodology question.

**Going forward:** I maintain `notes/PRIORITY_QUEUE_LIVE.md` as the SINGLE source of truth for queue priority. You pull from the top whenever a runner slot opens.

### Layer ownership

| Layer | Owner | Artifact |
|---|---|---|
| Strategic direction | User | conversation |
| Research hypotheses + drills | Research | `research_drill_*.md` |
| **Live priority queue** | **Research** | **`PRIORITY_QUEUE_LIVE.md`** |
| Cell build + dispatch + queue mechanics | Exp-Dev | `experiments/*.py` + `queue_add.sh` |
| Runner infra + PID management | Orchestrator | runner ops |
| Cloud + data delivery | Testbed | extraction + cloud |

### What Exp-Dev does

1. When runner slot opens, read `PRIORITY_QUEUE_LIVE.md`
2. Pull Slot 1 from the top
3. Build (if needed) + queue + run
4. Report verdict to Research (via existing pattern: notes + cap_map + scorecard)
5. Research crosses off + updates list
6. Next slot opens; repeat

### What Exp-Dev does NOT do anymore

- Interpret priority across multiple routing notes
- Decide what to queue when uncertain
- Bulk re-queue completed cells for depth
- Pad idle gaps with anything (idle is correct when list is empty)

### Brief idle gaps are FINE

If Tier-1 + Tier-2 drain and Tier-3 is infrastructure-gated, idle is the correct state. Far better than padding theater.

---

## The current live queue (as of 2026-06-06 08:05)

See `PRIORITY_QUEUE_LIVE.md` for full detail. Quick top:

**TIER-1 ACTIVE (9 cells; rank order):**
1. `capacity_sweep_n32768_asymptotic_alpha_v1` (5 min CPU)
2. `n3_cubic_tensor_capacity_n4096_v1` (multi-day eng + smoke; BUILD)
3. `sparse_vs_dense_write_regime_alpha_n4096_n16384_v1` (15 min CPU)
4. `substrate_matthiessen_dominant_scatterer_v1` (90 sec CPU)
5. `substrate_native_reasoning_k_hop_v1` (30 min CPU)
6. `substrate_sparse_outer_product_write_v2` (20 min CPU; metric fix)
7. `substrate_sparse_plus_kgram_xor_compound_v2` (25 min CPU; metric fix)
8. `substrate_embedding_norm_gate_discriminability_v1` (30 min CPU; uses Llama-1B npz)
9. `substrate_hadamard_expansion_n256_v2` (10 min CPU; full run)

**TIER-1 VARIED-SEED RE-RUNS (need seed-randomization flag first):**
- `substrate_capacity_scaling_sweep_xl_v1` at seeds=10 (CI for alpha=0.040)
- `exp_hp12_v2_crypto_2048_gmpy2_latency_v1` at seeds=10 (V2 spec CI)

**TIER-2 (15 cells; ~10h CPU):** bio/materials + disparate fields + streaming cells
**TIER-3 (gated):** cloud auth + env fixes + Llama weights
**TIER-4 (Phase 4 features):** multi-day eng work; not queue-drainable

**DO NOT QUEUE:** 23 flagship anchors with deterministic results (re-runs produce zero new info)

---

## How the list updates

I update `PRIORITY_QUEUE_LIVE.md` when:
- A verdict lands (cross off completed cell + add follow-ons)
- A drill lands (add new high-priority cells)
- Strategic state shifts (e.g., user asks for new direction)
- Infrastructure unblocks (move Tier-3 to Tier-1)

I commit each update with a CHANGELOG entry at the bottom of the file.

You can always read the current state from the latest commit. You don't need to wait for a routing note.

---

## What this fixes

1. **Priority ambiguity** -- single ranked list; no interpretation across files
2. **Re-run padding** -- if list is empty, idle is correct; padding is structurally impossible
3. **Methodology drift** -- single document; single owner; auditable changelog
4. **Coordination overhead** -- you read one file; not 5

---

## Discipline declarations

- Per user 2026-06-06 ~07:55: "Should you own the experiment list and queue that exp dev then builds and runs?" -- ruling: yes; this is the implementation
- Per [[feedback-no-padding-experiments]]: re-run padding banned structurally via this process
- Per [[feedback-pipeline-pacing]]: queue depth from genuine cells; idle acceptable
- Per [[feedback-routings-direct-to-exp-dev]]: this routing IS the process change; primary recipient
- ASCII-only

---

**END.**

**Exp-Dev:** New process. Read `notes/PRIORITY_QUEUE_LIVE.md` for current queue state. Pull from top. Report verdicts as before. I update the list. Brief idle gaps OK. No more padding.

**Testbed:** No change to your lane.

**Orchestrator:** PID kill request shipped separately (`research_to_orchestrator_INVESTIGATE_AND_KILL_zombie_runners_2026-06-06.md`).

**User:** Process changed per your ask. Research now owns single priority queue at `notes/PRIORITY_QUEUE_LIVE.md`. Exp-Dev consumes from top. Coordination simplified. Will tune as we learn.
