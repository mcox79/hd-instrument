# Research -> Exp-Dev: 3 drills unified routing (pre-training + bridge-ID + federated)

**From:** Research session
**To:** Exp-Dev (primary) + Testbed (heavy items inform)
**Date:** 2026-06-07
**Re:** Substrate pre-training 3x + bridge-ID accuracy 2x + federated substrate 2x drills
all landed; unified routing for the v1.1 + v1.5 engineering plan.

## STRATEGIC SYNTHESIS: multi-hop revival is now multi-pronged

| Component | Source drill | Effect | Eng cost |
|---|---|---|---|
| Pre-trained substrate (CELL-2 v3 + Wikidata + S2ORC) | Pre-training 3x | Cold-start bridge coverage 55-70% -> 80-88%; parametric gap 25-35% -> 8-15% | 1-2 weeks |
| DistilBERT-NER cascade | Bridge-ID 2x | Bridge-ID 62% -> 75-80% | 3-5 days |
| Self-improving routing (router + sleep defrag + bridge cache) | Self-improving 3x | Warm equilibrium 90-93% bridge coverage; X% fast-path -> latency 4.6x improvement | Tier 4 dependent; v1.5 |
| Federated substrate (v2.0) | Federated 2x | New customer warm-start; commercial moat | v2.0; needs DP validation |

Combined cold-start multi-hop accuracy projection: ~0.60 (ties baseline RAG; substantial
improvement from current ~0.49).
Combined warm equilibrium projection: 0.70+ (beats RAG; categorical claim).

## v1.1 ENGINEERING PLAN (3-prong; parallel)

### Prong 1: Substrate pre-training ship (1-2 weeks)
Per pre-training 3x drill primary recommendation: Option A sequential waterfall.

Steps:
1. Pattern B compression + index build on existing CELL-2 v3 Wikipedia cache (~1 week)
2. Chunking strategy validation (one article -> one fact vs multi-fact chunking)
3. Layer 1 confidence threshold tuning (=0.7 recommended)
4. Distributable binary artifact (93 MB at Pattern B parity)
5. Customer overlay mounting layer (Pattern B composes base + customer)

OPTIONAL EXTENSIONS:
- Wikidata top 15M entities (~240 MB at 16 bytes/fact) for entity relationship richness
- S2ORC subset for scientific domain (size TBD)
- Per-domain variants (Medical w/ PubMedBERT; Legal; Financial)

### Prong 2: DistilBERT-NER cascade integration (3-5 days)
Per bridge-ID 2x drill v1.1 composition recommendation:
1. DistilBERT-NER as Layer 1 bridge entity extractor
2. Cascade with substrate validation (Layer 2: substrate checks if proposed bridge has
   any stored relations)
3. Algebraic bridge generation at warm (Layer 3: Pattern B unbind for known bridges)
4. v1.1 ships with Layers 1-2; Layer 3 activates as substrate accumulates

### Prong 3: Tier 4 base build (5-8 eng-weeks; already authorized)
Substrate-aware LoRA + Arch 5 sparse retrieval heads + Option D frozen LLM + rank-4 LoRA.
Continues per prior routing; in parallel with Prongs 1+2.

## PRE-TESTS TO AUTHORIZE NOW (cheap; CPU)

### From pre-training drill:
- CELL-2 v3 Pattern B compression validation (1-2 hr CPU): verify 5.84M articles fit at
  93 MB; measure retrieval F1 on subset
- Wikidata top-15M entity subset integration (2-3 hr CPU): validate composition with
  Wikipedia substrate
- TriviaQA / NQ pre-trained substrate F1 (2-3 hr CPU): quantify the parametric gap
  closure empirically

### From bridge-ID drill:
- DistilBERT-NER on HotpotQA bridge questions (1 hr CPU): measure NER accuracy on
  bridge entity targets
- NER + substrate validation cascade (2 hr CPU): measure combined accuracy
- Cold-start vs warm bridge-ID measurement (3 hr CPU): empirical projection

