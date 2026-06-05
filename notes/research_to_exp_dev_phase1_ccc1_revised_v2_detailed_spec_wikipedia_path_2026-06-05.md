# Research -> Exp-Dev: Phase 1 detailed spec (CCC-1 REVISED-v2 + 4-benchmark eval) + Wikipedia-first knowledge-base path

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~09:00
**Subject:** User decisions: (1) Wikipedia-first KB scope, (2) keep current 6-cell scope (no drops), (3) defer Phase 3 budget. Adding Phase 1 detailed spec + Wikipedia prep work on top of current routing.

---

## Strategic context

User's audacious end-state: **substrate cognitive core that contains entire knowledge base, beats frontier LLMs on multi-hop / analogical / counterfactual / cross-domain reasoning, runs on commodity hardware, audits per-fact provenance, learns continually at near-zero cost.**

User strategic decisions (2026-06-05 ~08:50):
1. **Wikipedia first, then expand** -- Phase 3 builds full English Wikipedia substrate; Phase 4 (PubMed/arXiv/etc.) only if Phase 3 lands
2. **Keep current routing scope** -- existing 6 cells (CONT-LRN-1, GPU-OPT-1, MULTI-LAYER-TIER4-1, CROSS-MODAL-1, FULL-PYTHIA-1, LLAMA-1B-1) continue; this routing ADDS Phase 1 specifics on top
3. **Phase 3 budget deferred** -- decide Llama-1B vs Llama-8B for Phase 3 after Phase 1+2 verdicts

---

## Phase 1: Prove substrate cognitive core beats Pythia-160M on real Q&A (CCC-1 REVISED-v2 detailed spec)

### Anchor: `substrate_cognitive_core_ccc1_revised_v2_pythia160m_4benchmark_eval_v1`

### Architecture (per cognitive-core 3x drill + interface-preservation drill)

```
Stage 1: Encoder
  Frozen Pythia-160M Layer 12 activations on training corpus
  Per-token residuals (gated on Testbed --per-token extraction)
  Training corpus: Wikipedia subset (~100k passages)

Stage 2: VQ to concepts
  V_c=256 codebook (start small; scale to 1024 if needed)
  k-means VQ on ~1M sampled per-token activations

Stage 3: Substrate cognitive core
  N=8192; 20 hierarchical domains
  Bio-primitive stack: B2 DG sparse f=0.02 + position-binding + STDP + B6 D-ECR + B3a/B3b gating + hierarchical aggregator
  NO cf-RPE (inverts for generative)
  Mode 5 controller (4-state FSM minimum for 2-hop tasks; expandable to 13-state for TM-equivalent)
  Cleanup-augmented depth (production knob per NEW EXP 3 HP)

Stage 4: Decoder + bridges
  Pythia-160M as decoder
  Two-bridge hybrid:
    Bridge A (text-injection) for factual recall queries
    Bridge D (attention K/V injection at Pythia layer 8) for relational/analogical/counterfactual queries
  Controller (Stage 3) decides bridge per query type

Stage 5: Evaluation pipeline
  Same eval scaffold runs Pythia-160M baseline vs substrate cognitive core
  Identical question sets; identical scoring
```

### 4-benchmark evaluation suite

| Benchmark | Source | Test | Why substrate should win |
|---|---|---|---|
| **HotpotQA distractor dev** | 1k 2-3 hop questions | Multi-hop factual reasoning | K=12+ vs Pythia ~3-hop CoT |
| **NQ multi-hop subset** | 1k questions filtered to multi-hop | Real-world factual chains | Same multi-hop advantage |
| **Wikidata analogy completion** | 1k analogy pairs (A:B::C:?) | Relational reasoning | VSA binding native; Pythia has no analogy mechanism |
| **Custom counterfactual benchmark** | 500 synthetic (delete fact X; query Y) | Counterfactual queries | cf-RPE primitive native; Pythia cannot do this |

### Pre-registered HP/MID/HF (per dimension + overall)

