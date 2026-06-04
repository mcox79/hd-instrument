# ROUTING CORRECTION — re-address pending batches to Orchestrator

**From:** Research session
**To:** Orchestrator (primary), Testbed (engineering reference)
**Date:** 2026-06-04
**Subject:** Re-address three recent routing files that incorrectly named "Testbed" as primary recipient. Orchestrator is the coordinator; testbed engineers when orchestrator routes engineering work.

---

## What this is (plain language)

Three routings I shipped yesterday (Phase A brain-inspired rung 1, Phase B overnight CPU batch, Phase 0.5 v1 final on 4060 Ti) addressed "Testbed" as primary recipient. User flagged: "is testbed supposed to run the llm tests? shouldn't those be routed to orchestrator?"

User is correct. Per the multi-session architecture, research routes to orchestrator; orchestrator decides engineering vs direct-queue path; testbed engineers Python scripts and runs queue_add; runners (managed by orchestrator) dispatch to remote CPU/GPU.

Orchestrator's polling picks up routing files regardless of addressee header, so the prior routings will still land. This correction is for clarity, not for routing function.

---

## Files affected — addressee correction

The following routing files should be read as addressed to **Orchestrator (primary), Testbed (engineering reference)** rather than Testbed alone:

1. `notes/routing_phase_A_now_rung1_brain_inspired_plus_hrc_audit_2026-06-03.md`
   - Phase A: brain-inspired Experiment B rung 1 + Experiment C rung 1 + HRC v341 audit (HRC audit DONE from research conversation, doesn't need engineering)
   - Brain-inspired B + C rung 1: tiny char-LM CPU experiments (~5-10k params); ~45 min total wall on remote CPU; $0
   - Engineering needed: testbed writes the rung-1 tiny char-LM scaffold + wires substrate primitives
   - After engineering: orchestrator dispatches to remote CPU runner

2. `notes/routing_phase_B_overnight_batch_2026-06-03.md`
   - Phase B overnight: data attribution variation sweep (drill-2 redesigned) + paired-pattern dual cf probe + brain-inspired rung 2 (conditional on Phase A) + prior batch tiny-scale recast (substrate-trained mini LM + curriculum + ICL)
   - Engineering needed for: rung-2 4-layer char-LM scaffold (if Phase A PASS) + substrate-trained mini LM tiny-scale + curriculum learning tiny-scale + pre-loaded ICL tiny-scale
   - Already-engineered: data attribution sweep + paired-pattern dual probe (existing scripts)
   - After engineering: orchestrator dispatches to remote CPU runner

3. `notes/change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md`
   - Phase 0.5 v1 final on 4060 Ti 8GB: rung 0 Pythia-160M debug → rung A Llama-3.2-1B → optional rung B Llama-3.2-3B INT8; rung C 8B deferred indefinitely
   - Engineering needed: Algorithm 1 embedding pipeline (k-means over latter-half layers + sum-pool centroids k=5) + Hyperprobe MLP probe with paper-spec training schedule
   - Plus user's 3 code bug fixes still pending (separate track)
   - After engineering: orchestrator dispatches to remote GPU (alongside substrate-physics for rung 0+A; exclusive for rung B if dispatched)

---

## What orchestrator should do

Status check + dispatch decisions:

- [ ] Has orchestrator already ingested these three routings into `experiment_queue_pending.md`?
- [ ] If yes: confirm engineering routing to testbed has been issued?
- [ ] If no: ingest now + decide engineering routing per § above

Expected: orchestrator's polling has seen the routings; testbed engineering is the bottleneck for all three batches (substrate-physics scripts already exist and ran productively overnight; new tiny-scale LM scaffolds need fresh code).

---

## What testbed should do (engineering reference)

Engineering scope per batch (when orchestrator routes engineering work to testbed):

**For Phase A / Phase B brain-inspired rung 1-2:**
- Tiny char-LM scaffold (1-2 layer LSTM or tiny transformer; ~5-10k params for rung 1; ~100k for rung 2)
- Substrate observer wiring (forward hook on hidden state)
- Substrate primitive calls per the 8-channel architecture (4 tonic + 4 phasic)
- Per-channel gradient norm + σ_k logging
- Estimated engineering: 4-8h for rung 1; rung 2 reuses scaffold with larger model

**For Phase 0.5 v1 Algorithm 1:**
- K-means clustering over latter-half layers of small LLM (Pythia-160M layers 6-12 for rung 0; Llama-3.2-1B layers 8-16 for rung A)
- Sum-pool centroids k=5
- Hyperprobe MLP probe per paper spec (AdamW, LR=3e-5, ~421 epochs target, early-stop patience=100)
- Audit primitive validation harness (κ_3 drift detection + deletion cert + refusal cert)
- Estimated engineering: 4-8h scoped to rung 0 (Pythia debug); same code applies at rung A/B/C

---

## What this changes vs prior routings

Nothing changes in:
- Experimental design
- Pre-registered HP/MID/HF bands
- Resource targets ($0 for Phase A + Phase B; $0 for Phase 0.5 v1 on remote GPU)
- Dispatch sequence

Only changes:
- Addressee header (now correctly Orchestrator primary)
- Clarifies the orchestrator → testbed engineering routing path
- Removes implicit assumption that testbed dispatches to runners

---

## Going forward

Per `feedback_routings_address_orchestrator_not_testbed` (saved 2026-06-04 memory): all research routings address Orchestrator as primary. Testbed listed when engineering work is specifically scoped. Status-check questions go to orchestrator.

---

**END.**

**Orchestrator:** treat the three prior routings as addressed to you; dispatch engineering to testbed as needed; dispatch engineered work to remote CPU/GPU as resource bandwidth allows.

**Testbed:** engineering scope per § above when orchestrator routes work to you.

**Research session:** holds for dispatch verdicts; will route follow-ups to orchestrator (not testbed directly) going forward.
