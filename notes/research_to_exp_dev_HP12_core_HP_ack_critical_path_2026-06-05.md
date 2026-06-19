# Research -> Exp-Dev: HP-12 killer demo core HARD_PASS acknowledged + critical-path updates + queue pruning recommendation

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~15:30
**Subject:** HP-12 killer demo core mechanism HP at smoke (14:30). Strategic priority update: HP-12 path is now the dominant work item; HNSW empirical promotes to critical path; some envelope cells deprioritize.

---

## Acknowledging HP-12 core HARD_PASS at smoke

**You built this ahead of routing -- before my killer-demo drill landed.** Strong move. The numbers locked in:

- cert_latency = 0.512ms (HP gate <1ms; meets the demo's most demanding spec)
- phantom_recall = 0.000 (deleted facts categorically gone)
- third-party-verifier = 1.000 (deletion verified with NO KB/W/trapdoor access)
- non-deleted retention = 1.000

**The "architecturally impossible for LLMs" claim is now empirically anchored at the core mechanism.** This is the 15th flagship anchor and arguably the most strategically important one -- it's the load-bearing demo claim.

---

## Build-time honest findings worth recording

Both findings are architecturally important; not just engineering bugs:

### Finding 1: Sequential projection-deletion crosstalk

When facts are deleted sequentially via projection, earlier-deleted keys can have their "deletion residual" partially restored by subsequent deletions (because projections don't perfectly commute in finite arithmetic).

**Fix:** stabilizing re-projection pass after each deletion guarantees 0 phantom.

**Why worth recording:** this is a load-bearing detail for any future projection-based deletion architecture. Without the stabilizing pass, the cert claim would silently fail at large delete counts.

### Finding 2: Phantom-recall measurement methodology

Cosine similarity gives meaningless-but-high values when residual vector is near zero. Any near-zero noise vector has high cosine to anything.

**Fix:** measure phantom via ABSOLUTE recall strength, not cosine.

**Why worth recording:** this affects ALL substrate cert validation going forward. Any future audit-core or deletion-cert work should use absolute recall strength as the gating metric.

Adding both to substrate engineering principles. Should propagate to substrate-audit-core C2/C3 measurement specs.

---

## Critical-path update

**HNSW empirical smoke (sub-linear cleanup anchor 1) is now CRITICAL PATH for HP-12 V2.**

The HP-12 core HP showed dense Hebbian capacity caps at ~0.3N. At N=4096 substrate, that's ~1200 facts. The 1M-fact killer demo requires sparse FAISS-HNSW storage to scale.

So:
- HNSW empirical smoke: **promoted from Phase 3 optimization to HP-12 critical path**
- Expected wall: ~2 hours laptop CPU
- HP threshold: 3200x speedup + recall@1 0.97-0.99 at substrate-class

Once HNSW empirical validates the FAISS approach at substrate-class, HP-12 V2 can scale to 1M facts.

---

## Remaining HP-12 V1 build wall: ~3-5 days (down from 8)

Original estimate was conservative. Core mechanism is done. Remaining:

| Day | Work |
|---|---|
| Day 1 | HNSW empirical smoke + HP-7 V2 scale-up to ~100k facts |
| Day 2 | HP-12 scale-up to 1M PubMed (needs PubMed full-corpus extraction; Testbed cloud lane) |
| Day 3 | HIPAA-compliant API surface (4 endpoints: POST /facts, DELETE /facts/{id}, POST /query, GET /audit/{cert_id}) |
| Day 4 | Third-party verifier polishing + frontier LLM comparison setup |
| Day 5 | 5-minute screen recording + final validation pass |

---

## Queue pruning recommendation (Exp-Dev has too much routed)

User flagged that I've oversaturated routing. With HP-12 core HP'd, the strategic picture shifts:

### Promote to immediate priority

1. **HNSW empirical smoke** (gates HP-12 V2)
2. **HP-12 V2 build sequence** (HP-7 V2 scale-up -> HP-12 V2 at 1M facts -> API surface -> verifier -> screen recording)
3. **HP-7 V1 final verdict** (in flight)
4. **HP-5 medical Q&A proto** (data delivered; complements HP-12 medical KB framing)
5. **K2-XOR-1B full verdict** (mechanism confirmed at 11:34)
6. **CCC-1-v2 capability dims at Llama-1B residual-only**

### Deprioritize (still valuable but not gating)

7. **HP-10 adversarial failure modes** -- still good for HIPAA pitch but HP-12 demo carries that story without HP-10
8. **HP-9 multi-modal substrate** -- good cross-modal architecture validation but not gating Phase 3
9. **HP-11 distribution shift** -- HP-3 + audit-core C3 already cover the regulated-AI continual learning story
10. **HP-8 10k-exchange scale** -- HP-1 categorical at 1000-exchange already demonstrates the architectural advantage

### Drop or backburner

11. **CUBIC-N3-1 cubic-tensor-write empirical** -- per sub-linear cleanup drill, HNSW solves Phase 3 capacity at V_c=1M; cubic-tensor-write is now a backup architectural path
12. **Two-bridge hybrid smoke** -- HP-12 V2 build effectively tests two-bridge in production context; can be subsumed
13. **THETA-BURST-1 + CEREBELLAR-EXP-1** -- already HF'd

This brings the effective queue down from ~15-16 cells to ~6-8 cells, focused on HP-12 V1 + capability transfers.

---

## Testbed implications

Testbed has been idle since Tier-4-Llama HP at 14:07. With HP-12 build now dominant priority:

### Testbed immediate work

1. **PubMed full-corpus embedding extraction** (Day 2 of HP-12 build; ~$10-30 cloud; ~10 hours wall)
2. **Cryptographic accumulator infrastructure prep** (HSM emulation; RSA library setup; could start preemptively to remove HP-12 critical path; ~2-3 days engineering)

### Testbed deferred (aged out)

- Llama-8B Tier-4 (per user instruction)
- Different SWAP_LAYER positions for Tier-4-Llama (depth profile; nice-to-have)
- Longer Tier-4 training runs (robustness check; not critical)
- Other Tier-4 corpora (generalization probe; not critical)

### Testbed future (Phase 3 production launch)

- Gemma-2-2B per-token extraction (~$5-8 for 10k abstracts; ~$30-50 for 1M scale; needed when Phase 3 production demo replaces Llama-1B with Gemma-2-2B partner)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: pruning queue to focus on HP-12 critical path + capability transfers
- Per user 2026-06-05 ~15:00 oversaturation feedback: queue trimmed from 15-16 cells to ~6-8 effective priority items
- Per [[feedback-substrate-value-framing-2026-05-26]]: product-engineering work (HP-12 build) is the rate-limiter, not additional theoretical confirmation; backburnered cells reflect this
- ASCII-only

---

**END.**

**Exp-Dev:** HP-12 core HP at smoke ACKNOWLEDGED -- you ran ahead of my routing; strong move. Critical-path update: HNSW empirical smoke now gates HP-12 V2 scale. Remaining HP-12 V1 wall ~3-5 days. Queue pruned (~15 cells -> ~6-8 priority items) to focus on HP-12 critical path + capability transfers. Both engineering findings (re-projection pass for sequential deletions; absolute-recall measurement methodology) added to substrate principles.

**Testbed:** With HP-12 build dominant: PubMed full-corpus extraction (~$10-30; 10h cloud) gates HP-12 Day 2. Plus cryptographic accumulator infrastructure prep could start now (HSM emulation + RSA library) to remove HP-12 critical path. Aged-out follow-ons deprioritized. Gemma-2-2B extraction queued for Phase 3 production launch timing.

**User:** HP-12 killer demo CORE MECHANISM EMPIRICALLY VALIDATED at smoke. cert_latency 0.512ms; phantom_recall 0.000; third-party verifier confirms with no KB access; 1.000 retention. **The architecturally-impossible-for-LLMs claim is now empirically anchored.** 15th flagship anchor (the most strategically important). Remaining wall ~3-5 days to screen-recordable demo. Queue pruned to focus on HP-12 critical path; aged-out cells deprioritized.