**Per-dimension HARD-PASS:**
- Multi-hop factual: substrate >= 1.5x Pythia-160M EM accuracy
- Analogical: substrate >= 2.0x Pythia-160M EM accuracy
- Counterfactual: substrate >= 2.0x Pythia-160M EM accuracy
- Single-hop factual: substrate >= 0.9x Pythia-160M (tie acceptable; not substrate's strength)

**Overall HARD-PASS:** substrate cognitive core beats Pythia-160M on >=3 of 4 dimensions with combined avg accuracy >= 1.5x baseline

**MIDDLE:** beats baseline on 1-2 dimensions OR avg 1.1-1.5x

**HARD-FAIL:** substrate fails to beat baseline on any dimension OR avg <1.1x

### WHY-DRILL paths per HF dimension

If multi-hop HF: larger V_c (256 -> 1024); larger N (8192 -> 16384); cleanup augmentation enabled at all hops
If analogical HF: ensure Bridge D wiring correct; check VSA binding arithmetic preserved through controller
If counterfactual HF: verify cf-RPE primitive wired for inference-time delta computation (not just write-time gating)
If overall HF: substrate cognitive core architecture needs scale-up to Llama-1B before claiming productizability

### Cost + wall

- Pythia per-token extraction: $0 (Testbed action in flight; ~30 min wall)
- VQ training: $0 CPU; ~30 min wall
- Substrate training: $0 CPU; ~1 hour wall (~100k passages = ~10M patterns)
- Evaluation pipeline: $0 CPU; ~1 hour wall per system
- Total: ~3-4 hours wall + ~3-5 days engineering; $0 cloud

If Bridge D wiring needs cloud GPU for Pythia inference at scale: ~$10-30 cloud H100.

**Phase 1 total: ~$10-30 cloud + ~1 week engineering.**

---

## Phase 1 prep work (parallel to current 6-cell routing)

### Cell EVAL-SCAFFOLD-1: 4-benchmark evaluation harness

**Anchor:** `substrate_cognitive_core_4benchmark_eval_harness_v1`

Build the evaluation pipeline that runs identical question sets through:
- Pythia-160M baseline (raw)
- Substrate cognitive core (when CCC-1 REVISED-v2 ready)
- Same scoring; same metric methodology; statistical significance tests

Engineering: ~2-3 days
Cost: $0

This pipeline reused for Phase 2 + Phase 3. Build-once amortizes across all phases.

### Cell WIKI-PREP-1: Wikipedia subset preparation

**Anchor:** `substrate_cognitive_core_wikipedia_subset_preparation_v1`

Prepare the Wikipedia training corpus for substrate cognitive core:
- Download Wikipedia dump (English; latest; ~80 GB compressed)
- Extract clean text per article (strip markup, infoboxes, references)
- Sample subsets at multiple scales: 1k articles (smoke); 100k articles (Phase 1); 1M articles (Phase 2); full ~6M (Phase 3)
- Tokenize for Pythia-160M (Phase 1) and Llama-3.2-1B (Phase 2)
- Build train/eval splits

Engineering: ~3-5 days
Cost: $0

This is the foundation for Phase 1 substrate training corpus AND Phase 2-3 scale-up.

---

## Current 6-cell routing (continues per user decision)

NO drops. All 6 cells continue per earlier routing:

| Cell | Status | Priority |
|---|---|---|
| CONT-LRN-1 (continual learning empirical) | Tier 1; build NOW | HIGH |
| GPU-OPT-1 (substrate GPU kernels) | Tier 1; build NOW | HIGH |
| MULTI-LAYER-TIER4-1 (substrate-attention sweep) | Tier 1; build NOW | HIGH |
| CROSS-MODAL-1 (multi-modal anchor) | Tier 1; build NOW | HIGH |
| FULL-PYTHIA-1 (substrate-attention all layers) | Tier 2; after Tier 1 | MEDIUM |
| LLAMA-1B-1 (Llama scale-up) | Tier 2; after Tier 1 | MEDIUM |

Plus the 2 new Phase 1 prep cells: EVAL-SCAFFOLD-1 + WIKI-PREP-1

---

## Phase 2 path (after Phase 1 HP)

If Phase 1 lands HP, scale to Llama-3.2-1B tier:

- Use Llama-3.2-1B as encoder/decoder (user has Llama license)
- Wikipedia subset (~500k articles; ~5 GB)
- Substrate at N=16384, 100-200 hierarchical domains
- Same 4-benchmark eval
- Pre-reg: substrate cognitive core beats Llama-3.2-1B on >=3 of 4 dimensions

**Phase 2 cost: ~$500-2k cloud; ~1 month**

---

## Phase 3 path (after Phase 2 HP; user-deferred budget decision)

If Phase 2 lands HP, build full English Wikipedia substrate cognitive core:

- Full English Wikipedia (~6M articles; ~100M effective facts)
- Substrate at N=32768, 1000-2000 hierarchical domains, V_c=5000
- LLM interface: Llama-3.2-1B (~$10-50k Phase 3a) OR Llama-3.1-8B (~$50-200k Phase 3b)
- USER WILL DECIDE PHASE 3 BUDGET AFTER PHASE 1+2 VERDICTS

Total system: ~16-33 GB substrate + ~2 GB LLM = ~20 GB runnable on workstation.

**This is the audacious demo: substrate cognitive core that "knows Wikipedia" and reasons over it with audit + continual learning at consumer-hardware scale.**

---

## Phase 4 path (after Phase 3 demos well)

Comprehensive knowledge base:
- Wikipedia + PubMed + arXiv + Stack Overflow + key textbook corpora
- ~10B+ facts
- ~100-670 GB substrate (still smaller than frontier LLM weights)

Year-2 timeline; not committing now.

---

## What's gated / standing

**Testbed (in flight; 3 user-authorized actions):**
- Per-token Pythia extraction
- KG/QA datasets (HotpotQA + NQ + Wikidata)
- GPU runner inspection

**User actions:**
- UMLS license registration (for separate Medical Path Y prototype; not on Wikipedia critical path)

**No new Testbed asks this routing.**

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per user 2026-06-05 decisions: Wikipedia-first KB; keep current 6-cell breadth; defer Phase 3 budget
- Per [[feedback-no-padding-experiments]]: Phase 1 spec + 2 prep cells are load-bearing for audacious vision
- ASCII-only

PROT-018: anchors per cell
PROT-021: source=local CPU + remote 4060 Ti + cloud (Phase 3); n_seeds=3

---

**END.**

**Exp-Dev:** Phase 1 detailed spec + 2 Phase 1 prep cells (EVAL-SCAFFOLD-1 + WIKI-PREP-1) added on top of current 6-cell routing. Total scope: 8 cells (6 current + 2 prep) + Phase 1 build when Testbed gates land.

CCC-1 REVISED-v2 detailed: 4-benchmark eval suite (HotpotQA + NQ + Wikidata + counterfactual) with per-dimension HP thresholds. Substrate cognitive core architecture is two-bridge hybrid (text + attention K/V).

**Standing for: Tier 1 verdicts + Phase 1 prep cells + Phase 1 build when gated items land + Tier 2 verdicts after Tier 1.**

**User:** Wikipedia-first audacious vision routed. Phase 1 = ~$10-30 + 1 week eng. Phase 2 = ~$500-2k + 1 month. Phase 3 = ~$10-200k + 2-3 months (budget decision later). Phase 4 = year-2 scope.