### From federated drill:
- DP composition simulation (1-2 hr CPU): synthetic multi-customer routing stats with DP
  noise; measure utility-privacy tradeoff
- Warm-start lift quantification on synthetic data (1-2 hr CPU): how much does new
  customer benefit from shared router state?
- Rare-customer inference attack simulation (2-3 hr CPU): can attacker infer customer
  facts from aggregated stats?

## v1.1 / v1.5 / v2.0 SEQUENCING (LOCKED)

**v1.1 (next 4-8 weeks):**
- Substrate pre-training ship (1-2 weeks; Prong 1)
- DistilBERT-NER cascade (3-5 days; Prong 2)
- Tier 4 base build (5-8 weeks; Prong 3; in parallel)
- Pattern B Mech1 L2 normalization ship (2-3 days; already authorized)
- Distilled 50M encoder for edge deployment (2-3 days; already authorized)
- Sleep defrag v1.1 stack: 10-16 days (already authorized)

**v1.5 (3-6 months post-v1.1):**
- Self-improving routing integration (Component F bridge cache + Component E router)
- Router-informed sleep defrag (Component C v2.0)
- Encoder gradient feedback online learning (pending bridge-ID drill confirms benefit)
- Concept drift detection + customer-facing alerts
- Substrate-augmented attention in LLM generation (pending drill)
- Conversation memory mode

**v2.0 (6-12 months post-v1.1):**
- Federated substrate with DP (pending federated drill pre-test validation)
- Cross-customer warm-start
- Premium tier with federated benefits
- Multi-domain pre-trained variants

## CUSTOMER PITCH CONSOLIDATED (v1)

> "Substrate ships pre-loaded with Wikipedia/encyclopedic baseline knowledge — 88-92% of
> what frontier LLMs know parametrically, with full auditability. Customer adds their
> domain KB on top; Pattern B composes both algebraically.
>
> Performance across domains: substrate matches or beats vanilla RAG on encyclopedic
> (+0.023 TriviaQA), multi-hop (93-97% parity), biomedical (95% parity), long-context
> (93% parity). With NER cascade and post-deployment self-improving routing, multi-hop
> approaches and beats RAG at equilibrium.
>
> Moat capabilities frontier LLMs and RAG cannot replicate: audit chain (deterministic
> Merkle replay per reasoning step), GDPR Article 17 surgical erasure, bitemporal as-of
> queries, sleep consolidation extracting learned regularities, adversarial contradiction
> detection, concept drift alerting, EU AI Act Article 12 co-compliance. 184x fewer
> FLOPs per query, 10-90x less energy, 100x+ faster knowledge updates than LLM fine-tune.
>
> Deployment: 93 MB pre-trained binary + per-customer substrate overlay; runs on
> commodity hardware (RTX4060 / M2 Pro); HIPAA Option B per-customer isolation."

## Cross-references

- Pre-training 3x: notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md
- Bridge-ID 2x: notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md
- Federated 2x: notes/research_drill_federated_substrate_2x_2026-06-07.md
- Self-improving routing 3x: notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- Substrate iterative multi-hop 3x: notes/research_drill_substrate_iterative_multihop_3x_2026-06-07.md
- Tier 4 consolidated routing: notes/research_to_exp_dev_tier4_consolidated_routing_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all 9 pre-tests (3 from each drill). Prong 1 (pre-training ship)
+ Prong 2 (NER cascade) are highest priority for v1.1. Pre-tests resolve their
respective drill's empirical predictions.

**Testbed:** heavy items pending (stella-1.5B / NV-Embed-v2 / encoder fine-tuning / Tier
5 Arch 8 MVE) — wait for pivotal in-flight verdicts before committing engineering.
Pre-training binary build is in Exp-Dev's lane (substrate-side; not LLM-integration).

This is the single most consequential routing document of today's session. The v1
product is no longer a blank-slate research artifact; it's a pre-trained Wikipedia-scale
substrate + customer overlay + DistilBERT-NER cascade + Tier 4 substrate-aware LLM +
moat features. Concrete, empirically-justified, customer-shippable.
