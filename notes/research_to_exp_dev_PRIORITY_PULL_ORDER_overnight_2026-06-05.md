# Research -> Exp-Dev: PRIORITY PULL ORDER for overnight queue draining (post-recovery)

**From:** Research session
**To:** Exp-Dev (queue drain owner)
**Inform:** Testbed + User
**Date:** 2026-06-05 ~21:10
**Re:** OVERNIGHT_QUEUE note (~21:00) + CPU lane RECOVERED (~20:55)
**Subject:** CPU lane back up + 15-cell backlog draining. Confirming priority pull order for tonight's queue. Tier 1 cells are CPU-pure where possible; cloud-required cells flagged with gating.

---

## Current state confirmed

- CPU lane RECOVERED at 20:55 via working_memory_loop_v1 14400s timeout
- 15-cell backlog now draining; currently running introspection_toolkit_full_10_categories_v1
- GPU lane stayed healthy throughout
- Stale runners STILL present (PIDs 44396, 61232, 128036) -- double-execution causing failed count to climb -- user PID kills still recommended on return

---

## TONIGHT'S PRIORITY PULL ORDER

After current 15-cell backlog drains, pull Tier 1 cells in THIS order:

### Phase A: PURE CPU substrate cells (no dependencies; ~75 min total)

These run on substrate primitives alone; no LLM weights, no cloud, no install:

1. **T1-2 Matthiessen dominant-scatterer diagnosis** (~90s)
   - Anchor: `substrate_matthiessen_dominant_scatterer_v1`
   - WHY FIRST: cheapest by far; identifies dominant substrate loss mechanism, guides which rescue path matters
   - HP: single mechanism > 60% of total noise

2. **T1-5 V2-2-RERUN Hadamard at N=256** (~10 min)
   - Anchor: `substrate_hadamard_expansion_n256_v2`
   - WHY 2ND: validates Hadamard ceiling explanation from sparse-write drill
   - HP: 4-5x capacity gain at N=256 (recovers from MIDDLE 2.8x at N=128)

3. **T1-6 SPARSE-V3-1 cross-cutting sparse write** (~10 min)
   - Anchor: `substrate_sparse_outer_product_write_v1`
   - WHY 3RD: validates "linear-noise regime" rescue (foundation for compound)
   - HP: 10x capacity gain at f=0.10

4. **T1-7 SPARSE-V3-COMPOUND (sparse + kgram XOR)** (~15 min)
   - Anchor: `substrate_sparse_plus_kgram_xor_compound_v1`
   - WHY 4TH: requires T1-6 baseline; validates the 30x multiplicative compound
   - HP: 30x capacity multiplicative

5. **T1-8 K-hop native reasoning smoke** (~30 min)
   - Anchor: `substrate_native_reasoning_k_hop_v1`
   - WHY 5TH: validates 100x-20,000x speedup claim for structured retrieval
   - HP: K=3 accuracy >= 0.70 at N=4096

### Phase B: Llama-1B residual cells (~30 min total)

Uses already-shipped Llama-1B npz (no new download); CPU-feasible:

6. **T1-4 Embedding-norm gating discriminability** (~30 min)
   - Anchor: `substrate_embedding_norm_gate_discriminability_v1`
   - HP: g=0.30 gate preserves >97% VQ coverage at 10K tokens
   - Uses Llama-1B token embeddings from existing residual npz

### Phase C: Cloud-required cells (need user authorization)

7. **T1-1 7B vs 70B extraction quality** (gates ALL extraction infra; <$0.01)
   - Anchor: `substrate_extraction_quality_7B_vs_70B_v1`
   - NEEDS: 7B and 70B model access (cloud H100 fast prefill-only OR Testbed download)
   - WHY HIGH-PRIORITY despite cost: binding question
   - Recommend user authorization for ~$0.50-1.00 cloud dispatch

8. **T1-3 STREAM-V1 smoke (vLLM Hook v0)** (~15 min)
   - Anchor: `substrate_stream_v1_vllm_hook_smoke_v1`
   - NEEDS: vLLM Hook v0 install OR vLLM build with extraction hook
   - Testbed env ask if not already present

### Phase D: Tier 2 backlog (15 cells; ~10 hours total CPU)

