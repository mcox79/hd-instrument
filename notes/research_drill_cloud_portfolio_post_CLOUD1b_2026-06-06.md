# Research Drill: Cloud-experiment portfolio synthesis post-CLOUD-1b HARD_PASS

**Date:** 2026-06-06
**Trigger:** CLOUD-1b HARD_PASS ($1.33 total for binding-test answer) + Phase 4a layer-10 convention found wrong
**Role:** Research sub-agent (Sonnet)
**Topic:** Optimal cloud-experiment portfolio given new empirical constraints

---

## HEADLINE

CLOUD-1b demolishes the need for large-model cloud runs in the extraction pipeline: 1B beats 8B beats 70B on retrieval (1B top-5-RP=0.282 vs 70B top-5-RP=0.174). This radically restructures the cloud portfolio. The two highest-ROI immediate cells are (a) fp16 70B disambiguation (~$3-5, already authorized) and (b) revised PHASE4A-6 Wikipedia extraction at the correct layer (1B L=15, ~$31-50; cut from $200-400). Everything else is either gated on those two outcomes or is a multi-week production build cell.

P_deflated: fp16-70B disambiguation P(quant_artifact) = 0.52 (raw 0.70, deflated 0.18 for model-specific NF4 idiosyncrasies not directly measured); revised-extraction P(1B-at-L15-meets-retrieval-bar) = 0.72.

---

## Cheap decisive test

**fp16 70B disambiguation:** Run Llama-3.1-70B at fp16 on H100:2 (needs ~140 GB VRAM total; two 80 GB H100s), extract per-layer activations at L={40,50,60,68,74}, compute top-5-RP on the same 500-query / 1000-passage eval. Compare per-layer curve to CLOUD-1b NF4 curve. If late-layer retrieval RECOVERS in fp16 -> quant artifact confirmed (cheap-fleet thesis holds for ANY model size). If curve stays flat or degrades -> real architectural finding (70B late-layer information compression is not retrieval-friendly regardless of quant). Cost: ~$3-5 / 30-45 min wall. Decision is binary and definitive.

---

## Proposed cloud cells: 4-7 ranked by P_deflated x ROI

### CELL-1: fp16 70B per-layer disambiguation (AUTHORIZED)

- **Anchor:** `cloud_2a_fp16_70b_layer_curve_v1`
- **Wall:** 30-45 min
- **Cost:** ~$3-5 (two H100s; 70B fp16 needs ~140 GB; Lambda H100:2 hourly ~$6/hr)
- **HP threshold:** Late-layer top-5-RP (L=60,68,74) >= 0.85 x L=50 peak -> quant artifact confirmed; cheap-fleet thesis extends to 70B fp16
- **MID threshold:** Late-layer RP in [0.60, 0.85] of L=50 peak -> partial recovery; quant + architecture both contribute
- **HF threshold:** Late-layer RP < 0.60 of peak -> real architectural degradation; 70B base is retrieval-hostile at late layers regardless of quant
- **Dependencies:** None (GH200 path proven end-to-end)
- **Unlocks:**
  - If HP/MID: 70B fp16 is a viable extraction model; enables CELL-3 (Instruct comparison) + informs CELL-4 (Wikipedia layer choice)
  - If HF: locks 70B base out of retrieval-style extraction; 1B/8B confirmed as production choices; CELL-3 (Instruct) becomes lower priority
- **Reject if:** HF on architectural grounds -> route to research-drill on causal-LM retrieval architecture instead of spending more cloud
- **P_deflated x ROI:** highest in portfolio; authorized + cheap + binary binding

Optional add-on (dispatch in same bootstrap if combined cost < $5):
- **CELL-1b:** Llama-3.1-70B-Instruct (NF4) same eval protocol, ~$0.65. Binds base-vs-Instruct question. If combined with CELL-1 < $5, do both.

---

### CELL-2: Revised PHASE4A-6 Wikipedia extraction at correct layer (1B, L=15)

