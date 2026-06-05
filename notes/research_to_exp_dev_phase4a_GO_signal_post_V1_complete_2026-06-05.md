# Research -> Exp-Dev: GO SIGNAL -- Phase 4a starts NOW; HP-12 V1 software COMPLETE acknowledged

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~19:45
**Subject:** GO signal per Exp-Dev's 16:50 question. HP-12 V1 software deliverables all HARD_PASS (acknowledged). 5-min screen recording is user's task (independent of Exp-Dev). Phase 4a infrastructure work starts NOW. Plus 17 flagship anchors (added HP-12 frontier-contrast + V2-1 + V2-4).

---

## HP-12 V1 software COMPLETE -- acknowledged

All deliverables HARD_PASS:
- cert issuance 0.058ms at RSA-512 (was 3.46ms pure-Python; gmpy2 16-60x speedup)
- e2e backend: 0 phantom, retention 1.0
- HIPAA API: 4 endpoints all e2e; certs third-party-verified
- **Frontier-LLM contrast: post-deletion residual 0% vs ROME 38% / MEMIT 29%** (peer-reviewed published anchors)

**Anchors locked into scorecard:**
- 17th flagship: HP-12 V1 cert latency 0.058ms (sub-1ms HP gate met)
- 18th flagship: HP-12 V1 frontier-contrast 0% vs ROME 38% / MEMIT 29% (the categorical claim empirically anchored)
- 19th flagship: V2-1 theta-burst-endpoint HP (+44pp multi-step; recovers from earlier HF)
- 20th flagship: V2-4 kgram-XOR scaling HP (k=3 reaches trigram-class at N=4096; Phase 3 scaling validated)

Plus V2-2 MIDDLE in scorecard (Hadamard 2.8x; matches band).

5-minute screen recording is User's manual task -- independent of Exp-Dev queue. Backend + API + verifier + contrast all ready to drive it.

---

## GO SIGNAL: Phase 4a infrastructure starts NOW

Per unified Phase 4a routing earlier (~19:30), 6 components in priority order:

### Priority 1 (do first; quick wins)

**PHASE4A-4: Pre-registered rescues template (~1-2 days; P_deflated 0.80)**
- Update `experiments/_template_v2.py` to include rescue-cell stub
- Extend drill-handoff format to include pre-registered rescue paths
- When future cells HF, rescue cells auto-queue
- Compounds the negatives-drill methodology

**PHASE4A-3: Two-tier write/read path (~2-3 days)**
- Slow encoder at write time
- HNSW codebook lookup at read time
- Sub-1ms hallucination detection gate
- Reuses HP-12 V1 substrate + accumulator infrastructure

### Priority 2 (do in parallel)

**PHASE4A-1: MiniLM immediate encoder (0 eng-days, $0)**
- Drop in `sentence-transformers/all-MiniLM-L6-v2` (22M params; 384-dim)
- TESTBED ENV ASK: `pip install sentence-transformers` (likely already-cached on some systems)
- Then immediately enables Phase 4 work at V_c<=100k

**PHASE4A-5: Standardized substrate eval harness (~5-7 days)**
- `python eval_substrate <variant>` -> CCC-1-v2 + audit-core + capability dims
- Eliminates per-experiment scaffold work
- 3-5x throughput multiplier on Phase 4 b/c/d

### Priority 3 (background; one-time investment)

**PHASE4A-2: Distilled 22-26M student (~3 days + $15)**
- Train 6-layer 768-dim student distilled from Llama-1B layer 10
- L2 activation match + InfoNCE contrastive loss
- Wikipedia subset training data (~100k articles)
- **TESTBED CLOUD ASK: ~$15 cloud H100 training run (~2-4h)**
- Unlocks V_c=1M production scale + 20-40x extraction speedup forever after

**PHASE4A-6: Wikipedia layer-10 cache (~2-3 days + $200-400)**
- One-time extraction of Llama-1B layer-10 (or distilled-student) activations for full English Wikipedia
- ~6.7M articles; ~30 GB compressed npz
- **TESTBED CLOUD ASK: ~$200-400 cloud H100 (~8-10h overnight)**
- Eliminates extraction step forever for Wikipedia-derived experiments

---

## Testbed asks for Phase 4a

1. **`pip install sentence-transformers`** in runner .venv (~5 min) — gates PHASE4A-1 MiniLM
2. **PHASE4A-2 distilled student training** (~$15 cloud H100; ~2-4h wall) — after design landed; can dispatch when Exp-Dev hands off training script
3. **PHASE4A-6 Wikipedia cache extraction** (~$200-400 cloud H100; ~8-10h overnight) — after Day 6-7 of Phase 4a; not urgent

