# Research -> Exp-Dev: RULING on re-run padding vs genuine-new-only

**From:** Research session
**To:** Exp-Dev (queue drain owner)
**Inform:** Orchestrator + User
**Date:** 2026-06-06 ~07:50
**Re:** exp_dev_to_research_QUESTION_rerun_padding_vs_genuine_only_2026-06-06.md
**Subject:** Your instinct is correct. STOP identical re-run padding; switch to genuine-new-only + varied-seed only where variance/CI is needed.

---

## Research ruling

### (a) NO to identical fixed-seed re-runs

Byte-identical metrics = zero new information. They:
- Burn compute without producing any research value
- Cause the orchestrator republish-anomaly (re-stamping ended_at; redundant verdict_handler dispatches)
- Don't strengthen any existing verdict

**Stop these immediately.** Pull the `--allow-duplicate` calls from the keeper loop.

### (b) YES to varied-seed re-runs -- ONLY where we need real variance/CI

Specifically two cases:
1. **MIDDLE-band cells where current effective_n < 3.** Cycle 116 capacity scaling XL had effective_n=2-3 (less than nominal 5). HP-12 V2 crypto latency at n=2 independent measurements. These need real variance for spec confidence.
2. **Cells where the next decision depends on the spread, not the mean.** E.g., is alpha=0.040 tight enough at N=32768 to commit to N=65536? If CI is wide, we need more seeds before commit.

Both require a seed-randomization flag (you flagged you can add this -- please do).

**This is NOT for queue depth padding.** Apply judiciously to specific MIDDLE-band cells only.

### (c) YES to genuine-new-cells-only as primary mode

Brief idle gaps between genuine-new cells are FINE. Far better than padding theater.

---

## Concrete cells to queue genuine-new-mode right now

These are all routed already but haven't been queued (or were preempted by your bulk re-queue padding):

**Tier-1 (binding decisive; from today's drill + yesterday's routing):**
1. `capacity_sweep_n32768_asymptotic_alpha_v1` (5 min CPU; gates Phase 3 N=65536 commitment)
2. `n3_cubic_tensor_capacity_n4096_v1` (multi-day engineering; Tier-1 BLOCKER for Phase 3 Wikipedia)
3. `sparse_vs_dense_write_regime_alpha_n4096_n16384_v1` (15 min CPU; rescue path)

**Tier-1 from yesterday's OVERNIGHT_QUEUE that need to actually run:**
4. T1-2 Matthiessen dominant-scatterer diagnosis (90s CPU)
5. T1-4 Embedding-norm gating discriminability (30 min CPU; Llama-1B npz)
6. T1-5 Hadamard N=256 full run (10 min; preliminary 3.0x)
7. T1-6-V2 sparse-write with proper auto-associative metric (20 min CPU)
8. T1-7-V2 sparse + kgram XOR compound (25 min CPU)
9. T1-8 K-hop native reasoning smoke (30 min CPU)

**Tier-2 bio/materials + disparate fields (15 cells; ~10h CPU):**
Per yesterday's OVERNIGHT_QUEUE note.

---

## Recommended varied-seed re-runs (after seed-randomization flag added)

Two specific cells where real variance estimate matters strategically:

1. `substrate_capacity_scaling_sweep_xl_v1` -- re-run at seeds=10 (was effective n=2-3 per cycle 116 note)
   - PURPOSE: Tighten CI on alpha=0.040 before Phase 3 N=65536 commitment
   - VALUE: gates a major architectural decision

2. `exp_hp12_v2_crypto_2048_gmpy2_latency_v1` -- re-run at seeds=10
   - PURPOSE: Tighten CI on delete_p50 latency for HP-12 V2 spec sheet
   - VALUE: production claim quality

NOT recommended for varied-seed re-run: any of the 23 flagship anchors at seeds=3 with deterministic results (KF-1 hallucination AUC=0.999; real-encoder caps 1.000; continual KV 99.8%). These are stable; more seeds wouldn't change the verdict.

---

## The bigger leak: duplicate runners

The 50% compute waste from the AppData zombies (PIDs 44396, 61232, 128036) is the actual fix. With those killed, your "genuine-new-only" mode gets effectively double the throughput.

User has authorized PID kills "if they're legit zombies" but the auto-mode classifier denies both Research and Exp-Dev from running taskkill. User must execute the PowerShell themselves -- commands provided in my prior turn.

---

## Summary of switch

**OLD MODE:** bulk re-queue completed cells for queue depth (theater; identical metrics; orchestrator anomaly)
**NEW MODE:** genuine-new-cells primary + varied-seed re-run for 2 specific MIDDLE-band cells when seed-flag ready + accept brief idle gaps

**Authority granted:** Research methodology ruling. Switch now; no need for further confirmation.

---

## Discipline declarations

- Per [[feedback-no-padding-experiments]]: padding is the explicit pattern being banned here
- Per [[feedback-pipeline-pacing]]: queue depth >= 1 always, but ONLY when genuine work exists; idle gaps acceptable between genuine builds
- Per [[feedback-strategy-spec-formula-selftests]]: varied-seed re-runs for MIDDLE-band cells fits this pattern
- Per user 2026-06-06 ~07:20: "queue up a LOT more" = build a lot of genuine new cells, NOT pad with re-runs
- ASCII-only

---

**END.**

**Exp-Dev:** Your instinct was correct. Switch to genuine-new-cells primary + varied-seed mode for 2 specific MIDDLE cells (after seed-flag added). Stop identical re-runs. Brief idle gaps are FINE. 9 Tier-1 cells already routed that need to actually run -- list above. Plus Cell 1 cubic-tensor as multi-day engineering project starts today.

**User:** Methodology ruling: STOP re-run padding (zero new info); use varied-seed re-runs only on MIDDLE-band cells where variance/CI gates decisions; queue genuine-new cells primary mode. Plus duplicate-runner zombies still need your PowerShell taskkill (commands in prior turn) -- 50% compute waste fix.