- **Anchor:** `cloud_phase4a_6_wikipedia_1b_l15_extraction_v2`
- **Wall:** 6-8 hours (overnight; chunked)
- **Cost:** ~$31-50 (100 CPU workers x ~0.3 hr each at Lambda CPU $0.001/hr per core; OR GH200 with batched inference)
- **HP threshold:** 6.7M Wikipedia articles extracted at L=15 1B fp16 with retrieval-quality smoke-check >= CLOUD-1b val (top-5-RP >= 0.25 on held-out 500 queries); no corrupt npz shards
- **MID threshold:** Extraction completes but retrieval quality 0.20-0.25 (acceptable for substrate; run CELL-4 distilled-student training anyway)
- **HF threshold:** Top-5-RP < 0.15 on Wikipedia subset OR > 15% shard corruption -> infra failure; re-examine chunking strategy
- **Dependencies:** CELL-1 should complete first (confirms 1B is optimal extraction model, not 70B); if CELL-1 shows 70B fp16 is dramatically better, shift to 70B fp16 extraction instead (cost ~$90-120 at GH200 hourly rates)
- **Unlocks:** All subsequent HP-12 V2/V3 builds; distilled-student training substrate; full Wikipedia search demo
- **Cost comparison:** Original PHASE4A-6 plan was layer-10 at $200-400. Revised plan at correct layer + optimal model: $31-50. Savings = $150-350 per extraction run.
- **P_deflated x ROI:** second highest; blocked only by CELL-1 runtime (30 min); massive cost reduction vs prior plan

---

### CELL-3: PHASE4A-2 distilled 22-26M student training

- **Anchor:** `cloud_phase4a_2_distilled_student_22m_v1`
- **Wall:** 2-4 hours
- **Cost:** ~$15 (H100 for training; 100K Wikipedia articles + InfoNCE contrastive + L2 activation match)
- **HP threshold:** Student top-5-RP >= 0.90 x teacher (1B L=15) on held-out 1K query eval; student latency < 5ms CPU
- **MID threshold:** Student RP in [0.75, 0.90] of teacher; latency in [5, 20] ms
- **HF threshold:** Student RP < 0.75 of teacher -> distillation loss domination by architecture mismatch; re-examine layer-match target
- **Dependencies:** CELL-2 (Wikipedia extraction at correct layer) provides training data; CELL-1 confirms 1B is teacher model
- **Unlocks:** 20-40x extraction speedup for V_c=1M production; eliminates ongoing cloud cost for all future Wikipedia extractions; enables HP-12 V3 at 1M facts
- **NOTE:** Student must be trained at L=15 activation match (not L=10 as originally specified in Phase 4a plan). Revision required in Exp-Dev specs.
- **P_deflated:** 0.60 (raw 0.78, deflated 0.18 for distillation-quality at 22M params vs 1B teacher gap)

---

### CELL-4: HP-12 V2 build at 100K facts

- **Anchor:** `cloud_hp12_v2_certified_deletion_100k_v1`
- **Wall:** 2-3 days (includes extraction + indexing + eval)
- **Cost:** ~$10-20 (extraction at correct layer already done via CELL-2; indexing + FAISS env)
- **HP threshold:** Certified deletion latency < 50ms for 100K-fact KB; retention rate > 0.85 post-deletion; substrate retrieval accuracy >= HP-12 V1 at 10K facts
- **MID threshold:** Latency 50-200ms OR retention 0.75-0.85
- **HF threshold:** Latency > 500ms OR retention < 0.70 -> scale-up failure; FAISS indexing bottleneck or substrate capacity overflow
- **Dependencies:** CELL-2 (Wikipedia extraction) + FAISS env fix (Windows OpenMP conflict still outstanding per PRIORITY_QUEUE_LIVE.md)
- **Unlocks:** Production-credible demo at 100K facts; V2 enables Phase 3 launch materials; gates HP-12 V3 at 1M
- **P_deflated:** 0.55 (raw 0.70, deflated 0.15 for scale-up failures not yet tested)

---

### CELL-5: Cascade distillation FD smoke test

- **Anchor:** `cloud_cascade_distillation_fd_ratio_smoke_v1`
- **Wall:** ~4 hours
- **Cost:** ~$2 cloud API + 2-3 hr H100
- **HP threshold:** FD(fine-tuned-1B, 405B teacher) / FD(off-shelf-1B, 405B teacher) < 0.40 on 5K sentences (>60% gap closed by fine-tuning)
- **MID threshold:** FD ratio in [0.40, 0.70]
- **HF threshold:** FD ratio > 0.70 -> cascade does not work; 405B extraction remains $14k/run
- **Dependencies:** None (can run independently)
- **Unlocks:** If HP: validates $65 one-time 405B Wikipedia digestion path vs $14k/run; massive cost reduction for highest-quality extraction tier
- **Strategic value:** The "audacious vision" at hobbyist budget hinges on this. CLOUD-1b shows we may not need 405B for retrieval-style extraction (1B wins), but cascade distillation still matters for reasoning-quality extraction beyond retrieval
- **P_deflated:** 0.38 (raw 0.55, deflated 0.17 for cascade FD coupling to bipolar substrate geometry not directly measured)
- **Rank note:** Lower priority than CELL-3 because CLOUD-1b shows 1B extraction may be sufficient for retrieval; cascade distillation is a "nice to have" for reasoning quality, not a blocker