Plus standing items (not urgent):
- FAISS HNSW env fix (gates HP-12 V2 1M-fact scale)
- Llama-1B weights local (optional; for V2-3 HotpotQA + Test 3 live extraction speed)

---

## Other items Exp-Dev can pull into queue

### HP-5 medical Q&A proto (data already delivered; ~1-2 days)
- substrate-VQ on PubMed corpus (10K abstracts shipped)
- MedQA evaluation (500 USMLE Q shipped)
- Substrate-cognitive-core vs raw Pythia/Llama-1B baseline
- HP threshold: substrate >= 1.5x Pythia baseline AND deletion-cert operational
- **Dry run for HIPAA Medical Path Y** when UMLS license lands

### V2-3 HotpotQA-1B (if Testbed pulls Llama weights)
- Decisive test for Finding C (substrate multi-hop EM ceiling -- decoder bottleneck or substrate-side bound?)
- HP threshold: EM > 0.12 at Llama-1B (vs 0.083 floor at Pythia)
- ~30-60 min GPU once weights local
- Not blocking but high-value (resolves HotpotQA architectural question)

### HP-12 V2 build (when FAISS env fixed)
- Scale HP-12 demo from V1 (10K + 50 facts) to V2 (100K + 500 facts)
- Uses sparse FAISS-HNSW for cleanup (sub-linear retrieval drill recommendation)
- Production-credibility scale for HIPAA pitch
- ~2-3 days once FAISS env works

---

## Updated capability scorecard implications (20 flagship anchors)

| Anchor | Status |
|---|---|
| 1-13 | Prior flagship anchors |
| 14 | Tier-4-Llama 1B HP (cross-scale architectural primitive) |
| 15 | HP-12 V1 core HP at smoke (substrate + RSA accumulator) |
| 16 | HP-9 multimodal HP (16th anchor) |
| **17** | **HP-12 V1 cert latency 0.058ms (gmpy2; sub-1ms HP gate met)** |
| **18** | **HP-12 V1 frontier-contrast: 0% post-deletion residual vs ROME 38% / MEMIT 29% (categorical claim empirically anchored)** |
| **19** | **V2-1 theta-burst-endpoint HP (+44pp multi-step; rescues earlier HF)** |
| **20** | **V2-4 kgram-XOR scaling HP (k=3 trigram-class at N=4096; Phase 3 scaling validated)** |

20 flagship anchors after today.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per user 2026-06-05 ~18:00: explore all 20 ambitious ideas eventually; Phase 4 sequencing locked
- Per Exp-Dev 16:50: GO signal granted; Phase 4a starts NOW
- Per [[feedback-substrate-value-framing-2026-05-26]]: product-engineering work weighted higher; Phase 4a IS the product infrastructure
- ASCII-only

PROT-018: anchors per cell when execution starts
PROT-021: source=cloud H100 for PHASE4A-2 + PHASE4A-6; rest local CPU

---

**END.**

**Exp-Dev:** **GO signal granted.** Phase 4a starts NOW. Priority order: PHASE4A-4 + PHASE4A-3 (quick wins); PHASE4A-1 + PHASE4A-5 (in parallel); PHASE4A-2 + PHASE4A-6 (background cloud one-time investments). Plus HP-5 medical Q&A (data delivered; ~1-2 days) is a clean parallel cell. V2-3 HotpotQA-1B unblocks if Testbed pulls Llama weights. HP-12 V2 build awaits FAISS env fix. 17-20th flagship anchors locked from your HP-12 V1 + SPARSE-V2 work.

**Testbed:** Three new asks for Phase 4a: (1) `pip install sentence-transformers` in runner .venv (~5 min); (2) PHASE4A-2 distilled-student training (~$15 cloud H100; ~2-4h wall; after Exp-Dev hands off training script); (3) PHASE4A-6 Wikipedia layer-10 cache extraction (~$200-400 cloud H100; ~8-10h overnight; Day 6-7 of Phase 4a). Plus standing items (FAISS env fix; optional Llama weights).

**User:** HP-12 V1 software COMPLETE acknowledged (20 flagship anchors now; cert 0.058ms; frontier-contrast 0% vs ROME 38%/MEMIT 29%). **5-min screen recording is your manual task** (record at your leisure; doesn't block Exp-Dev). **Phase 4a infrastructure STARTS NOW per Exp-Dev's GO question.** 6 components routed; combined ~13-19 eng-days + ~$215-430 cloud. 3-5x throughput multiplier on rest of Phase 4. Plus HP-5 medical Q&A is staged for parallel build (data delivered).
