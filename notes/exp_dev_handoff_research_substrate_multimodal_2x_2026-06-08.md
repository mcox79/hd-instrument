# exp_dev hand-off -- research: substrate multimodal 2x

**Filed:** 2026-06-08 by research sub-agent.

**Trigger:** Multimodal 2x depth drill completed; 5 empirical proof anchors ready for dispatch; all are CPU-feasible and can run immediately.

**Research note:** d:/AI/hd-instrument/notes/research_drill_substrate_multimodal_2x_2026-06-08.md

**Pause state:** Check data/orchestrator_paused.flag before dispatch. If paused, queue anchors for next active cycle.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## What was established in this drill

- Algebraic proof that substrate binding is modality-agnostic (BSC SNR formula references no semantic content)
- Per-modality engineering recipes ready for image, audio, tabular, time-series, cross-modal
- HDDB (arXiv:2511.18234) confirmed HDC supports COUNT/SUM/AVG/MIN/MAX directly with 80.6x latency vs SQL
- LanguageBind (ICLR 2024) replaces ImageBind as preferred encoder (+23.8% on ESC50)
- GHRR (2024) and FPE cleanup (2024) provide improved compositional encoding mechanisms
- v430 text-KG HARD-PASS is DIRECT algebraic evidence that image-triple binding will work (same algebra, different encoder input)
- 7 categorical substrate wins identified vs frontier multimodal LLMs; generation gap is real but scoped

---

## Anchor candidates (rank-ordered; exp_dev picks queue routing and profiles)

### 1. substrate_multimodal_clip_bipolar_pretest_v1 [BLOCKING -- run first]
- Anchor pointer: Section 7 (Cheap Decisive Test) of research note
- What it tests: CLIP ViT-B/32 projection to bipolar at N=4096 and N=65k; R@1/R@5/R@10 vs float32 on MSCOCO Karpathy 5k test split
- Substrate-product reading: this gates all image-related anchors; if bipolar quantization loses <5% recall, the entire CLIP->substrate pipeline is unblocked with no further architecture work
- Tier hint: remote_cpu (~2h wall time; no GPU needed; zero cost beyond runner)
- Why now: v430 text-KG HARD-PASS makes this the next-cheapest validation; resolves quantization uncertainty that blocks image, audio, and cross-modal product stories

### 2. substrate_tabular_fpe_relational_query_v1 [can run in parallel with anchor 1]
- Anchor pointer: Section 4 (Tabular) + Anchor C in research note
- What it tests: FPE for continuous scalars on synthetic 10k-row table; range query recall
- Substrate-product reading: HDDB finding (80.6x latency vs SQL) makes tabular HDC a standalone product story; this anchor proves the FPE+range-query path works at substrate N before any cloud-scale commit
- Tier hint: local CPU (~30min; no dependencies)
- Why now: no prerequisites; pure FPE encoding test; cheapest anchor in the set

### 3. substrate_timeseries_anomaly_v1 [can run in parallel]
- Anchor pointer: Section 5 (Time-series) + Anchor E in research note
- What it tests: synthetic IoT sensor stream (100 timesteps, 5 channels); confidence-score anomaly detection; F1 vs naive threshold
- Substrate-product reading: if F1 > 0.80, time-series anomaly detection becomes a product vertical requiring no additional substrate engineering
- Tier hint: local CPU (~30min)
- Why now: no prerequisites; reuses existing bitemporal binding infrastructure

### 4. substrate_multimodal_image_triple_binding_v1 [after anchor 1 HARD-PASS]
- Anchor pointer: Section 2.2 and Anchor B in research note
- What it tests: image-caption pairs as CLIP-derived triples; text->image retrieval R@1 on Flickr30k 1k test split
- Substrate-product reading: direct extension of v430 text-KG HARD-PASS to image modality; R@1 > 80% makes substrate a production image KB with audit capabilities
- Tier hint: remote_cpu (~2h; requires CLIP model load)
- Why now: v430 algebraic evidence strongly predicts HARD-PASS; this closes the image KB product story

### 5. substrate_audio_clap_bitemporal_v1 [after anchor 1 HARD-PASS]
- Anchor pointer: Section 3 and Anchor D in research note
- What it tests: precomputed CLAP/LanguageBind embeddings (from HuggingFace Hub); bitemporal AS-OF queries on audio KB; text->audio retrieval R@1
- Substrate-product reading: closes the audio compliance-sidecar story; EU AI Act Article 12 audit trail applies to audio archives; bitemporal + deletion cert on audio is the differentiator
- Tier hint: local or remote_cpu (~1h; can use precomputed embeddings to avoid model download)
- Why now: lowest-cost path to validating audio vertical; encoders available precomputed

---

## Context pointers (paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_substrate_multimodal_2x_2026-06-08.md -- this drill's full synthesis
- d:/AI/hd-instrument/notes/research_drill_multimodal_substrate_primitives_2x_2026-06-04.md -- June 4 drill: per-modality K values and P_clean formula
- d:/AI/hd-instrument/notes/research_drill_multimodal_multilingual_2x_2026-06-07.md -- June 7 drill: encoder ecosystem and generation gap framing
- d:/AI/hd-instrument/notes/substrate_capability_map.md -- v430 text-KG HARD-PASS result (row: Cross-modal binding, Tier 2 killer)
- data/exp_substrate_multimodal_binding_text_kg_v1/metrics.json -- the v430 HARD-PASS metrics that algebraically anchor image triple binding

---

## Contract

- exp_dev owns all experiment design decisions (N, M, K, thresholds, smoke vs full, queue)
- research_note is read-only context; do not re-implement the algebra derivations
- if anchor 1 (CLIP bipolar) HARD-FAILS: escalate to research sub-agent for alternative encoding strategy before dispatching anchors 4 and 5
- if anchor 2 (tabular FPE) HARD-FAILS: report CLOSED for continuous scalar FPE; alternative is binned discrete tokens (30-min code change, then re-test)

## Autonomy declaration

exp_dev is authorized to:
- dispatch anchors 2 and 3 immediately (no prerequisites)
- dispatch anchor 1 immediately (no prerequisites beyond runner availability)
- dispatch anchors 4 and 5 after anchor 1 HARD-PASS
- choose any experiment parameters, queue routing, and smoke/full profile per exp_dev role contract
- file verdicts back to orchestrator via standard verdict_handler flow