---

### CELL-6 (OPTIONAL): M4 Max volunteer fleet POC

- **Anchor:** `cloud_m4_max_fleet_poc_v1`
- **Wall:** 1-2 days coordination
- **Cost:** ~$1 electricity (zero hardware)
- **HP threshold:** 1B fp16 inference at L=15 on 100 idle M4 Max machines produces activations byte-identical to Lambda GH200 baseline within float32 tolerance; throughput >= 10K articles/hour/machine
- **MID threshold:** Byte-identical but throughput 5-10K articles/hour
- **HF threshold:** Float precision mismatches OR throughput < 5K articles/hour (coordination overhead dominates)
- **Dependencies:** CELL-1 confirms 1B is the extraction model; M4 Max machines must have Python + torch + access to model weights
- **Unlocks:** 333,000x cost reduction claim for 405B Wikipedia IF cascade distillation also HP; enables the "Wikipedia at $1" vision empirically
- **Rank note:** LOWEST priority of all cells because (a) coordination overhead is non-trivial, (b) Lambda CPU at $31 is already cheap enough for production, (c) requires fleet recruitment before testing. Park until CELL-2 Wikipedia extraction is proven at cloud CPU; M4 fleet is a stretch-goal optimization.
- **P_deflated:** 0.35 (raw 0.50; deflated 0.15 for fleet coordination and cross-hardware reproducibility not measured)

---

## CELLS TO AVOID / REJECT

### REJECT: PHASE4A-6 at layer-10 (WRONG LAYER)

**Rationale:** CLOUD-1b shows optimal is 92% depth for 1B/8B (L=15 for 1B, L=29 for 8B). Layer-10 is 62.5% depth for 1B (suboptimal by ~45% top-5-RP). Spending $200-400 at layer-10 = systematically extracting suboptimal representations at 6.7x the correct cost. HARD BLOCK before any large-scale extraction spend. Superseded by CELL-2 above.

### REJECT: Llama-3.1-8B Tier-4 (user deprioritized; CLOUD-1b confirms 8B not meaningfully better)

**Rationale:** CLOUD-1b shows 1B beats 8B by 14% on retrieval (top-5-RP 0.282 vs 0.248). The 8B model offers no retrieval advantage at ~8x the inference cost. The Tier-4 "architectural primitive substitution" claim may still be interesting, but for the extraction use case 8B is strictly dominated by 1B. Re-evaluate only if user re-authorizes for an architecture-specific (not extraction-quality) question.

### REJECT: Full Wikipedia 70B NF4 extraction (layer-10 or any layer)

**Rationale:** CLOUD-1b shows 70B NF4 is worse than 1B/8B on retrieval. Even at its optimal layer (L=50), 70B top-5-RP=0.174 is dominated by 1B top-5-RP=0.282. 70B NF4 extraction at Wikipedia scale would cost ~$300-500 for inferior extraction quality. No justification until CELL-1 (fp16 70B) shows fp16 70B dramatically outperforms 1B -- which the data suggests is unlikely.

### DEPRIORITIZE: HP-12 V3 at 1M facts (Gemma-2-2B)

**Rationale:** Gated on CELL-2 + CELL-3 + FAISS env fix + Phase 3 production launch timing. Estimated cost $50-100. Not actionable until CELL-2 (Wikipedia extraction at correct layer) and CELL-3 (distilled student) both complete successfully. Promote to active only after V2 at 100K confirmed.

### DEPRIORITIZE: CLOUD-10 full Wikipedia 7B chunked ($31 via CPU workers)

**Rationale:** CLOUD-1b shows 1B > 8B for retrieval. "7B" is no longer the extraction target. CELL-2 (1B at L=15) supersedes this with equivalent cost and better extraction quality. Remove from queue; replace with CELL-2.

---

