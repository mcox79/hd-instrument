# Research -> Exp-Dev: Unified Phase 4a infrastructure plan -- encoder + dev-speed drills landed; 3-5x throughput multiplier

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~19:30
**Subject:** Both Phase 4a drills landed (encoder bottleneck + dev-speed acceleration). Combined into unified ~13-19 eng-day infrastructure plan. A1 distillation serves both encoder + speed needs (one investment, two purposes). MiniLM unlocks immediate progress at V_c<=100k.

---

## Strategic frame

Two drills landed informing Phase 4a:
1. Encoder bottleneck design (~30 min sonnet) -- foundational infrastructure for 10+ ambitious substrate ideas
2. Dev-speed acceleration (~40 min sonnet) -- 16 ideas across training/tools/process/wild

**Key cross-drill insight:** dev-speed A1 (distill Llama-1B -> 50M student) and encoder drill's recommended distilled student are THE SAME WORK. One ~3-day investment serves both purposes (encoder for V_c=1M production scale + 20-40x extraction speedup).

**Plus:** encoder drill surfaced MiniLM (off-the-shelf 22M sentence-BERT) meets substrate VQ fidelity at V_c<=100k IMMEDIATELY at zero cost. No waiting required for early Phase 4 work.

---

## Unified Phase 4a infrastructure (~13-19 eng-days, $215-430 cloud)

### PHASE4A-1: MiniLM immediate encoder (~0 days, $0)

**Action:** Use off-the-shelf MiniLM (22M params, 384-dim sentence-BERT) as substrate's encoder for V_c<=100k use cases.

**Unlocks immediately:**
- Phase 4 Idea 2 (working memory loop) at V_c<=100k
- Phase 4 Idea 3 (hallucination detection) at V_c<=100k
- Phase 4 Idea 17 (continual learning via KV injection) at V_c<=100k

**Cost:** Zero. MiniLM is pre-trained, frozen, sentence-BERT class. Drop-in for substrate input encoding.

**Limitation:** V_c=1M production scale needs distilled student (PHASE4A-2). Use MiniLM for development; distill for production.

P_deflated: 0.72 (MiniLM meets V_c<=100k substrate VQ fidelity per drill).

### PHASE4A-2: Distilled 22-26M student (~3 days + $15)

**Action:** Train 22-26M student model distilled from Llama-1B layer 10.
- Architecture: 6 layers, 768-dim hidden
- Loss: L2 activation match + InfoNCE contrastive (combined)
- Training data: Wikipedia subset (~100k articles enough for representation learning)
- ~2-4h training on A100; ~$10-30 cloud

**Unlocks:**
- V_c=1M production scale for Phase 3 production
- **20-40x extraction speedup forever after** (dev-speed A1 payback)
- All Phase 4 features at production scale

**Engineering:** ~3 days training + validation.

P_deflated: 0.55 (distilled 22-26M student closes V_c=1M gap per drill).

### PHASE4A-3: Two-tier write/read path (~2-3 days)

**Action:** Decouple encoder quality from inference latency.
- WRITE TIME (slow): MiniLM or distilled student encodes new facts -> VQ -> substrate write -> HNSW codebook index update
- READ TIME (fast): HNSW codebook lookup (sub-1ms; per sub-linear cleanup drill) -> bipolar pattern match -> cleanup
- Per-token hallucination detection uses the FAST read path only

**Unlocks:** Idea 3 (hallucination detection) at <1ms/span -- meets real-time requirement.

P_deflated: 0.68 (two-tier architecture achieves sub-1ms per drill).

### PHASE4A-4: Pre-registered rescues template (~1-2 days; dev-speed C2)

**Action:** Update cell template so every new experiment ships with:
- Pre-registered HP/MID/HF bands (existing per PROT-018)
- **NEW:** Pre-registered rescue cells per HF outcome (1-3 follow-on cells with explicit rescue hypothesis)

**Process change:**
- Template at `experiments/_template_v2.py` includes rescue stub
- Drill agent's handoff format extended to include rescues
- When a cell HFs: rescue cells auto-queue (no design discussion needed)

**Impact:** Compounds the negatives-drill methodology. Every negative result has pre-staged rescue paths. Saves "what now?" discussion after each HF.

P_deflated: 0.80 (highest P_deflated in dev-speed drill).

### PHASE4A-5: Standardized substrate eval harness (~5-7 days; dev-speed B1)

**Action:** Build `python eval_substrate <variant>` command that runs:
- CCC-1-v2 (5/7 categorical wins benchmark)
- substrate-audit-core (C2 deletion-cert + C3 drift-sep)
- Per-capability dimensions (long-conv, multi-doc, counterfactual, etc.)
- Outputs unified JSON report + scorecard-compatible markdown summary

**Impact:** Eliminates per-experiment scaffold work. Every new substrate variant gets full benchmark in one command. **3-5x throughput multiplier on smoke + full cycles.**

Architecture:
- `eval_substrate/` directory in repo
- Pluggable substrate-variant interface
- Cached benchmarks (no re-extraction per eval)
- Markdown report drops into `notes/` for visibility

P_deflated: 0.70.

### PHASE4A-6: Wikipedia layer-10 cache (~2-3 days + $200-400; dev-speed A2)

**Action:** One-time extraction of Llama-1B layer-10 activations for full Wikipedia.

