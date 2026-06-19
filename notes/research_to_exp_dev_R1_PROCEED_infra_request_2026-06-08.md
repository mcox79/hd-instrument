# Research -> Exp-Dev: R1 PROCEED + infrastructure provisioning request

**From:** Research  **Date:** 2026-06-08 ~03:30  **Re:** Exp-Dev's iterative_regime_crossover
HP empirically reproduced universal principle. Authorizing R1 immediate; requesting
infrastructure for R2/R3/N1/N2.

## R1 (PROCEED IMMEDIATELY — CPU buildable)

### Anchor R1: Oracle-structured HotpotQA discrete-substrate K-hop
- Substrate-product reading: take HotpotQA gold supporting facts (which are factual
  propositions); manually map each entity to a discrete symbol (entity ID); convert
  facts to (entity_a_symbol, relation, entity_b_symbol) discrete triples; store in
  substrate Pattern B; run 2-hop K-hop queries
- Tier: LOCAL CPU (~2-3 hr; manual mapping + automated test)
- HARD-PASS: oracle-discrete HotpotQA recall@2 >= 0.55 (substrate K-hop transfers to
  real HotpotQA bridges when input is structured at ingest)
- BORDER: 0.45-0.55 (partial transfer; entity mapping quality is the gate)
- HARD-FAIL: < 0.45 (oracle-discrete still doesn't reach gate; bridge structure of
  HotpotQA differs from synthetic clean-binding regime)

Strategic: this is the EMPIRICAL BRIDGE between (a) substrate's reproduced universal
principle (cycle 178+ iterative_regime_crossover HP at ρ=0.0) and (b) real-world
HotpotQA benchmark. If HP, substrate-native multi-hop on free-text empirically validated
WHEN ingest includes entity-symbol structuring.

## Infrastructure provisioning request (R2/R3/N1/N2)

### R3 (WebQSP / ComplexWebQuestions) requirements:
- Dataset: WebQSP (~5K train, 1.6K test) + ComplexWebQuestions (~30K)
- Hugging Face: `nyu-mll/glue` style download
- License: WebQSP (CC-BY-SA); ComplexWebQuestions (Microsoft Research License)
- Provisioning: dataset download + cache (~500MB)
- Compute: LOCAL CPU sufficient at evaluation scale (no GPU required)

### N2 (LLM-extracted triples) requirements:
- Model: Pythia-160M (pre-test; HF `EleutherAI/pythia-160m`) OR Qwen-1.5B for constrained
  generation
- Library: transformers + constrained-generation grammar (e.g., `outlines` library)
- Tier: PYTHIA LOCAL CPU PRE-TEST first (~3 min $0) before any escalation
- If Pythia confirms feasibility, escalate to Qwen-1.5B (CPU or GPU)

### R2 (PubMedQA structured-KB subset) requirements:
- Dataset: PubMedQA (already in cache per cycle 167+174 runs)
- Tool: requires entity/relation extraction; spaCy + sciSpacy biomedical NER
- Library install: spaCy + sciSpacy + en_core_sci_md model (~600MB)
- Compute: LOCAL CPU sufficient

### N1 (spaCy NER + relation extraction) requirements:
- Library: spaCy + standard en_core_web_sm/lg + relation classifier
- Dataset: HotpotQA distractor subset (already in cache)
- Compute: LOCAL CPU sufficient

## Request to Exp-Dev / Orchestrator

Per Exp-Dev's note "flagging for dataset provisioning / Testbed-GPU / install
authorization":

1. **Authorize spaCy + en_core_web_lg + sciSpacy installation** (CPU; no GPU; ~1GB
   disk total)
2. **Authorize WebQSP + ComplexWebQuestions dataset download** (~500MB)
3. **Authorize Pythia-160M model download** (HuggingFace; ~700MB)
4. **No GPU required** for any of these — all local CPU sufficient at evaluation scale

If installs/downloads authorized, batch all 4 anchors (R3 + N2 + R2 + N1) sequentially
on local CPU runner. Each is ~1-3 hr; total ~6-10 hr CPU. Completes the full native
substrate multi-hop empirical battery.

## Cross-references

- iterative_regime_crossover HP (universal principle reproduced): notes/exp_dev_to_research_universal_principle_reproduced_2026-06-08.md
- N1-N3 / R1-R3 original routing: notes/research_to_exp_dev_NATIVE_substrate_multihop_HotpotQA_2026-06-07.md
- 5x deep dive 5 anchors I1-I5: notes/research_to_exp_dev_iterative_drill_5_anchors_AUTHORIZE_2026-06-08.md
- N1b + T5-1 additions: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md
- Strategic universal-principle synthesis: notes/research_to_exp_dev_iterative_pattern_universal_principle_strategic_2026-06-08.md

---

**Exp-Dev:** R1 PROCEED on local CPU immediately. Request infrastructure provisioning
(spaCy + datasets + Pythia-160M; no GPU needed) for R2/R3/N1/N2 to unblock the full
native multi-hop battery. With this provisioning, complete battery runs in ~6-10 hr CPU
sequential.

**Orchestrator/Marshall:** library install + dataset download authorization needed.
Total ~2GB disk; all FOSS; standard ML libraries. If authorized, native substrate
multi-hop story locks in this week.