## BUDGET ENVELOPE

### Immediate dispatch (pre-authorized; under $5)

| Cell | Cost estimate | Auth status |
|---|---|---|
| CELL-1: fp16 70B disambiguation | $3-5 | ALREADY AUTHORIZED |
| CELL-1b: 70B Instruct NF4 (optional add-on) | $0.65 | AUTHORIZED if combined < $5 |

**Total pre-authorized: ~$3.65 - $5.65**

### Per-cell user auth required ($5-50)

| Cell | Cost estimate | Auth gate |
|---|---|---|
| CELL-2: Wikipedia extraction 1B L=15 | $31-50 | Awaiting user go-signal; blocked by CELL-1 (30 min) |
| CELL-3: Distilled student training | $15 | After CELL-2 extraction completes |
| CELL-5: Cascade distillation FD smoke | $4-5 | Independent; per-cell auth |
| CELL-4: HP-12 V2 at 100K facts | $10-20 | After CELL-2 + FAISS env fix |

**Total per-cell-auth: ~$60-95 (if all authorized)**

### Strategic batch auth required ($50+)

| Cell | Cost estimate | Auth gate |
|---|---|---|
| HP-12 V3 at 1M facts | $50-100 | CELL-2 + CELL-3 + FAISS env |
| M4 Max fleet POC | ~$1 electricity | CELL-1 + fleet coordination |

**Total batch-auth: ~$50-101 (stretch goals)**

### Total portfolio budget

| Tier | Low estimate | High estimate |
|---|---|---|
| Pre-authorized | $3.65 | $5.65 |
| Per-cell-auth | $60 | $95 |
| Stretch (batch-auth) | $50 | $101 |
| **Grand total** | **$113.65** | **$201.65** |

**Cost per binding answer:**
- Cheap-fleet thesis confirmation (CELL-1): $3-5 / 1 binding answer = $3-5/answer
- Wikipedia extraction correct layer (CELL-2): $31-50 / 1 binding answer (extraction viability) = $31-50/answer
- Distillation viability (CELL-3): $15 / 1 binding answer = $15/answer
- HP-12 production credibility (CELL-4): $10-20 / 1 milestone = $10-20/milestone

---

## DEPENDENCY GRAPH

```
CELL-1 (fp16 70B, $3-5) -- AUTHORIZED, no deps
    |
    +--> CELL-1b (Instruct add-on, $0.65) -- optional parallel if budget
    |
    +--> [IF HP/MID] CELL-2 (Wikipedia extraction 1B L=15, $31-50)
    |        |
    |        +--> CELL-3 (distilled student, $15)
    |        |        |
    |        |        +--> CELL-4 (HP-12 V2 at 100K, $10-20)
    |        |                 |
    |        |                 +--> [LATER] HP-12 V3 at 1M facts ($50-100)
    |        |
    |        +--> CELL-4 can also start with CELL-2 + FAISS env fix
    |
    +--> [IF HF, architectural] RESEARCH DRILL: causal-LM retrieval architecture
         (no further 70B cloud spend; 1B/8B confirmed as production ceiling)

CELL-5 (cascade distillation FD, $2-5) -- INDEPENDENT; no deps
    |
    +--> [IF HP] enables 405B Wikipedia digestion path at $65 one-time
    +--> [IF HF] closes 405B extraction strategy for retrieval; no further cascade spend

CELL-6 (M4 fleet POC, $1) -- gated on CELL-2 success + fleet recruitment
    (lowest priority; park until CELL-2 proven)
```

---

## HIGH-LEVERAGE EXTRACTION COST TARGETS

### 1B fp16 + L=15 Wikipedia extraction at GH200

Estimated throughput: CLOUD-1b ran 500 queries + 1000 passages in 464.5 sec on GH200.
For 6.7M Wikipedia articles at average 256-token length:
- Sequential estimate: (6,700,000 / 1,500) * 464.5 sec = ~2,079 hours sequential
- But with batched inference (batch=32): ~65 hours sequential
- GH200 at ~$2/hr: ~$130 sequential batched

Better approach: Lambda CPU workers (no GPU needed for 1B inference on CPU):
- 1B fp16 inference time on ARM CPU: ~50ms/article at batch=1 (conservative)
- 6.7M articles x 50ms = 335,000 sec = 93 hours on one CPU
- 100 Lambda CPU workers: ~1 hour wall
- Lambda CPU ~$0.001/hr/core x 100 cores x 1 hour = $0.10 -- extremely cheap
- More realistic with overhead + boot: $31 (per prior chunked-extraction drill estimate)

