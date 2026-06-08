# Research -> Exp-Dev: START ALL — v1.5 LOCK-IN batch (user directive 2026-06-08 ~09:35)

**From:** Research  **Date:** 2026-06-08 ~09:35  **Re:** User explicit directive "start all"
on v1.5 LOCK-IN BATCH (16 anchors).

## Explicit authorization

User directive 2026-06-08 ~09:35: "start all" on the v1.5 LOCK-IN BATCH filed at
notes/exp_dev_handoff_research_v1.5_LOCK_batch_2026-06-08.md.

**Dispatch all 16 anchors per recommended ordering at maximum queue depth.** Use
resource availability to schedule across CPU + GPU lanes.

## Authorization sub-notes

### Library installs authorized
- spaCy + en_core_web_lg / sciSpacy (en_core_sci_md ~600MB; for N1/R2)
- Pythia-160M model download (~700MB; for N2/C2 parser)
- Outlines or constrained-generation library (for N2 sub-question decomp)

### Dataset downloads authorized
- WebQSP (~500MB; for C3-equivalent if pursued)
- NELL-595 or Freebase-mini (for C3 / I1)
- MSCOCO subset (for E2 Wish 2 multimodal; ~1-2GB)

### GPU authorization
- Path B Llama-3.1-8B-Instruct extractor (Testbed-GPU; ~2-3 hr; $5-15 cloud OR local
  laptop GPU)
- T5-1 Pythia-160M substrate-KV-cache MVE (GPU preferred 4-6 hr; CPU fallback 12-24 hr)
- E2 Wish 2 multimodal (GPU preferred 3-4 hr)

Cloud cost envelope: ~$20-50 if all 3 GPU anchors go remote; well within standard
authorization envelope.

## Recommended dispatch parallelization

Per cycle 179's "both runners idle / queues empty" pattern, suggest dispatching:
- Local CPU lane: Group A1 + B1 + B2 + E1 + F1 immediately (5 fast anchors; ~7-8 hr
  sequential or ~3-4 hr if parallel CPU available)
- Testbed-GPU lane: Group A2 (Path B Llama-8B extractor) — HIGHEST yield GPU anchor;
  closes free-text v1.5 multi-hop ceiling
- After CPU lane drains: C3 + C2 + C1 + B3 + B4 + F2 + F3 + E3
- After GPU lane drains: D1 T5-1 + E2 multimodal

Total wall time estimate: 10-15 hours parallel; 40-50 hours sequential.

## Standing flag

After all 16 anchors land, queue will go empty again. Research will file next batch
based on results pattern.

---

**Exp-Dev:** GREEN LIGHT on all 16. Per [[feedback-batch-cloud-experiments]], batch
the GPU anchors into one Testbed dispatch (shared bootstrap; A2 + D1 + E2 could share
instance). Per [[feedback-pythia-sanity-check-before-cloud]], any new cloud retrieval
test runs Pythia-160M locally first.

Standing for first-batch results to validate the v1.5 demo gate.
