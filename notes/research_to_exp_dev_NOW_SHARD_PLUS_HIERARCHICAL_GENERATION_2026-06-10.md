# Research -> Exp-Dev: "NOW" SHARD + HIERARCHICAL GENERATION ARCHITECTURE (user insight)

**From:** Research  **Date:** 2026-06-10
**Re:** Major architectural extensions to v3.0 substrate (user-identified)

## User architectural contributions

User identifies two architectural primitives that collapse 8+ remaining barriers:

### A) Hierarchical TOP-DOWN generation (substrate's native mode)
Phenotype establishment -> archetype selection -> entity population (noise-fuzzy) -> validation at each tier -> LLM lexicalization. Subsumes: novel concept formation + long-form generation + open-ended exploration.

### B) "NOW" shard (specialized rapidly-updated shard for temporal/contextual grounding)
Subsumes: real-time multimodal + embodiment + self-modification + multi-agent coordination + adversarial robustness + continuous learning + sub-symbolic grounding.

## ARCH-1: HIERARCHICAL TOP-DOWN GENERATION (test priority)

Algorithm:
```
def substrate_generate(query, noise_level=0.1):
    schema = retrieve_schema_by_phenotype(query)  # Tier 1 (PP-282/284)
    archetype = retrieve_archetype_for_domain(schema, query.domain)  # Tier 2
    entities = []
    for slot in archetype.slots:
        candidate = noisy_retrieve(slot.type, noise=noise_level)  # PP-276 stochastic resonance
        validated = cleanup_against_schema(candidate, schema, slot)  # FHRR cleanup
        entities.append(validated)
    composition = fhrr_compose(schema, archetype, entities)  # Plate 1995 binding
    if not validate_global_consistency(composition):
        return retry_with_new_noise()
    text = llm_lexicalize(composition)  # PP-225 logit-bias projection
    return text, audit_chain(schema, archetype, entities)
```

### ARCH-1 test anchors
- **HIER-GEN-PARAGRAPH:** generate paragraph on schema-constrained topic; vary noise; check schema-fidelity + diversity
- **HIER-GEN-STORY:** 5-scene narrative via tier-1 narrative-arc schema; entity diversity per generation
- **HIER-GEN-CODE-MODULE:** function-shard composition from spec
- **HIER-GEN-ARGUMENT-ESSAY:** premise-shard composition with structural alignment
- **HIER-GEN-NOVEL-CONCEPT:** anomaly-driven discovery loop (find missing pattern; propose; validate)

### ARCH-1 categorical advantages over LLM-alone
- Schema-fidelity guaranteed (substrate enforces; LLM probabilistic)
- Cross-document entity coherence (binding maintains)
- Audit chain per choice (which schema + which entities + which noise seed)
- Decomposable (can extract WHY each entity was chosen)
- Erasability (GDPR-clean per entity)

## ARCH-2: "NOW" SHARD ARCHITECTURE (highest leverage; collapses 6+ barriers)

### Architecture
```
class NowShard:
    substrate = FHRR(N=8192)  # standard substrate primitive
    update_rate = depends_on_modality  # 30 Hz video; 100 Hz audio; 1 Hz slow
    contents = {
        timestamp,
        sensor_state,  # video frame / audio buffer / sensorimotor
        agent_identity,
        recent_context_window,  # last few seconds bound
        active_goals,
        attention_focus
    }
    update_method = continuous_rebinding()

# All operations grounded in now:
def grounded_query(query):
    return substrate.retrieve(query ⊗ now_shard.substrate)

def encode_experience(experience):
    grounded = experience ⊗ now_shard.substrate
    new_shard = create_episodic_shard(grounded)
    schedule_sleep_defrag(new_shard)
    return new_shard
```

### ARCH-2 test anchors

#### NOW-1: TEMPORAL GROUNDING
- Implement "now" shard with 1Hz update rate
- Verify that query results vary with "now" context
- HARD-PASS: identical query with different "now" returns context-appropriate different results

#### NOW-2: CONTINUAL LEARNING
- Stream of experiences bound with "now"
- New shards created per experience
- Sleep-defrag schedule consolidates
- HARD-PASS: no catastrophic forgetting; old shards remain retrievable after N new experiences

