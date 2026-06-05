# Research -> Exp-Dev: High-priority experiments for Phase 1.5 + Phase 2 prep

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~14:30
**Subject:** Phase 1 Pythia-tier essentially complete (5/7 categorical wins). 6 high-priority experiments for Phase 1.5 + Phase 2 prep. Plus drill dispatched on production architecture at scale.

---

## Strategic frame

Phase 1 outcome locked: substrate is memory+reasoning+audit core; NOT generative LM. The 5/7 categorical wins are the empirical foundation. Phase 2 (Llama-1B) will validate end-to-end demo quality and resolve Pythia-ceiling items.

Six high-priority experiments below scope where substrate's PROVEN strengths can be pushed further. Pythia-tier feasible; can run in parallel with Phase 2 prep.

---

## Cell HP-1: Long-conversation memory at SCALE (1000+ exchanges; multi-session)

**Anchor:** `substrate_long_conversation_scale_1000_exchanges_v1`

### Why this matters

Categorical win at 200 exchanges. Push to 1000+ exchanges spanning multiple simulated sessions. This is the kind of scale demo where substrate's persistent memory becomes obvious + impressive.

### Architecture

- Synthetic conversation generator with 1000+ exchanges; multi-day simulation
- 5 distinct topic threads woven across the conversation
- 100 recall questions targeting facts from various depths (exchange 50, 200, 500, 800, 1000)
- Substrate cognitive core vs Pythia-160M baseline (Pythia loses everything past 2048 tokens)

### Pre-reg
- HP: substrate recall >= 0.85 at exchange 1000; Pythia ~ 0.00 beyond context window
- MID: substrate 0.60-0.85 recall
- HF: substrate degrades at long horizons (architecturally concerning)

### Cost + wall
- $0 CPU
- ~2-3 hours wall
- 3 seeds

### Strategic
Scales the categorical win 5x beyond what we've already validated. Substantial demo material.

---

## Cell HP-2: Multi-document synthesis at corpus scale (1000+ docs)

**Anchor:** `substrate_multidoc_synthesis_1000plus_docs_v1`

### Why this matters

Already won at 300 docs (1.00 vs 0.08 vs Pythia). Push to 1000+ docs. This is the workload that Wikipedia-scope demos need.

### Architecture

- 1000 synthetic documents on related topics (sub-corpus of Wikipedia subset)
- Synthesis questions requiring information from 50-200 docs each
- Substrate (ingests all 1000) vs Pythia-160M (windowed RAG with k=top-10)

### Pre-reg
- HP: substrate accuracy >= 0.80 on multi-document synthesis questions; Pythia <= 0.30
- MID: substrate 0.50-0.80
- HF: substrate doesn't scale beyond ~300 docs

### Cost + wall
- $0 CPU
- ~3-4 hours wall
- 3 seeds

### Strategic
Validates substrate scales to Wikipedia-corpus magnitudes architecturally. Demo material for "ask question requiring reasoning across 1000+ documents."

---

## Cell HP-3: Continual learning with realistic update stream (30-day simulation)

**Anchor:** `substrate_continual_learning_30day_realistic_stream_v1`

### Why this matters

CONT-LRN-1 validated qualitative no-forgetting + 27x speedup at Pythia. Push to realistic 30-day simulation with daily knowledge updates. This is the deployment scenario for regulated AI (medical records, legal cases, financial news).

### Architecture

- Initial substrate trained on baseline corpus (~10k facts)
- Day 1-30: each day adds 100-500 new facts via Hebbian writes
- Day 30: query mix of (a) baseline facts; (b) day-N facts; (c) cross-day reasoning
- Compare substrate vs Pythia-160M (which would need 30 fine-tune cycles to absorb same content)

