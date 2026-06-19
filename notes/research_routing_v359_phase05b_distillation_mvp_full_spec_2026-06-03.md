# RESEARCH ROUTING — Phase 0.5b distillation MVP full testbed spec (with context-awareness additions)

**From:** Research session
**To:** Testbed / Orchestrator / exp_dev / user (Phase 0.5b GO gate)
**Date:** 2026-06-03
**Trigger:** User explicit ask — full Phase 0.5b spec incorporating context-awareness sub-cells (load-bearing for substrate's "third memory type" product narrative; not present in prior implicit sketch).
**Supersedes:** the implicit Phase 0.5b sketch in `research_routing_tier4_training_acceleration_FINAL_5drill_consolidation_2026-06-02.md` §1.Phase-0.5b. This file is the standalone testbed-ready spec; supersedes prior section as the dispatch reference.
**Status:** SPEC ONLY. Awaits user Phase 0.5b GO authorization. Also gated on Phase 0.5 v1+v2 verdict (per `research_routing_v359_drill_battery_synthesis_2026-06-03.md` §7).
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell-design parameters fully specified. Per-PROT compliance.

---

## 0. WHAT'S NEW VS PRIOR PHASE 0.5b SKETCH

| Aspect | Prior sketch | This spec |
|---|---|---|
| **Sub-cells** | 6 (distillation, recall, non-interference, MMLU, one-shot add, deletion cert) | **9** (prior 6 + 3 NEW context-awareness cells) |
| **Context-cost measurement** | not present | NEW Sub-cell G: tokens-per-query baseline vs substrate-augmented |
| **ICL replacement test** | not present | NEW Sub-cell H: substrate-loaded vs in-context-loaded few-shot |
| **Long-context regression** | not present | NEW Sub-cell I: 8K/16K/32K needle-in-haystack with substrate-augmented LLM |
| **Substrate primitive choices** | implicit PP-46 / PP-48 single-bank | PP-46 + PP-56 Sherman-Morrison dual; multi-bank B=4 option exposed; BBP audit observable available |
| **α regime** | implicit α=0.122 single-bank (88% of α_c) | explicit α budgeting: α=0.122 for primary distillation; multi-bank fallback to α=0.50 with α_per_bank=0.125 if single-bank near-capacity issues |
| **Drill-battery findings** | not integrated | All 5 product-narrative upgrades incorporated (Hebbian-vs-GD wall metric, ECC composition, κ_3 envelope 4.6× wider, BBP protocol, multi-bank capacity expansion) |

**Net delta:** 3 new sub-cells (G/H/I) for context-awareness; existing 6 cells lift to use the better substrate primitives validated yesterday.

---

## 1. EXPERIMENT OVERVIEW

**Goal:** empirically validate substrate-augmented Llama-3.1-8B as a production-class memory-augmented LLM that:
1. Stores 10K facts via Hebbian distillation (vs 1000+ GPU-hours of fine-tuning equivalent)
2. Preserves base LLM capability (MMLU, non-distilled-fact recall)
3. Operates audit primitives (deletion cert, BBP / κ_3 fingerprint) on the LLM-coupled substrate state
4. Achieves one-shot 100-fact addition in ≤1 minute at runtime
5. **Replaces context-window-stuffing with substrate retrieval (the load-bearing product-narrative test)**

**Architecture:**
- Base model: Llama-3.1-8B-Instruct via vLLM
- Substrate: N=8192 single-bank primary (α=0.122 from M=1000 distilled facts; well within α_c=0.138 per AGS); multi-bank B=4 fallback (α_per_bank=0.122 with M=4000 fact capacity)
- Encoding: VSA-bound bipolar patterns per triple ξ = bind(s, p, o); Hebbian-write to substrate W
- Retrieval at inference: substrate query via hyperprobe encoding of query residual → match to stored W → return retrieved value via either (a) residual-stream injection at layer ℓ, or (b) prompt-augmentation tool-call

**Eval corpus:**
- 1K held-out distilled facts (test set)
- 1K base-LLM facts NOT in distilled set (non-interference test)
- MMLU 1K-question subset (general capability test)
- 1K context-cost queries (NEW)
- Few-shot task suite (NEW)
- RULER long-context benchmark (NEW)

---

## 2. NINE SUB-CELLS

### Group 1 — Distillation capability (existing, lift to current best primitives)

#### Sub-cell A — Knowledge-graph distillation pathway

**Anchor name:** `phase05b_distillation_kg_pathway_llama31_n8192_v1`

**Capability question:** does extracting 10K (s, p, o) triples from Llama-3.1-8B via fact-elicitation prompts and Hebbian-writing each triple to substrate produce a queryable substrate state at distillation cost ≤ $30?

**Test design:**
- Generate fact-elicitation prompts targeting Wikipedia-class facts (10K-target corpus)
- Extract (s, p, o) triples via LLM-as-judge filtering
- Encode each triple as ξ = bind(VSA(s), VSA(p), VSA(o)) ∈ {-1,+1}^8192
- Hebbian-write to substrate: W = Σ ξ_k ξ_k^T / N
- α_final ≈ 10000/8192 = 1.22 — TOO HIGH; use M=1000 distilled facts at α=0.122 OR multi-bank B=10 (α_per_bank=0.122)
- **Default:** multi-bank B=10 to accommodate 10K facts at α_per_bank well below capacity

**Pre-registered bands:**
- HARD-PASS: 10K triples encoded; distillation cost ≤ $30 cloud; substrate W stored successfully; per-bank α ≤ 0.13
- MIDDLE: 5K-10K triples; cost $30-50
- HARD-FAIL: < 5K triples encoded OR cost > $50

**Cost:** ~$10-20 (LLM-call cost for triple extraction + filtering)

#### Sub-cell B — Distilled-fact recall

**Anchor name:** `phase05b_distilled_fact_recall_v1`

**Capability question:** when queries about distilled facts are sent to substrate-augmented Llama-3.1-8B, what fraction are answered correctly via substrate retrieval?

**Test design:**
- 1K test queries about distilled facts (held-out from distillation set)
- Run substrate-augmented LLM inference; retrieve from substrate; answer
- Compare to ground-truth fact answers (LLM-as-judge or exact-match for atomic facts)
- 5 seeds for retrieval randomness

**Pre-registered bands:**
- HARD-PASS: distilled-fact recall ≥ 0.85 across 5 seeds
- MIDDLE: recall ∈ [0.65, 0.85]
- HARD-FAIL: recall < 0.65 (worse than RAG baseline at same fact count)

**Cost:** ~$2-3 (1K queries × 5 seeds via vLLM)

### Group 2 — Non-interference (existing)

#### Sub-cell C — Non-distilled-fact retention

**Anchor name:** `phase05b_non_distilled_retention_v1`

**Capability question:** does substrate distillation interfere with base-LLM facts NOT in the distilled set?

**Test design:**
- 1K queries about base-LLM facts confirmed in baseline Llama-3.1-8B but NOT in distilled set
- Compare baseline-LLM accuracy vs substrate-augmented-LLM accuracy
- 5 seeds

**Pre-registered bands:**
- HARD-PASS: degradation ≤ 2pp absolute
- MIDDLE: degradation 2-5pp
- HARD-FAIL: degradation > 5pp (catastrophic interference)

**Cost:** ~$2-3

#### Sub-cell D — MMLU general-capability preservation

**Anchor name:** `phase05b_mmlu_preservation_v1`

**Capability question:** does substrate distillation preserve general reasoning capability on MMLU 1K-subset?

**Test design:**
- MMLU 1K-question subset; substrate-augmented vs baseline accuracy
- 5 seeds

**Pre-registered bands:**
- HARD-PASS: MMLU degradation ≤ 2pp absolute
- MIDDLE: 2-5pp degradation
- HARD-FAIL: > 5pp degradation (would refute Drill 5 mechanism-class separation argument empirically)

**Cost:** ~$2-3

### Group 3 — Operational (existing, lift to current best primitives)

#### Sub-cell E — One-shot fact addition at inference time

**Anchor name:** `phase05b_one_shot_fact_addition_v1`

**Capability question:** can substrate add 100 new facts at runtime (one-shot Hebbian write) in ≤1 minute total, with ≥85% recall on the added facts?

**Test design:**
- After distillation, write 100 new "post-distillation" facts via one-shot Hebbian
- Measure (a) total wall time for 100 additions; (b) recall on the 100 new facts; (c) recall on the original 1K distilled facts (interference check)
- 5 seeds

**Pre-registered bands:**
- HARD-PASS: 100 additions in ≤60 s wall; new-fact recall ≥ 0.85; original-fact recall maintained within ±2pp
- MIDDLE: 60-300 s wall OR new-fact recall ∈ [0.65, 0.85]
- HARD-FAIL: > 300 s wall OR new-fact recall < 0.65 OR original-fact interference > 5pp

**Cost:** ~$1-2

#### Sub-cell F — Deletion cert verification (dual-primitive)

**Anchor name:** `phase05b_deletion_cert_dual_primitive_v1`

**Capability question:** can substrate produce verifiable per-fact deletion certificates against the LLM-coupled state, using both PP-46 rank-1 subtraction AND PP-56 Sherman-Morrison primitives?

**Test design:**
- Delete 100 randomly-selected facts from the 1K distilled set
- 2 conditions: {PP-46, PP-56} × root-start protocol (per PP-49 2x drill finding; defensive)
- Measure (a) deleted-fact residual (substrate cosine), (b) retained-fact retention, (c) downstream-query reflects deletion (LLM no longer answers about deleted facts)
- Cert chain reproducibility check
- 5 seeds per condition

**Pre-registered bands per primitive:**
- HARD-PASS: deleted residual < 2σ noise floor AND retained retention > 0.85 AND downstream LLM forgets ≥ 95% of deleted facts AND cert byte-exact reproducible
- MIDDLE: deleted residual ∈ [2σ, 5σ] OR retention ∈ [0.65, 0.85]
- HARD-FAIL: deleted residual > 5σ OR retention < 0.65 OR downstream LLM still answers about deleted facts ≥ 30% of the time

**Discriminator:** if PP-56 HP and PP-46 MIDDLE, **PP-56 becomes flagship deletion primitive at LLM coupling** (lifts PP-56 row); if both HP, substrate has dual-primitive flexibility.

**Cost:** ~$3-5

### Group 4 — NEW context-awareness (load-bearing for product narrative)

#### Sub-cell G — Context-cost-per-query (NEW)

**Anchor name:** `phase05b_context_cost_per_query_v1`

**Capability question:** does substrate-augmented LLM achieve equivalent accuracy to baseline-LLM-with-RAG while using SIGNIFICANTLY FEWER context tokens per query? (The substrate's "third memory type" claim's load-bearing test.)

**Test design:**
- 1K test queries that match distilled facts
- 3 conditions:
  - (a) Baseline Llama-3.1-8B with RAG injection (retrieve top-5 chunks via FAISS over Wikipedia; inject into prompt)
  - (b) Baseline Llama-3.1-8B with NO retrieval (pure parametric memory)
  - (c) Substrate-augmented Llama-3.1-8B (substrate retrieval; minimal/no context injection beyond query)
- For each condition measure: accuracy, tokens-per-query (input + output), wall-time-per-query
- 5 seeds

**Pre-registered bands:**
- **HARD-PASS:** condition (c) accuracy ≥ 0.95 × condition (a) accuracy AND condition (c) input-tokens-per-query ≤ 0.10 × condition (a) input-tokens-per-query (substrate uses ≤10% of RAG context tokens at equivalent accuracy) — **THIS IS THE PRODUCT-NARRATIVE LOAD-BEARING TEST**
- MIDDLE: (c) accuracy ∈ [0.80, 0.95] × (a) OR (c) tokens ∈ [10%, 30%] × (a)
- HARD-FAIL: (c) accuracy < 0.80 × (a) OR (c) tokens > 30% × (a) (substrate doesn't materially save context vs RAG)

**Strategic significance:**
- HARD-PASS: **substrate's flagship product claim "third memory type that operates outside context window" empirically validated.** Direct competitive positioning vs RAG.
- HARD-FAIL: substrate offers no context savings vs RAG; product-narrative core broken.

**Cost:** ~$4-6 (3 conditions × 1K queries × 5 seeds)

#### Sub-cell H — ICL replacement (NEW)

**Anchor name:** `phase05b_icl_replacement_substrate_loaded_v1`

**Capability question:** can examples that would normally be loaded in-context for few-shot learning be PRE-LOADED into substrate and retrieved at inference time, achieving equivalent accuracy with substantially less context cost?

**Test design:**
- Few-shot task suite: 200 problems each from (a) analogy completion, (b) simple arithmetic-with-format, (c) sentiment classification
- 3 conditions per problem:
  - (i) In-context: K=10 examples in prompt + query
  - (ii) Substrate-loaded: K=10 examples Hebbian-written to substrate; only query in prompt; substrate retrieval at inference
  - (iii) Zero-shot: just query (baseline reference)
- Measure accuracy + context tokens + wall time
- 5 seeds

**Pre-registered bands:**
- HARD-PASS: condition (ii) accuracy within ±3pp of condition (i) accuracy AND condition (ii) context tokens ≤ 10% of (i) context tokens AND (ii) wall-time per "learning step" ≥100× faster than (i)
- MIDDLE: (ii) accuracy within ±10pp of (i) OR tokens 10-30% of (i)
- HARD-FAIL: (ii) accuracy < (iii) zero-shot baseline (substrate-loaded examples provide no signal)

**Strategic significance:**
- HARD-PASS: **substrate replaces ICL infrastructure** — examples pre-loaded once, queried many times, saves context per query; aligns with Cluster B3 design from earlier Tier-4 battery
- HARD-FAIL: substrate cannot serve as ICL replacement; restricts product positioning to RAG-replacement only

**Cost:** ~$3-5

#### Sub-cell I — Long-context regression check (NEW)

**Anchor name:** `phase05b_long_context_regression_ruler_v1`

**Capability question:** does substrate-augmented Llama-3.1-8B preserve baseline-LLM long-context capability across 8K / 16K / 32K context lengths, OR does substrate retrieval interact pathologically with long-context attention?

**Test design:**
- RULER benchmark (or equivalent needle-in-haystack) at 8K, 16K, 32K context lengths
- 2 conditions: baseline Llama-3.1-8B vs substrate-augmented (substrate loaded with distilled facts; substrate retrieval available but not directly used for needle queries)
- Measure needle-retrieval accuracy at each context length
- 5 seeds

**Pre-registered bands per context length:**
- HARD-PASS: substrate-augmented degradation ≤ 5pp absolute vs baseline at SAME context length, at all 3 lengths
- MIDDLE: degradation 5-10pp at one or more lengths
- HARD-FAIL: degradation > 10pp at any length (substrate pathologically interferes with LLM's long-context attention)

**Strategic significance:**
- HARD-PASS: substrate-augmented LLM is a transparent capability add — no regression on existing strengths
- HARD-FAIL: substrate retrieval interacts with LLM attention; can't be used in long-context scenarios; restricts product positioning

**Cost:** ~$5-8 (3 context lengths × 2 conditions × 5 seeds; long-context inference is the dominant cost driver)

---

## 3. SEQUENCING AND COST BREAKDOWN

### Within-bootstrap sequencing (single Lambda H100 instance)

```
Phase 0.5b Lambda H100 bootstrap (~$10 setup)
├── Sub-cell A: distillation pathway (~$10-20)
├── Sub-cell B: distilled-fact recall (~$2-3)
├── Sub-cell C: non-distilled retention (~$2-3) [parallel to D]
├── Sub-cell D: MMLU preservation (~$2-3) [parallel to C]
├── Sub-cell E: one-shot fact addition (~$1-2)
├── Sub-cell F: deletion cert dual-primitive (~$3-5)
├── Sub-cell G: context-cost-per-query (~$4-6)
├── Sub-cell H: ICL replacement (~$3-5)
└── Sub-cell I: long-context regression (~$5-8)
```

**Total estimate: $42-65 cloud + 1-2 weeks engineering for the 9-cell battery.**

(Note: prior implicit sketch said $15-40 for 6 cells; 9 cells with same per-cell scope gives $42-65; if costs run high, can defer sub-cell I as Wave-2 follow-on at $5-8.)

### Outer-loop sequencing (across phases)

```
T-0 (NOW)
├── Wave-5 CPU decisive experiments (MFPT / BBP cal / depth-parity) — $0
└── Phase 0.5 v1 finishes on H100 (in flight)

T+1 (~1 day)
├── Phase 0.5 v1 verdict
└── Phase 0.5 v2 selective extension dispatched per testbed Option Y plan ($30-50)

T+1-2 (gated on Phase 0.5 v1+v2 outcome)
├── IF Phase 0.5 v1+v2 = 3-of-3 sub-test HP (or 2-HP + 1-MIDDLE with sub-test B HP):
│     → Phase 0.5b distillation MVP authorized
│     → Same H100 instance if still running (preserves bootstrap savings)
│     → 9-cell battery per this spec ($42-65 + 1-2 weeks engineering)
└── IF Phase 0.5 v1+v2 hard-fails sub-test B:
      → DEFER Phase 0.5b indefinitely; substrate-LLM coupling redesign needed
```

### Cost ceiling

- **Optimistic (combined Phase 0.5 v1+v2 + 0.5b on shared H100 bootstrap):** $25 (v1 base) + $30-50 (v2 ext) + $42-65 (0.5b) = **~$97-140 total**
- **Pessimistic (separate bootstraps for each phase):** add ~$15-25 in extra bootstraps
- **User authorization ceiling:** Phase 0.5b portion was $15-40 in prior sketch; this 9-cell spec is $42-65 — surface for explicit user GO at the updated cost

---

## 4. PRE-LAUNCH DEPENDENCIES

### Required before Phase 0.5b dispatch:

1. **Phase 0.5 v1 verdict** — informs Phase 0.5b risk profile per sub-test outcomes (especially B for deletion cert)
2. **Phase 0.5 v2 selective extension verdict** — confirms BBP observable + PP-56 primitive viability at LLM coupling
3. **3 Wave-5 CPU experiments** — already queued; outputs would land before Phase 0.5b dispatches:
   - MFPT N-scaling → informs Sub-cell F deletion-cert interpretation (1-RSB phase implications)
   - BBP eigenspectrum calibration → validates BBP observable for sub-cell G context-cost measurement (BBP-style fingerprint of substrate's retrieval signal)
   - HRC depth-parity discriminator → resolves PP-49 mechanism for Sub-cell F protocol choice
4. **USER PHASE 0.5b GO authorization** — at updated cost ($42-65 vs prior $15-40)

### Strongly recommended:

5. **Cluster A1 (Hebbian-vs-GD identity)** — substantiates the "Hebbian = GD fixed point" claim used in product narrative for sub-cell H ICL-replacement (Hebbian write = ICL gradient step per mesa-optimization lit). Already queued; $0 CPU.

### Optional (not blocking):

6. **Probe-of-probe transfer drill** for cross-LLM probe portability (per Hyperprobe Tier-7 drill recommendation) — only needed if Phase 0.5b passes and we want to extend to non-Llama LLMs.

---

## 5. CAP_MAP IMPACT EXPECTATIONS (Phase 0.5b 9-cell battery, if all HP)

### Sub-cell outcomes → cap_map row impact:

| Sub-cell HP | Cap_map row impact |
|---|---|
| A + B HP | substrate-LLM coupling distillation pathway empirically validated; Phase 0.5b core claim locked |
| C + D HP | substrate non-interference confirmed; Drill 5 mechanism-class separation empirically validated |
| E HP | one-shot fact-addition product feature confirmed; PP-52 LIFT (production-LLM coupled) |
| F HP (dual-primitive) | PP-46 + PP-56 deletion cert LIFTs to LLM-coupled (potential BAND-LIFT for both) |
| **G HP** | **PP-12 / new row "substrate context-savings vs RAG"; substrate's flagship product-narrative claim empirically anchored** |
| **H HP** | **NEW row "substrate as ICL replacement" or PP-52 ICL extension; mesa-optimization Hebbian-equivalence claim validated** |
| **I HP** | substrate-augmented LLM is transparent capability add (no long-context regression); broadens product positioning |

### 3 new top-level row candidates from Group 4 (context-awareness):

- **NEW row candidate:** substrate context-savings primitive (Sub-cell G validation)
- **NEW row candidate:** substrate ICL-replacement primitive (Sub-cell H validation)
- **NEW row candidate:** substrate-augmented LLM long-context preservation (Sub-cell I validation)

These three would be the substrate's FIRST cap_map rows for LLM-COUPLED product features (vs. existing substrate-only rows). Cross-references the Phase 0.5 Tier-7 audit-primitive rows (PP-50/51/52 candidates from Phase 0.5 v1+v2).

### Framework reliability impact (projected if Phase 0.5b all-HP):

- Product-feature reliability: 86-98% → 88-99% (LLM-coupled validation crossing 90% lower bound)
- LLM-integration capability rows: 0 → 3+ new rows founded

---

## 6. TESTBED INTEGRATION CHECKLIST

When user authorizes Phase 0.5b:

- [ ] Confirm Phase 0.5 v1+v2 verdict state (gating decision)
- [ ] Confirm Wave-5 CPU experiments verdicts (informs Sub-cells F + G design)
- [ ] Confirm H100 instance status (still running from Phase 0.5? Or new bootstrap?)
- [ ] Apply distillation pathway: KG triple extraction from Llama-3.1-8B (Sub-cell A) — engineering: ~3 eng-days
- [ ] Wire VSA bind/unbind + Hebbian write to substrate N=8192 multi-bank B=10 (or single-bank if α=0.122 confirmed safe)
- [ ] Wire substrate retrieval into vLLM inference loop (sub-cell B+ requirement) — engineering: ~3 eng-days
- [ ] Wire dual-primitive deletion (PP-46 + PP-56 root-start) — engineering: ~1 eng-day
- [ ] Wire context-cost-per-query measurement (token counting; baseline FAISS RAG setup; sub-cell G) — engineering: ~2 eng-days
- [ ] Wire few-shot task suite with substrate-vs-context loading toggle (sub-cell H) — engineering: ~1 eng-day
- [ ] Wire RULER long-context benchmark (sub-cell I) — engineering: ~1 eng-day
- [ ] Pre-register HP/MIDDLE/HF bands per sub-cell per Section 2
- [ ] Per-cell partial JSON output for restart capability per `feedback_testbed_progress_logging_and_restart`
- [ ] Single-bootstrap commit per `feedback_batch_cloud_experiments`
- [ ] Cost tracker monitoring; cap at $80 incremental
- [ ] ASCII-only output per `feedback_ascii_only_in_scripts`

**Engineering total: ~10-12 eng-days for full 9-cell battery wiring (extension on top of Phase 0.5 v1+v2 wiring; reuses hyperprobe + vLLM scaffolding).**

---

## 7. DISCIPLINE DECLARATIONS

- **Capability questions only;** HP/MIDDLE/HARD-FAIL bands pre-registered per sub-cell.
- **Per `feedback_no_padding_experiments`:** every sub-cell justified — 6 from prior implicit sketch + 3 from context-awareness gap user surfaced today. No padding.
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** all HARD-FAIL trip-wires explicit; verdict_handler does honest re-read.
- **Per `feedback_obey_user_pause_explicitly`:** Phase 0.5b dispatch requires USER EXPLICIT GO AUTHORIZATION at the updated cost ($42-65 vs prior $15-40 sketch).
- **Per `feedback_short_cloud_runs_preferred`:** $42-65 is above prior per-case threshold of $30 but below long-overnight $50 cutoff for most cells individually; surface to user for explicit auth.
- **Per `feedback_batch_cloud_experiments`:** all 9 sub-cells share single Lambda H100 bootstrap; do NOT split across multiple instances.
- **Per `feedback_lit_scan_calibration_penalty`:** P_deflated for Phase 0.5b overall ~0.45-0.55 (per prior sketch; 9-cell expansion doesn't materially change since each new cell has independent HP path).
- **Per `feedback_substrate_value_framing_2026-05-26`:** Sub-cells G/H/I are load-bearing for substrate's "third memory type" product positioning — empirical validation of the claim that distinguishes substrate from RAG/fine-tuning/context-stuffing.
- **Per `feedback_capabilities_not_product_positioning`:** sub-cells framed as capability questions; product-narrative implications stated only as cap_map impact descriptions (Section 5).
- **PROT-018:** anchor names use `phase05b_*_v1` family; no `_n<N>` suffix needed (LLM-native d=4096 / substrate N=8192 fixed per Section 1).
- **Per-experiment `--timeout`:** A 7200s; B 1800s; C 1800s; D 1800s; E 1200s; F 3600s; G 3600s; H 2400s; I 5400s.

---

## 8. WHAT THIS ROUTING DOES NOT TOUCH

- **Phase 0.5 v1/v2 design** — `research_routing_v359_phase05_v2_testbed_spec_2026-06-03.md` is the spec; Phase 0.5b is the SEPARATE next phase
- **Phase 1+ (Tier-1 RAG-baseline, Tier-2 function-call, Tier-3 Tier-6 flagship)** — conditional on Phase 0.5b outcome; deferred
- **Tier-4-lite FFN swap** — deferred per `research_routing_tier4_training_acceleration_FINAL_5drill_consolidation_2026-06-02.md` (Phase 0.5b is the strategic substitute)
- **Engineering details** — exact vLLM integration code, hyperprobe weight loading, exact tokenizer setup are testbed engineering scope
- **Wave-5 CPU experiments** — separate dispatch; already queued at Tier 1 priority in `notes/experiment_queue_pending.md`

---

## 9. PHASE 0.5b DECISION-GATE UPDATE

**Updated user-decision-gate considerations:**

| Consideration | Prior sketch | This spec |
|---|---|---|
| Cost | $15-40 | $42-65 |
| Cells | 6 | 9 |
| Engineering | 1-2 weeks | 1-2 weeks (same; reuses 0.5 scaffolding) |
| Context-awareness | not present | 3 sub-cells (G/H/I) — load-bearing for product narrative |
| Substrate-side de-risking | 6/6 primitives | 6/6 primitives + 5 product-narrative upgrades from drill battery + 4 theoretical-class corroborations |
| Phase 0.5 v1 dependency | "combined bootstrap recommended" | Sequenced: Phase 0.5 v1+v2 verdict gates Phase 0.5b; Phase 0.5 v1 already in flight |

**Recommendation:** authorize Phase 0.5b at $42-65 contingent on Phase 0.5 v1+v2 verdict outcomes. The 3 NEW context-awareness sub-cells are load-bearing for the "substrate replaces context-stuffing" product-narrative core — running Phase 0.5b WITHOUT them would technically pass on operational metrics but fail to anchor the product-positioning differentiator.

---

**END.**

**To testbed:** integrate per Section 6 checklist when Phase 0.5b authorized. Sub-cells A-F are extensions of prior implicit sketch; sub-cells G/H/I are NEW per user explicit ask today; all share single Lambda H100 bootstrap.

**To user:** Phase 0.5b 9-cell spec ready. Updated cost is $42-65 (vs $15-40 prior sketch) reflecting 3 new context-awareness cells. Awaiting Phase 0.5 v1+v2 verdict outcomes before recommending dispatch; GO authorization request will surface at that decision point.

**To orchestrator:** queue Wave-5 CPU experiments NOW per prior routing (already at Tier 1 in `experiment_queue_pending.md`). Hold this Phase 0.5b spec for pickup when Phase 0.5 v1+v2 verdicts trigger gating decision.