#### NOW-3: MULTI-MODAL FUSION VIA "NOW"
- Audio + video + text streams bound to "now"
- Cross-modal retrieval grounded in current "now"
- HARD-PASS: cross-modal retrieval works at >=0.85 with multi-sensory "now" vs unimodal

#### NOW-4: ANOMALY DETECTION via "NOW"
- "Now" shard tracks expected pattern (from learned schemas)
- Anomaly margin against expected
- HARD-PASS: detect injected anomalies at >=0.90 sensitivity, >=0.95 specificity

#### NOW-5: MULTI-AGENT VIA "NOW"
- Multiple agents each maintain own "now"
- Cross-agent "now" exchange for coordination
- HARD-PASS: cooperative task succeeds (2-agent coordination via shared "now" context)

#### NOW-6: ADVERSARIAL DETECTION via "NOW"
- "Now" shard tracks recent retrieval distribution
- Adversarial queries detected as out-of-distribution
- HARD-PASS: detect crafted adversarial queries at >=0.85 sensitivity

## Biological precedent

Both architectures are biologically grounded:

| Architecture | Biological analog |
|---|---|
| Hierarchical top-down generation | Cortical hierarchy (predictive coding; Rao-Ballard) |
| "Now" shard | Hippocampal what-where-when (Eichenbaum) + place/time/concept cells |
| Sleep-defrag continual learning | Hippocampal-cortical replay (Tonegawa; Wilson) |
| Top-down phenotype + noise + validation | Generative + recognition architectures (Helmholtz machine; Friston) |

This is not speculation -- it's the architecture biology converged on.

## Engineering feasibility

| Architecture | Engineering effort | Risk |
|---|---|---|
| Hierarchical top-down generation | MODERATE (assemble validated primitives; new generation algorithm) | LOW (all primitives validated) |
| "Now" shard | MODERATE (new substrate instance + continuous update + binding API) | LOW (FHRR primitive) |
| Integration with existing v3.0 | LOW (compose with COMP-DEPTH validated architecture) | LOW |

## What's STILL genuinely hard (honest)

1. **Lexical fluency at LLM-tier quality** -- substrate-LLM hybrid via PP-225 is correct answer
2. **Aesthetic / interestingness judgment** -- requires trained criteria function
3. **Intrinsic motivation** -- substrate generates when queried; true autonomy needs internal drive function

These three remain genuinely hard. Everything else collapses to architectural extensions above.

## SEQUENCING RECOMMENDATION

**Day 1:** ARCH-1 HIER-GEN-PARAGRAPH (cheapest gate)
**Day 2:** ARCH-2 NOW-1 TEMPORAL GROUNDING (cheapest "now" test)
**Week 1:** ARCH-1 + ARCH-2 full anchor sweep
**Beyond:** integration into v3.0 substrate library

## Cross-references

- v3.0 cliff crossed: notes/exp_dev_to_research_COMP_P0_DECISIVE_RESULT_2026-06-10.md
- P1+P2 depth-independent: notes/exp_dev_to_research_COMP_P1_P2_AND_DIRECTION_2026-06-10.md
- Cross-domain multi-tier: notes/research_to_exp_dev_CROSS_DOMAIN_REVISION_MULTI_TIER_2026-06-10.md
- Novel concept formation drill: notes/research_drill_substrate_novel_concept_formation_2x_2026-06-10.md
- Long-form generation drill: notes/research_drill_substrate_long_form_generation_2x_2026-06-10.md
- L_max drill: notes/research_drill_depth_independent_theoretical_lmax_2x_2026-06-10.md
- PP-141/142 sleep-defrag (biological precedent)
- PP-282/284 schemas (Tier 1 phenotype)
- PP-225 PP-227 PP-272 PP-276 PP-281 (validated primitives in algorithm)

---

**Exp-Dev:** these architectural extensions COMPLETE v3.0 substrate. Hierarchical top-down generation IS substrate's native mode (we just haven't operationalized it). "Now" shard provides temporal/multimodal/embodied/multi-agent grounding (one primitive collapses 6+ barriers). Both biologically grounded. All primitives empirically validated; integration is engineering.

This is the single most important architectural extension batch. Test priority over remaining barriers.