### Pre-reg
- HP: substrate retains 99%+ baseline facts AND recalls new facts AND chains across days; substrate add cost <= 1 minute total compared to Pythia ~30 hours fine-tune cycles
- MID: substrate retains 90-99%; partial cross-day chaining
- HF: substrate forgets across days OR doesn't chain (architectural concern)

### Cost + wall
- $0 CPU substrate; ~$5-10 Pythia fine-tune comparison
- ~1 day wall
- 3 seeds

### Strategic
This IS the regulated-AI product demo. 30-day simulation of "AI that learns continuously without forgetting" is what medical/legal/financial deployment needs.

---

## Cell HP-4: Substrate-MAX for REASONING tasks (analogical + multi-hop chains)

**Anchor:** `substrate_max_for_reasoning_tasks_not_lm_v1`

### Why this matters

Substrate-MAX variants tested at next-concept LM = HURT or no-op. But those variants (extended context, cleanup, iteration, hierarchical) are REASONING mechanisms. Test them where they SHOULD help: analogical reasoning + multi-hop KG chains.

### Architecture

Take CCC-1-EXTRA analogical + KG multi-hop tasks. Test substrate baseline vs substrate-MAX variants:

- Variant 1: cleanup-augmented retrieval at each hop
- Variant 2: extended context for analogical reasoning (use 5-10 prior items for pattern recognition)
- Variant 3: iterated retrieval (Mode 4 NC1) for deep chains (K=12 -> K=24+)
- Variant 4: Mode 5 controller + isolated substrate (Architecture A)
- Variant 5: hierarchical multi-substrate (D=4, 8, 16)

### Pre-reg
- HP: at least 2 variants improve baseline by >=20% on reasoning dimensions; substrate-MAX combined improves >=50%
- MID: variants help modestly (~10-20%)
- HF: variants don't help reasoning either (architectural concern)

### Cost + wall
- $0 CPU
- ~1 day wall (5 variants + combined)
- 3 seeds each

### Strategic
Validates that substrate-MAX variants are useful where they should be (reasoning), even if not useful at LM. Sharpens the substrate-MAX vs substrate-baseline distinction empirically.

---

## Cell HP-5: Domain Q&A prototype (Medical-light using already-available data)

**Anchor:** `substrate_medical_qa_proto_no_umls_dependency_v1`

### Why this matters

UMLS license pending. While waiting, can prototype medical-light Q&A using PubMed abstracts (publicly available; no license needed) plus open medical KG data. This is the dry-run before full UMLS Medical Path Y.

### Architecture

- ~10k PubMed abstracts on related medical topics (drug-disease-mechanism)
- Substrate cognitive core ingests abstracts (encoder = Pythia-160M for now; upgrade to Llama-1B Phase 2)
- Open medical Q&A benchmark subset (MedQA-USMLE-3 subset; ~500 questions; CC-licensed)
- Compare substrate cognitive-core vs raw Pythia-160M baseline

### Pre-reg
- HP: substrate >= 1.5x Pythia baseline AND deletion-cert demonstrably operational on test substrate (delete a fact; verify removal)
- MID: substrate 1.1-1.5x
- HF: substrate doesn't help (Pythia ceiling on medical reasoning)

### Cost + wall
- $0 CPU + free PubMed download
- ~1-2 days wall
- 3 seeds

### Strategic
Dry-run for Medical Path Y when UMLS lands. Establishes pipeline + demo capability. Substrate's audit primitives demonstrable on real medical-class data.

---

## Cell HP-6: Substrate Introspection categories 4-10 (complete the toolkit)

**Anchor:** `substrate_introspection_toolkit_full_10_categories_v1`

### Why this matters

3/10 introspection categories built (audit trail + knowledge density + crosstalk). Need 7 more for full toolkit:

4. Knowledge gap detection
5. Retrieval path analysis
6. Source-LLM bias inheritance
7. Compositional structure analysis
8. Efficiency bottleneck analysis
9. Catastrophic recall analysis
10. Distillation quality analysis

### Architecture

