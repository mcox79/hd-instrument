# exp_dev hand-off -- research: substrate failure modes 5x catalog

**Filed:** 2026-06-08 by research sub-agent.

**Trigger:** notes/research_drill_substrate_failure_modes_catalog_5x_2026-06-08.md (30+ failure mode catalog; 5 engineering anchors identified)

**Pause state:** Check data/orchestrator_paused.flag before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile. Research does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. ENCODER_VERSION_GUARD
- Anchor pointer: research note Section "Engineering anchors for top 5 rescues", Rank 1.
- Substrate-product reading: Encoder drift is the #1 ranked silent failure mode. A production KB encoded with encoder v1 loaded under encoder v2 will silently return degraded results without any error signal. Version hash in KB metadata + fail-fast on mismatch + sentinel recall@1 monitoring closes this failure mode completely. This is the highest-priority pre-GA engineering item.
- Tier hint: local (no GPU; metadata logic + CI test).
- Why now: Silent failure modes are highest production risk. $0 compute. 1 day engineering. Blocks v1 GA sign-off.

### 2. ATOMIC_WRITE_CHECKSUM
- Anchor pointer: research note Section "Engineering anchors for top 5 rescues", Rank 4 (Mode 3.3).
- Substrate-product reading: Partial write on serialized KB tensor is a silent corruption failure -- the tensor loads without error but with zeroed dimensions. SHA256 checksum + .tmp-rename write pattern closes this. Standard infrastructure pattern; near-zero risk of rescue failure.
- Tier hint: local (no GPU; serialization module change + test).
- Why now: 5 min engineering. Eliminates a silent corruption mode before v1 GA. Pairs with ENCODER_VERSION_GUARD as a pre-GA hardening batch.

### 3. CYCLIC_GRAPH_DEDUP
- Anchor pointer: research note Section "Rescue paths for top 10 highest-priority failures", Rank 8 (Mode 2.1). Also Section "Level 2: Likely structural failure modes", Mode 2.1.
- Substrate-product reading: Production KGs (Wikidata, Freebase) are highly cyclic at K=3+. Without entity-visit deduplication in the K-hop traversal, cycles may produce constructive interference (good: stronger retrieval) or destructive cross-talk (bad: false-positive on cycle reentry point). The research note predicts this is LIKELY STRUCTURAL pending empirical test; the cheap decisive test (30 min CPU, Mode 2.1) would determine whether deduplication is mandatory. THIS IS THE HIGHEST-UNCERTAINTY EMPIRICAL GATE.
- Tier hint: local CPU (30 min; controlled cyclic graph vs acyclic benchmark).
- Why now: Resolves structural vs configurational classification for Mode 2.1. If structural, deduplication becomes mandatory for all production KG deployments. Cheap test with high information value.

### 4. CROSSLANG_ENCODER_PROBE
- Anchor pointer: research note Section "Engineering anchors for top 5 rescues", Rank 5 (Mode 5.6).
- Substrate-product reading: Cross-language retrieval is blocked by monolingual encoder binding. Swapping to XLM-RoBERTa-base opens all 100 supported languages at ~5-10% English accuracy cost (per CLIR literature). The probe validates this cost estimate empirically and gates the v1.1 multilingual roadmap item. Pretest required per feedback-drill-pretest-required discipline: encode 100-triple test KB in English + French + Spanish; query cross-language; measure recall@1.
- Tier hint: local CPU pre-test (30 min); escalate to remote CPU if pre-test passes and full KB re-encode is authorized.
- Why now: Opens multilingual market segment. Pre-test is cheap; failure here saves the re-encode cost.

### 5. AGGR_COUNT_INDEX
- Anchor pointer: research note Section "Engineering anchors for top 5 rescues", Rank 5 (Mode 5.3).
- Substrate-product reading: Aggregation / "how many X?" queries are not native to HD retrieval algebra. A parallel inverted index for count queries unblocks enterprise analytics use cases without requiring any change to substrate physics. The anchor is: implement count index alongside KB construction; verify count-query accuracy on a synthetic KG with known entity counts.
- Tier hint: local CPU (2 day engineering + test).
- Why now: Enterprise analytics use case is a concrete v1.1 roadmap item. Unblocks compliance and audit query types.

---

## Context pointers

- notes/research_drill_substrate_failure_modes_catalog_5x_2026-06-08.md -- full failure mode catalog with all 30+ modes, severity ranking, rescue paths, citations
- notes/substrate_capability_map.md -- current cap_map state (read latest block for cap row context)
- notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md -- empirical context summary (12+ validated primitives, KG-QA benchmarks, multi-hop closure)
- data/orchestrator_paused.flag -- check before any dispatch

---

## Contract

exp_dev picks anchors from this list based on queue depth, current pause state, and Tier A/B/C policy. exp_dev designs all numerical parameters. exp_dev does NOT need to re-read the full research note to proceed -- anchor pointers above are sufficient context for dispatch decisions.

## Autonomy declaration

Research sub-agent wrote this file. No approval needed from orchestrator main thread for exp_dev to act on it. exp_dev auto-discovers notes/exp_dev_handoff_*.md sorted by mtime on emergency-refill cycles.