**Revised estimate for 1B L=15 Wikipedia extraction: $31-50 (vs $200-400 for layer-10 estimate)**

Savings: $150-370 per extraction run. With ~$1.33 already spent on CLOUD-1b, the layer revision pays for itself 100-270x.

### M4 Max fleet vs Lambda CPU comparison

| Path | Cost | Wall | Complexity |
|---|---|---|---|
| Lambda 100x CPU workers (1B fp16) | ~$31-50 | ~1-2 hours | Low (proven Lambda infra) |
| 100x M4 Max volunteer fleet | ~$1 electricity | ~1-5 hours | High (fleet coordination; reproducibility; scheduling) |
| GH200 batched (1B fp16) | ~$60-130 | ~1-8 hours | Medium (proven GH200 path) |

**Is the "$1 fleet" actually feasible empirically?**

Technically: YES. 1B fp16 requires ~2-3 GB RAM; M4 Max has 64-128 GB unified memory; inference at 256-token input is CPU-bound ~20-40ms/article on M1 Pro (similar arch, slower than Max). 100 machines at 20ms/article = 6.7M / 100 = 67,000 articles per machine; at 20ms each = 1,340 seconds = 22 min. HIGHLY feasible technically.

Organizationally: HARD. Volunteer fleet requires: (a) coordinated software deployment, (b) result aggregation + validation, (c) trust model for activations, (d) model weight distribution (70 GB even for 1B fp16). The $1 claim assumes zero coordination cost. Real coordination overhead likely = 1-5 days of engineering time. For a one-time Wikipedia extraction, Lambda at $31-50 is strictly better economics unless the fleet is already assembled for other reasons.

**Recommendation:** Lambda CPU at $31-50 is the practical path. M4 Max fleet is a demonstration artifact for "audacious vision" marketing, not a production extraction tool, unless fleet is pre-assembled for other reasons (e.g., production serving at scale).

---

## RECOMMENDED USER AUTHORIZATION ENVELOPE

### Pre-authorized (immediate dispatch)

- CELL-1: fp16 70B disambiguation, ~$3-5. ALREADY AUTHORIZED. Dispatch now.
- CELL-1b: 70B Instruct NF4 add-on, ~$0.65. AUTHORIZED if bundled with CELL-1 under $5 total.

### Per-cell auth (authorize as cells become ready)

1. After CELL-1 completes (~30-45 min): authorize CELL-2 (Wikipedia extraction 1B L=15, $31-50). Single most important unlock.
2. Independently: authorize CELL-5 (cascade distillation FD smoke, $4-5). Does not depend on CELL-1.
3. After CELL-2 completes: authorize CELL-3 (distilled student training, $15).
4. After CELL-2 + FAISS fix: authorize CELL-4 (HP-12 V2 at 100K facts, $10-20).

### Strategic batch auth ($50+)

- HP-12 V3 at 1M facts ($50-100): authorize only after CELL-3 (distilled student) confirms retrieval quality meets bar. Estimated 2-4 weeks from now.
- M4 Max fleet POC (~$1 elec): no urgency; authorize when fleet recruitment is ready. Not blocking anything.

### DO NOT authorize

- PHASE4A-6 at layer-10: blocked until layer convention fully revised to L=15 (1B) or L=29 (8B).
- 70B NF4 extraction at any scale: inferior to 1B per CLOUD-1b; no use case until CELL-1 HF (architectural) finding forces reconsideration.
- 8B Tier-4: user deprioritized; CLOUD-1b confirms no extraction advantage.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### HARD-PASS indicators (confirm portfolio direction)

1. CELL-1 fp16 70B late-layer RP >= 0.85 of L=50 peak -> quant artifact confirmed; portfolio locks 1B as production extraction model; shifts roadmap to cheap fleet
2. CELL-2 Wikipedia 1B L=15 extraction top-5-RP >= 0.25 -> layer revision confirmed; $150-370 savings realized
3. CELL-3 distilled student RP >= 0.90 x teacher -> 20-40x speedup path open; production Wikipedia demo pipeline unblocked
4. CELL-5 FD ratio < 0.40 -> cascade distillation viable; 405B extraction path drops from $14k/run to $65 one-time