For each category: build analysis module on existing substrate weights. Smoke test on EX-CONCEPT-1 / CCC-1-v2 substrates.

### Pre-reg
- HP per category: module functional + finds actionable insight on existing substrate
- MID: module functional; insights weak
- HF: module produces no actionable output

### Cost + wall
- $0 CPU
- ~2-3 days wall per category (build + smoke test)
- Total: ~7-10 days for all 7 remaining

### Strategic
Completes the substrate introspection product feature. Each category produces a demo-able insight. Together: the regulated-AI "show your work" pitch becomes concrete.

---

## Sequencing recommendation

**Highest strategic priority (Phase 1.5; do now):**
1. HP-3: Continual learning 30-day simulation (regulated-AI demo material)
2. HP-1: Long-conversation memory at scale (substantial demo material)
3. HP-2: Multi-doc synthesis at corpus scale (scales the categorical win)

**Phase 2 prep (in parallel with Llama-1B extraction):**
4. HP-4: Substrate-MAX for reasoning (sharpens architectural distinction)
5. HP-5: Medical Q&A prototype (dry-run for UMLS Medical Path Y)
6. HP-6: Introspection toolkit categories 4-10 (ongoing; complete product feature)

**Already running:**
- Phase 1 capability benchmark completion (HotpotQA + NQ; expected Pythia-ceiling)
- EX-CONCEPT-1 stronger baselines + variants (honest negative confirmed)

**Held for Phase 2 (when Llama-1B lands):**
- Multi-hop factual at Llama-1B (resolves Pythia-ceiling)
- Tier 4 substitution at Llama-1B
- CONT-LRN-1 at Llama-1B baseline (validates 1000x ratio)
- Substrate cognitive-core end-to-end demo quality

---

## Total cost + time

All 6 HP cells: ~$5-10 cloud + ~2-3 weeks engineering parallel + ~3-5 weeks wall total.

Per user "engineering time not a constraint" + "stay at Pythia for iteration speed": all 6 buildable in parallel.

---

## Plus drill dispatched: production substrate-LLM hybrid architecture at scale

Dispatched 2x research drill on:
- Optimal substrate sizing at Wikipedia-scale (N, D, sparsity, cleanup)
- Optimal 1B-tier LLM partner selection (Llama-3.2-1B vs alternatives)
- Optimal bridge architecture at 1B scale
- Production inference cost + latency analysis
- Comparison vs RAG / kNN-LM / NTM / DNC / pure LLM at matched scale

Privacy-locked generic framing. Should land in ~15-20 min. Will surface Phase 3 architectural recommendations.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: each cell tests distinct architectural hypothesis where substrate's PROVEN strengths can be pushed further
- Per [[feedback-cloud-only-when-absolutely-necessary]]: all cells $0 except small Pythia fine-tune ($5-10)
- Per stay-at-Pythia methodology: all cells at Pythia tier; Pythia-ceiling notes per finding
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: production architecture drill follows privacy lock-in
- ASCII-only

PROT-018: anchors per cell
PROT-021: source=local CPU + occasional fine-tune; n_seeds=3

---

**END.**

**Exp-Dev:** 6 high-priority cells aligned with refined audacious vision (substrate = memory+reasoning+audit core). Each pushes a proven strength further. Total ~$5-10 + ~2-3 weeks parallel engineering.

**Highest immediate priority: HP-3 (30-day continual learning) -- this is the regulated-AI product demo.** Plus HP-1 + HP-2 scale the categorical wins. The other 3 in parallel.

**Standing for: HP-1 through HP-6 verdicts + production architecture drill landing + Llama-1B extraction (Testbed) + Phase 2 work when extraction lands.**

**User:** 6 high-priority experiments routed + production architecture drill dispatched. All build on Phase 1's 5/7 categorical wins. Total cost ~$5-10. The 30-day continual learning simulation (HP-3) is the regulated-AI demo material.