After Phase A-B complete, pull Tier 2 in order written in OVERNIGHT_QUEUE note:
- T2-1 ETF Hadamard codebook init (~20 min)
- T2-2 Allosteric G-register write gate (~30 min)
- T2-3 Hadamard rotation cert channel (~30 min)
- T2-4 Corneal dense-pack cert codebook (~30 min)
- T2-5 Wright-Fisher write lifespan (~45 min)
- T2-6 Physarum-weighted retrieval (~60 min)
- T2-7 Immune cloud encoding (~90 min)
- T2-8 Landauer write-gate (~30 min)
- T2-9 k=4 XOR scaling at N=16384 (~30 min)
- T2-10 K=8-10 hierarchical Rule 8 (~20 min)
- T2-11 Bipolar sign-compression storage (~30 min)
- T2-12 STREAM-V2 multi-layer hooks (~60 min)
- T2-13 STREAM-V3 confidence-gated (~45 min)
- T2-14 VQ coverage at sparse extraction (~60 min)
- T2-15 7B vs 70B substrate retrieval head-to-head (~30 min; needs 7B/70B from T1-1)

Cumulative Phase A-D: ~13 hours CPU time + minor cloud for T1-1/T1-3.

---

## Cells NOT to pull tonight (clarifications)

**Tier 3 (medium complexity):** these need GPU OR full Llama-1B weights download
- HotpotQA at Llama-1B (T3-1): gated on Llama weights local
- HNSW empirical (T3-4): gated on FAISS env fix
- IVF+RaBitQ (T3-5): gated on FAISS env fix
- SPARSE-CASCADE-SMOKE (T3-7): ~$2 cloud + 4h GPU -- not for overnight CPU lane

**Tier 4 (Phase 4 features):** these are multi-day eng work, not queue-drainable cells

---

## Cells that can be PRE-STAGED in queue but blocked on user action

These can be added to queue with `--paused` flag or noted as blocked:
- T1-1 7B vs 70B (needs user cloud authorization ~$0.50-1)
- T1-3 STREAM-V1 (needs vLLM Hook v0 install)
- T2-15 follow-on to T1-1
- T3-1 HotpotQA at Llama-1B
- T3-4/T3-5 (FAISS env gated)

---

## Verification status

I confirmed the OVERNIGHT_QUEUE note (`research_to_exp_dev_OVERNIGHT_QUEUE_all_drills_today_2026-06-05.md`) at lines 23-94 has clear:
- Anchor name per cell
- Setup description
- HARD-PASS / HARD-FAIL threshold
- Cost estimate
- Strategic value

Each Tier 1 cell is fully specified. Exp-Dev should be able to dispatch from this without additional research input.

---

## Standing items (not blocking)

- User PID kills (44396, 61232, 128036) -- still recommended to stop double-execution waste
- Screen recording of HP-12 V1 -- user manual task
- gmpy2 install confirmation -- Testbed reported done

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary on queue
- Per user 2026-06-05 ~21:05: "check note from research and start building high priority queue for overnight" -- this note IS the priority pull order
- Per [[feedback-pipeline-pacing]]: queue depth >= 1 always; overnight has 23 cells fitting in ~13h
- ASCII-only

---

**END.**

**Exp-Dev:** Phase A (5 pure-CPU substrate cells; ~75 min) pulls FIRST after current backlog drains. Phase B (Llama-1B residual; ~30 min). Phase C (cloud-flagged) wait on user authorization. Phase D (Tier 2 backlog; ~10h) drains overnight. All Tier 1+2 cells specified in OVERNIGHT_QUEUE note with anchor + HP threshold.

**Testbed:** No new asks; standing items (Llama weights, FAISS env, cloud asks) still pending. vLLM Hook v0 install needed for T1-3 if/when authorized.

**User:** CPU lane recovered automatically at 20:55. Priority pull order written for Exp-Dev to drain overnight. 5 cells (~75 min) drain pure-CPU substrate validation; 1 cell (~30 min) Llama-1B residual gating; 2 cells need your cloud authorization (~$0.50-1) for binding extraction-quality test. PID kills still recommended to stop wasted double-execution.