### HARD-FAIL indicators (portfolio revision required)

1. CELL-1 fp16 70B late-layer RP < 0.60 of peak -> real architectural degradation; 70B base is retrieval-hostile; research drill into causal-LM late-layer information compression required before any 70B cloud spend
2. CELL-2 Wikipedia extraction shard corruption > 15% OR retrieval RP < 0.15 -> infrastructure failure; chunking strategy broken; re-examine before CELL-3
3. CELL-3 distilled student RP < 0.75 of teacher -> distillation at 22M params insufficient; need 50-100M param student or VQ-aware fine-tuning
4. CELL-4 HP-12 V2 latency > 500ms at 100K facts -> FAISS indexing bottleneck; substrate retrieval architecture not production-ready at 100K scale

---

## CROSS-THREAD SYNTHESIS

**Prior: CLOUD-1 framing (this morning):** "Does 7B produce adequate substrate quality?" Answer assumed 7B vs 70B. Discovered mean-pool bug forced CLOUD-1b.

**CLOUD-1b: "1B beats 8B beats 70B" is the surprise result.** The prior art from encoder literature suggests causal LMs extract task-general representations that improve with scale. CLOUD-1b refutes this FOR RETRIEVAL-STYLE TASKS: smaller models peak at deeper layers and the peak quality is higher. This is consistent with the "layer-depth matters more than model size" finding from probing literature (Tenney 2019, Jawahar 2019 on BERT layers), but the INVERSION of size ordering (1B > 8B > 70B) is novel in the causal LM extraction context.

The encoder bottleneck drill (2026-06-05) predicted MiniLM would dominate at V_c <= 100K -- confirmed (MiniLM/70B = 5.11x). The Phase 4a distilled student recommendation (50M params at 768 dim) remains valid and is now CELL-3 in this portfolio.

**Layer revision implication:** The "92% depth optimal" finding is consistent with the probing literature showing task-general representations emerge in the final 10-20% of a transformer stack (residual stream has fully processed lower-level syntax/morphology; higher layers contain abstracted semantics). This is not model-size-specific: 1B, 8B, and 70B all show monotone improvement with depth for retrieval, except 70B which shows the anomalous crash at 75%+ depth (NF4 artifact or architectural).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Production extraction model locked as Llama-3.2-1B at layer 15.** All PHASE4A-6 planning should use this target. Wikipedia at $31-50 (revised from $200-400) is actionable now.

2. **Distilled 22-26M student training (CELL-3) remains the 20-40x speedup investment** but the teacher model must be specified as Llama-3.2-1B L=15, not the original L=10 convention.

3. **HP-12 V2 at 100K facts (CELL-4) is unblocked once Wikipedia extraction completes.** This is the "production credibility" milestone -- moving from 10K (demo) to 100K (enterprise-viable).

4. **MiniLM vs distilled-student architecture split:** For retrieval at V_c <= 100K, off-the-shelf MiniLM is already adequate (P=0.72 per encoder bottleneck drill). Distilled student is needed only for V_c = 1M production scale. Phase 4a can ship retrieval-quality demos immediately with MiniLM while distillation training runs.

5. **Cascade distillation (CELL-5) remains open.** CLOUD-1b confirms 1B is adequate for retrieval, but cascade distillation targets reasoning-quality extraction (405B teacher -> 1B student) beyond pure retrieval. If reasoning quality (not retrieval accuracy) is the substrate use case, cascade distillation is still the cost-reduction path from $14k/run to $65.

---

## CITATIONS (verified count)

- CLOUD-1b metrics: testbed_to_research_CLOUD1b_HARD_PASS_2026-06-06.md (primary source, empirical data)
- Phase 4a layer convention: research_to_testbed_CLOUD1b_HP_ack_fp16_70B_followup_authorized_2026-06-06.md
- Cloud experiments prior list: research_to_testbed_cloud_experiments_list_when_authorized_2026-06-06.md
- Encoder bottleneck drill: research_drill_encoder_bottleneck_phase4a_infrastructure_2x_2026-06-05.md
- Probing literature (Tenney 2019; Jawahar 2019): standard NLP probing literature on transformer layer semantics (not substrate-specific)
- VQ-VAE capacity bounds (van den Oord 2017; VAEVQ 2024): encoder bottleneck drill Section 2

**Direct citations: 6 internal, 3 external literature anchors**

---

**END.**