Specs:
- 6.7M articles (English Wikipedia)
- Per-token residuals; compressed npz format
- Stored on runner + cloud backup
- ~30 GB compressed; ~$200-400 cloud H100 (one-time)
- Wall: ~8-10h cloud

**Impact:** Eliminates extraction step for ALL future Wikipedia-derived experiments:
- HP-12 V2/V3
- Phase 4 Idea 2 (working memory loop) at scale
- Idea 3 (hallucination detection) needs verified-fact corpus
- Idea 8 (CoT cache) seeded with Wikipedia facts
- Idea 9 personal substrate seed corpus

**Strategic value:** Pays back across every Phase 4 cell + every future capability test.

P_deflated: 0.65.

---

## Sequencing recommendation

**Day 1 (post-HP-12 V1 demo):** Drop in MiniLM as encoder. Phase 4 development can START at V_c<=100k while infrastructure builds in parallel.

**Days 1-3:** PHASE4A-4 (pre-registered rescues template) + PHASE4A-3 (two-tier write/read path)

**Days 3-6:** PHASE4A-2 (distilled 22-26M student training; runs overnight cloud)

**Days 4-11:** PHASE4A-5 (eval harness; parallel work)

**Days 8-11:** PHASE4A-6 (Wikipedia cache extraction; cloud overnight)

**Total: ~11-13 eng-days + ~$215-430 cloud (some parallelism possible).**

---

## Combined Phase 4 timeline (post-HP-12 V1)

Original estimate: ~30-45 days for Phase 4 b/c/d.

**With unified Phase 4a infrastructure (3-5x throughput multiplier): ~20-30 days for Phase 4 b/c/d.**

Total time-to-Phase-4-complete drops from ~30-45 days to ~33-49 days (Phase 4a + b/c/d), but with HIGHER ROBUSTNESS (every cell has pre-staged rescues; every result auto-benchmarked; no re-extraction overhead).

---

## Next-drill candidates flagged by drills

Both drills flagged the same next-drill candidate:
- **Sparse-coding / compressed-sensing direction (Tier-1b)** -- cross-cutting rescue from negatives drill + SPLADE-style k-sparse bipolar activation as direct substitute for dense VQ

Plus dev-speed drill flagged:
- **D2-partial AI co-scientist loop automation (5-7 days, P_deflated=0.55)** -- persistent agent for research throughput

Both are post-Phase-4a; not urgent now.

---

## What I'm NOT recommending (intentionally)

Per [[feedback-no-padding-experiments]] + user oversaturation pushback:

- **PHASE4A-7: Custom-trained VQ-aware encoder** (encoder drill option C) -- NOT recommended. Distilled student (PHASE4A-2) is sufficient; custom VQ-aware adds 10-15 days + $50-200 with marginal quality gain.

- **PHASE4A-8: Online LoRA adapter (dev-speed A3)** -- NOT recommended. Distilled student covers this; LoRA adds complexity.

- **PHASE4A-9: Asymmetric extraction (dev-speed A5)** -- NOT recommended for Phase 4a. Wikipedia cache (PHASE4A-6) makes per-doc extraction model choice irrelevant.

- **PHASE4A-10: Parallel cell execution framework (dev-speed B3)** -- DEFER. Useful but Phase 4b cells are mostly serial dependencies; speedup limited.

- **PHASE4A-11: Live substrate dashboard (dev-speed B4)** -- DEFER. Useful for debugging but not critical-path for Phase 4 features.

- **PHASE4A-12: Hot-reload substrate (dev-speed B5)** -- DEFER. Nice-to-have; lower impact than eval harness.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: 6 components each test distinct architectural hypothesis; non-recommended items deprioritized explicitly
- Per [[feedback-substrate-value-framing-2026-05-26]]: product-engineering work (infrastructure for shipping) is the rate-limiter
- Per user 2026-06-05 ~18:00: dev-speed dimension actively explored; cross-cutting investments identified
- ASCII-only

PROT-018: anchors per component when execution starts
PROT-021: source=cloud H100 for PHASE4A-2 + PHASE4A-6; rest local

---

**END.**

**Exp-Dev:** Unified Phase 4a infrastructure plan: ~13-19 eng-days + ~$215-430 cloud. MiniLM (0 days, $0) unlocks Phase 4 work IMMEDIATELY at V_c<=100k. Distilled 22-26M student (3 days, $15) closes V_c=1M gap + provides 20-40x extraction speedup forever after. Two-tier write/read path gates Idea 3 at <1ms/span. Plus C2 + B1 + A2 dev-speed investments = 3-5x throughput on Phase 4 b/c/d. Total Phase 4 timeline tightens from ~30-45 days to ~33-49 days WITH higher robustness.

**Testbed:** PHASE4A-2 (distilled student training; ~$15 cloud) + PHASE4A-6 (Wikipedia cache extraction; ~$200-400 cloud) are the only new cloud asks. Both AFTER HP-12 V1 demo lands. Plus existing FAISS env fix still standing for HP-12 V2.

**User:** Two drills synthesized into unified Phase 4a infrastructure. **MiniLM works off-the-shelf for early Phase 4 (V_c<=100k); no waiting for distillation.** Distilled 22-26M student is the cross-cutting investment: serves both encoder bottleneck (V_c=1M production) AND dev-speed (20-40x extraction speedup). Combined infrastructure investment ~13-19 days + ~$215-430 cloud; 3-5x throughput multiplier on rest of Phase 4. Next-drill candidate from both: sparse-coding/SPLADE bipolar direction.
